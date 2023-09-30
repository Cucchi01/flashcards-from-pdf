# Copyright 2022, 2023 Andrea Cucchietti
# This file is part of flashcards-from-pdf.

# flashcards-from-pdf is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# flashcards-from-pdf is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with flashcards-from-pdf. If not, see <https://www.gnu.org/licenses/>.
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import decks_tree


class TestRetrivalDeckStructure(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestRetrivalDeckStructure, self).__init__(*args, **kwargs)
        self.test_root_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "fixtures/test_structure")
        )

    def test_correct_import(self):
        self.assertEqual("", "")

    def test_empty_folder(self):
        expected_result = {}
        test_folder_path = os.path.join(self.test_root_folder_path, "/01_test")
        self.assertEqual(
            decks_tree.get_decks_structure_from_disk(test_folder_path),
            expected_result,
        )

    def test_one_file_folder(self):
        expected_result = {}
        test_folder_path = os.path.join(self.test_root_folder_path, "/02_test")
        self.assertEqual(
            decks_tree.get_decks_structure_from_disk(test_folder_path),
            expected_result,
        )

    def test_folder(self):
        expected_result = {}
        test_folder_path = os.path.join(self.test_root_folder_path, "/03_test")
        self.assertEqual(
            decks_tree.get_decks_structure_from_disk(test_folder_path),
            expected_result,
        )

    def test_one_folder(self):
        expected_result = {}
        test_folder_path = os.path.join(self.test_root_folder_path, "/04_test")
        self.assertEqual(
            decks_tree.get_decks_structure_from_disk(test_folder_path),
            expected_result,
        )


if __name__ == "__main__":
    unittest.main()
