from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import Qt, QPointF
from PyQt6 import QtPdf, QtPdfWidgets

import os
from typing import Optional
from random import shuffle


from typing import TYPE_CHECKING

# always false at running time. It is used for mypy typing check and avoiding circular imports
if TYPE_CHECKING:
    from pdf_visualization.pdf_visualization_model import PDFWindowVisualizationModel
from flashcard.flashcard import Flashcard
from flashcard.pdf_page import PdfPage
from flashcard.card import Card
from IO_flashcards_management import IOFlashcards
from test_management.pdf_test_info import PDFTestsInfo


class CardNavigator:
    def __init__(self, pdf_window_model: "PDFWindowVisualizationModel") -> None:
        self.__pdf_window_model: "PDFWindowVisualizationModel" = pdf_window_model
        self.__flashcards_from_pdf_page: dict[
            int, list[Flashcard]
        ] = self.__pdf_window_model.get_flashcards_from_pdf_page()

        self.__current_card_index: int = 0
        self.__is_page_spinbox_event_disabled: bool = False
        self.__is_previous_page_button_disabled = True
        self.__is_next_page_button_disabled: bool = False
        self.__is_previous_flashcard_button_disabled: bool = True
        self.__is_previous_card_button_disabled: bool = True
        self.__is_next_card_button_disabled: bool = False
        self.__is_next_flashcard_button_disabled: bool = True
        self.__shuffle_pdf_navigator: CardNavigator.ShufflePdfPageNavigator = (
            CardNavigator.ShufflePdfPageNavigator()
        )

        self.__setup_current_card_bottom_layout()

    def get_current_card_index(self) -> int:
        return self.__current_card_index

    def __get_num_pdf_pages(self) -> int:
        return self.__pdf_window_model.get_num_pdf_pages()

    def __get_cards_to_display(self) -> list[Card]:
        return self.__pdf_window_model.get_cards_to_display()

    def __get_num_pdf_page_to_card_index(self) -> list[int]:
        return self.__pdf_window_model.get_num_pdf_page_to_card_index()

    def __get_num_flashcard_to_card_index(self) -> list[int]:
        return self.__pdf_window_model.get_num_flashcard_to_card_index()

    def __get_num_cards(self) -> int:
        return self.__pdf_window_model.get_num_cards()

    def __get_is_deck_ordered(self) -> bool:
        return self.__pdf_window_model.get_is_deck_ordered()

    def __setup_current_card_bottom_layout(self) -> None:
        if self.__get_num_cards() == 1:
            self.__is_next_card_button_disabled = True

    def restart_visualization(self) -> None:
        self.change_card_index(0)
        self.__shuffle_pdf_navigator.set_is_page_navigator_active(False)

    def update_page_spinbox_change(self) -> None:
        if not self.__is_page_spinbox_event_disabled:
            new_page_num: int = self.__get_pdf_page_from_spinbox()
            if new_page_num < 0 or new_page_num >= self.__get_num_pdf_pages():
                raise ValueError("Page value not valid")

            self.change_card_index(
                self.__get_num_pdf_page_to_card_index()[new_page_num]
            )

    def __get_pdf_page_from_spinbox(self) -> int:
        return self.__pdf_window_model.get_pdf_page_from_spinbox()

    def previous_page(self) -> None:
        new_card_index: int
        index_page_before: int = self.__get_previous_page_index_previous_page_button()
        if index_page_before >= 0:
            new_card_index = self.__get_new_card_index_page_buttons(index_page_before)
            self.__check_activation_shuffle_navigator()
            self.change_card_index(new_card_index)

    def next_page(self) -> None:
        new_card_index: int
        next_page_index: int = self.__get_next_page_index()
        if next_page_index >= 0 and next_page_index < self.__get_num_pdf_pages():
            new_card_index = self.__get_new_card_index_page_buttons(next_page_index)
            self.__check_activation_shuffle_navigator()
            self.change_card_index(new_card_index)

    def __get_new_card_index_page_buttons(self, next_page_index: int) -> int:
        new_card_index: int
        if (
            True
            or self.__get_is_deck_ordered()
            or isinstance(
                self.__get_cards_to_display()[self.__current_card_index], PdfPage
            )
        ):
            new_card_index = self.__get_num_pdf_page_to_card_index()[next_page_index]
        else:
            # if the deck is not ordered and the current card is a flashcard, the next page card index is the next card
            # TODO: modify, it doesn't work for previous page btn
            new_card_index = self.__current_card_index + 1
        return new_card_index

    def __check_activation_shuffle_navigator(self):
        # In shuffle mode, after clicking previous page or next page on a pdf page the shuffle navigator should be active
        if (
            self.__shuffle_pdf_navigator.get_is_page_navigator_active() == False
            and isinstance(
                self.__get_cards_to_display()[self.__current_card_index], PdfPage
            )
            and self.__get_is_deck_ordered() == False
        ):
            self.__active_shuffle_navigator()

    def __active_shuffle_navigator(self):
        self.__shuffle_pdf_navigator.set_is_page_navigator_active(True)
        self.__shuffle_pdf_navigator.set_starting_pdf_page(
            self.__get_cards_to_display()[self.__current_card_index]
        )

    class ShufflePdfPageNavigator:
        """It is possible to navigate through the PDF during the shuffle mode. This class is used to know when you are on a PDF page that is the same as the one that started the navigation."""

        def __init__(self):
            self.__starting_pdf_page: PdfPage
            self.__is_page_navigator_active: bool = False

        def set_starting_pdf_page(self, starting_pdf_page: PdfPage) -> None:
            self.__starting_pdf_page = starting_pdf_page

        def set_is_page_navigator_active(self, is_page_navigator_active: bool) -> None:
            self.__is_page_navigator_active = is_page_navigator_active

        def get_starting_pdf_page(self) -> PdfPage:
            return self.__starting_pdf_page

        def get_is_page_navigator_active(self) -> bool:
            return self.__is_page_navigator_active

    def previous_card(self) -> None:
        if isinstance(
            self.__get_cards_to_display()[self.__current_card_index], Flashcard
        ):
            flashcard: Flashcard = self.__get_cards_to_display()[
                self.__current_card_index
            ]
            # if an answer is visualized, the previous step is the question
            if flashcard.get_answer() == self.__get_flashcard_label_text():
                self.__set_flashcard_label_text(flashcard.get_question())
                self.__update_previous_card_button_state()
                self.__update_next_card_button_state()
                return

        if self.__current_card_index <= 0:
            return

        self.change_card_index(self.__current_card_index - 1)

    def next_card(self) -> None:
        if self.__current_card_index >= self.__get_num_cards() - 1:
            return None

        # if an question is visualized, the next step is the answer, if present
        card: Card = self.__get_cards_to_display()[self.__current_card_index]
        if isinstance(
            self.__get_cards_to_display()[self.__current_card_index], Flashcard
        ):
            flashcard: Flashcard = card
            if (
                self.__get_flashcard_label_text() != flashcard.get_answer()
                and flashcard.get_answer() != ""
            ):
                self.__set_flashcard_label_text(flashcard.get_answer())
                self.__update_previous_card_button_state()
                self.__update_next_card_button_state()
                return

        self.change_card_index(self.__current_card_index + 1)

    def __get_flashcard_label_text(self) -> str:
        return self.__pdf_window_model.get_flashcard_label_text()

    def __set_flashcard_label_text(self, new_string: str) -> str:
        return self.__pdf_window_model.set_flashcard_label_text(new_string)

    def previous_flashcard(self) -> None:
        new_card_index: int
        index_flashcard_before: int = self.__get_index_flashcard_before()
        if index_flashcard_before != -1:
            new_card_index = self.__get_num_flashcard_to_card_index()[
                index_flashcard_before
            ]
            self.change_card_index(new_card_index)

    def next_flashcard(self) -> None:
        new_card_index: int
        next_flashcard_index: int = self.__get_next_flashcard_index()
        if next_flashcard_index < self.__get_num_flashcards():
            new_card_index = self.__get_num_flashcard_to_card_index()[
                next_flashcard_index
            ]
            self.change_card_index(new_card_index)

    def __get_index_flashcard_before(self) -> int:
        index_flashcard_before: int
        if (
            self.__get_is_deck_ordered() == False
            and self.__shuffle_pdf_navigator.get_is_page_navigator_active()
        ):
            index_flashcard_before = (
                self.__shuffle_pdf_navigator.get_starting_pdf_page().get_flashcard_index_before()
            )
        else:
            index_flashcard_before = self.__get_cards_to_display()[
                self.__current_card_index
            ].get_flashcard_index_before()
        return index_flashcard_before

    def change_card_index(self, new_index) -> None:
        if new_index < 0 or new_index >= self.__get_num_cards():
            raise ValueError("Error: card index out of range")

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.__current_card_index = new_index
        self.__check_deactivation_shuffle_navigator()
        self.__update_layout()
        QApplication.restoreOverrideCursor()

    def __check_deactivation_shuffle_navigator(self) -> None:
        # In shuffle mode, multiple PdfPage instances of the same pdf page could have been created. So, the comparison has to be done on the content and not on the reference.
        # The reason for this design choice is that a PDF page could be referenced by multiple flashcards, so you can't store in a single instance of a PdfPage the last flashcard because this value would overwrite the other admissible values. A set of all possible previous flashcards isn't also a possible choice, because in that case, you wouldn't know which is the last flashcard among them, that we want to consider.
        # When using the next page button or the previous page button the change of card is made using a num_pdf_page_to_card_index a vector that gives for each pdf_page_index the corresponding card_index. The choice of the vector is for the same reasons explained before. It is only a vector so it can store only one of the possible instances of a PdfPage. For this reason, doing next_page and then previous_page can take to a different PdfPage instance from the starting one.
        if self.__shuffle_pdf_navigator.get_is_page_navigator_active() and (
            (
                self.__get_cards_to_display()[self.__current_card_index].__class__
                == self.__shuffle_pdf_navigator.get_starting_pdf_page().__class__
                and self.__get_cards_to_display()[self.__current_card_index].compare_to(
                    self.__shuffle_pdf_navigator.get_starting_pdf_page()
                )
            )
        ):
            self.__shuffle_pdf_navigator.set_is_page_navigator_active(False)
            self.change_card_index(
                self.__shuffle_pdf_navigator.get_starting_pdf_page().get_card_index()
            )
        elif self.__shuffle_pdf_navigator.get_is_page_navigator_active() and isinstance(
            self.__get_cards_to_display()[self.__current_card_index], Flashcard
        ):
            # the navigator is active only when going through pdf pages
            self.__shuffle_pdf_navigator.set_is_page_navigator_active(False)

    def __update_layout(self) -> None:
        self.__update_previous_flashcard_button_state()
        self.__update_next_flashcard_button_state()
        self.__update_previous_page_button_state()
        self.__update_next_page_button_state()

        self.__update_card(None)

        self.__pdf_window_model.update_page_pos_layout()
        self.__update_previous_card_button_state()
        self.__update_next_card_button_state()

    def __update_previous_page_button_state(self) -> None:
        previous_page_index: int = self.__get_previous_page_index_previous_page_button()
        if previous_page_index >= 0 and self.__is_previous_page_button_disabled:
            self.__get_previous_page_button().setDisabled(False)
            self.__is_previous_page_button_disabled = False
        elif previous_page_index < 0 and not self.__is_previous_page_button_disabled:
            self.__get_previous_page_button().setDisabled(True)
            self.__is_previous_page_button_disabled = True

    def __get_previous_page_button(self) -> QPushButton:
        return self.__pdf_window_model.get_previous_page_button()

    def __get_previous_page_index_previous_page_button(self) -> int:
        previous_page_index: int
        # When there is an ordered visualization or the current card is a PDF page, it uses the information saved during the generation of the cards. When the deck is shuffled and it is currently displayed a Flashcard, the PDF page before is the one referenced by the flashcard before, if present
        if self.__get_is_deck_ordered() == False and isinstance(
            self.__get_cards_to_display()[self.__current_card_index], Flashcard
        ):
            index_flashcard_before: int = self.__get_cards_to_display()[
                self.__current_card_index
            ].get_flashcard_index_before()
            if index_flashcard_before == -1:
                previous_page_index = Flashcard.GENERIC_PAGE
            else:
                card: Card = self.__get_cards_to_display()[
                    self.__get_num_flashcard_to_card_index()[index_flashcard_before]
                ]
                previous_page_index = card.get_pdf_page_index_before() + 1
        else:
            previous_page_index = self.__get_cards_to_display()[
                self.__current_card_index
            ].get_pdf_page_index_before()

        return previous_page_index

    def __update_next_page_button_state(self) -> None:
        next_page_index: int = self.__get_next_page_index()

        if next_page_index < 0 or next_page_index == self.__get_num_pdf_pages():
            self.__get_next_page_button().setDisabled(True)
            self.__is_next_page_button_disabled = True
        elif next_page_index < self.__get_num_pdf_pages():
            self.__get_next_page_button().setDisabled(False)
            self.__is_next_page_button_disabled = False

    def __get_next_page_index(self) -> int:
        next_page_index: int = (
            self.__get_cards_to_display()[
                self.__current_card_index
            ].get_pdf_page_index_before()
            + 1
        )
        if isinstance(
            self.__get_cards_to_display()[self.__current_card_index], PdfPage
        ):
            next_page_index += 1
        return next_page_index

    def __get_next_page_button(self) -> QPushButton:
        return self.__pdf_window_model.get_next_page_button()

    def __update_previous_flashcard_button_state(self) -> None:
        previous_flashcard_index: int = self.__get_index_flashcard_before()
        if previous_flashcard_index >= 0:
            self.__get_previous_flashcard_button().setDisabled(False)
            self.__is_previous_flashcard_button_disabled = False
        elif previous_flashcard_index == -1:
            self.__get_previous_flashcard_button().setDisabled(True)
            self.__is_previous_flashcard_button_disabled = True

    def __get_previous_flashcard_button(self) -> QPushButton:
        return self.__pdf_window_model.get_previous_flashcard_button()

    def __update_next_flashcard_button_state(self) -> None:
        next_flashcard_index = self.__get_next_flashcard_index()
        if next_flashcard_index == self.__get_num_flashcards():
            self.__get_next_flashcard_button().setDisabled(True)
            self.__is_next_flashcard_button_disabled = True
        elif (
            next_flashcard_index >= 0
            and next_flashcard_index < self.__get_num_flashcards()
        ):
            self.__get_next_flashcard_button().setDisabled(False)
            self.__is_next_flashcard_button_disabled = False

    def __get_next_flashcard_index(self) -> int:
        next_flashcard_index: int = self.__get_index_flashcard_before() + 1
        if isinstance(
            self.__get_cards_to_display()[self.__current_card_index], Flashcard
        ):
            next_flashcard_index += 1
        return next_flashcard_index

    def __get_next_flashcard_button(self) -> QPushButton:
        return self.__pdf_window_model.get_next_flashcard_button()

    def __get_num_flashcards(self):
        return self.__pdf_window_model.get_num_flashcards()

    def __update_previous_card_button_state(self) -> None:
        if self.__shuffle_pdf_navigator.get_is_page_navigator_active():
            self.__get_previous_card_button().setDisabled(True)
            self.__is_previous_card_button_disabled = True

        elif self.__current_card_index > 0:
            self.__get_previous_card_button().setDisabled(False)
            self.__is_previous_card_button_disabled = False

        elif self.__current_card_index == 0 and isinstance(
            self.__get_cards_to_display()[self.__current_card_index], Flashcard
        ):
            # if the card index is 0 and it is currently visualized an answer, then the previous card is the corresponding question
            flashcard: Flashcard = self.__get_cards_to_display()[
                self.__current_card_index
            ]
            if flashcard.get_answer() == self.__get_flashcard_label_text():
                self.__get_previous_card_button().setDisabled(False)
                self.__is_previous_card_button_disabled = False
            else:
                self.__get_previous_card_button().setDisabled(True)
                self.__is_previous_card_button_disabled = True
        elif self.__current_card_index == 0:
            self.__get_previous_card_button().setDisabled(True)
            self.__is_previous_card_button_disabled = True

    def __get_previous_card_button(self) -> QPushButton:
        return self.__pdf_window_model.get_previous_card_button()

    def __update_next_card_button_state(self) -> None:
        if self.__shuffle_pdf_navigator.get_is_page_navigator_active():
            self.__get_next_card_button().setDisabled(True)
            self.__is_next_card_button_disabled = True
        elif self.__current_card_index == self.__get_num_cards() - 1 and isinstance(
            self.__get_cards_to_display()[self.__current_card_index], Flashcard
        ):
            # if the last element is a flashcard and it is currently visualized a question, then the next card is the corresponding answer
            flashcard: Flashcard = self.__get_cards_to_display()[
                self.__current_card_index
            ]
            if flashcard.get_question() == self.__get_flashcard_label_text():
                self.__get_next_card_button().setDisabled(False)
                self.__is_next_card_button_disabled = False
            else:
                self.__get_next_card_button().setDisabled(True)
                self.__is_next_card_button_disabled = True
        elif self.__current_card_index == self.__get_num_cards() - 1:
            self.__get_next_card_button().setDisabled(True)
            self.__is_next_card_button_disabled = True
        elif self.__current_card_index < self.__get_num_cards() - 1:
            self.__get_next_card_button().setDisabled(False)
            self.__is_next_card_button_disabled = False

    def __get_next_card_button(self) -> QPushButton:
        return self.__pdf_window_model.get_next_card_button()

    def __update_card(self, event) -> None:
        self.__pdf_window_model.update_card(self.__current_card_index)


