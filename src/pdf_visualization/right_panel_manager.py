from PyQt6.QtWidgets import QApplication, QPushButton, QPlainTextEdit, QCheckBox
from PyQt6.QtCore import Qt

from typing import Optional
from typing import TYPE_CHECKING

# always false at running time. It is used for mypy typing check and avoiding circular imports
if TYPE_CHECKING:
    from pdf_visualization.pdf_visualization_model import PDFWindowVisualizationModel
from pdf_visualization.cards_navigator import (
    CardNavigator,
)
from flashcard.flashcard import Flashcard
from flashcard.pdf_page import PdfPage
from flashcard.card import Card


class RightPanelManager:
    def __init__(self, pdf_visualization_model: "PDFWindowVisualizationModel") -> None:
        self.__pdf_visualization_model: "PDFWindowVisualizationModel" = (
            pdf_visualization_model
        )

    def add_page_flashcard(self, flag_generic: bool = False) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        app: Optional[Flashcard] = self.__get_new_flashcard()
        if app is None:
            return
        flashcard: Flashcard = app

        if flag_generic:
            flashcard.set_reference_page(Flashcard.GENERIC_PAGE)
            flashcard.set_question_type(Flashcard.QuestionType.GENERIC)

        index_in_list: int = self.__get_index_list_position()

        self.__add_flashcard_at_index(flashcard, index_in_list)

        self.__get_cards_navigator().set_current_card_index(
            self.__get_current_card_index() + 1
        )
        self.__pdf_visualization_model.save_flashcards_to_file()
        self.clear_input_fields()

        QApplication.restoreOverrideCursor()

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
        if self.__get_page_specific_checkbox().isChecked():
            flashcard.set_question_type(Flashcard.QuestionType.PAGE_SPECIFIC)
        else:
            flashcard.set_question_type(Flashcard.QuestionType.GENERIC)

        return flashcard

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
        while flashcards_current_page[i] != current_flashcard:
            i += 1
            if i >= len(flashcards_current_page):
                raise ValueError("Not expected value")

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

        self.__pdf_visualization_model.refresh_merged_cards(
            self.__get_is_deck_ordered()
        )

    def remove_current_flashcard(self) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        card: Card = self.__get_cards_to_display()[self.__get_current_card_index()]
        if isinstance(
            card,
            PdfPage,
        ):
            raise TypeError()

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

    def __get_cards_navigator(self) -> CardNavigator:
        return self.__pdf_visualization_model.get_cards_navigator()

    def __get_is_deck_ordered(self) -> bool:
        return self.__pdf_visualization_model.get_is_deck_ordered()

    def update_remove_flashcard_button(self) -> None:
        if isinstance(
            self.__get_cards_to_display()[self.__get_current_card_index()],
            Flashcard,
        ):
            self.__get_remove_flashcard_button().setDisabled(False)
        else:
            self.__get_remove_flashcard_button().setDisabled(True)

    def __get_cards_to_display(self) -> list[Card]:
        return self.__pdf_visualization_model.get_cards_to_display()

    def __get_current_card_index(self) -> int:
        return self.__pdf_visualization_model.get_current_card_index()

    def __get_remove_flashcard_button(self) -> QPushButton:
        return self.__pdf_visualization_model.get_remove_flashcard_button()

    def modify_current_flashcard(self) -> None:
        pass

    def __get_flashcards_from_pdf_page(self) -> dict[int, list[Flashcard]]:
        return self.__pdf_visualization_model.get_flashcards_from_pdf_page()
