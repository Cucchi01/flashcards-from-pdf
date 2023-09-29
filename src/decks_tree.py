from PyQt6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QStyle,
    QMenu,
    QHeaderView,
    QApplication,
)
from PyQt6.QtGui import QColor, QFont, QAction, QCursor
from PyQt6.QtCore import Qt

import os
from typing import Optional

import application_constants
from pdf_visualization.pdf_visualization_control import PDFWindowVisualizationControl
from pdf_visualization.pdf_visualization_layout import PDFWindowVisualizationLayout
from deck_directory import DirectoryEntryFolder, DirectoryEntryFile, FILE, FOLDER
from update_pdf import update_file
from IO_flashcards_management import IOFlashcards


class DecksStructure(QTreeWidget):
    def __init__(self, parent, path: str) -> None:
        super().__init__(parent)

        self.__set_state_variable(path)
        self.__create_tree()

        # app = self.headerItem()
        # col = app.takeChild(self.num_col - self.num_hidden_col)
        # col.setHidden(True)
        self.__set_menu_right_click()
        self.itemDoubleClicked.connect(self.__on_entry_double_clicked)

    def __set_state_variable(self, path: str) -> None:
        self.__num_col: int = 4
        self.__col_path: int = self.__num_col - 1  # path column is the last
        self.__path: str = path
        self.__root_folder: DirectoryEntryFolder
        self.__pdf_window_control: PDFWindowVisualizationControl
        self.__menu_right_click: QMenu
        self.__path_to_update: str

    def __create_tree(self) -> None:
        self.__set_style_tree()
        self.create_top_level_tree()

    def __set_style_tree(self) -> None:
        self.setColumnCount(self.__num_col)
        self.setFont(QFont("Calisto MT", 12))
        self.setHeaderLabels(["Name", "Type", "Buttons", "Path"])
        base_width = application_constants.BASE_HOME_WIDTH // (self.__num_col)
        app: Optional[QHeaderView] = self.header()
        if app is None:
            raise ValueError()
        header: QHeaderView = app
        header.setDefaultSectionSize(base_width)

    def create_top_level_tree(self) -> None:
        self.clear()
        self.__root_folder = DirectoryEntryFolder(entry_name="root", path=self.__path)
        entries = self.__get_subtree(self.__root_folder)
        self.insertTopLevelItems(
            0,
            filter(
                lambda entry: entry.text(0)
                not in application_constants.HIDDEN_ROOT_ENTRIES,
                entries,
            ),
        )

    def __get_subtree(self, folder: DirectoryEntryFolder) -> list[QTreeWidgetItem]:
        entries: list[QTreeWidgetItem] = []

        folder_path = folder.get_path()
        self.__process_entry(
            folder_path, list(folder.get_immediate_decks().values()), entries
        )
        self.__process_entry(
            folder_path, list(folder.get_immediate_folders().values()), entries
        )

        return entries

    def __process_entry(
        self,
        folder_path: str,
        list_entries: list[DirectoryEntryFile] | list[DirectoryEntryFolder],
        entries: list[QTreeWidgetItem],
    ) -> None:
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

    def __create_entry_file(self, entry_name: str, path: str) -> QTreeWidgetItem:
        ext = entry_name.split(".")[-1].upper()
        child = QTreeWidgetItem([entry_name, ext, "", path])

        pixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPlay")
        app: Optional[QStyle] = self.style()
        if app is None:
            raise ValueError()
        style: QStyle = app
        icon = style.standardIcon(pixmapi)
        child.setIcon(2, icon)

        return child

    def __set_menu_right_click(self) -> None:
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__open_right_click_menu)

        self.__menu_right_click = QMenu("Menu", self)

        update_button = QAction("Update", self.__menu_right_click)
        update_button.setStatusTip(
            "Update the pdf and change accordingly the flashcard positions"
        )
        update_button.triggered.connect(self.__update_file)

        export_anki_button = QAction("Export to txt", self.__menu_right_click)
        export_anki_button.setStatusTip(
            "Creates the txt file that should be used to import the flashcards in Anki"
        )
        export_anki_button.triggered.connect(self.__export_to_anki)

        self.__menu_right_click.addAction(update_button)
        self.__menu_right_click.addAction(export_anki_button)

    def __open_right_click_menu(self, event) -> None:
        selected_items = self.selectedItems()

        if self.__is_valid_click(selected_items):
            full_path = self.__get_entry_full_path(selected_items[0])
            self.__path_to_update = full_path
            self.__menu_right_click.popup(QCursor.pos())

    def __is_valid_click(self, selected_items: list[QTreeWidgetItem]) -> bool:
        return len(selected_items) > 0

    def __update_file(self, event) -> None:
        update_file(self.__path_to_update)

    def __export_to_anki(self, event) -> None:
        _, ext = os.path.splitext(self.__path_to_update)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        if ext == ".pdf":
            IOFlashcards.save_flashcards_to_anki(self.__path_to_update)
        elif ext == "":
            self.__export_directory_to_anki(self.__path_to_update)

        QApplication.restoreOverrideCursor()

    def __export_directory_to_anki(self, path_dir_to_update: str) -> None:
        dirpath: str
        dirnames: list[str]
        filenames: list[str]
        filename: str
        for dirpath, dirnames, filenames in os.walk(path_dir_to_update):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                IOFlashcards.save_flashcards_to_anki(full_path)

    def __on_entry_double_clicked(
        self, entry_pressed: QTreeWidgetItem, col_pressed: int
    ) -> None:
        full_path: str = self.__get_entry_full_path(entry_pressed)
        app = full_path.strip().lower()[-4:]
        if app == ".pdf":
            self.__pdf_window_control = PDFWindowVisualizationControl(full_path)
            self.__pdf_window_control.get_pdf_window_visualization_layout().showMaximized()

    def __get_entry_full_path(self, entry: QTreeWidgetItem) -> str:
        name_col = 0
        full_name = entry.text(name_col)
        path_name = entry.text(self.__col_path)
        full_path = os.path.join(path_name, full_name)
        return full_path