# How the cards are created is strictly connected to how the navigator behave


def merge_cards_ordered(
    flashcards_per_page: dict[int, list[Flashcard]], num_pdf_pages: int
) -> tuple[list[Card], list[int], list[int]]:
    """Merge the flashcards and the pages in the correct order.

    It orders the flashcards and the pdf pages in a unique list that matches the visualization outcome.

    Parameters
    ----------
    flashcards_per_page : dict[int, list[Flashcard]]
        The key is a page number, and the corresponding items are the flashcards for that page.
    num_pdf_pages : int
        The number of pages in the pdf visualized.

    Returns
    -------
    tuple[list[Card]], list[int], list[int]]
    The first returned parameter is a list of all ordered cards to be displayed. The second element is a vector that stores for each pdf page number the corresponding visualization position. The last returned value does the same with flashcards.

    """
    # sort the flashcards by page number, same page number leaves the order that there was before. In this way the order in which the user put the flashcards is left
    flashcards_per_page = dict(sorted(flashcards_per_page.items(), key=lambda x: x[0]))
    flashcards: list[Flashcard] = get_flashcards_list(flashcards_per_page)

    num_flashcards: int = len(flashcards)
    num_cards: int = num_flashcards + num_pdf_pages

    card_pos: int
    index_flashcard_to_add: int = 0
    index_pdf_page_to_add: int = 0

    num_pdf_page_to_card_index: list[int] = []
    num_flashcard_to_card_index: list[int] = []
    merged_cards: list[Card] = []

    for card_pos in range(0, num_cards, 1):
        card: Card
        is_flashcard_next = is_a_flashcard_next(
            index_flashcard_to_add,
            num_flashcards,
            index_pdf_page_to_add,
            num_pdf_pages,
            flashcards,
        )

        if is_flashcard_next:
            card = flashcards[index_flashcard_to_add]
        else:
            card = PdfPage(index_pdf_page_to_add)

        card.set_pdf_page_index_before(index_pdf_page_to_add - 1)
        card.set_flashcard_index_before(index_flashcard_to_add - 1)

        if is_flashcard_next:
            num_flashcard_to_card_index.append(len(merged_cards))
            index_flashcard_to_add += 1
        else:
            num_pdf_page_to_card_index.append(len(merged_cards))
            index_pdf_page_to_add += 1

        merged_cards.append(card)

    return (merged_cards, num_pdf_page_to_card_index, num_flashcard_to_card_index)


