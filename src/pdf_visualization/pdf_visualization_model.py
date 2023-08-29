from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPointF
from PyQt6 import QtPdf, QtPdfWidgets

import os
from typing import Optional

from pdf_visualization.pdf_visualization_layout import PDFWindowVisualizationLayout
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
            with open(path_of_flashcards, "w") as file:
                file.write("0\n")

        self.__io_flashcards_info: PDFTestsInfo = IOFlashcards.get_past_tests_info(
            path_of_flashcards
        )
        self.__flashcards: dict[
            int, list[Flashcard]
        ] = IOFlashcards.get_flashcards_from_pdf(path_of_flashcards)

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
        ) = merge_cards(self.__flashcards, self.__num_pdf_pages)

        self.__current_card_index: int = 0
        self.__current_pdf_page: int = 0
        self.__num_cards: int = len(self.__cards_to_display)
        self.__is_page_spinbox_event_disabled: bool = False
        self.__is_back_button_disabled: bool = True
        self.__is_next_button_disabled: bool = False

        self.__window_layout: PDFWindowVisualizationLayout = (
            PDFWindowVisualizationLayout(self.__filename, self.__num_pdf_pages)
        )

        self.__setup_window_layout()

    def __setup_window_layout(self) -> None:
        self.__setup_left_panel()
        self.__setup_bottom_widget()

    def __set_page_position(self) -> None:
        # the num_page stored is 0-based, but the visualization is 1-based numbering
        self.__current_pdf_page = self.__cards_to_display[
            self.__current_card_index
        ].get_pdf_page()
        self.__window_layout.set_num_page(self.__current_pdf_page)
        self.__is_page_spinbox_event_disabled = False

    def update_page(self) -> None:
        if not self.__is_page_spinbox_event_disabled:
            self.__current_pdf_page = (
                self.__window_layout.get_pdf_page_num_spinbox().value()
            )
            new_page_num: int = self.__current_pdf_page - 1
            if new_page_num < 0 or new_page_num >= self.__num_pdf_pages:
                raise ValueError("Page value not valid")

            self.__change_card_index(self.__num_pdf_page_to_card_index[new_page_num])

    def __setup_left_panel(self) -> None:
        # TODO: add the management of the flashcards
        self.__load_pdf_doc(self.__path_of_pdf)
        self.__update_card(None)

    def __load_pdf_doc(self, path_of_pdf: str) -> None:
        self.__window_layout.get_pdf_doc().load(path_of_pdf)

    def __setup_bottom_widget(self) -> None:
        self.__setup_current_card_bottom_layout()

    def __setup_current_card_bottom_layout(self) -> None:
        if self.__num_cards == 1:
            self.__window_layout.get_next_card_btn().setDisabled(True)
            self.__is_next_button_disabled = True

    def previous_card(self) -> None:
        if self.__current_card_index <= 0:
            return None

        self.__change_card_index(self.__current_card_index - 1)
        return None

    def next_card(self) -> None:
        if self.__current_card_index >= self.__num_cards - 1:
            return None

        self.__change_card_index(self.__current_card_index + 1)
        return None

    def __change_card_index(self, new_index) -> None:
        if new_index < 0 or new_index >= self.__num_cards:
            print("Error: card index out of range")
            return None

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.__current_card_index = new_index
        self.__update_card(None)

        self.__update_page_pos_layout()
        self.__update_back_btn_state()
        self.__update_next_btn_state()

        QApplication.restoreOverrideCursor()

    def __update_page_pos_layout(self) -> None:
        # the pages are 0-based, but the visualization is 1-based
        page_index: int = (
            self.__cards_to_display[self.__current_card_index].get_pdf_page() + 1
        )

        self.__is_page_spinbox_event_disabled = True
        self.__window_layout.get_pdf_page_num_spinbox().setValue(page_index)
        self.__is_page_spinbox_event_disabled = False

    def __update_back_btn_state(self) -> None:
        if self.__current_card_index > 0 and self.__is_back_button_disabled:
            self.__window_layout.get_back_card_btn().setDisabled(False)
            self.__is_back_button_disabled = False
        elif self.__current_card_index == 0 and not self.__is_back_button_disabled:
            self.__window_layout.get_back_card_btn().setDisabled(True)
            self.__is_back_button_disabled = True

    def __update_next_btn_state(self) -> None:
        if (
            self.__current_card_index == self.__num_cards - 1
            and not self.__is_next_button_disabled
        ):
            self.__window_layout.get_next_card_btn().setDisabled(True)
            self.__is_next_button_disabled = True
        elif (
            self.__current_card_index < self.__num_cards - 1
            and self.__is_next_button_disabled
        ):
            self.__window_layout.get_next_card_btn().setDisabled(False)
            self.__is_next_button_disabled = False

    def __update_card(self, event) -> None:
        if (
            self.__current_card_index < 0
            or self.__current_card_index >= self.__num_cards
        ):
            raise IndexError("Error: not existing card")

        element_to_display: Card = self.__cards_to_display[self.__current_card_index]
        if isinstance(element_to_display, PdfPage):
            self.__window_layout.get_question_label().setVisible(False)
            self.__window_layout.get_pdf_nav().jump(
                element_to_display.get_pdf_page(), self.__point
            )
            self.__window_layout.get_pdf_view().setVisible(True)
        elif isinstance(element_to_display, Flashcard):
            quest: Flashcard = element_to_display
            self.__window_layout.get_pdf_view().setVisible(False)
            self.__window_layout.get_question_label().setText(quest.get_question())
            self.__window_layout.get_question_label().setVisible(True)
        else:
            raise TypeError("Class type is different from what is expected")
        return None

    def get_pdf_window_visualization(self) -> PDFWindowVisualizationLayout:
        return self.__window_layout

    def add_page_flashcard(self, flag_generic: bool = False) -> None:
        app: Optional[Flashcard] = self.get_new_flashcard()
        if app is None:
            return
        flashcard: Flashcard = app

        if flag_generic:
            flashcard.set_reference_page(Flashcard.NO_REFERENCE_PAGE)
            flashcard.set_question_type(Flashcard.QuestionType.GENERIC)

        self.__add_flashcard(flashcard)
        self.add_flashcard_to_file()
        self.clear_input_fields()

    def __add_flashcard(self, flashcard: Flashcard):
        if flashcard.get_pdf_page() in self.__flashcards.keys():
            self.__flashcards[flashcard.get_pdf_page()].append(flashcard)
        else:
            self.__flashcards[flashcard.get_pdf_page()] = [flashcard]

        self.__num_cards += 1

    def get_num_flashcards(self):
        return self.__num_cards - self.__num_pdf_pages

    def get_new_flashcard(self) -> Optional[Flashcard]:
        flashcard: Flashcard = Flashcard()
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

        flashcard.set_reference_page(
            self.__window_layout.get_pdf_page_num_spinbox().value()
        )
        return flashcard

    def clear_input_fields(self) -> None:
        self.__window_layout.get_input_text_question().setPlainText("")
        self.__window_layout.get_input_text_answer().setPlainText("")
        self.__window_layout.get_page_specific_checkbox().setChecked(True)

    def add_flashcard_to_file(self) -> None:
        IOFlashcards.save_flashcards_file(
            self.__path_of_pdf,
            self.__io_flashcards_info,
            self.get_num_flashcards(),
            self.__flashcards,
        )


