from PyQt6 import QtPdf
from pdf2image import convert_from_path
from PIL import Image as PILImage

from io import TextIOWrapper
from typing import overload
import os
from datetime import date
from random import randint

from flashcard.flashcard import Flashcard
from test_management.pdf_test_info import PDFTestsInfo
from application_constants import TYPE_QUEST_PAGE_SPECIFIC_CONSTANT
from application_constants import ONGOING_TEST_FLAG_YES
from application_constants import NO_ANSWER_FLAG
from application_constants import FILE_FLASHCARDS_SEPARATOR
from application_constants import ANKI_FLASHCARDS_SEPARATOR
from application_constants import ANKI_CONTENT_DIRECTORY


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
    def get_flashcards_from_txt(path_of_file: str) -> dict[int, list[Flashcard]]:
        flashcards: dict[int, list[Flashcard]] = dict()
        if os.path.exists(path_of_file) == False:
            return flashcards
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
            line: str = ""
            for next_line in file:
                line += next_line
                # a field can have a \n and has to be manged
                if line.count(FILE_FLASHCARDS_SEPARATOR) != 6:
                    continue

                quest = Flashcard()
                num_col = -1
                for word in line.split(FILE_FLASHCARDS_SEPARATOR):
                    num_col += 1

                    IOFlashcards.__manage_flashcard_field(
                        num_col, word, quest, ongoing_test
                    )

                line = ""

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

        if path_already_existing:
            os.remove(path_without_ext + ".txt")
            os.rename(tmp_path_without_ext + ".txt", path_without_ext + ".txt")

    @staticmethod
    def get_pdf_page_count(path_to_pdf: str) -> int:
        pdf_doc = QtPdf.QPdfDocument(None)
        pdf_doc.load(path_to_pdf)
        return pdf_doc.pageCount()

    @staticmethod
    def save_flashcards_to_anki(path_of_pdf: str) -> None:
        path_without_ext: str
        path_without_ext, _ = os.path.splitext(path_of_pdf)
        flashcards_from_pdf_page: dict[
            int, list[Flashcard]
        ] = IOFlashcards.get_flashcards_from_txt(path_without_ext + ".txt")

        IOFlashcards.__save_flashcards_to_anki_txt(
            path_of_pdf, flashcards_from_pdf_page
        )

    @staticmethod
    def __save_flashcards_to_anki_txt(
        path_of_file: str,  # could be the pathname of the pdf or the txt
        flashcards_from_pdf_page: dict[int, list[Flashcard]],
    ) -> None:
        path_without_ext: str
        relative_directory_position_anki: str
        path_of_pdf: str
        basename_pdf_without_ext: str
        media_folder_anki: str
        (
            path_without_ext,
            relative_directory_position_anki,
            path_of_pdf,
            basename_pdf_without_ext,
            media_folder_anki,
        ) = IOFlashcards.__get_path_information_to_anki(path_of_file)

        num_pdf_pages: int = IOFlashcards.get_pdf_page_count(path_of_pdf)

        tmp_path_without_ext: str
        is_path_already_existing: bool
        (
            tmp_path_without_ext,
            is_path_already_existing,
        ) = IOFlashcards.__get_tmp_path_without_ext(path_without_ext)

        os.makedirs(os.path.dirname(tmp_path_without_ext + ".txt"), exist_ok=True)

        with open(tmp_path_without_ext + ".txt", "w", encoding="utf-8") as file:
            file.write("#separator:tab\n#html:true\n#notetype:basic\n")

            list_flashcards: list[Flashcard]
            reference_page: int

            for reference_page, list_flashcards in sorted(
                flashcards_from_pdf_page.items(), key=lambda x: x[0]
            ):
                for flashcard in list_flashcards:
                    if (
                        flashcard.get_question_type()
                        == Flashcard.QuestionType.PAGE_SPECIFIC
                    ):
                        IOFlashcards.__save_page_sp_flashcard_to_anki_txt(
                            file,
                            flashcard,
                            path_of_pdf,
                            num_pdf_pages,
                            media_folder_anki,
                            relative_directory_position_anki,
                        )
                    else:
                        file.write(
                            ANKI_FLASHCARDS_SEPARATOR.join(
                                [
                                    flashcard.get_question(),
                                    '"' + flashcard.get_answer() + '"\n',
                                ]
                            )
                        )

        if is_path_already_existing:
            os.remove(path_without_ext + ".txt")
            os.rename(tmp_path_without_ext + ".txt", path_without_ext + ".txt")

    @staticmethod
    def __get_path_information_to_anki(
        path_of_file: str,
    ) -> tuple[str, str, str, str, str]:
        path_without_ext: str
        basename_pdf: str = os.path.basename(path_of_file)
        basename_pdf_without_ext, _ = os.path.splitext(basename_pdf)
        path_without_ext, _ = os.path.splitext(path_of_file)

        path_of_pdf: str = path_without_ext + ".pdf"
        if os.path.exists(path_of_pdf) == False:
            raise IOError("Not existing path: " + path_of_pdf)

        relative_file_position: str = path_without_ext.removeprefix(
            os.getcwd() + "\\data"
        )
        relative_directory_position_anki: str
        relative_directory_position_anki, _ = os.path.splitext(relative_file_position)
        relative_directory_position_anki = "\\data" + relative_directory_position_anki
        path_without_ext = os.getcwd() + "\\data\\Anki" + relative_file_position

        media_folder_anki: str = os.path.expandvars(ANKI_CONTENT_DIRECTORY)

        return (
            path_without_ext,
            relative_directory_position_anki,
            path_of_pdf,
            basename_pdf_without_ext,
            media_folder_anki,
        )

    @staticmethod
    def __get_tmp_path_without_ext(path_without_ext: str) -> tuple[str, bool]:
        tmp_path_without_ext: str = path_without_ext
        is_path_already_existing: bool = os.path.exists(path_without_ext + ".txt")
        if is_path_already_existing:
            while os.path.exists(tmp_path_without_ext + ".txt"):
                tmp_path_without_ext = "".join([tmp_path_without_ext, "_app"])
        return (tmp_path_without_ext, is_path_already_existing)

    @staticmethod
    def __save_page_sp_flashcard_to_anki_txt(
        file: TextIOWrapper,
        flashcard: Flashcard,
        path_of_pdf: str,
        num_pdf_pages: int,
        media_folder_anki: str,
        relative_directory_position_anki: str,
    ) -> None:
        # if the reference_page exeeds the boundaries, then it is set to the last pdf page. This can happen when there are old flashcards and a pdf is updated to a pdf with fewer pages
        reference_page: int = (
            flashcard.get_pdf_page()
            if flashcard.get_pdf_page() < num_pdf_pages
            else num_pdf_pages - 1
        )

        filename: str = (
            relative_directory_position_anki.replace("\\", "_")
            + "_"
            + date.today().strftime("%y_%m_%d")
            + "_"
            + str(reference_page)
            + "_"
            + str(randint(0, 10000)).zfill(5)
            + ".jpg"
        ).replace(" ", "_")

        page: list[PILImage.Image] = convert_from_path(
            path_of_pdf,
            dpi=200,
            first_page=reference_page + 1,  # base-1
            last_page=reference_page + 1,  # base-1
        )
        if (
            len(page) != 0
            and os.path.exists(media_folder_anki + "\\" + filename) == False
        ):
            page[0].save(media_folder_anki + "\\" + filename, "JPEG")
            file.write(
                ANKI_FLASHCARDS_SEPARATOR.join(
                    [
                        flashcard.get_question(),
                        '"'
                        + flashcard.get_answer()
                        + '<br><img src=""'
                        + filename
                        + '"">"\n',
                    ]
                )
            )
        else:
            # if the reference page do not exists or there are problems with the saving of the image
            file.write(
                ANKI_FLASHCARDS_SEPARATOR.join(
                    [
                        flashcard.get_question(),
                        '"' + flashcard.get_answer() + '"\n',
                    ]
                )
            )