def is_a_flashcard_next(
    index_flashcard_to_add: int,
    num_flashcards: int,
    index_pdf_page_to_add: int,
    num_pdf_pages: int,
    flashcards: list[Flashcard],
) -> bool:
    is_flashcard_next: bool = True

    if index_flashcard_to_add == num_flashcards:
        is_flashcard_next = False
    elif index_pdf_page_to_add == num_pdf_pages:
        is_flashcard_next = True
    elif (
        flashcards[index_flashcard_to_add].get_reference_page() <= index_pdf_page_to_add
    ):
        is_flashcard_next = True
    else:
        is_flashcard_next = False
    return is_flashcard_next


def merge_cards_shuffle(
    flashcards_per_page: dict[int, list[Flashcard]], num_pdf_pages: int
) -> tuple[list[Card], list[int], list[int]]:
    """It shuffles the flashcards and it merges it with the corresponding pdf pages. The pdf pages that are not referenced by any flashcards are positioned at the end.

    The result is saved in a list that matches the visualization outcome.

    Parameters
    ----------
    flashcards_per_page : dict[int, list[Flashcard]]
        The key is a page number, and the corresponding items are the flashcards for that page.
    num_pdf_pages : int
        The number of pages in the pdf visualized.

    Returns
    -------
    tuple[list[Card]], list[int], list[int]]
    The first returned parameter is a list of all ordered cards to be displayed. The second element is a vector that stores for each pdf page number that is visualized the corresponding visualization position. The last returned value does the same with flashcards.

    """

    flashcards = get_shuffled_flashcards(flashcards_per_page)
    num_flashcards: int = len(flashcards)

    card_pos: int
    pdf_pages_referenced_by_flashcard: set[int] = set()

    num_pdf_page_to_card_index: list[int] = [-1] * num_pdf_pages
    num_flashcard_to_card_index: list[int] = []
    merged_cards: list[Card] = []
    card: Card
    flashcard: Flashcard

    add_flashcards(
        merged_cards,
        flashcards,
        num_flashcard_to_card_index,
        num_pdf_page_to_card_index,
        pdf_pages_referenced_by_flashcard,
    )
    last_flashcard: Flashcard = None
    if len(flashcards) != 0:
        last_flashcard = flashcards[-1]
    add_remaining_pdf_pages(
        num_pdf_pages,
        pdf_pages_referenced_by_flashcard,
        num_flashcards,
        last_flashcard,
        merged_cards,
        num_pdf_page_to_card_index,
    )

    return (merged_cards, num_pdf_page_to_card_index, num_flashcard_to_card_index)


