from abc import ABC, abstractmethod


class Card(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_pdf_page(self) -> int:
        pass

    def get_pdf_page_for_visualization(self) -> int:
        return self.get_pdf_page() + 1
