from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPointF
from PyQt6 import QtPdf, QtPdfWidgets

import os

from pdf_visualization.pdf_visualization_layout import PDFWindowVisualizationLayout
from pdf_visualization.question import Question
from pdf_visualization.pdf_page import PdfPage
from pdf_visualization.card import Card


class PDFWindowVisualizationModel:
    def __init__(self, path_of_pdf: str) -> None:
        path_without_ext: str
        path_without_ext, _ = os.path.splitext(path_of_pdf)
        path_of_questions: str = path_without_ext + ".txt"

        is_questions_file_present: bool = os.path.isfile(path_of_questions)

        if not is_questions_file_present:
            with open(path_of_questions, "w") as file:
                file.write("0\n")

        questions: dict[int, list[Question]] = get_questions(path_of_questions)

        self.__path_of_pdf: str = path_of_pdf
        self.__filename: str = os.path.basename(path_of_pdf)
        self.__num_pdf_pages: int = get_pdf_page_count(self.__path_of_pdf)
        self.__point: QPointF = QPointF(0, 0)

        self.__cards_to_display: list[Card]
        self.__num_pdf_page_to_card_index: list[int]
        self.__num_question_to_card_index: list[int]
        (
            self.__cards_to_display,
            self.__num_pdf_page_to_card_index,
            self.__num_question_to_card_index,
        ) = merge_cards(questions, self.__num_pdf_pages)

        self.__current_card_index: int = 0
        self.__current_pdf_page: int = 0
        self.__num_cards: int = len(self.__cards_to_display)
        self.__is_page_spinbox_event_disabled: bool = False
        self.__is_back_button_disabled: bool = True
        self.__is_next_button_disabled: bool = False

        self.__window_layout: PDFWindowVisualizationLayout = (
            PDFWindowVisualizationLayout(self.__filename, self.__num_pdf_pages)
        )

        self.__setup_window_layout()

    def __setup_window_layout(self) -> None:
        self.__setup_left_panel()
        self.__setup_bottom_widget()

    def __set_page_position(self) -> None:
        # the num_page stored is 0-based, but the visualization is 1-based numbering
        self.__current_pdf_page = self.__cards_to_display[
            self.__current_card_index
        ].get_pdf_page()
        self.__window_layout.set_num_page(self.__current_pdf_page)
        self.__is_page_spinbox_event_disabled = False

        # TODO: move to control
        # self.pdf_page_num_spinbox.valueChanged.connect(self.update_page)
        # self.back_page_button.clicked.connect(self.__previous_card)
        # self.next_page_button.clicked.connect(self.__previous_card)

    def update_page(self) -> None:
        if not self.__is_page_spinbox_event_disabled:
            self.__current_pdf_page = (
                self.__window_layout.get_pdf_page_num_spinbox().value()
            )
            new_page_num: int = self.__current_pdf_page - 1
            if new_page_num < 0 or new_page_num >= self.__num_pdf_pages:
                raise ValueError("Page value not valid")

            self.__change_card_index(self.__num_pdf_page_to_card_index[new_page_num])

    def __setup_left_panel(self) -> None:
        # TODO: add the management of the questions
        self.__load_pdf_doc(self.__path_of_pdf)
        self.__update_card(None)

    def __load_pdf_doc(self, path_of_pdf: str) -> None:
        self.__window_layout.get_pdf_doc().load(path_of_pdf)

    def __setup_bottom_widget(self) -> None:
        self.__setup_current_card_bottom_layout()

    def __setup_current_card_bottom_layout(self) -> None:
        if self.__num_cards == 1:
            self.__window_layout.get_next_card_button().setDisabled(True)
            self.__is_next_button_disabled = True

    def previous_card(self) -> None:
        if self.__current_card_index <= 0:
            return None

        self.__change_card_index(self.__current_card_index - 1)
        return None

    def next_card(self) -> None:
        if self.__current_card_index >= self.__num_cards - 1:
            return None

        self.__change_card_index(self.__current_card_index + 1)
        return None

    def __change_card_index(self, new_index) -> None:
        if new_index < 0 or new_index >= self.__num_cards:
            print("Error: card index out of range")
            return None

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.__current_card_index = new_index
        self.__update_card(None)

        self.__update_page_pos_layout()
        self.__update_back_btn_state()
        self.__update_next_btn_state()

        QApplication.restoreOverrideCursor()

    def __update_page_pos_layout(self) -> None:
        # the pages are 0-based, but the visualization is 1-based
        page_index: int = (
            self.__cards_to_display[self.__current_card_index].get_pdf_page() + 1
        )

        self.__is_page_spinbox_event_disabled = True
        self.__window_layout.get_pdf_page_num_spinbox().setValue(page_index)
        self.__is_page_spinbox_event_disabled = False

    def __update_back_btn_state(self) -> None:
        if self.__current_card_index > 0 and self.__is_back_button_disabled:
            self.__window_layout.get_back_card_button().setDisabled(False)
            self.__is_back_button_disabled = False
        elif self.__current_card_index == 0 and not self.__is_back_button_disabled:
            self.__window_layout.get_back_card_button().setDisabled(True)
            self.__is_back_button_disabled = True

    def __update_next_btn_state(self) -> None:
        if (
            self.__current_card_index == self.__num_cards - 1
            and not self.__is_next_button_disabled
        ):
            self.__window_layout.get_next_card_button().setDisabled(True)
            self.__is_next_button_disabled = True
        elif (
            self.__current_card_index < self.__num_cards - 1
            and self.__is_next_button_disabled
        ):
            self.__window_layout.get_next_card_button().setDisabled(False)
            self.__is_next_button_disabled = False

    def __update_card(self, event) -> None:
        if (
            self.__current_card_index < 0
            or self.__current_card_index >= self.__num_cards
        ):
            raise IndexError("Error: not existing card")

        element_to_display: Card = self.__cards_to_display[self.__current_card_index]
        if isinstance(element_to_display, PdfPage):
            self.__window_layout.get_question_label().setVisible(False)
            self.__window_layout.get_pdf_nav().jump(
                element_to_display.get_pdf_page(), self.__point
            )
            self.__window_layout.get_pdf_view().setVisible(True)
        elif isinstance(element_to_display, Question):
            quest: Question = element_to_display
            self.__window_layout.get_pdf_view().setVisible(False)
            self.__window_layout.get_question_label().setText(quest.get_question())
            self.__window_layout.get_question_label().setVisible(True)
        else:
            raise TypeError("Class type is different from what is expected")
        return None

    def get_pdf_window_visualization(self) -> PDFWindowVisualizationLayout:
        return self.__window_layout