def get_shuffled_flashcards(flashcards_per_page) -> list[Flashcard]:
    flashcards: list[Flashcard] = get_flashcards_list(flashcards_per_page)
    shuffle(flashcards)
    return flashcards


def get_flashcards_list(flashcards_per_page) -> list[Flashcard]:
    flashcards: list[Flashcard] = []
    for app in flashcards_per_page.values():
        flashcards.extend(app)
    return flashcards


def add_flashcards(
    merged_cards: list[Card],
    flashcards: list[Flashcard],
    num_flashcard_to_card_index: list[int],
    num_pdf_page_to_card_index: list[int],
    pdf_pages_referenced_by_flashcard: set[int],
) -> None:
    # add flashcards with the referenced PDF page afterwards
    index_flashcard_to_add: int
    num_flashcards: int = len(flashcards)
    for index_flashcard_to_add in range(0, num_flashcards, 1):
        flashcard: Flashcard = flashcards[index_flashcard_to_add]
        flashcard.set_flashcard_index_before(index_flashcard_to_add - 1)
        if (
            flashcard.get_reference_page() - 1 >= 0
            and flashcard.get_question_type() != Flashcard.QuestionType.GENERIC
        ):
            flashcard.set_pdf_page_index_before(flashcard.get_reference_page() - 1)
        else:
            flashcard.set_pdf_page_index_before(Flashcard.GENERIC_PAGE)

        num_flashcard_to_card_index.append(len(merged_cards))
        merged_cards.append(flashcard)

        if flashcard.get_question_type() == Flashcard.QuestionType.PAGE_SPECIFIC:
            add_page_specific_flashcard(
                flashcard,
                index_flashcard_to_add,
                merged_cards,
                num_pdf_page_to_card_index,
                pdf_pages_referenced_by_flashcard,
            )


