from PyQt6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QStyle,
    QMenu,
)
from PyQt6.QtGui import QColor, QFont, QAction, QCursor
from PyQt6.QtCore import Qt


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
        self._path: str = path
        self.__set_entries()

    def __set_entries(self):
        self._immediate_decks: dict[str, DirectoryEntryFile]
        self._sub_folders: dict[str, DirectoryEntryFolder]
        self._immediate_decks, self._sub_folders = get_entries_from_path(self._path)

    def get_immediate_decks(self) -> dict[str, DirectoryEntryFile]:
        return self._immediate_decks

    def get_immediate_folders(self) -> dict[str, "DirectoryEntryFolder"]:
        return self._sub_folders

    def get_path(self):
        return self._path


def get_decks_structure_from_disk(root_folder_path: str) -> DirectoryEntryFolder:
    """Retrieve the decks structure

    Parameters
    ----------
    root_folder_path : str
        Path to the root folder of the decks structure

    Returns
    -------
    DirectoryEntryFolder
        Rappresentation of the directory

    """
    deck_structure = DirectoryEntryFolder(entry_name="root", path=root_folder_path)
    return deck_structure


def get_entries_from_path(
    path: str,
) -> tuple[dict[str, DirectoryEntryFile], dict[str, DirectoryEntryFolder]]:
    """Returns the entries of the path provided.

    It is a function used to retrieve the content of a folder containing .pdf and .txt files

    Parameters
    ----------
    path : str
        Path of folder containing the decks we want to extract

    Returns
    -------
    tuple[dict[str, DirectoryEntryFile], dict[str, DirectoryEntryFile]]
        The keys are the filename and the items are either the DirectoryEntryFile in the first case and the DirectoryEntryFolder for the second that are contained in the path.

    """
    immediate_decks: dict[str, DirectoryEntryFile] = dict({})
    immediate_folder: dict[str, DirectoryEntryFolder] = dict({})
    with os.scandir(path) as entries:
        files_processed: set[str] = set({})
        for entry in entries:
            if not entry.name.startswith(".") and entry.is_file():
                process_entry_file(immediate_decks, files_processed, entry.name)
            elif not entry.name.startswith(".") and entry.is_dir():
                process_entry_folder(immediate_folder, path, entry.name)
    return (immediate_decks, immediate_folder)


def process_entry_file(
    immediate_decks: dict[str, DirectoryEntryFile],
    files_processed: set[str],
    entry_name: str,
) -> None:
    """Process a file of a directory.

    It adds the DirectoryEntryFile if the filename, excluding the extension, was not encountered before. If the corrisponding .txt file is met then questions_available of that entry is set to True.

    Parameters
    ----------
    decks : dict[str, DirectoryEntryFile]
        The keys are the filename and the items are DirectoryEntryFiles contained in the path
    files_processed : set[str]
        Set containing the filenames already processed in the current folder
    entry_name : str
        Name of the entry that is going to be processed by the function

    Returns
    -------
    None


    """
    filename, file_extension = os.path.splitext(entry_name)

    match file_extension:
        case ".pdf":
            if filename not in files_processed:
                immediate_decks[filename] = DirectoryEntryFile(
                    entry_name=entry_name,
                    questions_available=False,
                )
                files_processed.add(filename)
        case ".txt":
            if filename not in files_processed:
                immediate_decks[filename] = DirectoryEntryFile(
                    entry_name=entry_name,
                    questions_available=True,
                )
                files_processed.add(filename)
            else:
                immediate_decks[filename].set_questions_available(status=True)

        case _:
            print("File {filename} not processed".format(filename=entry_name))


def process_entry_folder(
    immediate_folders: dict[str, DirectoryEntryFolder],
    path_to_folder: str,
    entry_name: str,
) -> None:
    """Process an inner directory.

    It adds the DirectoryEntryFolder to the dictionary containing the folders passed as a parameter. The creation of the sub DirectoryEntryFolder goes on recursively.

    Parameters
    ----------
    immediate_folders : dict[str, DirectoryEntryFolder]
        The keys are directory names and the items the DirectoryEntryFolder contained in the path
    path_to_folder : str
        Path to the current entry
    entry_name : str
        Name of the entry that is going to be processed by the function

    Returns
    -------
    None


    """
    child_folder = os.path.join(path_to_folder, entry_name)
    immediate_folders[entry_name] = DirectoryEntryFolder(
        entry_name=entry_name, path=child_folder
    )


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


# TODO: move this function in the proper fi.e
def update_pdf(path_pdf_to_update: str):
    print(path_pdf_to_update)
