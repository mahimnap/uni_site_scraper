import unittest
from src.course_search import *

class TestArgsParser(unittest.TestCase):
    # Subject tests
    def test_bad_subject(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], [], [], ["CIZ"])
        self.assertEqual(parsed, -1)
    def test_good_subject(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], [], [], ["CIS"])
        self.assertNotEqual(parsed, -1)

    # Level tests
    def test_bad_level(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], [], ["1001"], [])
        self.assertEqual(parsed, -1)
    def test_good_level(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], [], ["1000"], [])
        self.assertNotEqual(parsed, -1)

    # Term tests
    def test_bad_term(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], ["Inter"], [], [])
        self.assertEqual(parsed, -1)
    def test_good_term(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], ["Winter"], [], [])
        self.assertNotEqual(parsed, -1)

    # Term range tests
    def test_bad_term_range(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], [], ["1000", "-", "4000"], [])
        self.assertEqual(sorted(parsed["levels"]), ['1000', '2000', '3000', '4000'])
    def test_good_term_range(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], [], ["1000", "-", "4001"], [])
        self.assertEqual(parsed, -1)

    # Credit tests
    def test_bad_credit(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, ["0.88"], [], [], [])
        self.assertEqual(parsed, -1)
    def test_good_credit(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, ["0.75"], [], [], [])
        self.assertNotEqual(parsed, -1)

    # Credit range tests
    def test_bad_credit_range(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, ["0.25", "-", "1.1"], [], [], [])
        self.assertEqual(parsed, -1)
    def test_good_credit_range(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, ["0.25", "-", "1.0"], [], [], [])
        self.assertEqual(sorted(parsed["credits"]), ['0.25', '0.50', '0.75', '1.00'])   
       

class TestCourseSearch(unittest.TestCase):
    def test_found_none(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], [], ["5000"], [])
        finalList = search(output, parsed["credits"], parsed["terms"], True, parsed["subjects"], parsed["levels"])
        self.assertEqual(finalList, set())

    def test_found_one(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, [], [], ["5000"], [])
        finalList = search(output, parsed["credits"], parsed["terms"], False, parsed["subjects"], parsed["levels"])
        self.assertEqual(finalList, {'COOP*5000'})

    def test_found_two(self):
        output = getJSONData('test/test_data/scraped_data.json')
        parsed = argument_parser(output, ["0.75"], ["W"], ["3000"], ["CIS"])
        finalList = search(output, parsed["credits"], parsed["terms"], False, parsed["subjects"], parsed["levels"])
        self.assertEqual(finalList, {'CIS*3750', 'CIS*3760'})


class TestFileOpening(unittest.TestCase):
    def test_file_does_not_exist(self):
        self.assertEqual(getJSONData('./jhsadgfiuwegrraouewyhgrbdsfky2gwui'), -1)
    def test_file_exists(self):
        self.assertNotEqual(getJSONData('test/test_data/scraped_data.json'), -1)
