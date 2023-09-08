from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import Qt, QPointF
from PyQt6 import QtPdf, QtPdfWidgets

import os
from typing import Optional
from random import shuffle

from pdf_visualization.pdf_visualization_layout import PDFWindowVisualizationLayout
from pdf_visualization.cards_navigator import (
    CardNavigator,
    merge_cards_shuffle,
    merge_cards_ordered,
)
from flashcard.flashcard import Flashcard
from flashcard.pdf_page import PdfPage
from flashcard.card import Card
from IO_flashcards_management import IOFlashcards
from test_management.pdf_test_info import PDFTestsInfo


class PDFWindowVisualizationModel:
    def __init__(self, path_of_pdf: str) -> None:
        path_without_ext: str
        path_without_ext, _ = os.path.splitext(path_of_pdf)
        path_of_flashcards: str = path_without_ext + ".txt"

        is_flashcards_file_present: bool = os.path.isfile(path_of_flashcards)

        if not is_flashcards_file_present:
            with open(path_of_flashcards, "w", encoding="utf-8") as file:
                file.write("0\n0\n0\n")

        self.__io_flashcards_info: PDFTestsInfo = IOFlashcards.get_past_tests_info(
            path_of_flashcards
        )
        self.__flashcards_from_pdf_page: dict[
            int, list[Flashcard]
        ] = IOFlashcards.get_flashcards_from_txt(path_of_flashcards)

        self.__path_of_pdf: str = path_of_pdf
        self.__filename: str = os.path.basename(path_of_pdf)
        self.__num_pdf_pages: int = IOFlashcards.get_pdf_page_count(self.__path_of_pdf)
        self.__point: QPointF = QPointF(0, 0)

        self.__cards_to_display: list[Card]
        self.__num_pdf_page_to_card_index: list[int]
        self.__num_flashcard_to_card_index: list[int]

        (
            self.__cards_to_display,
            self.__num_pdf_page_to_card_index,
            self.__num_flashcard_to_card_index,
        ) = merge_cards_ordered(self.__flashcards_from_pdf_page, self.__num_pdf_pages)
        self.__is_deck_ordered: bool = True

        self.__cards_navigator: CardNavigator = CardNavigator(self)

        self.__window_layout: PDFWindowVisualizationLayout = (
            PDFWindowVisualizationLayout(self.__filename, self.__num_pdf_pages)
        )

        self.__setup_window_layout()
        self.__cards_navigator.set_current_card_index(0)

    def get_flashcards_from_pdf_page(self) -> dict[int, list[Flashcard]]:
        return self.__flashcards_from_pdf_page

    def get_num_pdf_pages(self) -> int:
        return self.__num_pdf_pages

    def get_cards_to_display(self) -> list[Card]:
        return self.__cards_to_display

    def get_num_pdf_page_to_card_index(self) -> list[int]:
        return self.__num_pdf_page_to_card_index

    def get_num_flashcard_to_card_index(self) -> list[int]:
        return self.__num_flashcard_to_card_index

    def get_num_cards(self) -> int:
        return len(self.__cards_to_display)

    def get_flashcard_label_text(self) -> str:
        return self.__window_layout.get_flashcard_label().text()

    def set_flashcard_label_text(self, new_string: str) -> str:
        return self.__window_layout.get_flashcard_label().setText(new_string)

    def get_previous_page_button(self) -> QPushButton:
        return self.__window_layout.get_previous_page_button()

    def get_next_page_button(self) -> QPushButton:
        return self.__window_layout.get_next_page_button()

    def get_previous_flashcard_button(self) -> QPushButton:
        return self.__window_layout.get_previous_flashcard_button()

    def get_next_flashcard_button(self) -> QPushButton:
        return self.__window_layout.get_next_flashcard_button()

    def get_previous_card_button(self) -> QPushButton:
        return self.__window_layout.get_previous_card_button()

    def get_next_card_button(self) -> QPushButton:
        return self.__window_layout.get_next_card_button()

    def get_is_deck_ordered(self) -> bool:
        return self.__is_deck_ordered

    def __setup_window_layout(self) -> None:
        self.__setup_left_panel()
        self.__setup_bottom_widget()

    def get_current_page_index(self) -> int:
        return self.__cards_to_display[
            self.__cards_navigator.get_current_card_index()
        ].get_pdf_page()

    def shuffle_button_pressed(self) -> None:
        self.refresh_page(not self.__is_deck_ordered)

    def refresh_page(self, is_deck_ordered: bool) -> None:
        if is_deck_ordered:
            self.__reorder_cards()
            self.__window_layout.get_shuffle_button().setText("Shuffle")
            self.__window_layout.get_pdf_page_num_spinbox().setDisabled(False)
        else:
            self.__shuffle_cards()
            self.__window_layout.get_shuffle_button().setText("Order")
            self.__window_layout.get_pdf_page_num_spinbox().setDisabled(True)

    def __reorder_cards(self) -> None:
        self.__refresh_merged_cards(ordered_deck=True)
        self.__is_deck_ordered = True
        self.__cards_navigator.restart_visualization()

    def __shuffle_cards(self) -> None:
        self.__refresh_merged_cards(ordered_deck=False)
        self.__is_deck_ordered = False
        self.__cards_navigator.restart_visualization()

    def __refresh_merged_cards(self, ordered_deck: bool) -> None:
        if ordered_deck:
            (
                self.__cards_to_display,
                self.__num_pdf_page_to_card_index,
                self.__num_flashcard_to_card_index,
            ) = merge_cards_ordered(
                self.__flashcards_from_pdf_page, self.__num_pdf_pages
            )
        else:
            (
                self.__cards_to_display,
                self.__num_pdf_page_to_card_index,
                self.__num_flashcard_to_card_index,
            ) = merge_cards_shuffle(
                self.__flashcards_from_pdf_page, self.__num_pdf_pages
            )

    def update_page_spinbox_change(self) -> None:
        if not self.__is_page_spinbox_event_disabled:
            new_page_num: int = self.get_pdf_page_from_spinbox()
            if new_page_num < 0 or new_page_num >= self.__num_pdf_pages:
                raise ValueError("Page value not valid")

            self.__cards_navigator.set_current_card_index(
                self.__num_pdf_page_to_card_index[new_page_num]
            )

    def get_pdf_page_from_spinbox(self) -> int:
        return self.__window_layout.get_pdf_page_num_spinbox().value() - 1

    def previous_page(self) -> None:
        self.__cards_navigator.previous_page()

    def next_page(self) -> None:
        self.__cards_navigator.next_page()

    def __setup_left_panel(self) -> None:
        # TODO: add the management of the flashcards
        self.__load_pdf_doc(self.__path_of_pdf)
        self.update_card(self.__cards_navigator.get_current_card_index())

    def __load_pdf_doc(self, path_of_pdf: str) -> None:
        self.__window_layout.get_pdf_doc().load(path_of_pdf)

    def __setup_bottom_widget(self) -> None:
        self.__setup_current_card_bottom_layout()

    def __setup_current_card_bottom_layout(self) -> None:
        if self.get_num_cards() == 1:
            self.__window_layout.get_next_card_button().setDisabled(True)

    def previous_card(self) -> None:
        self.__cards_navigator.previous_card()

    def next_card(self) -> None:
        self.__cards_navigator.next_card()

    def previous_flashcard(self) -> None:
        self.__cards_navigator.previous_flashcard()

    def next_flashcard(self) -> None:
        self.__cards_navigator.next_flashcard()

    def update_page_pos_layout(self) -> None:
        page_index: int = self.__cards_to_display[
            self.__cards_navigator.get_current_card_index()
        ].get_pdf_page_for_visualization()

        self.__is_page_spinbox_event_disabled = True
        self.__window_layout.get_pdf_page_num_spinbox().setValue(page_index)
        self.__is_page_spinbox_event_disabled = False

    def update_card(self, current_card_index: int) -> None:
        if current_card_index < 0 or current_card_index >= self.get_num_cards():
            raise IndexError("Error: not existing card")

        element_to_display: Card = self.__cards_to_display[current_card_index]
        if isinstance(element_to_display, PdfPage):
            self.__window_layout.get_flashcard_label().setVisible(False)
            self.__window_layout.get_pdf_nav().jump(
                element_to_display.get_pdf_page(), self.__point
            )
            self.__window_layout.get_pdf_view().setVisible(True)
        elif isinstance(element_to_display, Flashcard):
            quest: Flashcard = element_to_display
            self.__window_layout.get_pdf_view().setVisible(False)
            self.__window_layout.get_flashcard_label().setText(quest.get_question())
            self.__window_layout.get_flashcard_label().setVisible(True)
        else:
            raise TypeError("Class type is different from what is expected")
        return None

    def get_pdf_window_visualization(self) -> PDFWindowVisualizationLayout:
        return self.__window_layout

    def add_page_flashcard(self, flag_generic: bool = False) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        app: Optional[Flashcard] = self.get_new_flashcard()
        if app is None:
            return
        flashcard: Flashcard = app

        if flag_generic:
            flashcard.set_reference_page(Flashcard.GENERIC_PAGE)
            flashcard.set_question_type(Flashcard.QuestionType.GENERIC)

        index_in_list: int = self.__get_index_list_position()

        self.__add_flashcard_at_index(flashcard, index_in_list)
        self.__cards_navigator.set_current_card_index(
            self.__cards_navigator.get_current_card_index() + 1
        )
        self.save_flashcard_to_file()
        self.clear_input_fields()

        QApplication.restoreOverrideCursor()

    def __get_index_list_position(self) -> int:
        current_card: Card = self.__cards_to_display[
            self.__cards_navigator.get_current_card_index()
        ]
        flashcards_current_page: Optional[
            list[Flashcard]
        ] = self.__flashcards_from_pdf_page.get(current_card.get_pdf_page())
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
        if flashcard.get_reference_page() in self.__flashcards_from_pdf_page.keys():
            self.__flashcards_from_pdf_page[flashcard.get_reference_page()].append(
                flashcard
            )
        else:
            self.__flashcards_from_pdf_page[flashcard.get_reference_page()] = [
                flashcard
            ]

        self.__refresh_merged_cards(self.__is_deck_ordered)

    def __add_flashcard_at_index(self, flashcard: Flashcard, index_in_list):
        if flashcard.get_reference_page() in self.__flashcards_from_pdf_page.keys():
            self.__flashcards_from_pdf_page[flashcard.get_reference_page()].insert(
                index_in_list, flashcard
            )
        else:
            self.__flashcards_from_pdf_page[flashcard.get_reference_page()] = [
                flashcard
            ]

        self.__refresh_merged_cards(self.__is_deck_ordered)

    def get_num_flashcards(self) -> int:
        return len(self.__num_flashcard_to_card_index)

    def get_new_flashcard(self) -> Optional[Flashcard]:
        flashcard: Flashcard = Flashcard()

        flashcard.set_reference_page(self.get_current_page_index())

        question_text: str = (
            self.__window_layout.get_input_text_question().toPlainText().strip()
        )
        if question_text == "":
            self.__window_layout.get_input_text_question().setStyleSheet(
                "border: 1px solid red;"
            )
            self.__window_layout.get_input_text_question().setFocus(
                Qt.FocusReason.OtherFocusReason
            )
            return None
        else:
            self.__window_layout.get_input_text_question().setStyleSheet(
                "border: 1px solid black;"
            )

        flashcard.set_question(question_text)
        answer_text: str = (
            self.__window_layout.get_input_text_answer().toPlainText().strip()
        )
        flashcard.set_answer(answer_text)
        if self.__window_layout.get_page_specific_checkbox().isChecked():
            flashcard.set_question_type(Flashcard.QuestionType.PAGE_SPECIFIC)
        else:
            flashcard.set_question_type(Flashcard.QuestionType.GENERIC)

        return flashcard

    def clear_input_fields(self) -> None:
        self.__window_layout.get_input_text_question().setPlainText("")
        self.__window_layout.get_input_text_answer().setPlainText("")
        self.__window_layout.get_page_specific_checkbox().setChecked(True)

    def save_flashcard_to_file(self) -> None:
        IOFlashcards.save_flashcards_file(
            self.__path_of_pdf,
            self.__io_flashcards_info,
            self.get_num_flashcards(),
            self.__flashcards_from_pdf_page,
        )
