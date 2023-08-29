from enum import Enum

from application_constants import FILE_FLASHCARDS_SEPARATOR


class PDFTestsInfo:
    class OngoingTestState(Enum):
        NO = 0
        YES = 1

        def to_string(self) -> str:
            return str(self.value)

    def __init__(self):
        self.__num_completed_tests: int = 0
        self.__completed_tests: dict[str, float] = dict()
        self.__ongoing_test_flag: OngoingTestState = False

    def set_num_completed_tests(self, num_completed_tests: int) -> None:
        self.__num_completed_tests = num_completed_tests

    def add_completed_test(self, date: str, percentace: float) -> None:
        self.__completed_tests[date] = percentace

    def set_ongoing_test_flag(self, flag: OngoingTestState) -> None:
        self.__ongoing_test_flag = flag

    def get_num_completed_tests(self) -> int:
        return self.__num_completed_tests

    def get_completed_tests(self) -> dict[str, float]:
        return self.__completed_tests

    def get_ongoing_test_flag(self) -> OngoingTestState:
        return self.__ongoing_test_flag

    def to_string(self) -> str:
        return_value: str = str(self.get_num_completed_tests()) + "\n"
        date: str
        percentage: float
        for [date, percentage] in self.get_completed_tests().items():
            return_value += FILE_FLASHCARDS_SEPARATOR.join(
                [date, str(percentage), "\n"]
            )

        return return_value + self.get_ongoing_test_flag().to_string() + "\n"
