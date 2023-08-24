from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QPlainTextEdit,
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import (
    QFont,
    QPixmap,
    QResizeEvent,
    QShortcut,
    QKeySequence,
    QIcon,
    QFont,
)
from PyQt6 import QtPdf, QtPdfWidgets
from PIL import Image as PILImage

import sys
import os
import tempfile
from typing import Optional

from application_constants import APPLICATION_NAME
from pdf_visualization.question import Question
from pdf_visualization.pdf_page import PdfPage
from pdf_visualization.card import Card


class PDFWindowVisualization(QWidget):
    def __init__(self, path_of_pdf: str) -> None:
        super().__init__()

        # change the CursorShape while loading the pdf
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        path_without_ext: str
        path_without_ext, _ = os.path.splitext(path_of_pdf)
        path_of_questions: str = path_without_ext + ".txt"

        is_questions_file_present: bool = os.path.isfile(path_of_questions)

        if not is_questions_file_present:
            with open(path_of_questions, "w") as file:
                file.write("0\n")

        questions: dict[int, list[Question]] = get_questions(path_of_questions)

        self.path_of_pdf: str = path_of_pdf
        self.filename: str = os.path.basename(path_of_pdf)

        self.num_pdf_pages: int = get_pdf_page_count(self.path_of_pdf)
        self.pdf_doc: QtPdf.QPdfDocument
        self.pdf_nav: QtPdf.QPdfPageNavigator

        self.cards_to_display: list[Card]
        self.num_pdf_page_to_card_index: list[int]
        self.num_question_to_card_index: list[int]
        (
            self.cards_to_display,
            self.num_pdf_page_to_card_index,
            self.num_question_to_card_index,
        ) = merge_cards(questions, self.num_pdf_pages)

        self.current_card_index: int = 0
        self.num_cards: int = len(self.cards_to_display)
        self.pdf_page_num_spinbox: QSpinBox
        self.is_page_spinbox_event_disabled: bool
        self.question_label: QLabel
        self.back_button: QPushButton
        self.next_button: QPushButton
        self.is_back_button_disabled: bool = True
        self.is_next_button_disabled: bool = False
        self.main_layout: QVBoxLayout

        self.__set_window_style()
        self.__set_window_layout()

        QApplication.restoreOverrideCursor()

    def __set_window_style(self) -> None:
        self.setWindowTitle(APPLICATION_NAME)

    def __set_window_layout(self) -> None:
        # TODO: change the position of the button and put them on the right of the pdf_view. Add some text boxes for creating new questions
        window_layout: QVBoxLayout = QVBoxLayout(self)
        self.setLayout(window_layout)

        header = self.__set_header_widget()
        main_layout: QHBoxLayout = QHBoxLayout(self)
        left_panel = self.__set_left_panel_widget()
        right_panel = self.__set_right_panel_widget()
        bottom = self.__set_bottom_widget()

        window_layout.addWidget(header)
        main_layout.addWidget(left_panel, stretch=4)
        main_layout.addWidget(right_panel, stretch=1)
        window_layout.addLayout(main_layout)
        window_layout.addWidget(bottom)

    def __set_header_widget(self) -> QWidget:
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
        # TODO: add a spinbox for the question number and for the card number. Not only the pdf number

        # the num_page stored is 0-based, but the visualization is 1-based numbering
        num_page: int = self.cards_to_display[self.current_card_index].get_pdf_page()

        page_pos_layout = QWidget(self)
        layout = QHBoxLayout()

        label = QLabel("Pdf page:", page_pos_layout)
        self.pdf_page_num_spinbox = QSpinBox(page_pos_layout)
        self.pdf_page_num_spinbox.setMinimum(1)
        self.pdf_page_num_spinbox.setMaximum(self.num_pdf_pages)
        self.pdf_page_num_spinbox.setValue(num_page)
        self.is_page_spinbox_event_disabled = False
        self.pdf_page_num_spinbox.valueChanged.connect(self.__update_page)

        self.back_page_button = QPushButton()
        self.back_page_button.setText("Previous Page")
        self.back_page_button.setDisabled(True)
        # self.back_page_button.clicked.connect(self.__previous_card)

        self.next_page_button = QPushButton()
        self.next_page_button.setText("Next Page")
        self.next_page_button.setDisabled(True)
        # self.next_page_button.clicked.connect(self.__previous_card)

        layout.addWidget(label)
        layout.addWidget(self.back_page_button)
        layout.addWidget(self.next_page_button)
        layout.addWidget(self.pdf_page_num_spinbox)

        return layout

    def __update_page(self) -> None:
        if not self.is_page_spinbox_event_disabled:
            new_page_num: int = self.pdf_page_num_spinbox.value() - 1
            if new_page_num < 0 or new_page_num >= self.num_pdf_pages:
                raise ValueError("Page value not valid")

            self.__change_card_index(self.num_pdf_page_to_card_index[new_page_num])

    def __set_left_panel_widget(self) -> QWidget:
        # visualization of the various pages or the questions before them, one at the time
        main = QWidget(self)

        self.main_layout = QVBoxLayout()

        # TODO: add the management of the questions

        self.question_label = QLabel(main)
        self.question_label.setVisible(False)
        self.question_label.setText("")

        self.pdf_view = QtPdfWidgets.QPdfView(self)
        self.pdf_view.setPageMode(QtPdfWidgets.QPdfView.PageMode.SinglePage)
        self.pdf_view.setZoomMode(QtPdfWidgets.QPdfView.ZoomMode.Custom)
        self.shortcut_zoom_increase = QShortcut(QKeySequence("Ctrl++"), self)
        self.shortcut_zoom_increase.activated.connect(self.__increase_zoom)
        self.shortcut_zoom_decrease = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_zoom_decrease.activated.connect(self.__decrease_zoom)
        self.main_layout.addWidget(self.pdf_view)

        self.pdf_doc = QtPdf.QPdfDocument(self)
        self.pdf_doc.load(self.path_of_pdf)
        self.pdf_view.setDocument(self.pdf_doc)

        app: Optional[QtPdf.QPdfPageNavigator]
        app = self.pdf_view.pageNavigator()
        if app is None:
            raise Exception("No page navigator")
        self.pdf_nav = app
        self.point = QPointF(0, 0)
        self.pdf_nav.jump(0, self.point)

        self.__update_card(None)

        self.main_layout.addWidget(self.question_label)
        main.setLayout(self.main_layout)
        return main

    def __load_pdf_doc(self, path_of_pdf: str) -> None:
        self.pdf_doc.load(path_of_pdf)

    def __set_right_panel_widget(self) -> QWidget:
        # bottom
        bottom = QWidget(self)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Question:"))
        self.question_input = QPlainTextEdit("")
        self.question_input.setMaximumWidth
        layout.addWidget(self.question_input)
        layout.addWidget(QLabel("Answer:"))
        self.answer_input = QPlainTextEdit("")
        layout.addWidget(self.answer_input)

        layout_general = self.__set_add_question_button_layout()

        layout.addLayout(layout_general)

        bottom.setLayout(layout)
        return bottom

    def __set_bottom_widget(self) -> QWidget:
        # bottom
        bottom = QWidget(self)
        layout = QVBoxLayout()

        layout_current_card = self.__set_current_card_bottom_layout()
        layout_current_question_correctness = (
            self.__set_current_question_bottom_layout()
        )

        # layout_general = self.__set_general_bottom_layout()

        layout.addLayout(layout_current_card)
        layout.addLayout(layout_current_question_correctness)
        # layout.addLayout(layout_general)

        bottom.setLayout(layout)
        return bottom

    def __set_current_card_bottom_layout(self) -> QHBoxLayout:
        layout_current_card = QHBoxLayout()

        bold_font = QFont()
        bold_font.setBold(True)

        # TODO: handle previous and next question button
        self.back_question_button = QPushButton()
        self.back_question_button.setText("|< Previous question")
        self.back_question_button.setFont(bold_font)
        self.back_question_button.setDisabled(True)
        # self.back_question_button.clicked.connect(self.__previous_card)

        self.back_button = QPushButton()
        self.back_button.setText("<< Back")
        self.back_button.setDisabled(True)
        self.back_button.clicked.connect(self.__previous_card)

        self.next_button = QPushButton()
        self.next_button.setText("Next >>")
        if self.num_cards == 1:
            self.next_button.setDisabled(True)
            self.is_next_button_disabled = True
        self.next_button.clicked.connect(self.__next_card)

        self.next_question_button = QPushButton()
        self.next_question_button.setText("Next question >|")
        self.next_question_button.setFont(bold_font)
        self.next_question_button.setDisabled(True)
        # self.next_question_button.clicked.connect(self.__previous_card)

        layout_current_card.addWidget(self.back_question_button)
        layout_current_card.addWidget(self.back_button)
        layout_current_card.addWidget(self.next_button)
        layout_current_card.addWidget(self.next_question_button)

        return layout_current_card

    def __set_current_question_bottom_layout(self) -> QHBoxLayout:
        # TODO: manage correct and mistake answers
        layout_current_card = QHBoxLayout()

        self.mistake_button = QPushButton()
        self.mistake_button.setText("Still Learning")
        self.mistake_button.setDisabled(True)
        self.mistake_button.setStyleSheet(
            """
            QPushButton {background-color: #C70039; padding:2.495px; border: 0.5px solid #bfbfbf;}
            QPushButton:disabled {background-color: #CCCCCC; padding:2.495px; border: 0.5px solid #bfbfbf;}
            """
        )
        # self.mistake_button.clicked.connect(self.__previous_card)

        self.correct_button = QPushButton()
        self.correct_button.setText("Know")
        self.correct_button.setDisabled(True)
        self.correct_button.setStyleSheet(
            """
            QPushButton {background-color: #82CD47; padding:2.495px; border: 0.5px solid #bfbfbf;}
            QPushButton:disabled {background-color: #CCCCCC; padding:2.495px; border: 0.5px solid #bfbfbf;}
            """
        )
        # self.correct_button.clicked.connect(self.__next_card)

        # add_page_question = QPushButton()
        # add_page_question.setText("Add question to the card")

        layout_current_card.addWidget(self.mistake_button)
        layout_current_card.addWidget(self.correct_button)
        # layout_current_card.addWidget(add_page_question)

        return layout_current_card

    def __set_add_question_button_layout(self):
        layout_general = QVBoxLayout()

        add_page_question = QPushButton()
        add_page_question.setText("Add question")
        add_general_question = QPushButton()
        add_general_question.setText("Add general question")

        layout_general.addWidget(add_page_question)
        layout_general.addWidget(add_general_question)

        return layout_general

    def __get_number_of_pdf_pages(self) -> int:
        return self.pdf_doc.pageCount()

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
        page_index: int = (
            self.cards_to_display[self.current_card_index].get_pdf_page() + 1
        )

        self.is_page_spinbox_event_disabled = True
        self.pdf_page_num_spinbox.setValue(page_index)
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

    def __update_card(self, event) -> None:
        if self.current_card_index < 0 or self.current_card_index >= self.num_cards:
            raise IndexError("Error: not existing card")

        element_to_display: Card = self.cards_to_display[self.current_card_index]
        if isinstance(element_to_display, PdfPage):
            self.question_label.setVisible(False)
            self.pdf_nav.jump(element_to_display.get_pdf_page(), self.point)
            self.pdf_view.setVisible(True)
        elif isinstance(element_to_display, Question):
            self.pdf_view.setVisible(False)
            self.question_label.setText(element_to_display.question)
            self.question_label.setVisible(True)
        else:
            raise TypeError("Class type is different from what is expected")
        return None

    def __increase_zoom(self) -> None:
        self.pdf_view.setZoomFactor(self.pdf_view.zoomFactor() * 1.25)

    def __decrease_zoom(self) -> None:
        self.pdf_view.setZoomFactor(self.pdf_view.zoomFactor() / 1.25)


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


