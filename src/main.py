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
    PRIVATE_DB_FILENAME,
    DB_START_TIMESTAMP_TYPE,
    DB_END_TIMESTAMP_TYPE,
    APPLICATION_LOG_PATH,
)
from decks_tree import DecksStructure
from statistics.statistics import get_statistics, create_table_timestamp

import sys
import sqlite3
import os
from datetime import datetime
import logging
import traceback


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
        layout.addWidget(get_statistics())
        layout.addWidget(label)
        stats_page.setLayout(layout)
        return stats_page


def add_new_start_timestamp() -> None:
    add_time_stamp(DB_START_TIMESTAMP_TYPE)


def add_new_end_timestamp() -> None:
    add_time_stamp(DB_END_TIMESTAMP_TYPE)


def add_time_stamp(type_ins: str) -> None:
    try:
        con: sqlite3.Connection = sqlite3.connect(
            os.path.join(PATH_TO_DECKS_ABS, PRIVATE_DB_FILENAME)
        )
        cur: sqlite3.Cursor = con.cursor()
        create_table_timestamp(cur)
        __insert_timestamp(con, cur, type_ins)
        cur.close()
    finally:
        if con:
            con.close()


def __insert_timestamp(
    con: sqlite3.Connection, cur: sqlite3.Cursor, type_ins: str
) -> None:
    insert_query = """INSERT INTO 'timestamp'
                            ('timestamp', 'type') 
                            VALUES (?, ?);"""

    data_insert = (datetime.now(), type_ins)
    cur.execute(insert_query, data_insert)
    con.commit()


def __write_error_log(exc: Exception) -> None:
    logging.error(traceback.format_exc())


if __name__ == "__main__":
    add_new_start_timestamp()
    exit_code: int = 0
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(APPLICATION_STYLE)
        app.setFont(FONT)
        window = MainWindow()
        exit_code = app.exec()
    except Exception as exc:
        __write_error_log(exc)
    finally:
        add_new_end_timestamp()

        sys.exit(exit_code)
