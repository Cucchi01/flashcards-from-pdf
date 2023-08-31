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
