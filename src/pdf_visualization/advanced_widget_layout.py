# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
)


class AdvancedOptionsLayout(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Advanced Options")

        self.__window_layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.__window_layout)

        self.__info_label_left: QLabel
        self.__shift_left_button_till_here: QPushButton
        self.__shift_right_button_till_here: QPushButton
        self.__shift_custom_layout_till_here: QHBoxLayout = QHBoxLayout()
        self.__shift_custom_button_till_here: QPushButton
        self.__shift_custom_spinbox_till_here: QSpinBox

        self.__info_label_right: QLabel
        self.__shift_left_button_from_here: QPushButton
        self.__shift_right_button_from_here: QPushButton
        self.__shift_custom_layout_from_here: QHBoxLayout = QHBoxLayout()
        self.__shift_custom_button_from_here: QPushButton
        self.__shift_custom_spinbox_from_here: QSpinBox

        self.__set_layout()

    def __set_layout(self) -> None:
        self.__set_till_here_actions()
        self.__set_from_here_actions()

    def __set_till_here_actions(self) -> None:
        self.__info_label_left = QLabel("These actions modify till this card")
        self.__shift_left_button_till_here = QPushButton(
            "Shift flashcards one page left"
        )
        self.__shift_right_button_till_here = QPushButton(
            "Shift flashcards one page right"
        )

        self.__shift_custom_button_till_here = QPushButton("Shift custom till here")
        self.__shift_custom_spinbox_till_here = QSpinBox()
        self.__shift_custom_spinbox_till_here.setMinimum(-1000)
        self.__shift_custom_spinbox_till_here.setMaximum(1000)

        self.__shift_custom_layout_till_here.addWidget(
            self.__shift_custom_button_till_here
        )
        self.__shift_custom_layout_till_here.addWidget(
            self.__shift_custom_spinbox_till_here
        )

        self.__window_layout.addWidget(self.__info_label_left)
        self.__window_layout.addWidget(self.__shift_left_button_till_here)
        self.__window_layout.addWidget(self.__shift_right_button_till_here)
        self.__window_layout.addLayout(self.__shift_custom_layout_till_here)

    def __set_from_here_actions(self) -> None:
        self.__info_label_right = QLabel("These actions modify from this card on")
        self.__shift_left_button_from_here = QPushButton(
            "Shift flashcards one page left"
        )
        self.__shift_right_button_from_here = QPushButton(
            "Shift flashcards one page right"
        )

        self.__shift_custom_button_from_here = QPushButton("Shift custom from here")
        self.__shift_custom_spinbox_from_here = QSpinBox()
        self.__shift_custom_spinbox_from_here.setMinimum(-1000)
        self.__shift_custom_spinbox_from_here.setMaximum(1000)

        self.__shift_custom_layout_from_here.addWidget(
            self.__shift_custom_button_from_here
        )
        self.__shift_custom_layout_from_here.addWidget(
            self.__shift_custom_spinbox_from_here
        )

        self.__window_layout.addWidget(self.__info_label_right)
        self.__window_layout.addWidget(self.__shift_left_button_from_here)
        self.__window_layout.addWidget(self.__shift_right_button_from_here)
        self.__window_layout.addLayout(self.__shift_custom_layout_from_here)

    def get_shift_left_button_till_here(self) -> QPushButton:
        return self.__shift_left_button_till_here

    def get_shift_right_button_till_here(self) -> QPushButton:
        return self.__shift_right_button_till_here

    def get_shift_custom_button_till_here(self) -> QPushButton:
        return self.__shift_custom_button_till_here

    def get_shift_custom_spinbox_till_here(self) -> QSpinBox:
        return self.__shift_custom_spinbox_till_here

    def get_shift_left_button_from_here(self) -> QPushButton:
        return self.__shift_left_button_from_here

    def get_shift_right_button_from_here(self) -> QPushButton:
        return self.__shift_right_button_from_here

    def get_shift_custom_button_from_here(self) -> QPushButton:
        return self.__shift_custom_button_from_here

    def get_shift_custom_spinbox_from_here(self) -> QSpinBox:
        return self.__shift_custom_spinbox_from_here
