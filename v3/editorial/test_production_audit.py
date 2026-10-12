"""Do not require private lore; all tests are safe for public GitHub Actions."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from production_audit import (audit_pdf,choose_plan, load_catalog, simulate,
    sudoku_solutions_9x9, validate_catalog, verify_plan)

CATALOG = Path(__file__).with_name('departments.yaml')

# Canonical unique-solution 9x9 from a classic Sudoku example.
PUZZLE = [
[5,3,0,0,7,0,0,0,0],
[6,0,0,1,9,5,0,0,0],
[0,9,8,0,0,0,0,6,0],
[8,0,0,0,6,0,0,0,3],
[4,0,0,8,0,3,0,0,1],
[7,0,0,0,2,0,0,0,6],
[0,6,0,0,0,0,2,8,0],
[0,0,0,4,1,9,0,0,5],
[0,0,0,0,8,0,0,7,9],
]

class EditorialAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(CATALOG)

    def test_catalog_32_departments_and_128_formats(self):
        self.assertEqual(validate_catalog(self.catalog), [])

    def test_sudoku_9x9_unique_solution(self):
        self.assertEqual(sudoku_solutions_9x9(PUZZLE),1)
        self.assertEqual(sudoku_solutions_9x9([[1]*9]+[[0]*9 for _ in range(8)]),0)
        self.assertEqual(sudoku_solutions_9x9([[0]*9 for _ in range(9)]),2)
        with self.assertRaises(ValueError):
            sudoku_solutions_9x9([[0]*4 for _ in range(4)])

    def test_plan_rejects_invalid_pages(self):
        plan = choose_plan(self.catalog, [], 1, '2026-10-12')
        self.assertFalse(verify_plan(plan,self.catalog))
        plan['pages'] = 6
        self.assertTrue(any('czterech' in s for s in verify_plan(plan,self.catalog)))

    def test_60_issues_rotation(self):
        result=simulate(self.catalog,60)
        self.assertEqual(result['issues'],60)
        self.assertEqual(result['unique_departments'],32)
        self.assertGreaterEqual(result['unique_formats'],80)
        self.assertGreaterEqual(result['min_departments_per_7_issues'],12)
        self.assertGreaterEqual(result['min_departments_per_14_issues'],20)
        self.assertEqual(result['repeat_formats_within_previous_2_issues'],[])
        self.assertTrue(result['different_main_desks_every_issue'])

    def test_pdf_checks_four_a4_and_comic(self):
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.lib.pagesizes import A4
        from PIL import Image
        import io
        from reportlab.lib.utils import ImageReader
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'issue.pdf'
            c=Canvas(str(p),pagesize=A4)
            for i in range(4):
                c.drawString(30,800,f'PORANNA PRASA NR 001 PAGE {i+1}')
                if i==3:
                    img=Image.new('RGB',(160,80),'white')
                    c.drawImage(ImageReader(img),35,550,120,60)
                c.showPage()
            c.save()
            self.assertEqual(audit_pdf(p)['status'],'PASS')
            bad=Path(temp)/'bad.pdf'
            c=Canvas(str(bad),pagesize=A4)
            c.drawString(30,800,'STR. 10')
            c.showPage();c.save()
            failures=audit_pdf(bad)['errors']
            self.assertTrue(any('4 stron' in s for s in failures))

if __name__ == '__main__':unittest.main()
