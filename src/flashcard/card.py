from abc import ABC, abstractmethod


class Card(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_pdf_page(self) -> int:
        pass
