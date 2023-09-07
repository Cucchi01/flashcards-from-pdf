from PyQt6 import QtPdf

from io import TextIOWrapper
import os

from flashcard.flashcard import Flashcard
from test_management.pdf_test_info import PDFTestsInfo
from application_constants import TYPE_QUEST_PAGE_SPECIFIC_CONSTANT
from application_constants import ONGOING_TEST_FLAG_YES
from application_constants import NO_ANSWER_FLAG
from application_constants import FILE_FLASHCARDS_SEPARATOR


class IOFlashcards:
    @staticmethod
    def get_past_tests_info(path_of_file: str) -> PDFTestsInfo:
        pdf_test_info: PDFTestsInfo = PDFTestsInfo()
        with open(path_of_file, "r", encoding="utf-8") as file:
            num_test: int = int(file.readline())
            pdf_test_info.set_num_completed_tests(num_test)
            for i in range(0, num_test):
                fields: list[str] = file.readline().split(FILE_FLASHCARDS_SEPARATOR)
                pdf_test_info.add_completed_test(fields[0].strip(), float(fields[1]))

            if int(file.readline()) == PDFTestsInfo.OngoingTestState.YES.value:
                pdf_test_info.set_ongoing_test_flag(PDFTestsInfo.OngoingTestState.YES)
            else:
                pdf_test_info.set_ongoing_test_flag(PDFTestsInfo.OngoingTestState.NO)

        return pdf_test_info

    @staticmethod
    def get_flashcards_from_pdf(path_of_file: str) -> dict[int, list[Flashcard]]:
        flashcards: dict[int, list[Flashcard]] = dict()
        with open(path_of_file, "r", encoding="utf-8") as file:
            IOFlashcards.__skip_history_tests(file)

            # check ongoing test
            # TODO: manage ongoing test
            ongoing_test: bool = False
            if file.readline().strip() == ONGOING_TEST_FLAG_YES:
                ongoing_test = True

            num_col: int = -1
            num_flashcards: int = int(file.readline())
            pages_with_flashcards: set[int] = set()
            quest: Flashcard = Flashcard()
            for line in file:
                quest = Flashcard()
                num_col = -1
                for word in line.split(FILE_FLASHCARDS_SEPARATOR):
                    num_col += 1

                    IOFlashcards.__manage_flashcard_field(
                        num_col, word, quest, ongoing_test
                    )

                # Adding flashcard
                num_page: int = quest.get_pdf_page()
                if num_page in pages_with_flashcards:
                    flashcards[num_page].append(quest)
                else:
                    flashcards[num_page] = [quest]
                    pages_with_flashcards.add(num_page)

        return flashcards

    @staticmethod
    def __skip_history_tests(file: TextIOWrapper) -> None:
        num_completed_tests: int = int(file.readline())
        for i in range(0, num_completed_tests):
            file.readline()

    @staticmethod
    def __manage_flashcard_field(
        num_col: int, string: str, flashcard: Flashcard, ongoing_test: bool
    ) -> None:
        string = string.strip()
        match num_col:
            case 0:
                # Page number
                flashcard.set_reference_page_from_visualization(int(string))

            case 1:
                # flashcard
                flashcard.set_question(string)

            case 2:
                # Answer
                if string == NO_ANSWER_FLAG:
                    flashcard.set_answer("")
                else:
                    flashcard.set_answer(string)

            case 3:
                # Type
                type_quest_str: str = string
                if type_quest_str == TYPE_QUEST_PAGE_SPECIFIC_CONSTANT:
                    flashcard.set_question_type(Flashcard.QuestionType.PAGE_SPECIFIC)
                else:
                    flashcard.set_question_type(Flashcard.QuestionType.GENERIC)

            case 4:
                # Past results
                char: str
                results: list[Flashcard.Result] = []
                for char in string:
                    if char == "1":
                        results.append(Flashcard.Result.NOT_DONE)
                    elif char == "0":
                        results.append(Flashcard.Result.ERROR)
                    else:
                        results.append(Flashcard.Result.TRUE)

                flashcard.set_past_results(results)

            case 5:
                # current result
                current_result: Flashcard.Result = Flashcard.Result.NOT_DONE
                if string != "" and ongoing_test:
                    match int(string):
                        case Flashcard.Result.ERROR.value:
                            current_result = Flashcard.Result.ERROR
                        case Flashcard.Result.NOT_DONE.value:
                            current_result = Flashcard.Result.NOT_DONE
                        case Flashcard.Result.TRUE.value:
                            current_result = Flashcard.Result.TRUE

                flashcard.set_current_result(current_result)

    @staticmethod
    def save_flashcards_file(
        path_of_file: str,  # could be the pathname of the pdf or the txt
        pdf_test_info: PDFTestsInfo,
        num_flashcards: int,
        flashcards: dict[int, list[Flashcard]],
    ) -> None:
        path_without_ext, _ = os.path.splitext(path_of_file)
        tmp_path_without_ext: str = path_without_ext
        path_already_existing: bool = os.path.exists(path_without_ext + ".txt")
        if path_already_existing:
            while os.path.exists(tmp_path_without_ext + ".txt"):
                tmp_path_without_ext = "".join([tmp_path_without_ext, "_app"])

        with open(tmp_path_without_ext + ".txt", "w", encoding="utf-8") as file:
            file.write(pdf_test_info.to_string())
            file.write(str(num_flashcards) + "\n")

            list_flashcards: list[Flashcard]
            reference_page: int
            for reference_page, list_flashcards in sorted(
                flashcards.items(), key=lambda x: x[0]
            ):
                for flashcard in list_flashcards:
                    file.write(
                        FILE_FLASHCARDS_SEPARATOR.join([flashcard.to_string(), "\n"])
                    )

        os.remove(path_without_ext + ".txt")
        os.rename(tmp_path_without_ext + ".txt", path_without_ext + ".txt")

    @staticmethod
    def get_pdf_page_count(path_to_pdf: str) -> int:
        pdf_doc = QtPdf.QPdfDocument(None)
        pdf_doc.load(path_to_pdf)
        return pdf_doc.pageCount()
