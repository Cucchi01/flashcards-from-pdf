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
