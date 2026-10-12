"""V3 tests, catalog-backed; no private canon or spoilers."""
import unittest
from pathlib import Path
from pipeline import outline
from production_audit import load_catalog,verify_plan

class EditorialV3Test(unittest.TestCase):
    def test_plan_uses_full_catalog(self):
        catalog=load_catalog(Path(__file__).with_name('departments.yaml'))
        plan=outline(catalog,[],2,'2026-10-12')
        self.assertEqual(plan['pages'],4)
        self.assertEqual(len(plan['roles']),8)
        self.assertEqual(len(plan['main_departments']),2)
        self.assertEqual(len(plan['formats']),6)
        self.assertFalse(plan['editorial_constraints']['publication_allowed'])
        self.assertFalse(plan['editorial_constraints']['ai_agents_executed'])
        self.assertFalse(verify_plan(plan,catalog))
