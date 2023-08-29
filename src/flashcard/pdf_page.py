from flashcard.card import Card


class PdfPage(Card):
    def __init__(
        self,
        # the number of the page in a pdf is 0-based
        num_page: int = 0,
    ) -> None:
        super().__init__()
        self.set_num_page(num_page)

    def set_num_page(self, num_page: int) -> None:
        self.num_page: int = num_page

    def get_num_page(self) -> int:
        return self.num_page

    def get_pdf_page(self) -> int:
        return self.get_num_page()
