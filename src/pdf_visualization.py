from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from pdf2image import convert_from_path
from PIL import Image as PILImage

import sys
import os
import tempfile

from application_costants import *


class PDFWindowVisualization(QWidget):
    def __init__(self, path_of_pdf: str) -> None:
        super().__init__()

        # change the CursorShape because it takes a lot of time to load the pdf
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        self.path_of_pdf: str = path_of_pdf
        self.filename: str = os.path.basename(path_of_pdf)
        self.pdf_pages: list[PILImage.Image] = convert_from_path(
            self.path_of_pdf, dpi=500
        )
        self.index_current_page: int = 0
        self.num_pages: int = len(self.pdf_pages)
        self.tmp_dir: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
        self.question_label: QLabel
        self.back_button: QPushButton
        self.next_button: QPushButton
        self.is_back_button_disabled: bool = True
        self.is_next_button_disabled: bool = False

        self.__set_window_style()
        self.__set_window_layout()

        QApplication.restoreOverrideCursor()

    def __set_window_style(self) -> None:
        self.setWindowTitle(APPLICATION_NAME)
        self.resize(BASE_HOME_WIDTH, BASE_HOME_HEIGHT)

    def __set_window_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        header = self.__get_header_widget()
        main = self.__get_main_widget()
        bottom = self.__get_bottom_widget()

        main_layout.addWidget(header)
        main_layout.addWidget(main)
        main_layout.addWidget(bottom)

    def __get_header_widget(self) -> QWidget:
        # header
        title = QWidget(self)
        layout = QVBoxLayout()
        label = QLabel(self.filename, title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Calisto MT", 17))
        layout.addWidget(label)
        title.setLayout(layout)
        return title

    def __get_main_widget(self) -> QWidget:
        # visualization of the various pages or the questions before them
        main = QWidget(self)
        layout = QVBoxLayout()

        # TODO: add the management of the questions

        self.question_label = QLabel(main)
        self.__update_question(None)

        layout.addWidget(self.question_label)
        main.setLayout(layout)
        return main

    def __get_bottom_widget(self) -> QWidget:
        # bottom
        bottom = QWidget(self)
        layout = QHBoxLayout()

        self.back_button = QPushButton()
        self.back_button.setText("Back")
        self.back_button.setDisabled(True)
        self.back_button.clicked.connect(self.__previous_card)

        self.next_button = QPushButton()
        self.next_button.setText("Next")
        if self.num_pages == 1:
            self.next_button.setDisabled(True)
            self.is_next_button_disabled = True
        self.next_button.clicked.connect(self.__next_card)

        layout.addWidget(self.back_button)
        layout.addWidget(self.next_button)
        bottom.setLayout(layout)
        return bottom

    def __previous_card(self) -> None:
        if self.index_current_page <= 0:
            return None

        self.__change_card_index(self.index_current_page - 1)
        return None

    def __next_card(self) -> None:
        if self.index_current_page >= self.num_pages - 1:
            return None

        self.__change_card_index(self.index_current_page + 1)
        return None

    def __change_card_index(self, new_index) -> None:
        if new_index < 0 or new_index >= self.num_pages:
            print("Error: card index out of range")
            return None

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.index_current_page = new_index
        self.__update_question(None)

        self.__update_back_btn_state()
        self.__update_next_btn_state()

        QApplication.restoreOverrideCursor()
        return None

    def __update_back_btn_state(self) -> None:
        if self.index_current_page > 0 and self.is_back_button_disabled:
            self.back_button.setDisabled(False)
            self.is_back_button_disabled = False
        elif self.index_current_page == 0 and not self.is_back_button_disabled:
            self.back_button.setDisabled(True)
            self.is_back_button_disabled = True

    def __update_next_btn_state(self) -> None:
        if (
            self.index_current_page == self.num_pages - 1
            and not self.is_next_button_disabled
        ):
            self.next_button.setDisabled(True)
            self.is_next_button_disabled = True
        elif (
            self.index_current_page < self.num_pages - 1
            and self.is_next_button_disabled
        ):
            self.next_button.setDisabled(False)
            self.is_next_button_disabled = False

    def __update_question(self, event) -> IndexError | None:
        if self.index_current_page < 0 or self.index_current_page >= self.num_pages:
            print("Error: not existing card")
            return IndexError()

        #  The design choice of the creator of tempdir is to open the tmp_dir with with .. as dirname.
        #  I prefer to create a single tempdir at the start of the window and closing it at the
        #  closure of the latter
        tmp_dirname = self.tmp_dir.__enter__()
        file_path = os.path.join(tmp_dirname, "page.pgn")
        first_page = self.pdf_pages[self.index_current_page]
        # TODO: can be improved with the visualization of the page without passing from disk
        first_page.save(file_path, "png")

        pixmap = QPixmap(file_path)

        # TODO: improve the quality of this action
        pixmap = pixmap.scaled(
            BASE_HOME_WIDTH,
            BASE_HOME_HEIGHT,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        )
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setPixmap(pixmap)

        return None

    def closeEvent(self, event):
        # add the closure of the tempdir
        self.tmp_dir.cleanup()
        super().closeEvent(event)
