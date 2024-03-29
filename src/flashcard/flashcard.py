# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from enum import Enum

from flashcard.card import Card
from application_constants import NO_ANSWER_FLAG
from application_constants import FILE_FLASHCARDS_SEPARATOR


class Flashcard(Card):
    GENERIC_PAGE: int = -2

    class QuestionType(Enum):
        GENERIC = 1
        PAGE_SPECIFIC = 2

        def to_string(self) -> str:
            if self.value == 2:
                return "p"
            else:
                return "g"

    class Result(Enum):
        STILL_LEARNING = 0
        NOT_DONE = 1
        KNOW = 2

        def to_string(self) -> str:
            return str(self.value)

    def __init__(
        self,
        question: str = "",
        answer: str = "",
        question_type: QuestionType = QuestionType.GENERIC,
        past_results: list[Result] = list(),
        reference_page: int = 0,
        current_result: Result = Result.NOT_DONE,
    ) -> None:
        super().__init__()
        self.set_question(question)
        self.set_answer(answer)
        self.set_question_type(question_type)
        self.set_past_results(past_results)
        self.set_reference_page(reference_page)
        self.set_current_result(current_result)

    def set_question(self, question: str) -> None:
        self.__question: str = question

    def set_answer(self, answer: str) -> None:
        self.__answer: str = answer

    def set_question_type(self, question_type: QuestionType) -> None:
        self.__question_type: Flashcard.QuestionType = question_type

    def set_past_results(self, past_results: list[Result]) -> None:
        self.__past_results: list[Flashcard.Result] = past_results

    def set_reference_page(self, reference_page: int = 0) -> None:
        self.__reference_page: int = reference_page

    def set_reference_page_from_visualization(self, reference_page: int = 0) -> None:
        self.__reference_page = reference_page - 1

    def set_current_result(self, current_result: Result = Result.NOT_DONE) -> None:
        self.__current_result: Flashcard.Result = current_result

    def get_reference_page(self) -> int:
        return self.__reference_page

    def get_pdf_page(self) -> int:
        return self.get_reference_page()

    def get_question(self) -> str:
        return self.__question

    def get_answer(self) -> str:
        return self.__answer

    def get_question_type(self) -> QuestionType:
        return self.__question_type

    def get_past_results(self) -> list["Flashcard.Result"]:
        return self.__past_results

    def get_current_result(self) -> Result:
        return self.__current_result

    def to_string(self) -> str:
        return_value: str = ""

        answer: str
        if self.get_answer().strip() == "":
            answer = NO_ANSWER_FLAG
        else:
            answer = self.get_answer()

        past_results: str = ""
        for res in self.get_past_results():
            past_results = "".join([past_results, res.to_string()])

        return FILE_FLASHCARDS_SEPARATOR.join(
            [
                str(self.get_pdf_page_for_visualization()),
                self.get_question(),
                answer,
                self.get_question_type().to_string(),
                past_results,
                self.get_current_result().to_string(),
            ]
        )

    def compare_to(self, value: "Flashcard") -> bool:
        if (
            self.get_question() == value.get_question()
            and self.get_answer() == value.get_answer()
            and self.get_question_type().value == value.get_question_type().value
            and self.get_past_results() == value.get_past_results()
            and self.get_current_result() == value.get_current_result()
        ):
            return True
        else:
            return False
