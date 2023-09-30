# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget


from typing import Callable


class QLabelCustom(QLabel):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.__method_to_call: Callable[..., None]

    def mouseDoubleClickEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            super().mouseDoubleClickEvent(event)
            return
        mouse_event: QMouseEvent = event
        if mouse_event.button() == Qt.MouseButton.LeftButton:
            self.__method_to_call()

        super().mouseDoubleClickEvent(event)

    def set_method_to_call(self, method_to_call: Callable[..., None]) -> None:
        self.__method_to_call = method_to_call
