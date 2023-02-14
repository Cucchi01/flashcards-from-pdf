from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

data = {
    "Project A": ["file_a.py", "file_a.txt", "something.xls"],
    "Project B": ["file_b.csv", "photo.jpg"],
    "Project C": [],
}


def get_decks_structure_from_disk(root_folder: str) -> dict:
    decks = {}

    return decks


class DecksStructure(QTreeWidget):
    def __init__(self, parent) -> QTreeWidget:
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["Name", "Type"])

        items = []
        for key, values in data.items():
            item = QTreeWidgetItem([key])
            for value in values:
                ext = value.split(".")[-1].upper()
                child = QTreeWidgetItem([value, ext])
                item.addChild(child)
            items.append(item)

        self.insertTopLevelItems(0, items)
