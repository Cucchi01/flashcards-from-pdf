import os

APPLICATION_NAME = "Flashcards from PDF"
PATH_TO_DECKS_FROM_SRC = "../data/"
PATH_TO_DECKS_ABS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), PATH_TO_DECKS_FROM_SRC)
)
BASE_HOME_WIDTH = 800
BASE_HOME_HEIGHT = 600
# TODO: make it choose the right language for the pdf
LANGUAGE = "italian"