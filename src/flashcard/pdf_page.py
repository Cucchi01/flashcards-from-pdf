# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from flashcard.card import Card


class PdfPage(Card):
    GENERIC_CARD_INDEX = -1

    def __init__(
        self,
        num_page: int = 0,
    ) -> None:
        super().__init__()
        self.set_num_page(num_page)
        self.__card_index: int = PdfPage.GENERIC_CARD_INDEX

    def set_num_page(self, num_page: int) -> None:
        self.num_page: int = num_page

    def get_num_page(self) -> int:
        return self.num_page

    def get_pdf_page(self) -> int:
        return self.get_num_page()

    def get_card_index(self) -> int:
        return self.__card_index

    def set_card_index(self, new_card_index: int) -> None:
        self.__card_index = new_card_index

    def compare_to(self, value: "PdfPage") -> bool:
        return self.get_num_page() == value.get_num_page()
