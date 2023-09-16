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

from application_constants import (
    APPLICATION_NAME,
    PATH_TO_DECKS_ABS,
    BASE_HOME_WIDTH,
    BASE_HOME_HEIGHT,
    APPLICATION_STYLE,
    FONT,
)
from decks_tree import DecksStructure

import sys


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__decks_page: QWidget
        self.__tree: DecksStructure
        self.__reload_tree_structure_button: QPushButton

        self.__set_window_style()
        self.__set_window_layout()
        self.show()

    def __set_window_style(self):
        self.setWindowTitle(APPLICATION_NAME)
        self.resize(BASE_HOME_WIDTH, BASE_HOME_HEIGHT)

    def __set_window_layout(self):
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        tab = self.__get_tab_widget()
        main_layout.addWidget(tab)

    def __get_tab_widget(self) -> QTabWidget:
        tab = QTabWidget(self)

        deck_tab = self.__get_tab_decks()
        stats_tab = self.__get_tab_stats()

        # add panes to the tab widget
        tab.addTab(deck_tab, "Decks")
        tab.addTab(stats_tab, "Stats")
        return tab

    def __get_tab_decks(self) -> QWidget:
        # decks page
        self.__decks_page = QWidget(self)
        layout = QVBoxLayout()

        self.__reload_tree_structure_button = QPushButton("Reload tree structure")
        self.__reload_tree_structure_button.clicked.connect(
            self.__reload_tree_structure
        )
        self.__reload_tree_structure_button.setStyleSheet("background-color: #F5F5F5")

        self.__tree = DecksStructure(self.__decks_page, PATH_TO_DECKS_ABS)
        self.__tree.show()

        layout.addWidget(self.__reload_tree_structure_button)
        layout.addWidget(self.__tree)
        self.__decks_page.setLayout(layout)
        return self.__decks_page

    def __reload_tree_structure(self) -> None:
        self.__tree.create_top_level_tree()

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
    app.setStyleSheet(APPLICATION_STYLE)
    app.setFont(FONT)
    window = MainWindow()
    sys.exit(app.exec())
