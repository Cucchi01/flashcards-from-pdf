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
