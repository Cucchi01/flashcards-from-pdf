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
)
from PyQt6.QtCore import Qt
from application_costants import *
from decksStructure import DecksStructure

import sys

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__set_window_style()
        self.__set_window_layout()
        self.show()

    def __set_window_style(self):
        self.setWindowTitle(APPLICATION_NAME)
        self.resize(800, 600)

    def __set_window_layout(self):
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        tab = self.__get_tab_widget()
        main_layout.addWidget(tab, 0, 0, 2, 1)

    def __get_tab_widget(self) -> QTabWidget:
        # create a tab widget
        tab = QTabWidget(self)

        deck_tab = self.__get_tab_decks()
        stats_tab = self.__get_tab_stats()

        # add panes to the tab widget
        tab.addTab(deck_tab, "Decks")
        tab.addTab(stats_tab, "Stats")
        return tab

    def __get_tab_decks(self) -> QWidget:
        # personal page
        decks_page = QWidget(self)
        layout = QVBoxLayout()
        tree = DecksStructure(decks_page)
        tree.show()
        layout.addWidget(tree)
        return decks_page

    def __get_tab_stats(self) -> QWidget:
        # personal page
        personal_page = QWidget(self)
        layout = QFormLayout()
        personal_page.setLayout(layout)
        layout.addRow("First Name:", QLineEdit(self))
        layout.addRow("Last Name:", QLineEdit(self))
        layout.addRow("DOB:", QDateEdit(self))
        return personal_page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