def add_page_specific_flashcard(
    flashcard: Flashcard,
    index_flashcard_to_add: int,
    merged_cards: list[Card],
    num_pdf_page_to_card_index: list[int],
    pdf_pages_referenced_by_flashcard: set[int],
) -> None:
    # add PDF page afterwards
    pdf_page: PdfPage = PdfPage(flashcard.get_reference_page())
    pdf_page.set_card_index(len(merged_cards))
    pdf_page.set_flashcard_index_before(index_flashcard_to_add)

    pdf_pages_referenced_by_flashcard.add(flashcard.get_reference_page())
    num_pdf_page_to_card_index[flashcard.get_reference_page()] = len(merged_cards)
    if (
        flashcard.get_reference_page() - 1 >= 0
        and flashcard.get_question_type() != Flashcard.QuestionType.GENERIC
    ):
        pdf_page.set_pdf_page_index_before(flashcard.get_reference_page() - 1)
    else:
        pdf_page.set_pdf_page_index_before(Flashcard.GENERIC_PAGE)
    merged_cards.append(pdf_page)


def add_remaining_pdf_pages(
    num_pdf_pages: int,
    pdf_pages_referenced_by_flashcard: set[int],
    num_flashcards: int,
    last_flashcard: Flashcard,
    merged_cards: list[Card],
    num_pdf_page_to_card_index: list[int],
) -> None:
    # add remaining PDF pages. They are used if during a review the students needs to move more than one page onwards or move on a different pdf page
    index_pdf_page_to_add: int

    # the remaining PDF pages have all the same reference to the same previous flashcard
    index_flashcard_before: int
    if (
        num_flashcards > 0
        and last_flashcard.get_question_type() != Flashcard.QuestionType.GENERIC
    ):
        index_flashcard_before = num_flashcards - 1
    else:
        index_flashcard_before = Flashcard.GENERIC_PAGE

    for index_pdf_page_to_add in range(0, num_pdf_pages, 1):
        if index_pdf_page_to_add not in pdf_pages_referenced_by_flashcard:
            pdf_page = PdfPage(index_pdf_page_to_add)
            pdf_page.set_flashcard_index_before(index_flashcard_before)
            pdf_page.set_pdf_page_index_before(index_pdf_page_to_add - 1)
            pdf_page.set_card_index(len(merged_cards))

            num_pdf_page_to_card_index[index_pdf_page_to_add] = len(merged_cards)
            merged_cards.append(pdf_page)
