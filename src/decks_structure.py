from PyQt6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QStyle,
)

import os

data = {
    "Project A": ["file_a.py", "file_a.txt", "something.xls"],
    "Project B": ["file_b.csv", "photo.jpg"],
    "Project C": [],
}

FOLDER = 0
FILE = 1


class DecksStructure(QTreeWidget):
    def __init__(self, parent, path) -> QTreeWidget:
        super().__init__(parent)
        self.root_folder = DirectoryEntryFolder(entry_name="root", path=path)
        self.__create_tree()

    def __create_tree(self) -> None:
        self.setColumnCount(2)
        self.setHeaderLabels(["Name", "Type", "Buttons"])
        items = []
        for key, values in data.items():
            item = QTreeWidgetItem([key])
            for value in values:
                ext = value.split(".")[-1].upper()
                child = QTreeWidgetItem([value, ext, ""])
                pixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPlay")
                icon = self.style().standardIcon(pixmapi)
                child.setIcon(2, icon)
                item.addChild(child)

            items.append(item)

        self.insertTopLevelItems(0, items)

    def __create_tree(self) -> None:
        self.setColumnCount(3)
        self.setHeaderLabels(["Name", "Type", "Buttons"])
        items = []

        item = QTreeWidgetItem(["root"])
        decks = self.root_folder.get_entries().items()
        for key, value in decks:
            type = value.get_type()
            entry_name = value.get_entry_name()
            if type == FILE:
                ext = entry_name.split(".")[-1].upper()
                child = QTreeWidgetItem([entry_name, ext, ""])
                pixmapi = getattr(QStyle.StandardPixmap, "SP_MediaPlay")
                icon = self.style().standardIcon(pixmapi)
                child.setIcon(2, icon)
                item.addChild(child)
            elif type == FOLDER:
                pass
            else:
                print("Element not considered")

            item.addChild(child)

        items.append(item)
        self.insertTopLevelItems(0, items)


class DirectoryEntry:
    def __init__(self, type: int, entry_name: str):
        self._type = type
        self._entry_name = entry_name

    def get_type(self):
        return self._type

    def get_entry_name(self):
        return self._entry_name


class DirectoryEntryFile(DirectoryEntry):
    def __init__(self, entry_name: str, questions_available: bool = None):
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


def get_decks_structure_from_disk(root_folder_path: str) -> DirectoryEntryFolder:
    deck_structure = DirectoryEntryFolder(entry_name="root", path=root_folder_path)
    return deck_structure


def get_entries_from_path(path: str) -> dict:
    decks = dict({})
    with os.scandir(path) as entries:
        files_processed = set({})
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
