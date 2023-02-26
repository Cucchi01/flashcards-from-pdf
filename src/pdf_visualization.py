from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QResizeEvent
from pdf2image import convert_from_path
from PIL import Image as PILImage

import sys
import os
import tempfile

from application_constants import *
from image_visualization import ZoomableImage


class PDFWindowVisualization(QWidget):
    def __init__(self, path_of_pdf: str) -> None:
        super().__init__()

        # change the CursorShape because it takes a lot of time to load the pdf
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        path_without_ext, _ = os.path.splitext(path_of_pdf)
        path_of_questions = path_without_ext + ".txt"

        is_questions_file_present: bool = os.path.isfile(path_of_questions)

        if not is_questions_file_present:
            with open(path_of_questions, "w") as file:
                file.write("0\n")

        questions: dict[int, list[Question]] = get_questions(path_of_questions)

        self.path_of_pdf: str = path_of_pdf
        self.filename: str = os.path.basename(path_of_pdf)
        # TODO: move the retrieval of the images on a different thread. So I can preload all
        #  the images of the current pdf and then move smoothly between them
        pdf_pages: list[PILImage.Image] = convert_from_path(self.path_of_pdf, dpi=200)

        self.cards_to_display: list[PILImage.Image | Question]
        self.num_page_to_index_card: list[int]
        # the number of the page is 0-based
        self.index_card_to_num_page: list[int]
        (
            self.cards_to_display,
            self.num_page_to_index_card,
            self.index_card_to_num_page,
        ) = merge_questions_pages(questions, pdf_pages)

        self.current_card_index: int = 0
        self.num_cards: int = len(self.cards_to_display)
        self.num_pdf_pages: int = len(pdf_pages)
        self.tmp_dir: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
        self.page_num_spinbox: QSpinBox
        self.is_page_spinbox_event_disabled: bool
        self.question_label: QLabel
        self.back_button: QPushButton
        self.next_button: QPushButton
        self.is_back_button_disabled: bool = True
        self.is_next_button_disabled: bool = False
        self.main_layout: QVBoxLayout
        self.zoomable_image: ZoomableImage

        self.__set_window_style()
        self.__set_window_layout()

        QApplication.restoreOverrideCursor()

    def __set_window_style(self) -> None:
        self.setWindowTitle(APPLICATION_NAME)

    def __set_window_layout(self) -> None:
        main_window_layout = QVBoxLayout(self)
        self.setLayout(main_window_layout)

        header = self.__get_header_widget()
        main = self.__get_main_widget()
        bottom = self.__get_bottom_widget()

        main_window_layout.addWidget(header)
        main_window_layout.addWidget(main)
        main_window_layout.addWidget(bottom)

    def __get_header_widget(self) -> QWidget:
        # header
        title = QWidget(self)
        layout = QVBoxLayout()
        label = QLabel(self.filename, title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Calisto MT", 17))
        layout.addWidget(label)
        layout.addLayout(self.__get_page_position_layout())
        title.setLayout(layout)
        return title

    def __get_page_position_layout(self) -> QHBoxLayout:
        # the num_page stored is 0-based, but the visualization is 1-based numbering
        num_page: int = self.index_card_to_num_page[self.current_card_index] + 1

        page_pos_layout = QWidget(self)
        layout = QHBoxLayout()

        label = QLabel("Pdf page:", page_pos_layout)
        self.page_num_spinbox = QSpinBox(page_pos_layout)
        self.page_num_spinbox.setMinimum(1)
        self.page_num_spinbox.setMaximum(self.num_pdf_pages)
        self.page_num_spinbox.setValue(num_page)
        self.is_page_spinbox_event_disabled = False
        self.page_num_spinbox.valueChanged.connect(self.__update_page)

        layout.addWidget(label)
        layout.addWidget(self.page_num_spinbox)

        return layout

    def __update_page(self) -> None:
        if not self.is_page_spinbox_event_disabled:
            new_page_num: int = self.page_num_spinbox.value() - 1
            if new_page_num < 0 or new_page_num >= self.num_pdf_pages:
                raise ValueError("Page value not valid")

            self.__change_card_index(self.num_page_to_index_card[new_page_num])

    def __get_main_widget(self) -> QWidget:
        # visualization of the various pages or the questions before them
        main = QWidget(self)

        self.main_layout = QVBoxLayout()

        # TODO: add the management of the questions

        self.question_label = QLabel(main)
        self.question_label.setVisible(False)
        self.question_label.setText("")

        self.zoomable_image = ZoomableImage(self)
        self.main_layout.addWidget(self.zoomable_image)
        self.__update_card(None)

        self.main_layout.addWidget(self.question_label)
        main.setLayout(self.main_layout)
        return main

    def __get_bottom_widget(self) -> QWidget:
        # bottom
        bottom = QWidget(self)
        layout = QVBoxLayout()
        layout_current_card = self.__get_current_card_bottom_layout()
        layout_general = self.__get_general_bottom_layout()

        layout.addLayout(layout_current_card)
        layout.addLayout(layout_general)

        bottom.setLayout(layout)
        return bottom

    def __get_current_card_bottom_layout(self) -> QHBoxLayout:
        layout_current_card = QHBoxLayout()

        self.back_button = QPushButton()
        self.back_button.setText("Back")
        self.back_button.setDisabled(True)
        self.back_button.clicked.connect(self.__previous_card)

        self.next_button = QPushButton()
        self.next_button.setText("Next")
        if self.num_cards == 1:
            self.next_button.setDisabled(True)
            self.is_next_button_disabled = True
        self.next_button.clicked.connect(self.__next_card)

        add_page_question = QPushButton()
        add_page_question.setText("Add question to the card")

        layout_current_card.addWidget(self.back_button)
        layout_current_card.addWidget(self.next_button)
        layout_current_card.addWidget(add_page_question)

        return layout_current_card

    def __get_general_bottom_layout(self):
        layout_general = QHBoxLayout()

        add_general_question = QPushButton()
        add_general_question.setText("Add general question")

        layout_general.addWidget(add_general_question)

        return layout_general

    def __previous_card(self) -> None:
        if self.current_card_index <= 0:
            return None

        self.__change_card_index(self.current_card_index - 1)
        return None

    def __next_card(self) -> None:
        if self.current_card_index >= self.num_cards - 1:
            return None

        self.__change_card_index(self.current_card_index + 1)
        return None

    def __change_card_index(self, new_index) -> None:
        if new_index < 0 or new_index >= self.num_cards:
            print("Error: card index out of range")
            return None

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.current_card_index = new_index
        self.__update_card(None)

        self.__update_page_pos_layout()
        self.__update_back_btn_state()
        self.__update_next_btn_state()

        QApplication.restoreOverrideCursor()
        return None

    def __update_page_pos_layout(self) -> None:
        # the pages are 0-based, but the visualization is 1-based
        page_index: int = self.index_card_to_num_page[self.current_card_index] + 1

        self.is_page_spinbox_event_disabled = True
        self.page_num_spinbox.setValue(page_index)
        self.is_page_spinbox_event_disabled = False

    def __update_back_btn_state(self) -> None:
        if self.current_card_index > 0 and self.is_back_button_disabled:
            self.back_button.setDisabled(False)
            self.is_back_button_disabled = False
        elif self.current_card_index == 0 and not self.is_back_button_disabled:
            self.back_button.setDisabled(True)
            self.is_back_button_disabled = True

    def __update_next_btn_state(self) -> None:
        if (
            self.current_card_index == self.num_cards - 1
            and not self.is_next_button_disabled
        ):
            self.next_button.setDisabled(True)
            self.is_next_button_disabled = True
        elif (
            self.current_card_index < self.num_cards - 1
            and self.is_next_button_disabled
        ):
            self.next_button.setDisabled(False)
            self.is_next_button_disabled = False

    def __update_card(self, event) -> IndexError | None:
        if self.current_card_index < 0 or self.current_card_index >= self.num_cards:
            print("Error: not existing card")
            return IndexError()

        #  The design choice of the creator of tempdir is to open the tmp_dir with with .. as dirname.
        #  I prefer to create a single tempdir at the start of the window and closing it at the
        #  closure of the latter
        element_to_display: PILImage.Image | Question = self.cards_to_display[
            self.current_card_index
        ]
        if isinstance(element_to_display, PILImage.Image):
            self.question_label.setVisible(False)
            self.zoomable_image.setVisible(True)
            tmp_dirname = self.tmp_dir.__enter__()
            file_path = os.path.join(tmp_dirname, "page.jpg")
            # TODO: can be improved with the visualization of the page without passing from disk
            element_to_display.save(file_path, "JPEG")

            self.zoomable_image.load_image(file_path)
        else:
            self.zoomable_image.setVisible(False)
            self.question_label.setText(element_to_display.question)
            self.question_label.setVisible(True)

        return None

    def resizeEvent(self, a0: QResizeEvent) -> None:
        return_value = super().resizeEvent(a0)
        self.zoomable_image.fitInView()
        return return_value

    def closeEvent(self, event):
        # add the closure of the tempdir
        self.tmp_dir.cleanup()
        super().closeEvent(event)


class Question:
    def __init__(
        self,
        num_page: int = 0,
        question: str = "",
        answer: str = "",
        type_quest: str = "g",
    ) -> None:
        self.num_page: int = num_page
        self.type: str = type_quest
        self.question: str = question
        self.answer: str = answer


def get_questions(path_of_file: str) -> dict[int, list[Question]]:
    questions: dict[int, list[Question]] = dict()
    with open(path_of_file, "r") as file:
        num_col: int = -1
        num_questions: int = int(file.readline())
        pages_with_questions = set()
        string: str = ""
        for line in file:
            for word in line.split():
                if word == "?^?":
                    num_col += 1
                    match num_col:
                        case 0:
                            # Page number
                            num_page: int = int(string)

                        case 1:
                            # Question
                            question: str = string

                        case 2:
                            # Answer
                            answer: str = string

                        case 3:
                            # Type
                            type_quest: str = string.strip()
                            if num_page in pages_with_questions:
                                questions[num_page].append(
                                    Question(num_page, question, answer, type_quest)
                                )
                            else:
                                questions[num_page] = [
                                    Question(num_page, question, answer, type_quest)
                                ]
                                pages_with_questions.add(num_page)

                            num_col = -1

                    string = ""
                else:
                    string = " ".join([string, word])

    return questions


def merge_questions_pages(
    questions_per_page: dict[int, list[Question]], pdf_pages: list[PILImage.Image]
) -> tuple[list[PILImage.Image | list[Question]], list[int], list[int]]:
    """Merge the questions and the pages in the correct order.

    It orders the questions and the pdf pages in a unique list that matches the visualization outcome.

    Parameters
    ----------
    questions_per_page : dict[int, list[Question]]
        The key is a page number, and the corresponding items are the questions for that page.
    pdf_pages : list[PILImage.Image]
        List of the pdf images.

    Returns
    -------
    tuple[list[PILImage.Image | list[Question]], list[int], list[int]]
    The first returned parameter is a list containing the merged elements. The second element is a vector that stores for each page number the corresponding visualization position. The last returned value does the opposite.

    """
    # TODO: restructure the code
    num_card_with_quests: int = len(questions_per_page)
    num_tot: int = num_card_with_quests + len(pdf_pages)
    positions_card_questions: list[int] = sorted(questions_per_page.keys())
    num_page_to_card_index: list[int] = []
    index_card_to_num_page: list[int] = []

    merged_cards: list[PILImage.Image | list[Question]] = []

    index_quests: int = 0
    index_pdf_page: int = 0
    card_pos: int = 0
    for _ in range(num_tot):
        if (
            index_quests < len(positions_card_questions)
            and positions_card_questions[index_quests] <= index_pdf_page
        ):
            pos_next_quest = positions_card_questions[index_quests]
            for quest in questions_per_page[pos_next_quest]:
                merged_cards.append(quest)
                index_card_to_num_page.append(index_pdf_page)
                card_pos += 1

            index_quests += 1
        else:
            merged_cards.append(pdf_pages[index_pdf_page])
            index_card_to_num_page.append(index_pdf_page)
            # hashmap that stores the position of a card in the visualization
            num_page_to_card_index.append(card_pos)
            index_pdf_page += 1
            card_pos += 1

    return (merged_cards, num_page_to_card_index, index_card_to_num_page)
