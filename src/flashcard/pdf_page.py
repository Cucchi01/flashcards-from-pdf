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
