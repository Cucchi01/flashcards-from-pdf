import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import decksStructure

class TestRetrivalDeckStructure(unittest.TestCase):    
    def test_correct_import(self):
        self.assertEqual("", "")
    # def test_empty_folder(self):
    #     expected_result = {}
    #     self.assertEqual(decksStructure.get_decks_structure_from_disk("./test_structure/01_test"), expected_result)


if __name__ == '__main__':
    unittest.main()