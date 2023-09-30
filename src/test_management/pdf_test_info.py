# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from enum import Enum

from application_constants import FILE_FLASHCARDS_SEPARATOR
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from test_management.pdf_test_info import FirstPass


class PDFTestsInfo:
    class FirstPass(Enum):
        FALSE = 0
        TRUE = 1

        def to_string(self) -> str:
            return str(self.value)

    def __init__(self):
        self.__completed_tests: dict[str, float] = dict()
        self.__first_pass_flag: "FirstPass" = False

    def add_completed_test(self, date: datetime, percentace: float) -> None:
        key: str = date.strftime("%Y/%m/%d_%H:%M:%S")
        if key not in self.__completed_tests.keys():
            self.__completed_tests[key] = percentace

    def set_first_pass_flag(self, flag: "FirstPass") -> None:
        self.__first_pass_flag = flag

    def get_num_completed_tests(self) -> int:
        return len(self.get_completed_tests())

    def get_completed_tests(self) -> dict[str, float]:
        return self.__completed_tests

    def get_first_pass_flag(self) -> "FirstPass":
        return self.__first_pass_flag

    def to_string(self) -> str:
        return_value: str = str(len(self.get_completed_tests())) + "\n"
        date: str
        percentage: float
        for [date, percentage] in self.get_completed_tests().items():
            return_value += FILE_FLASHCARDS_SEPARATOR.join(
                [date, str(percentage), "\n"]
            )

        return return_value + self.get_first_pass_flag().to_string() + "\n"
