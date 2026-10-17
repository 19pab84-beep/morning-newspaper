import hashlib
import tempfile
import unittest
from pathlib import Path
from v3.editorial.review_gate import review_errors, REQUIRED

class ReviewGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.pdf=Path(self.tmp.name)/'issue.pdf';self.pdf.write_bytes(b'PDF revision A')
        self.report={'pdf_sha256':hashlib.sha256(self.pdf.read_bytes()).hexdigest(),
                     'pages_inspected':[1,2,3,4], 'editorial_checks':{k:'Observed evidence' for k in REQUIRED},
                     'technical_errors':[], 'defects':[], 'limitations':'Self-review is subjective.'}
    def test_review_becomes_invalid_after_render_changes(self):
        self.pdf.write_bytes(b'PDF revision B')
        self.assertTrue(review_errors(self.report,self.pdf))
    def test_technical_pass_cannot_override_bad_story(self):
        self.report['defects']=[{'severity':'major','description':'Unmotivated action','status':'open'}]
        self.assertTrue(review_errors(self.report,self.pdf))
    def test_missing_page_blocks_handoff(self):
        self.report['pages_inspected']=[1,2,4]
        self.assertTrue(review_errors(self.report,self.pdf))
    def test_empty_editorial_attestation_blocks_handoff(self):
        self.report['editorial_checks']['logic']=' '
        self.assertTrue(review_errors(self.report,self.pdf))
    def test_reviewed_document_can_pass(self):
        self.assertEqual(review_errors(self.report,self.pdf),[])
