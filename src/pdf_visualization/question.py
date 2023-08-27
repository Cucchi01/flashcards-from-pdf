from enum import Enum
from io import TextIOWrapper

from pdf_visualization.card import Card
from application_constants import TYPE_QUEST_PAGE_SPECIFIC_CONSTANT
from application_constants import ONGOING_TEST_FLAG_YES
from application_constants import NO_ANSWER_FLAG


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
        self.__question: str = question

    def set_answer(self, answer: str) -> None:
        self.__answer: str = answer

    def set_question_type(self, question_type: QuestionType) -> None:
        self.__question_type: Question.QuestionType = question_type

    def set_past_results(self, past_results: list[Result]) -> None:
        self.__past_results: list[Question.Result] = past_results

    def set_reference_page(self, reference_page: int = 0) -> None:
        self.__reference_page: int = reference_page

    def set_current_result(self, current_result: Result = Result.NOT_DONE) -> None:
        self.__current_result: Question.Result = current_result

    def get_reference_page(self) -> int:
        return self.__reference_page

    def get_pdf_page(self) -> int:
        return self.get_reference_page()

    def get_question(self) -> str:
        return self.__question

    @staticmethod
    def get_questions_from_pdf(path_of_file: str) -> dict[int, list["Question"]]:
        questions: dict[int, list[Question]] = dict()
        with open(path_of_file, "r") as file:
            Question.__skip_history_tests(file)

            # check ongoing test
            # TODO: manage ongoing test
            ongoing_test: bool = False
            if file.readline().strip() == ONGOING_TEST_FLAG_YES:
                ongoing_test = True

            num_col: int = -1
            num_questions: int = int(file.readline())
            pages_with_questions: set[int] = set()
            string: str = ""
            quest: Question = Question()
            for line in file:
                # TODO: change to split using separator = "?^?"
                for word in line.split():
                    if word == "?^?":
                        num_col += 1

                        if num_col == 0:
                            quest = Question()

                        Question.__manage_question_field(
                            num_col, string, quest, ongoing_test
                        )

                        if num_col == 5:
                            # Adding question
                            num_page: int = quest.get_reference_page()
                            if num_page in pages_with_questions:
                                questions[num_page].append(quest)
                            else:
                                questions[num_page] = [quest]
                                pages_with_questions.add(num_page)

                            num_col = -1
                        string = ""
                    else:
                        # reconstruction of the field
                        string = " ".join([string, word])

        return questions

    @staticmethod
    def __skip_history_tests(file: TextIOWrapper) -> None:
        num_completed_tests: int = int(file.readline())
        for i in range(0, num_completed_tests):
            file.readline()

    @staticmethod
    def __manage_question_field(
        num_col: int, string: str, question: "Question", ongoing_test: bool
    ) -> None:
        string = string.strip()
        match num_col:
            case 0:
                # Page number
                question.set_reference_page(int(string))

            case 1:
                # Question
                question.set_question(string)

            case 2:
                # Answer
                if string == NO_ANSWER_FLAG:
                    question.set_answer("")
                else:
                    question.set_answer(string)

            case 3:
                # Type
                type_quest_str: str = string
                if type_quest_str == TYPE_QUEST_PAGE_SPECIFIC_CONSTANT:
                    question.set_question_type(Question.QuestionType.PAGE_SPECIFIC)
                else:
                    question.set_question_type(Question.QuestionType.GENERIC)

            case 4:
                # Past results
                char: str
                results: list[Question.Result] = []
                for char in string:
                    if char == "1":
                        results.append(Question.Result.TRUE)
                    elif char == "0":
                        results.append(Question.Result.ERROR)
                    else:
                        results.append(Question.Result.NOT_DONE)

                question.set_past_results(results)

            case 5:
                # current result
                current_result: Question.Result = Question.Result.NOT_DONE
                if string != "" and ongoing_test:
                    match int(string):
                        case Question.Result.ERROR.value:
                            current_result = Question.Result.ERROR
                        case Question.Result.NOT_DONE.value:
                            current_result = Question.Result.NOT_DONE
                        case Question.Result.TRUE.value:
                            current_result = Question.Result.TRUE

                question.set_current_result(current_result)
