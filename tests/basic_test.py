import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import decks_structure


class TestRetrivalDeckStructure(unittest.TestCase):
    def test_correct_import(self):
        self.assertEqual("", "")

    def test_empty_folder(self):
        expected_result = {}
        test_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "test_structure/01_test")
        )
        print(test_folder_path)
        self.assertEqual(
            decks_structure.get_decks_structure_from_disk(test_folder_path),
            expected_result,
        )

    def test_one_file_folder(self):
        expected_result = {}
        test_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "test_structure/02_test")
        )
        print(test_folder_path)
        self.assertEqual(
            decks_structure.get_decks_structure_from_disk(test_folder_path),
            expected_result,
        )

    def test_folder(self):
        expected_result = {}
        test_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "test_structure/03_test")
        )
        print(test_folder_path)
        self.assertEqual(
            decks_structure.get_decks_structure_from_disk(test_folder_path),
            expected_result,
        )

    def test_one_folder(self):
        expected_result = {}
        test_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "test_structure/04_test")
        )
        print(test_folder_path)
        self.assertEqual(
            decks_structure.get_decks_structure_from_disk(test_folder_path),
            expected_result,
        )


if __name__ == "__main__":
    unittest.main()
