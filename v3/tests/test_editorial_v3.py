"""Public catalog/rotation tests; the retired 4×4 prototype is not a V3 contract."""
import sys
import unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'editorial'))
from continuity import sudoku_solution_count
from pipeline import outline
from production_audit import load_catalog,choose_plan,verify_plan
from test_production_audit import PUZZLE

class TestEditorialPublic(unittest.TestCase):
    def test_catalog_and_plan(self):
        catalog=load_catalog(BASE/'editorial/departments.yaml')
        self.assertEqual(len(catalog['departments']),32)
        p=outline(catalog,[],1,'2026-10-16')
        self.assertFalse(p['editorial_constraints']['publication_allowed'])
        self.assertEqual(len(p['roles']),8)
        self.assertEqual(p['pages'],4)
        self.assertEqual(len(p['formats']),6)
        self.assertFalse(verify_plan(p,catalog))

    def test_no_repeating(self):
        c=load_catalog(BASE/'editorial/departments.yaml')
        first=choose_plan(c,[],1,'2026-10-16')
        history=[{'issue_no':1,'formats':first['formats'],'main_departments':first['main_departments']}]
        second=choose_plan(c,history,2,'2026-10-17')
        self.assertFalse(set(first['formats']) & set(second['formats']))

    def test_sudoku(self):
        self.assertEqual(sudoku_solution_count(PUZZLE),1)
        self.assertEqual(sudoku_solution_count([[0]*9 for _ in range(9)]),2)
        with self.assertRaises(ValueError):
            sudoku_solution_count([[0]*4 for _ in range(4)])

if __name__=='__main__':
    unittest.main()
