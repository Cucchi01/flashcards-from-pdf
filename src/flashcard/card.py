# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from abc import ABC, abstractmethod


class Card(ABC):
    DEFAULT_VALUE: int = -5

    def __init__(self) -> None:
        self.__pdf_page_index_before: int = -1
        self.__flashcard_index_before: int = -1
        pass

    @abstractmethod
    def get_pdf_page(self) -> int:
        pass

    @abstractmethod
    def compare_to(self, value: "Card") -> bool:
        pass

    def get_pdf_page_for_visualization(self) -> int:
        return self.get_pdf_page() + 1

    def get_pdf_page_index_before(self) -> int:
        return self.__pdf_page_index_before

    def get_flashcard_index_before(self) -> int:
        return self.__flashcard_index_before

    def set_pdf_page_index_before(self, new_value: int) -> None:
        self.__pdf_page_index_before = new_value

    def set_flashcard_index_before(self, new_value: int) -> None:
        self.__flashcard_index_before = new_value
