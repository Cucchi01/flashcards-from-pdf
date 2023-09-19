from PyQt6.QtWidgets import QApplication, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

import datetime
from typing import TYPE_CHECKING

# always false at running time. It is used for mypy typing check and avoiding circular imports
if TYPE_CHECKING:
    from pdf_visualization.pdf_visualization_model import PDFWindowVisualizationModel

from pdf_visualization.pdf_visualization_layout import PDFWindowVisualizationLayout
from pdf_visualization.cards_navigator import CardsNavigator

if TYPE_CHECKING:
    from pdf_test_info import PDFTestsInfo
from flashcard.flashcard import Flashcard
from flashcard.pdf_page import PdfPage
from flashcard.card import Card
from IO_flashcards_management import IOFlashcards


class TestManager:
    def __init__(
        self,
        pdf_window_model: "PDFWindowVisualizationModel",
        pdf_window_layout: PDFWindowVisualizationLayout,
    ) -> None:
        self.__pdf_window_model: "PDFWindowVisualizationModel" = pdf_window_model
        self.__pdf_window_layout: PDFWindowVisualizationLayout = pdf_window_layout

    def update_still_learning_button(self) -> None:
        self.__update_test_button(self.__pdf_window_layout.get_still_learning_button())

    def update_know_button(self) -> None:
        self.__update_test_button(self.__pdf_window_layout.get_know_button())

    def __update_test_button(self, button: QPushButton) -> None:
        if (
            self.__pdf_window_model.get_is_deck_ordered()
            or self.__pdf_window_model.get_num_not_done_flashcards() == 0
        ):
            button.setDisabled(True)
        else:
            button.setDisabled(False)

    def still_learning_answer(self) -> None:
        self.__change_current_flashcard_result(Flashcard.Result.STILL_LEARNING)

    def know_answer(self) -> None:
        self.__change_current_flashcard_result(Flashcard.Result.KNOW)

    def __change_current_flashcard_result(self, result: Flashcard.Result) -> None:
        if (
            self.__pdf_window_model.get_is_deck_ordered()
            or self.__pdf_window_model.get_num_not_done_flashcards() == 0
        ):
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        flashcard: Flashcard = self.__get_current_flashcard()
        flashcard.set_current_result(result)
        self.__finalize_flashcard_change()
        QApplication.restoreOverrideCursor()

    def __get_current_flashcard(self) -> Flashcard:
        cards_to_display: list[Card] = self.get_cards_navigator().get_cards_to_display()
        num_flashcard_to_card_index: list[
            int
        ] = self.get_cards_navigator().get_num_flashcard_to_card_index()
        current_flashcard_card_index: int = num_flashcard_to_card_index[
            self.get_cards_navigator().get_current_flashcard_index()
        ]
        if isinstance(cards_to_display[current_flashcard_card_index], Flashcard):
            flashcard: Flashcard = cards_to_display[current_flashcard_card_index]
        else:
            raise ValueError()
        return flashcard

    def __finalize_flashcard_change(self) -> None:
        if self.__pdf_window_model.get_num_not_done_flashcards() == 1:
            # this is the last flashcard
            self.__update_tests_info()
            self.__show_dialog_test_completed()
            self.__setup_next_test()

        self.__pdf_window_model.save_flashcards_to_file()
        self.__pdf_window_model.refresh_merged_cards(
            self.__pdf_window_model.get_is_deck_ordered()
        )

        self.get_cards_navigator().set_current_card_index(0)

    def __update_tests_info(self) -> None:
        pdf_tests_info: "PDFTestsInfo" = self.get_pdf_tests_info()
        if pdf_tests_info.get_first_pass_flag() == pdf_tests_info.FirstPass.TRUE:
            current_moment: datetime.datetime = datetime.datetime.now()
            percentage: float = self.__get_current_test_percentage()
            pdf_tests_info.add_completed_test(current_moment, percentage)

    def __show_dialog_test_completed(self) -> None:
        percentage: float = self.__get_current_test_percentage()
        dialog: QMessageBox = QMessageBox(self.__pdf_window_layout)
        dialog.setText("Result: " + str(percentage) + "%")
        dialog.setWindowTitle("Test completed")
        dialog.show()

    def __get_current_test_percentage(self) -> float:
        num_know: int = 0
        num_flashcards: int = 0
        list_flashcard: list[Flashcard]
        for (
            _,
            list_flashcard,
        ) in self.__pdf_window_model.get_flashcards_from_pdf_page().items():
            for flashcard in list_flashcard:
                num_flashcards += 1
                if flashcard.get_current_result() == Flashcard.Result.KNOW:
                    num_know += 1

        return num_know / num_flashcards * 100

    def __setup_next_test(self) -> None:
        list_flashcard: list[Flashcard]
        finished: bool = abs(self.__get_current_test_percentage() - 100.0) <= 4e-4
        if finished:
            self.get_pdf_tests_info().set_first_pass_flag(
                self.get_pdf_tests_info().FirstPass.TRUE
            )
            self.__pdf_window_model.refresh_page(is_deck_ordered=True)
        else:
            self.get_pdf_tests_info().set_first_pass_flag(
                self.get_pdf_tests_info().FirstPass.FALSE
            )

        for (
            _,
            list_flashcard,
        ) in self.__pdf_window_model.get_flashcards_from_pdf_page().items():
            for flashcard in list_flashcard:
                if finished or flashcard.get_current_result() != Flashcard.Result.KNOW:
                    flashcard.set_current_result(Flashcard.Result.NOT_DONE)

    def get_cards_navigator(self) -> CardsNavigator:
        return self.__pdf_window_model.get_cards_navigator()

    def get_pdf_tests_info(self) -> "PDFTestsInfo":
        return self.__pdf_window_model.get_pdf_tests_info()
