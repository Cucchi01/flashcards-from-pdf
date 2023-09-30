# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
from PyQt6.QtWidgets import QFileDialog

import os
import shutil

from application_constants import PDFS_DIRECTORY_PATH


def update_file(path_to_update: str) -> None:
    path_of_updated_version: str = ""
    filename_type_updated: str = ""

    (path_of_updated_version, filename_type_updated) = __get_path_updated_version(
        path_to_update
    )

    __update_files(path_of_updated_version, filename_type_updated, path_to_update)


def __get_path_updated_version(path_pdf_to_update: str) -> tuple[str, str]:
    path_of_updated_version: str = ""
    filename_type: str = ""
    _, extension = os.path.splitext(path_pdf_to_update)
    if extension == ".pdf":
        path_of_updated_version, filename_type = QFileDialog.getOpenFileName(
            caption="Open file", filter="*.pdf", directory=PDFS_DIRECTORY_PATH
        )
    elif extension == "":
        path_of_updated_version = QFileDialog.getExistingDirectory(
            caption="Open file", directory=PDFS_DIRECTORY_PATH
        )

    return (path_of_updated_version, filename_type)


def __update_files(
    path_of_updated_version: str, filename_type_updated: str, path_to_update: str
) -> None:
    _, extension = os.path.splitext(path_to_update)
    if path_of_updated_version == "":
        # cancel has been clicked
        return

    if filename_type_updated == "" and extension == "":
        # update folder
        shutil.copytree(path_of_updated_version, path_to_update, dirs_exist_ok=True)
    elif os.path.splitext(path_of_updated_version)[1] == ".pdf" and extension == ".pdf":
        shutil.copy2(
            path_of_updated_version,
            path_to_update,
        )
