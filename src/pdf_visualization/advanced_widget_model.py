from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


from pdf_visualization.advanced_widget_layout import AdvancedOptionsLayout
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdf_visualization.pdf_visualization_model import PDFWindowVisualizationModel
from flashcard.flashcard import Flashcard
from flashcard.pdf_page import PdfPage
from flashcard.card import Card


class AdvancedOptionsModel:
    def __init__(
        self,
        advance_options_layout: AdvancedOptionsLayout,
        pdf_visualization_model: "PDFWindowVisualizationModel",
    ) -> None:
        self.__advance_options_layout: AdvancedOptionsLayout = advance_options_layout
        self.__pdf_visualization_model: "PDFWindowVisualizationModel" = (
            pdf_visualization_model
        )

    def shift_left_flashcards_till_here(self) -> None:
        self.__shift_flashcards(increment=-1, end=-1)

    def shift_right_flashcards_till_here(self) -> None:
        self.__shift_flashcards(increment=+1, end=-1)

    def shift_custom_button_till_here(self) -> None:
        increment: int = (
            self.__advance_options_layout.get_shift_custom_spinbox_till_here().value()
        )
        self.__shift_flashcards(increment=increment, end=-1)

    def shift_left_flashcards_from_here(self) -> None:
        self.__shift_flashcards(
            increment=-1, end=self.__pdf_visualization_model.get_num_cards()
        )

    def shift_right_flashcards_from_here(self) -> None:
        self.__shift_flashcards(+1, end=self.__pdf_visualization_model.get_num_cards())

    def shift_custom_button_from_here(self) -> None:
        increment: int = (
            self.__advance_options_layout.get_shift_custom_spinbox_from_here().value()
        )
        self.__shift_flashcards(
            increment=increment, end=self.__pdf_visualization_model.get_num_cards()
        )

    def __shift_flashcards(self, increment: int, end: int) -> None:
        if increment == 0:
            return
        current_index: int = self.__pdf_visualization_model.get_current_card_index()
        cards: list[Card] = self.__pdf_visualization_model.get_cards_to_display()
        num_pdf_pages: int = self.__pdf_visualization_model.get_num_pdf_pages()
        step: int = 1
        if end < current_index:
            step = -1

        for i in range(current_index, end, step):
            if isinstance(cards[i], Flashcard):
                flashcard: Flashcard = cards[i]
                if flashcard.get_question_type() == Flashcard.QuestionType.GENERIC:
                    continue
                new_reference_page: int = flashcard.get_reference_page() + increment
                if flashcard.get_reference_page() + increment >= num_pdf_pages:
                    new_reference_page = num_pdf_pages - 1
                elif flashcard.get_reference_page() + increment < 0:
                    new_reference_page = 0

                flashcard.set_reference_page(new_reference_page)

        # update
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.__pdf_visualization_model.refresh_merged_cards(
            self.__pdf_visualization_model.get_is_deck_ordered()
        )
        self.__pdf_visualization_model.save_flashcards_to_file()
        self.__pdf_visualization_model.set_current_card_index(current_index)
        QApplication.restoreOverrideCursor()
