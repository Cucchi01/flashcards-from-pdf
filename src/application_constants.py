from PyQt6.QtGui import QFont

import os
from io import TextIOWrapper

APPLICATION_NAME: str = "Flashcards from PDF"
PATH_TO_DECKS_FROM_SRC: str = "../data/"
PATH_TO_DECKS_ABS: str = os.path.abspath(
    os.path.join(os.path.dirname(__file__), PATH_TO_DECKS_FROM_SRC)
)
if os.path.exists(PATH_TO_DECKS_ABS) == False:
    PATH_TO_DECKS_FROM_SRC = "./data/"
    PATH_TO_DECKS_ABS = os.path.abspath(
        os.path.join(os.path.dirname(__file__), PATH_TO_DECKS_FROM_SRC)
    )
BASE_HOME_WIDTH: int = 800
BASE_HOME_HEIGHT: int = 600
# TODO: make it choose the right language for the pdf
LANGUAGE: str = "italian"
APPLICATION_STYLE: str = 'QWidget {font: "Calisto MT", size: 14}'
FONT: QFont = QFont("Calisto MT", 14)

# file
TYPE_QUEST_GENERAL_CONSTANT: str = "g"
TYPE_QUEST_PAGE_SPECIFIC_CONSTANT: str = "p"
FIRST_PASS_TEST_FLAG_YES: str = "1"
FIRST_PASS_TEST_FLAG_NO: str = "0"
NO_ANSWER_FLAG: str = "!-!"
FILE_FLASHCARDS_SEPARATOR: str = " ?^? "
ANKI_FLASHCARDS_SEPARATOR: str = "\t"

file: TextIOWrapper
ANKI_CONTENT_DIRECTORY: str = ""
PRIVATE_FILE_WITH_FOLDER_ANKI: str = "private_folder_anki.txt"
with open(PATH_TO_DECKS_ABS + "\\" + PRIVATE_FILE_WITH_FOLDER_ANKI) as file:
    ANKI_CONTENT_DIRECTORY = file.readline().strip(" \n")


PDFS_DIRECTORY_PATH: str = ""
PRIVATE_FILE_WITH_PDFS_DIRECTORY: str = "private_pdf_folder.txt"
with open(PATH_TO_DECKS_ABS + "\\" + PRIVATE_FILE_WITH_PDFS_DIRECTORY) as file:
    PDFS_DIRECTORY_PATH = file.readline().strip(" \n")

PRIVATE_DB_FILENAME = "private_flashcards_from_pdf.db"
DB_START_TIMESTAMP_TYPE = "S"
DB_END_TIMESTAMP_TYPE = "E"

HIDDEN_ROOT_ENTRIES: list[str] = [
    PRIVATE_FILE_WITH_FOLDER_ANKI,
    PRIVATE_FILE_WITH_PDFS_DIRECTORY,
    "Anki",
    PRIVATE_DB_FILENAME,
]
