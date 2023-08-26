from enum import Enum
from pdf_visualization.card import Card


class Question(Card):
    class QuestionType(Enum):
        GENERIC = 1
        PAGE_SPECIFIC = 2

    class Result(Enum):
        ERROR = 0
        NOT_DONE = 1
        TRUE = 2

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
        self.question: str = question

    def set_answer(self, answer: str) -> None:
        self.answer: str = answer

    def set_question_type(self, question_type: QuestionType) -> None:
        self.question_type: Question.QuestionType = question_type

    def set_past_results(self, past_results: list[Result]) -> None:
        self.past_results: list[Question.Result] = past_results

    def set_reference_page(self, reference_page: int = 0) -> None:
        self.reference_page: int = reference_page

    def set_current_result(self, current_result: Result = Result.NOT_DONE) -> None:
        self.current_result: Question.Result = current_result

    def get_reference_page(self) -> int:
        return self.reference_page

    def get_pdf_page(self) -> int:
        return self.get_reference_page()

    def get_question(self) -> str:
        return self.question
