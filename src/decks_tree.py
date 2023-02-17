from PyQt6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QStyle,
    QMenu,
)
from PyQt6.QtGui import QColor, QFont, QAction, QCursor
from PyQt6.QtCore import Qt


import os

import application_costants
import pdf_visualization
from deck_directory import DirectoryEntryFolder, FILE, FOLDER
from update_pdf import update_pdf


class DecksStructure(QTreeWidget):
    def __init__(self, parent, path) -> None:
        super().__init__(parent)
        self.num_col: int = 4
        self.col_path: int = self.num_col - 1  # path column is the last
        self.root_folder: DirectoryEntryFolder = DirectoryEntryFolder(
            entry_name="root", path=path
        )
        self.pdf_window: pdf_visualization.PDFWindowVisualization
        self.menu_right_click: QMenu
        self.path_pdf_to_update: str
        self.__create_tree()

        # app = self.headerItem()
        # col = app.takeChild(self.num_col - self.num_hidden_col)
        # col.setHidden(True)
        self.__set_menu_right_click()
        self.itemDoubleClicked.connect(self.__on_emtry_double_clicked)

    def __set_menu_right_click(self) -> None:
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__open_right_click_menu)

        self.menu_right_click = QMenu("Menu", self)

        update_button = QAction("Update PDF", self.menu_right_click)
        update_button.setStatusTip(
            "Update the pdf and change accordingly the question positions"
        )
        update_button.triggered.connect(self.__update_pdf)

        self.menu_right_click.addAction(update_button)

    def __open_right_click_menu(self, event) -> None:
        full_path = self.__get_entry_full_path(self.selectedItems()[0])
        self.path_pdf_to_update = full_path
        self.menu_right_click.popup(QCursor.pos())

    def __update_pdf(self, event) -> None:
        update_pdf(self.path_pdf_to_update)

    def __on_emtry_double_clicked(
        self, entry_pressed: QTreeWidgetItem, col_pressed: int
    ):
        full_path: str = self.__get_entry_full_path(entry_pressed)
        self.pdf_window = pdf_visualization.PDFWindowVisualization(full_path)
        self.pdf_window.showMaximized()

    def __get_entry_full_path(self, entry: QTreeWidgetItem) -> str:
        name_col = 0
        full_name = entry.text(name_col)
        path_name = entry.text(self.col_path)
        full_path = os.path.join(path_name, full_name)
        return full_path

    def __create_tree(self) -> None:
        self.__set_style_tree()
        self.__create_top_level_tree()

    def __set_style_tree(self):
        self.setColumnCount(self.num_col)
        self.setFont(QFont("Calisto MT", 12))
        self.setHeaderLabels(["Name", "Type", "Buttons", "Path"])
        base_width = application_costants.BASE_HOME_WIDTH // (self.num_col)
        self.header().setDefaultSectionSize(base_width)

    def __create_top_level_tree(self):
        entries = self.__get_subtree(self.root_folder)
        self.insertTopLevelItems(0, entries)

    def __get_subtree(self, folder: DirectoryEntryFolder):
        entries: list[QTreeWidgetItem] = []

        folder_path = folder.get_path()
        self.__process_entry(
            folder_path, folder.get_immediate_decks().values(), entries
        )
        self.__process_entry(
            folder_path, folder.get_immediate_folders().values(), entries
        )

        return entries

    def __process_entry(
        self, folder_path: str, list_entries, entries: list[QTreeWidgetItem]
    ):
        for entry in list_entries:
            type = entry.get_type()
            entry_name = entry.get_entry_name()
            if type == FILE:
                child = self.__create_entry_file(entry_name, folder_path)
            elif type == FOLDER:
                assert isinstance(entry, DirectoryEntryFolder), True
                child_entries = self.__get_subtree(entry)
                child = QTreeWidgetItem([entry_name, "Dir", "", folder_path])
                child.setBackground(0, QColor(218, 224, 126))
                child.addChildren(child_entries)
            else:
                print("Element not considered")

            entries.append(child)

    def __create_entry_file(self, entry_name, path):
        ext = entry_name.split(".")[-1].upper()
        child = QTreeWidgetItem([entry_name, ext, "", path])

        pixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPlay")
        icon = self.style().standardIcon(pixmapi)
        child.setIcon(2, icon)

        return child
