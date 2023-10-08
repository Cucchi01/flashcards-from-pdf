# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QPlainTextEdit,
)


class SearchFlashcardLayout(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Search a flashcard")

        self.__window_layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.__window_layout)

        self.__info_label_left: QLabel
        self.__search_input_text: QPlainTextEdit
        self.__continue_search: QPushButton

        self.__set_layout()

    def __set_layout(self) -> None:
        self.__info_label_left = QLabel(
            "Add the text to search. The text should be a continouos subset of either the question or the answer of a flashcard"
        )
        self.__info_label_left.setWordWrap(True)
        self.__search_input_text = QPlainTextEdit()
        self.__continue_search = QPushButton("Continue the search")

        self.__window_layout.addWidget(self.__info_label_left)
        self.__window_layout.addWidget(self.__search_input_text)
        self.__window_layout.addWidget(self.__continue_search)

    def get_search_input_text(self) -> QPlainTextEdit:
        return self.__search_input_text

    def get_continue_search(self) -> QPushButton:
        return self.__continue_search
