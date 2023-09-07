from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QPlainTextEdit,
    QCheckBox,
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QFont
from PyQt6 import QtPdf, QtPdfWidgets

from typing import Optional

from application_constants import APPLICATION_NAME


class PDFWindowVisualizationLayout(QWidget):
    def __init__(self, filename: str, num_pdf_pages: int) -> None:
        super().__init__()

        self.__num_pdf_pages: int = num_pdf_pages
        self.__filename: str = filename
        self.__num_page: int = 1

        # header
        self.__shuffle_button: QPushButton
        self.__pdf_page_num_spinbox: QSpinBox
        self.__previous_page_button: QPushButton
        self.__next_page_button: QPushButton
        self.__advanced_options_button: QPushButton

        # main
        # left panel
        self.__left_panel_layout: QVBoxLayout
        self.__flashcard_label: QLabel
        self.__pdf_view: QtPdfWidgets.QPdfView
        self.__pdf_doc: QtPdf.QPdfDocument
        self.__pdf_nav: QtPdf.QPdfPageNavigator
        self.__point: QPointF
        # right panel
        self.__question_input: QPlainTextEdit
        self.__answer_input: QPlainTextEdit
        self.__page_specific_checkbox: QCheckBox
        self.__add_page_flashcard_button: QPushButton
        self.__add_generic_flashcard_button: QPushButton

        # bottom
        self.__previous_flashcard_button: QPushButton
        self.__previous_card_button: QPushButton
        self.__next_card_button: QPushButton
        self.__next_flashcard_button: QPushButton
        self.__is_back_card_button_disabled: bool = True
        self.__is_next_card_button_disabled: bool = False
        self.__mistake_button: QPushButton
        self.__correct_button: QPushButton

        self.__set_window_style()
        self.__set_window_layout()

    def __set_window_style(self) -> None:
        self.setWindowTitle(APPLICATION_NAME)

    def __set_window_layout(self) -> None:
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

        layout_title = QHBoxLayout()
        label = QLabel(self.__filename, title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Calisto MT", 17))

        self.__shuffle_button = QPushButton()
        self.__shuffle_button.setText("Shuffle")

        layout_title.addWidget(self.__shuffle_button, stretch=1)
        layout_title.addWidget(label, stretch=4)

        layout.addLayout(layout_title)
        layout.addLayout(self.__set_page_position_layout())
        title.setLayout(layout)
        return title

    def __set_page_position_layout(self) -> QHBoxLayout:
        # TODO: add a spinbox for the flashcard number and for the card number. Not only the pdf number

        page_pos_layout = QWidget(self)
        layout = QHBoxLayout()

        self.__previous_page_button = QPushButton()
        self.__previous_page_button.setText("Previous Page")
        self.__previous_page_button.setDisabled(True)

        self.__next_page_button = QPushButton()
        self.__next_page_button.setText("Next Page")

        label = QLabel("Pdf page:", page_pos_layout)
        self.__pdf_page_num_spinbox = QSpinBox(page_pos_layout)
        self.__pdf_page_num_spinbox.setMinimum(1)
        self.__pdf_page_num_spinbox.setMaximum(self.__num_pdf_pages)
        self.__pdf_page_num_spinbox.setValue(self.__num_page)

        self.__advanced_options_button = QPushButton()
        self.__advanced_options_button.setText("Advanced options")
        self.__advanced_options_button.setDisabled(True)

        layout.addWidget(self.__previous_page_button)
        layout.addWidget(self.__next_page_button)
        layout.addWidget(label)
        layout.addWidget(self.__pdf_page_num_spinbox)
        layout.addWidget(self.__advanced_options_button)

        return layout

    def __set_left_panel_widget(self) -> QWidget:
        # visualization of the various pages or the flashcards before them, one at the time
        main = QWidget(self)

        self.__left_panel_layout = QVBoxLayout()

        self.__flashcard_label = QLabel(main)
        self.__flashcard_label.setVisible(False)
        self.__flashcard_label.setText("")

        self.__pdf_view = QtPdfWidgets.QPdfView(self)
        self.__pdf_view.setPageMode(QtPdfWidgets.QPdfView.PageMode.SinglePage)
        self.__pdf_view.setZoomMode(QtPdfWidgets.QPdfView.ZoomMode.Custom)
        self.__left_panel_layout.addWidget(self.__pdf_view)

        self.__pdf_doc = QtPdf.QPdfDocument(self)
        self.__pdf_view.setDocument(self.__pdf_doc)

        app: Optional[QtPdf.QPdfPageNavigator]
        app = self.__pdf_view.pageNavigator()
        if app is None:
            raise Exception("No page navigator")
        self.__pdf_nav = app
        self.__point = QPointF(0, 0)
        self.__pdf_nav.jump(0, self.__point)

        self.__left_panel_layout.addWidget(self.__flashcard_label)
        main.setLayout(self.__left_panel_layout)
        return main

    def __set_right_panel_widget(self) -> QWidget:
        bottom = QWidget(self)
        layout = QVBoxLayout()

        question_label = QLabel("Question:")
        self.__question_input = QPlainTextEdit("")
        self.__answer_input = QPlainTextEdit("")
        answer_label = QLabel("Answer:")
        self.__page_specific_checkbox = QCheckBox("Page specific")
        self.__page_specific_checkbox.setChecked(True)

        layout.addWidget(question_label)
        layout.addWidget(self.__question_input)
        layout.addWidget(answer_label)
        layout.addWidget(self.__answer_input)
        layout.addWidget(self.__page_specific_checkbox)
        self.__add_flashcard_buttons(layout)

        bottom.setLayout(layout)
        return bottom

    def __add_flashcard_buttons(self, layout: QVBoxLayout) -> None:
        self.__add_page_flashcard_button = QPushButton()
        self.__add_page_flashcard_button.setText("Add flashcard")
        self.__add_generic_flashcard_button = QPushButton()
        self.__add_generic_flashcard_button.setText("Add generic flashcard")

        layout.addWidget(self.__add_page_flashcard_button)
        layout.addWidget(self.__add_generic_flashcard_button)

    def __set_bottom_widget(self) -> QWidget:
        # bottom
        bottom = QWidget(self)
        layout = QVBoxLayout()

        layout_current_card = self.__set_current_card_bottom_layout()
        layout_current_flashcard_correctness = (
            self.__set_current_flashcard_bottom_layout()
        )

        # layout_general = self.__set_general_bottom_layout()

        layout.addLayout(layout_current_card)
        layout.addLayout(layout_current_flashcard_correctness)
        # layout.addLayout(layout_general)

        bottom.setLayout(layout)
        return bottom

    def __set_current_card_bottom_layout(self) -> QHBoxLayout:
        layout_current_card = QHBoxLayout()

        bold_font = QFont()
        bold_font.setBold(True)

        self.__previous_flashcard_button = QPushButton()
        self.__previous_flashcard_button.setText("|< Previous flashcard")
        self.__previous_flashcard_button.setFont(bold_font)
        self.__previous_flashcard_button.setDisabled(True)

        self.__previous_card_button = QPushButton()
        self.__previous_card_button.setText("<< Back")
        self.__previous_card_button.setDisabled(True)

        self.__next_card_button = QPushButton()
        self.__next_card_button.setText("Next >>")

        self.__next_flashcard_button = QPushButton()
        self.__next_flashcard_button.setText("Next flashcard >|")
        self.__next_flashcard_button.setFont(bold_font)

        layout_current_card.addWidget(self.__previous_flashcard_button)
        layout_current_card.addWidget(self.__previous_card_button)
        layout_current_card.addWidget(self.__next_card_button)
        layout_current_card.addWidget(self.__next_flashcard_button)

        return layout_current_card

    def __set_current_flashcard_bottom_layout(self) -> QHBoxLayout:
        # TODO: manage correct and mistake answers
        layout_current_card = QHBoxLayout()

        self.__mistake_button = QPushButton()
        self.__mistake_button.setText("Still Learning")
        self.__mistake_button.setDisabled(True)
        self.__mistake_button.setStyleSheet(
            """
            QPushButton {background-color: #C70039; padding:2.495px; border: 0.5px solid #bfbfbf;}
            QPushButton:disabled {background-color: #CCCCCC; padding:2.495px; border: 0.5px solid #bfbfbf;}
            """
        )

        self.__correct_button = QPushButton()
        self.__correct_button.setText("Know")
        self.__correct_button.setDisabled(True)
        self.__correct_button.setStyleSheet(
            """
            QPushButton {background-color: #82CD47; padding:2.495px; border: 0.5px solid #bfbfbf;}
            QPushButton:disabled {background-color: #CCCCCC; padding:2.495px; border: 0.5px solid #bfbfbf;}
            """
        )

        layout_current_card.addWidget(self.__mistake_button)
        layout_current_card.addWidget(self.__correct_button)

        return layout_current_card

    def increase_zoom(self) -> None:
        self.__pdf_view.setZoomFactor(self.__pdf_view.zoomFactor() * 1.25)

    def decrease_zoom(self) -> None:
        self.__pdf_view.setZoomFactor(self.__pdf_view.zoomFactor() / 1.25)

    def set_num_page(self, new_num_page: int) -> None:
        self.__num_page = new_num_page
        self.__pdf_page_num_spinbox.setValue(self.__num_page)

    def get_shuffle_button(self) -> QPushButton:
        return self.__shuffle_button

    def get_pdf_page_num_spinbox(self) -> QSpinBox:
        return self.__pdf_page_num_spinbox

    def get_flashcard_label(self) -> QLabel:
        return self.__flashcard_label

    def get_pdf_view(self) -> QtPdfWidgets.QPdfView:
        return self.__pdf_view

    def get_pdf_doc(self) -> QtPdf.QPdfDocument:
        return self.__pdf_doc

    def get_pdf_nav(self) -> QtPdf.QPdfPageNavigator:
        return self.__pdf_nav

    def get_previous_page_button(self) -> QPushButton:
        return self.__previous_page_button

    def get_previous_flashcard_button(self) -> QPushButton:
        return self.__previous_flashcard_button

    def get_next_page_button(self) -> QPushButton:
        return self.__next_page_button

    def get_previous_card_button(self) -> QPushButton:
        return self.__previous_card_button

    def get_next_card_button(self) -> QPushButton:
        return self.__next_card_button

    def get_next_flashcard_button(self) -> QPushButton:
        return self.__next_flashcard_button

    def get_input_text_question(self) -> QPlainTextEdit:
        return self.__question_input

    def get_input_text_answer(self) -> QPlainTextEdit:
        return self.__answer_input

    def get_page_specific_checkbox(self) -> QCheckBox:
        return self.__page_specific_checkbox

    def get_page_flashcard_button(self) -> QPushButton:
        return self.__add_page_flashcard_button

    def get_generic_flashcard_button(self) -> QPushButton:
        return self.__add_generic_flashcard_button