def merge_cards(
    questions_per_page: dict[int, list[Question]], num_pdf_pages: int
) -> tuple[list[Card], list[int], list[int]]:
    """Merge the questions and the pages in the correct order.

    It orders the questions and the pdf pages in a unique list that matches the visualization outcome.

    Parameters
    ----------
    questions_per_page : dict[int, list[Question]]
        The key is a page number, and the corresponding items are the questions for that page.
    num_pdf_pages : int
        The number of pages in the pdf visualized.

    Returns
    -------
    tuple[list[Card]], list[int], list[int]]
    The first returned parameter is a list of all ordered cards to be displayed. The second element is a vector that stores for each pdf page number the corresponding visualization position. The last returned value does the same with questions.

    """
    # sort the questions by page number, same page number leaves the order that there was before. In this way the order in which the user put the questions is left
    questions_per_page = dict(sorted(questions_per_page.items(), key=lambda x: x[0]))
    questions: list[Question] = list(questions_per_page.values())
    num_questions: int = len(questions_per_page.values())
    num_cards: int = num_questions + num_pdf_pages

    card_pos: int
    index_quest_to_add: int = 0
    index_pdf_page_to_add: int = 0

    num_pdf_page_to_card_index: list[int] = []
    num_question_to_card_index: list[int] = []
    merged_cards: list[Card] = []
    for card_pos in range(0, num_cards, 1):
        card: Card
        if index_quest_to_add == num_questions:
            card = PdfPage(index_pdf_page_to_add)
            num_pdf_page_to_card_index.append(len(merged_cards))
            index_pdf_page_to_add += 1
        elif index_pdf_page_to_add == num_pdf_pages:
            card = questions[index_quest_to_add]
            num_question_to_card_index.append(len(merged_cards))
            index_quest_to_add += 1
        elif (
            questions[index_quest_to_add].get_reference_page() <= index_pdf_page_to_add
        ):
            card = questions[index_quest_to_add]
            num_question_to_card_index.append(len(merged_cards))
            index_quest_to_add += 1
        else:
            card = PdfPage(index_pdf_page_to_add)
            num_pdf_page_to_card_index.append(len(merged_cards))
            index_pdf_page_to_add += 1
        merged_cards.append(card)

    return (merged_cards, num_pdf_page_to_card_index, num_question_to_card_index)


# TODO: move the function in a better place
def get_pdf_page_count(path_to_pdf: str) -> int:
    pdf_doc = QtPdf.QPdfDocument(None)
    pdf_doc.load(path_to_pdf)
    return pdf_doc.pageCount()
