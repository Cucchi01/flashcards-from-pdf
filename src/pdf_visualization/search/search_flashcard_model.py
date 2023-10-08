# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


from pdf_visualization.search.search_flashcard_layout import SearchFlashcardLayout
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdf_visualization.pdf_visualization_model import PDFWindowVisualizationModel

from pdf_visualization.cards_navigator import get_flashcards_list
from flashcard.flashcard import Flashcard
from flashcard.card import Card


class SearchFlashcardModel:
    def __init__(
        self,
        search_flashcard_layout: SearchFlashcardLayout,
        pdf_visualization_model: "PDFWindowVisualizationModel",
        starting_card_index: int,
    ) -> None:
        self.__search_flashcard_layout: SearchFlashcardLayout = search_flashcard_layout
        self.__pdf_visualization_model: "PDFWindowVisualizationModel" = (
            pdf_visualization_model
        )
        self.__starting_card_index: int = starting_card_index

    def search_flashcard(self, consider_current_card: bool = True) -> None:
        if self.__pdf_visualization_model.get_is_deck_ordered() == False:
            # no search on shuffle mode
            return
        text_to_search = (
            self.__search_flashcard_layout.get_search_input_text()
            .toPlainText()
            .strip()
            .lower()
        )
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        card_index: int = self.__pdf_visualization_model.get_current_card_index()
        cards: list[Card] = self.__pdf_visualization_model.get_cards_to_display()
        num_cards: int = len(cards)

        num_pdf_pages: int = self.__pdf_visualization_model.get_num_pdf_pages()
        if num_pdf_pages > 2000:
            print(
                "Warning: search_flashcard is not efficient with a great number of pdf pages\n"
            )

        # consider the cards in a position >= than the current one
        result_search = self.__search_flashcard_interval(
            card_index, num_cards, text_to_search, cards, consider_current_card
        )

        # consider the cards in a position < than the current one
        if result_search == -1:
            result_search = self.__search_flashcard_interval(
                0, card_index, text_to_search, cards, consider_current_card
            )

        if result_search != -1:
            # jumping to a flashcard, even in shuffle mode, is allowed
            self.__pdf_visualization_model.set_current_card_index(result_search)
        else:
            self.__pdf_visualization_model.set_current_card_index(
                self.__starting_card_index
            )
        QApplication.restoreOverrideCursor()

    def __search_flashcard_interval(
        self,
        start_index: int,
        end_index: int,
        text_to_search: str,
        cards: list[Card],
        consider_current_card: bool,
    ) -> int:
        """
        Search if a text is present in the question or the answer of the flashcards in a certain interval

        Parameters
        ----------
        start_index:int
        end_index:int
                The end_index is the first index to not be considered
        text_to_search: str
        cards: list[Card]
        consider_current_card: bool

        Returns
        -------
        int
            -1 if the search was not successful. Otherwise it is returned the card index

        """
        for card_index in range(start_index, end_index):
            if (
                consider_current_card == False
                and card_index
                == self.__pdf_visualization_model.get_current_card_index()
            ):
                continue
            if isinstance(cards[card_index], Flashcard):
                flashcard: Flashcard = cards[card_index]
                if (
                    text_to_search
                    in (flashcard.get_question() + flashcard.get_answer()).lower()
                ):
                    return card_index

            card_index += 1
        return -1
