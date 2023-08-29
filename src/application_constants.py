import os

from PyQt6.QtGui import QFont

APPLICATION_NAME = "Flashcards from PDF"
PATH_TO_DECKS_FROM_SRC = "../data/"
PATH_TO_DECKS_ABS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), PATH_TO_DECKS_FROM_SRC)
)
BASE_HOME_WIDTH = 800
BASE_HOME_HEIGHT = 600
# TODO: make it choose the right language for the pdf
LANGUAGE = "italian"
APPLICATION_STYLE = 'QWidget {font: "Calisto MT", size: 14}'
FONT = QFont("Calisto MT", 14)

# file
TYPE_QUEST_GENERAL_CONSTANT = "g"
TYPE_QUEST_PAGE_SPECIFIC_CONSTANT = "p"
ONGOING_TEST_FLAG_YES = "1"
ONGOING_TEST_FLAG_NO = "0"
NO_ANSWER_FLAG = "!-!"
FILE_FLASHCARDS_SEPARATOR = " ?^? "
