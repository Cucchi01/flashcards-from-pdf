from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QFormLayout,
    QGridLayout,
    QTabWidget,
    QLineEdit,
    QDateEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from application_costants import *
from decks_tree import DecksStructure

import sys


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__set_window_style()
        self.__set_window_layout()
        self.show()

    def __set_window_style(self):
        self.setWindowTitle(APPLICATION_NAME)
        self.resize(BASE_HOME_WIDTH, BASE_HOME_HEIGHT)

    def __set_window_layout(self):
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        tab = self.__get_tab_widget()
        main_layout.addWidget(tab, 0, 0, 2, 1)

    def __get_tab_widget(self) -> QTabWidget:
        tab = QTabWidget(self)
        tab.setFont(QFont("Calisto MT", 14))

        deck_tab = self.__get_tab_decks()
        stats_tab = self.__get_tab_stats()

        # add panes to the tab widget
        tab.addTab(deck_tab, "Decks")
        tab.addTab(stats_tab, "Stats")
        return tab

    def __get_tab_decks(self) -> QWidget:
        # decks page
        decks_page = QWidget(self)
        layout = QVBoxLayout()
        tree = DecksStructure(decks_page, PATH_TO_DECKS_ABS)
        tree.show()
        layout.addWidget(tree)
        decks_page.setLayout(layout)
        return decks_page

    def __get_tab_stats(self) -> QWidget:
        # statistics page
        stats_page = QWidget(self)
        layout = QVBoxLayout()
        label = QLabel(self)
        label.setText("Work in progress...")
        layout.addWidget(label)
        stats_page.setLayout(layout)
        return stats_page


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
