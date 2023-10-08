# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.

from functools import partial

from pdf_visualization.search.search_flashcard_layout import SearchFlashcardLayout
from pdf_visualization.search.search_flashcard_model import SearchFlashcardModel


class SearchFlashcardControl:
    def __init__(
        self,
        search_flashcard_layout: SearchFlashcardLayout,
        search_flashcard_model: SearchFlashcardModel,
    ) -> None:
        self.__search_flashcard_layout: SearchFlashcardLayout = search_flashcard_layout
        self.__search_flashcard_model: SearchFlashcardModel = search_flashcard_model

        self.__set_buttons()

    def __set_buttons(self) -> None:
        self.__search_flashcard_layout.get_search_input_text().textChanged.connect(
            partial(
                self.__search_flashcard_model.search_flashcard,
                consider_current_card=True,
            )
        )
        self.__search_flashcard_layout.get_continue_search().clicked.connect(
            partial(
                self.__search_flashcard_model.search_flashcard,
                consider_current_card=False,
            )
        )
