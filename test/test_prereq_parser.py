import unittest
from src.scraper.course_scraper import *

class TestPrereqClean(unittest.TestCase):
    def test_prereq_clean_no_data(self):
        parsed = cleanPrerequisites("2.00 credits")
        correct = "No Data"
        self.assertEqual(parsed, correct)
    def test_prereq_clean_cut_off_start(self):
        parsed = cleanPrerequisites("14.00 credits including ANSC*3080")
        correct = "ANSC*3080"
        self.assertEqual(parsed, correct)
    def test_prereq_clean_cut_off_end(self):
        parsed = cleanPrerequisites("CHEM*1040. Students in the BASC.AHN, BAS, BBRM.EM, BENG, BSAG, BSES and BSC programs cannot take this course for credit")
        correct = "CHEM*1040"
        self.assertEqual(parsed, correct)
    def test_prereq_clean_no_change(self):
        parsed = cleanPrerequisites("CHEM*1050, [IPS*1510 OR (MATH*1210, (1 OF PHYS*1010, PHYS*1070, PHYS*1300))]")
        correct = "CHEM*1050, [IPS*1510 OR (MATH*1210, (1 OF PHYS*1010, PHYS*1070, PHYS*1300))]"
        self.assertEqual(parsed, correct)
      
        
class TestPrereqParser(unittest.TestCase):
    def test_prereq_parser_single_course(self):
        parsed = parsePrerequisites("ANSC*3080")
        correct = { "AND": ["ANSC*3080"], "OR": [] }
        self.assertEqual(parsed, correct)
    def test_prereq_parser_two_groups(self):
        parsed = parsePrerequisites("(ACCT*3330 OR BUS*3330), (ACCT*3340 OR BUS*3340)")
        correct = { "AND": [], "OR": ["ACCT*3330", "BUS*3330", "ACCT*3340", "BUS*3340"] }
        self.assertEqual(parsed, correct)
    def test_prereq_parser_multiple_groups(self):
        parsed = parsePrerequisites("ECON*1100, (ECON*1050 OR FARE*1040), (1 OF ECON*2740, STAT*2040, STAT*2060, STAT*2080), (ECON*2770 OR MATH*1210)")
        correct = { "AND": ["ECON*1100"], "OR": ["ECON*1050", "FARE*1040", "ECON*2740", "STAT*2040", "STAT*2060", "STAT*2080", "ECON*2770", "MATH*1210"] }
        self.assertEqual(parsed, correct)
    def test_prereq_parser_mix_and_or(self):
        parsed = parsePrerequisites("ANTH*2160, ANTH*2180, IDEV*2000), (1 OF ANTH*2230, ANTH*2660, IDEV*2400, IDEV*2500)")
        correct = { "AND": ["ANTH*2160", "ANTH*2180", "IDEV*2000"], "OR": ["ANTH*2230", "ANTH*2660", "IDEV*2400", "IDEV*2500"] }
        self.assertEqual(parsed, correct)
    def test_prereq_parser_nested(self):
        parsed = parsePrerequisites("CHEM*1050, [IPS*1510 OR (MATH*1210, (1 OF PHYS*1010, PHYS*1070, PHYS*1300))]")
        correct = { "AND": ["CHEM*1050"], "OR": ["IPS*1510","MATH*1210","PHYS*1010","PHYS*1070","PHYS*1300"] }
        self.assertEqual(parsed, correct)
