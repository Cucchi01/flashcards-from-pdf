# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from PyQt6.QtWidgets import QApplication, QPushButton, QPlainTextEdit, QCheckBox
from PyQt6.QtCore import Qt

from typing import Optional
from typing import TYPE_CHECKING

# always false at running time. It is used for mypy typing check and avoiding circular imports
if TYPE_CHECKING:
    from pdf_visualization.pdf_visualization_model import PDFWindowVisualizationModel
    from pdf_visualization.cards_navigator import CardsNavigator
from flashcard.flashcard import Flashcard
from flashcard.pdf_page import PdfPage
from flashcard.card import Card


class RightPanelManager:
    def __init__(self, pdf_visualization_model: "PDFWindowVisualizationModel") -> None:
        self.__pdf_visualization_model: "PDFWindowVisualizationModel" = (
            pdf_visualization_model
        )
        self.__is_flashcard_being_modified = False
        self.__current_modified_flashcard: Flashcard

    def manage_page_button_flashcard(self, flag_generic: bool = False) -> None:
        # the question cannot be empty
        if (
            self.__pdf_visualization_model.get_input_text_question()
            .toPlainText()
            .strip()
            == ""
        ):
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        if self.__is_flashcard_being_modified:
            self.__modify_flashcard(flag_generic)
        else:
            self.__add_page_flashcard(flag_generic)

        self.__pdf_visualization_model.save_flashcards_to_file()
        self.clear_input_fields()
        QApplication.restoreOverrideCursor()

    def __modify_flashcard(self, flag_generic: bool) -> None:
        flashcard: Flashcard = self.__current_modified_flashcard
        flashcard.set_question(
            self.__pdf_visualization_model.get_input_text_question().toPlainText()
        )
        flashcard.set_answer(
            self.__pdf_visualization_model.get_input_text_answer().toPlainText()
        )

        # remove flashcard from old position
        self.__get_flashcards_from_pdf_page()[flashcard.get_reference_page()].remove(
            flashcard
        )

        if flag_generic:
            flashcard.set_reference_page(Flashcard.GENERIC_PAGE)
            flashcard.set_question_type(Flashcard.QuestionType.GENERIC)
        else:
            flashcard.set_reference_page(
                self.__pdf_visualization_model.get_current_page_index()
            )
            self.__set_page_specific_field(flashcard)

        # add flashcard in the new position
        index_in_list: int = self.__get_index_list_position()
        self.__add_flashcard_at_index(flashcard, index_in_list)

        self.__pdf_visualization_model.refresh_merged_cards(
            self.__get_is_deck_ordered()
        )

        self.__is_flashcard_being_modified = False
        self.__reset_card_before_modification(flashcard)

    def __get_flashcard_index(self, flashcard_to_search: Flashcard) -> int:
        i: int = 0
        list_flashcards: list[Flashcard]
        for _, list_flashcards in sorted(
            self.__get_flashcards_from_pdf_page().items(), key=lambda x: x[0]
        ):
            for flashcard in list_flashcards:
                if flashcard == flashcard_to_search:
                    return i
                i += 1
        return -1

    def __add_page_flashcard(self, flag_generic: bool = False) -> None:
        app: Optional[Flashcard] = self.__get_new_flashcard()
        if app is None:
            return
        flashcard: Flashcard = app

        if flag_generic:
            flashcard.set_reference_page(Flashcard.GENERIC_PAGE)
            flashcard.set_question_type(Flashcard.QuestionType.GENERIC)

        index_in_list: int = self.__get_index_list_position()

        self.__add_flashcard_at_index(flashcard, index_in_list)

        self.__pdf_visualization_model.refresh_merged_cards(
            self.__get_is_deck_ordered()
        )

        self.__get_cards_navigator().set_current_card_index(
            self.__get_current_card_index() + 1
        )

    def __get_new_flashcard(self) -> Optional[Flashcard]:
        flashcard: Flashcard = Flashcard()

        flashcard.set_reference_page(
            self.__pdf_visualization_model.get_current_page_index()
        )

        question_text: str = self.__get_input_text_question().toPlainText().strip()
        if question_text == "":
            self.__get_input_text_question().setStyleSheet("border: 1px solid red;")
            self.__get_input_text_question().setFocus(Qt.FocusReason.OtherFocusReason)
            return None
        else:
            self.__get_input_text_question().setStyleSheet("border: 1px solid black;")

        flashcard.set_question(question_text)
        answer_text: str = self.__get_input_text_answer().toPlainText().strip()
        flashcard.set_answer(answer_text)
        self.__set_page_specific_field(flashcard)

        return flashcard

    def __set_page_specific_field(self, flashcard: Flashcard) -> None:
        if (
            self.__get_page_specific_checkbox().isChecked()
            and flashcard.get_reference_page() != Flashcard.GENERIC_PAGE
        ):
            flashcard.set_question_type(Flashcard.QuestionType.PAGE_SPECIFIC)
        else:
            flashcard.set_question_type(Flashcard.QuestionType.GENERIC)

    def clear_input_fields(self) -> None:
        self.__get_input_text_question().setPlainText("")
        self.__get_input_text_answer().setPlainText("")
        self.__get_page_specific_checkbox().setChecked(True)

    def __get_input_text_question(self) -> QPlainTextEdit:
        return self.__pdf_visualization_model.get_input_text_question()

    def __get_input_text_answer(self) -> QPlainTextEdit:
        return self.__pdf_visualization_model.get_input_text_answer()

    def __get_page_specific_checkbox(self) -> QCheckBox:
        return self.__pdf_visualization_model.get_page_specific_checkbox()

    def __get_index_list_position(self) -> int:
        current_card: Card = self.__get_cards_to_display()[
            self.__get_current_card_index()
        ]
        flashcards_current_page: Optional[
            list[Flashcard]
        ] = self.__get_flashcards_from_pdf_page().get(current_card.get_pdf_page())
        current_flashcard: Flashcard
        if isinstance(current_card, Flashcard):
            current_flashcard = current_card
        else:
            if flashcards_current_page is None:
                return 0
            return len(flashcards_current_page)

        if flashcards_current_page is None:
            raise ValueError("Not expected value")
        i: int = 0
        while (
            i < len(flashcards_current_page)
            and flashcards_current_page[i] != current_flashcard
        ):
            i += 1

        return i

    def __add_flashcard(self, flashcard: Flashcard):
        if (
            flashcard.get_reference_page()
            in self.__get_flashcards_from_pdf_page().keys()
        ):
            self.__get_flashcards_from_pdf_page()[
                flashcard.get_reference_page()
            ].append(flashcard)
        else:
            self.__get_flashcards_from_pdf_page()[flashcard.get_reference_page()] = [
                flashcard
            ]

        self.__pdf_visualization_model.refresh_merged_cards(
            self.__get_is_deck_ordered()
        )

    def __add_flashcard_at_index(self, flashcard: Flashcard, index_in_list):
        if (
            flashcard.get_reference_page()
            in self.__get_flashcards_from_pdf_page().keys()
        ):
            self.__get_flashcards_from_pdf_page()[
                flashcard.get_reference_page()
            ].insert(index_in_list, flashcard)
        else:
            self.__get_flashcards_from_pdf_page()[flashcard.get_reference_page()] = [
                flashcard
            ]

    def remove_current_flashcard(self) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        card: Card = self.__get_cards_to_display()[self.__get_current_card_index()]
        if isinstance(
            card,
            PdfPage,
        ):
            return

        flashcard: Flashcard = card
        self.__get_flashcards_from_pdf_page()[flashcard.get_reference_page()].remove(
            flashcard
        )

        self.__pdf_visualization_model.refresh_merged_cards(
            self.__get_is_deck_ordered()
        )
        self.__pdf_visualization_model.save_flashcards_to_file()
        self.__get_cards_navigator().set_current_card_index(
            self.__get_current_card_index()
        )
        QApplication.restoreOverrideCursor()

    def __get_cards_navigator(self) -> "CardsNavigator":
        return self.__pdf_visualization_model.get_cards_navigator()

    def __get_is_deck_ordered(self) -> bool:
        return self.__pdf_visualization_model.get_is_deck_ordered()

    def update_add_flashcard_button(self) -> None:
        if self.get_is_flashcard_being_modified() == True:
            self.__get_page_flashcard_button().setText("Modify flashcard")
        else:
            self.__get_page_flashcard_button().setText("Add flashcard")

    def __get_page_flashcard_button(self) -> QPushButton:
        return self.__pdf_visualization_model.get_page_flashcard_button()

    def update_add_generic_flashcard_beginning_button(self) -> None:
        if self.get_is_flashcard_being_modified() == True:
            self.__get_generic_flashcard_beginning_button().setText(
                "Modify generic flashcard at the beginning"
            )
        else:
            self.__get_generic_flashcard_beginning_button().setText(
                "Add generic flashcard at the beginning"
            )

    def __get_generic_flashcard_beginning_button(self) -> QPushButton:
        return self.__pdf_visualization_model.get_generic_flashcard_beginning_button()

    def update_remove_flashcard_button(self) -> None:
        if isinstance(
            self.__get_cards_to_display()[self.__get_current_card_index()],
            Flashcard,
        ):
            self.__get_remove_flashcard_button().setDisabled(False)
        else:
            self.__get_remove_flashcard_button().setDisabled(True)

    def update_cancel_modification_flashcard_button(self) -> None:
        if self.get_is_flashcard_being_modified() == True:
            self.__get_cancel_modification_flashcard_button().setEnabled(True)
        else:
            self.__get_cancel_modification_flashcard_button().setEnabled(False)

    def __get_cancel_modification_flashcard_button(self) -> QPushButton:
        return self.__pdf_visualization_model.get_cancel_modification_flashcard_button()

    def __get_cards_to_display(self) -> list[Card]:
        return self.__pdf_visualization_model.get_cards_to_display()

    def __get_current_card_index(self) -> int:
        return self.__pdf_visualization_model.get_current_card_index()

    def __get_remove_flashcard_button(self) -> QPushButton:
        return self.__pdf_visualization_model.get_remove_flashcard_button()

    def modify_current_flashcard(self) -> None:
        if (
            isinstance(
                self.__get_cards_to_display()[self.__get_current_card_index()],
                Flashcard,
            )
            == False
        ):
            return
        flashcard: Flashcard = self.__get_cards_to_display()[
            self.__get_current_card_index()
        ]
        self.__set_right_panel_flashcard(flashcard)
        self.__is_flashcard_being_modified = True
        self.__current_modified_flashcard = flashcard
        reference_page_card_index: int = self.__get_reference_page_card_index(flashcard)
        self.__get_cards_navigator().set_current_card_index(reference_page_card_index)

    def __get_reference_page_card_index(self, flashcard: Flashcard) -> int:
        reference_page_card_index: int
        if flashcard.get_reference_page() == Flashcard.GENERIC_PAGE:
            reference_page_card_index = self.get_num_pdf_page_to_card_index()[0]
        else:
            reference_page_card_index = self.get_num_pdf_page_to_card_index()[
                flashcard.get_reference_page()
            ]
        return reference_page_card_index

    def __set_right_panel_flashcard(self, flashcard: Flashcard) -> None:
        flashcard.set_reference_page(flashcard.get_reference_page())
        self.__set_input_text_question(flashcard.get_question())
        self.__set_input_text_answer(flashcard.get_answer())

        if flashcard.get_question_type() == Flashcard.QuestionType.GENERIC:
            self.__get_page_specific_checkbox().setChecked(False)
        else:
            self.__get_page_specific_checkbox().setChecked(True)

    def get_num_pdf_page_to_card_index(self) -> list[int]:
        return self.__pdf_visualization_model.get_num_pdf_page_to_card_index()

    def get_num_flashcard_to_card_index(self) -> list[int]:
        return self.__pdf_visualization_model.get_num_flashcard_to_card_index()

    def __set_input_text_question(self, string: str) -> None:
        return self.__pdf_visualization_model.set_input_text_question(string)

    def __set_input_text_answer(self, string: str) -> None:
        return self.__pdf_visualization_model.set_input_text_answer(string)

    def __get_flashcards_from_pdf_page(self) -> dict[int, list[Flashcard]]:
        return self.__pdf_visualization_model.get_flashcards_from_pdf_page()

    def get_is_flashcard_being_modified(self) -> bool:
        return self.__is_flashcard_being_modified

    def cancel_current_flashcard_modification(self) -> None:
        if self.__is_flashcard_being_modified == False:
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.__is_flashcard_being_modified = False
        self.__reset_card_before_modification(self.__current_modified_flashcard)
        self.clear_input_fields()
        QApplication.restoreOverrideCursor()

    def __reset_card_before_modification(self, flashcard: Flashcard) -> None:
        flashcard_index: int = self.__get_flashcard_index(flashcard)
        # riposition on the flashcard
        self.__get_cards_navigator().set_current_card_index(
            self.get_num_flashcard_to_card_index()[flashcard_index]
        )