def merge_cards(
    flashcards_per_page: dict[int, list[Flashcard]], num_pdf_pages: int
) -> tuple[list[Card], list[int], list[int]]:
    """Merge the flashcards and the pages in the correct order.

    It orders the flashcards and the pdf pages in a unique list that matches the visualization outcome.

    Parameters
    ----------
    flashcards_per_page : dict[int, list[Flashcard]]
        The key is a page number, and the corresponding items are the flashcards for that page.
    num_pdf_pages : int
        The number of pages in the pdf visualized.

    Returns
    -------
    tuple[list[Card]], list[int], list[int]]
    The first returned parameter is a list of all ordered cards to be displayed. The second element is a vector that stores for each pdf page number the corresponding visualization position. The last returned value does the same with flashcards.

    """
    # sort the flashcards by page number, same page number leaves the order that there was before. In this way the order in which the user put the flashcards is left
    flashcards_per_page = dict(sorted(flashcards_per_page.items(), key=lambda x: x[0]))
    flashcards: list[Flashcard] = []
    for app in flashcards_per_page.values():
        flashcards.extend(app)

    num_flashcards: int = len(flashcards)
    num_cards: int = num_flashcards + num_pdf_pages

    card_pos: int
    index_quest_to_add: int = 0
    index_pdf_page_to_add: int = 0

    num_pdf_page_to_card_index: list[int] = []
    num_flashcard_to_card_index: list[int] = []
    merged_cards: list[Card] = []
    for card_pos in range(0, num_cards, 1):
        card: Card
        if index_quest_to_add == num_flashcards:
            card = PdfPage(index_pdf_page_to_add)
            num_pdf_page_to_card_index.append(len(merged_cards))
            index_pdf_page_to_add += 1
        elif index_pdf_page_to_add == num_pdf_pages:
            card = flashcards[index_quest_to_add]
            num_flashcard_to_card_index.append(len(merged_cards))
            index_quest_to_add += 1
        elif (
            flashcards[index_quest_to_add].get_reference_page()
            - 1  # reference page start from 1 and not 0
            <= index_pdf_page_to_add
        ):
            card = flashcards[index_quest_to_add]
            num_flashcard_to_card_index.append(len(merged_cards))
            index_quest_to_add += 1
        else:
            card = PdfPage(index_pdf_page_to_add)
            num_pdf_page_to_card_index.append(len(merged_cards))
            index_pdf_page_to_add += 1
        merged_cards.append(card)

    return (merged_cards, num_pdf_page_to_card_index, num_flashcard_to_card_index)