def get_questions(path_of_file: str) -> dict[int, list[Question]]:
    questions: dict[int, list[Question]] = dict()
    with open(path_of_file, "r") as file:
        num_col: int = -1
        num_questions: int = int(file.readline())
        pages_with_questions = set()
        string: str = ""
        for line in file:
            for word in line.split():
                if word == "?^?":
                    num_col += 1
                    match num_col:
                        case 0:
                            # Page number
                            num_page: int = int(string)

                        case 1:
                            # Question
                            question: str = string

                        case 2:
                            # Answer
                            answer: str = string

                        case 3:
                            # Type
                            type_quest: str = string.strip()
                            if num_page in pages_with_questions:
                                questions[num_page].append(
                                    Question(question, answer, type_quest, [], num_page)
                                )
                            else:
                                questions[num_page] = [
                                    Question(question, answer, type_quest, [], num_page)
                                ]
                                pages_with_questions.add(num_page)

                            num_col = -1
                        case 4:
                            # Past results
                            # TODO: manage past results
                            pass

                    string = ""
                else:
                    string = " ".join([string, word])

    return questions


def merge_cards(
    questions_per_page: dict[int, list[Question]], num_pdf_pages: int
) -> tuple[list[Card], list[int], list[int]]:
    """Merge the questions and the pages in the correct order.

    It orders the questions and the pdf pages in a unique list that matches the visualization outcome.

    Parameters
    ----------
    questions_per_page : dict[int, list[Question]]
        The key is a page number, and the corresponding items are the questions for that page.
    num_pdf_pages : int
        The number of pages in the pdf visualized.

    Returns
    -------
    tuple[list[Card]], list[int], list[int]]
    The first returned parameter is a list of all ordered cards to be displayed. The second element is a vector that stores for each pdf page number the corresponding visualization position. The last returned value does the same with questions.

    """
    # sort the questions by page number, same page number leaves the order that there was before. In this way the order in which the user put the questions is left
    questions_per_page = dict(sorted(questions_per_page.items(), key=lambda x: x[0]))
    questions: list[Question] = []
    for app in questions_per_page.values():
        questions.extend(app)

    num_questions: int = len(questions)
    num_cards: int = num_questions + num_pdf_pages

    card_pos: int
    index_quest_to_add: int = 0
    index_pdf_page_to_add: int = 0

    num_pdf_page_to_card_index: list[int] = []
    num_question_to_card_index: list[int] = []
    merged_cards: list[Card] = []
    for card_pos in range(0, num_cards, 1):
        card: Card
        if index_quest_to_add == num_questions:
            card = PdfPage(index_pdf_page_to_add)
            num_pdf_page_to_card_index.append(len(merged_cards))
            index_pdf_page_to_add += 1
        elif index_pdf_page_to_add == num_pdf_pages:
            card = questions[index_quest_to_add]
            num_question_to_card_index.append(len(merged_cards))
            index_quest_to_add += 1
        elif (
            questions[index_quest_to_add].get_reference_page()
            - 1  # reference page start from 1 and not 0
            <= index_pdf_page_to_add
        ):
            card = questions[index_quest_to_add]
            num_question_to_card_index.append(len(merged_cards))
            index_quest_to_add += 1
        else:
            card = PdfPage(index_pdf_page_to_add)
            num_pdf_page_to_card_index.append(len(merged_cards))
            index_pdf_page_to_add += 1
        merged_cards.append(card)

    return (merged_cards, num_pdf_page_to_card_index, num_question_to_card_index)


# TODO: move the function in a better place
def get_pdf_page_count(path_to_pdf: str) -> int:
    pdf_doc = QtPdf.QPdfDocument(None)
    pdf_doc.load(path_to_pdf)
    return pdf_doc.pageCount()
