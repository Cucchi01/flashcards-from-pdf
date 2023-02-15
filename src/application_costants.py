import os

APPLICATION_NAME = "Flashcards from PDF"
PATH_TO_DECKS_FROM_SRC = "../data/"
PATH_TO_DECKS_ABS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), PATH_TO_DECKS_FROM_SRC)
)
BASE_WIDTH = 800
BASE_HEIGHT = 600
