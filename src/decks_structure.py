from PyQt6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QStyle,
)
from PyQt6.QtGui import QColor, QFont

import os
import tempfile

import application_costants
import pdf_visualization

FOLDER = 0
FILE = 1


class DirectoryEntry:
    def __init__(self, type: int, entry_name: str):
        self._type = type
        self._entry_name = entry_name

    def get_type(self):
        return self._type

    def get_entry_name(self):
        return self._entry_name


class DirectoryEntryFile(DirectoryEntry):
    def __init__(self, entry_name: str, questions_available: bool = False):
        super().__init__(type=FILE, entry_name=entry_name)
        self.questions_available = questions_available

    def set_questions_available(self, status: bool):
        self.questions_available = status


class DirectoryEntryFolder(DirectoryEntry):
    def __init__(self, entry_name: str, path: str):
        super().__init__(type=FOLDER, entry_name=entry_name)
        self._path = path
        self.__set_entries()

    def __set_entries(self):
        self._entries = get_entries_from_path(self._path)

    def get_entries(self):
        return self._entries

    def get_path(self):
        return self._path


def get_decks_structure_from_disk(root_folder_path: str) -> DirectoryEntryFolder:
    deck_structure = DirectoryEntryFolder(entry_name="root", path=root_folder_path)
    return deck_structure


def get_entries_from_path(path: str) -> dict:
    decks: dict[str, DirectoryEntryFile | DirectoryEntryFolder] = dict({})
    with os.scandir(path) as entries:
        files_processed: set[str] = set({})
        for entry in entries:
            if not entry.name.startswith(".") and entry.is_file():
                process_entry_file(decks, files_processed, entry.name)
            elif not entry.name.startswith(".") and entry.is_dir():
                process_entry_folder(decks, path, entry.name)
    return decks


def process_entry_file(decks, files_processed, entry_name):
    filename, file_extension = os.path.splitext(entry_name)
    match file_extension:
        case ".pdf":
            if filename not in files_processed:
                decks[filename] = DirectoryEntryFile(
                    entry_name=entry_name,
                    questions_available=False,
                )
                files_processed.add(filename)
        case ".txt":
            if filename not in files_processed:
                decks[filename] = DirectoryEntryFile(
                    entry_name=entry_name,
                    questions_available=True,
                )
                files_processed.add(filename)
            else:
                decks[filename].set_questions_available(status=True)
        case _:
            print("File {filename} not processed".format(filename=entry_name))


def process_entry_folder(decks, path, entry_name):
    child_folder = os.path.join(path, entry_name)
    decks[entry_name] = DirectoryEntryFolder(entry_name=entry_name, path=child_folder)


class DecksStructure(QTreeWidget):
    def __init__(self, parent, path) -> None:
        super().__init__(parent)
        self.num_col = 4
        self.path_col = self.num_col - 1  # path column is the last
        self.root_folder = DirectoryEntryFolder(entry_name="root", path=path)
        self.pdf_window = None
        self.__create_tree()

        # app = self.headerItem()
        # col = app.takeChild(self.num_col - self.num_hidden_col)
        # col.setHidden(True)
        self.itemDoubleClicked.connect(self.__onItemClicked)

    def __onItemClicked(self, entry_pressed, col_pressed):
        name_col = 0
        full_name = entry_pressed.text(name_col)
        path_name = entry_pressed.text(self.path_col)
        full_path = os.path.join(path_name, full_name)
        self.pdf_window = pdf_visualization.PDFWindowVisualization(full_path)
        self.pdf_window.show()

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
        entries = []
        decks = folder.get_entries().items()
        for _, value in decks:
            type = value.get_type()
            entry_name = value.get_entry_name()
            entry_pathname = folder.get_path()
            if type == FILE:
                child = self.__create_entry_file(entry_name, entry_pathname)
            elif type == FOLDER:
                child_entries = self.__get_subtree(value)
                child = QTreeWidgetItem([entry_name, "Dir", "", entry_pathname])
                child.setBackground(0, QColor(218, 224, 126))
                child.addChildren(child_entries)
            else:
                print("Element not considered")

            entries.append(child)

        return entries

    def __create_entry_file(self, entry_name, path):
        ext = entry_name.split(".")[-1].upper()
        child = QTreeWidgetItem([entry_name, ext, "", path])

        pixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPlay")
        icon = self.style().standardIcon(pixmapi)
        child.setIcon(2, icon)

        return child
