"""Safe-to-commit tests: no secret canon or arc solutions."""
import sys,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'editorial'))
from continuity import read_yaml,choose_rubrics,sudoku_solution_count
from pipeline import outline
class TestEditorialPublic(unittest.TestCase):
 def test_catalog_and_plan(self):
  catalog=read_yaml(BASE/'editorial/rubrics.yaml')
  self.assertEqual(len(catalog['rubrics']),30)
  p=outline(catalog,[],1,'2026-10-11')
  self.assertFalse(p['editorial_constraints']['publishing_enabled'])
  self.assertEqual(len(p['roles']),8)
  self.assertEqual(p['rubrics'][0],'reportaz_dnia')
  self.assertEqual(p['rubrics'][-2:],['ogloszenia','listy'])
 def test_no_repeating(self):
  c=read_yaml(BASE/'editorial/rubrics.yaml');p=choose_rubrics(c,[],1)
  n=choose_rubrics(c,[{'issue_no':1,'rubrics':p}],2)
  self.assertFalse(set(n[1:-2]) & set(p[1:-2]))
 def test_sudoku(self):
  self.assertEqual(sudoku_solution_count([[1,2,0,4],[0,4,1,0],[0,1,4,0],[4,0,0,1]]),1)
  self.assertEqual(sudoku_solution_count([[1,0,0,4],[0,4,1,0],[0,1,4,0],[4,0,0,1]]),2)
if __name__=='__main__':unittest.main()
