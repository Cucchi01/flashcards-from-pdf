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

import sys
import os

from application_costants import *


class PDFWindowVisualization(QWidget):
    def __init__(self, path_of_pdf: str) -> None:
        super().__init__()

        self.path_of_pdf = path_of_pdf
        self.filename = os.path.basename(path_of_pdf)

        self.__set_window_style()
        self.__set_window_layout()
        self.show()

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

        file_path = "".join([os.path.dirname(__file__), "\\night.jpg"])
        pixmap = QPixmap(file_path)
        pixmap = pixmap.scaled(
            BASE_HOME_WIDTH // 2,
            BASE_HOME_HEIGHT // 2,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        )
        label = QLabel(main)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(pixmap)

        label.setMaximumSize(BASE_HOME_WIDTH, BASE_HOME_HEIGHT)

        layout.addWidget(label)
        main.setLayout(layout)
        return main

    def __get_bottom_widget(self) -> QWidget:
        # bottom
        bottom = QWidget(self)
        layout = QHBoxLayout()

        back_button = QPushButton()
        back_button.setText("Back")
        next_button = QPushButton()
        next_button.setText("Next")

        layout.addWidget(back_button)
        layout.addWidget(next_button)
        bottom.setLayout(layout)
        return bottom


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # TODO: put the right path
    window = PDFWindowVisualization("/path/to/file.pdf")
    sys.exit(app.exec())
