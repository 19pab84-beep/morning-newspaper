"""Meaningful negative gates. All synthetic secrets are test sentinels, not lore."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from v3.editorial.authoring import ResponsesAuthor,REVIEW_SCHEMA
from v3.editorial.private_state import PrivateStore,REPO
from v3.editorial.production_audit import load_catalog,sudoku_solutions_9x9
from v3.editorial.puzzles import sudoku_answer
from v3.editorial.quality import validate
from v3.renderer.press import Press,Overflow
from v3.renderer.preflight import check
from v3.build import build

ROOT=Path(__file__).resolve().parents[1]

def pilot(n):
    folder=os.environ.get('PORANNA_PRASA_PILOTS')
    if not folder:
        raise unittest.SkipTest('Drive integration fixtures: set PORANNA_PRASA_PILOTS and PORANNA_PRASA_ASSETS')
    return json.loads((Path(folder)/f'{n:03d}.json').read_text())


def history(issue):
    return {'issue_no':issue['issue_no'], 'formats':[s['format_id'] for s in issue['stories'] if s['role']=='short'],
            'main_departments':[s['department_id'] for s in issue['stories'] if s['role']=='feature'],
            'topics':[s['topic'] for s in issue['stories']],'cover_angle':issue['cover_angle']}


def synthetic_state(issue):
    return {'revision':0,'facts':[
                {'id':'library-location','published_claim':'Biblioteka przy Brzozowej','reveal_min_issue':6}],
            'arcs':[{'secret_truth':'TEST_ONLY_UNREVEALED_SENTINEL','payoff_due':90}],
            'clues':[{'id':cid,'introduced_in':6,'carrier':'006-cover','public_text':'4519',
                      'visibility':'explicit' if k==0 else 'subtle','payoff_due':90,
                      'solution':'Synthetic test solution','deduction':'Synthetic test derivation'}
                     for k,cid in enumerate(issue['clue_ids'])],
            'ledger':[]}


class ContentGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.issues=[pilot(n) for n in (6,7,8)]
        cls.catalog=load_catalog(ROOT/'editorial/departments.yaml')

    def test_three_manuscripts_against_real_history(self):
        past=[]
        for i in self.issues:
            self.assertEqual(validate(i,self.catalog,past),[])
            self.assertEqual(sudoku_solutions_9x9(i['sudoku']),1)
            past.append(history(i))

    def test_sudoku_answers_preserve_givens_and_all_units(self):
        digits=set(range(1,10))
        for issue in self.issues:
            answer=sudoku_answer(issue['sudoku'])
            for row in range(9):
                self.assertEqual(set(answer[row]),digits)
                self.assertEqual({answer[r][row] for r in range(9)},digits)
                for col in range(9):
                    if issue['sudoku'][row][col]:
                        self.assertEqual(answer[row][col],issue['sudoku'][row][col])
            for br in (0,3,6):
                for bc in (0,3,6):
                    self.assertEqual({answer[r][c] for r in range(br,br+3) for c in range(bc,bc+3)},digits)

    def test_duplicate_id_and_false_teaser(self):
        i=deepcopy(self.issues[0]);i['stories'][1]['story_id']=i['stories'][0]['story_id']
        i['teasers'][0]['story_id']='does-not-exist'
        errors=validate(i,self.catalog,[])
        self.assertTrue(any('unikalne' in e for e in errors))
        self.assertTrue(any('Zapowiedź' in e for e in errors))

    def test_bogus_source_and_missing_evidence(self):
        i=deepcopy(self.issues[0]);i['sources']['census']['url']='https://fake.invalid/source'
        i['stories'][1]['claims'][0]['evidence_id']='fabricated'
        errors=validate(i,self.catalog,[])
        self.assertTrue(any('URL' in e for e in errors))
        self.assertTrue(any('dowodu' in e for e in errors))

    def test_ambiguous_and_invalid_sudoku(self):
        i=deepcopy(self.issues[0]);i['sudoku']=[[0]*9 for _ in range(9)]
        self.assertTrue(any('rozwiązania' in e for e in validate(i,self.catalog,[])))
        i['sudoku']=[[0]*4 for _ in range(4)]
        self.assertTrue(any('9 × 9' in e for e in validate(i,self.catalog,[])))

    def test_ai_pagination_and_private_fields_rejected(self):
        i=deepcopy(self.issues[0]);i['stories'][1]['paragraphs'][0]+=' Zobacz str. 7.'
        i['secret_truth']='TEST SENTINEL'
        errors=validate(i,self.catalog,[])
        self.assertTrue(any('odsyłaczy' in e for e in errors))
        self.assertTrue(any('Prywatne' in e for e in errors))

    def test_rotation_blocks_actual_repeated_manuscript(self):
        i=deepcopy(self.issues[0]);i['issue_no']=7
        self.assertTrue(any('powtórzenie' in e or 'powtórzony' in e
                            for e in validate(i,self.catalog,[history(self.issues[0])])))


class PrivateGates(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'state.json'
        self.issue=pilot(6)
        self.state=synthetic_state(self.issue)
        self.path.write_text(json.dumps(self.state))
        self.store=PrivateStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_private_path_inside_repository_rejected(self):
        with self.assertRaises(ValueError):
            PrivateStore(REPO/'world/canon.yaml')

    def test_spoiler_and_false_claim_block(self):
        i=deepcopy(self.issue);i['stories'][0]['paragraphs'].append('TEST_ONLY_UNREVEALED_SENTINEL')
        i['stories'][0]['canon_claims'][0]['value']='Wrong place'
        e=self.store.check(i)
        self.assertTrue(any('ujawnienie' in s for s in e))
        self.assertTrue(any('Sprzeczność' in s for s in e))

    def test_future_clue_and_unknown_correction_block(self):
        i=deepcopy(self.issue);i['clue_ids'][0]='future'
        i['stories'][0]['correction_refs']=['unpublished-story']
        e=self.store.check(i)
        self.assertTrue(any('trop' in s for s in e))
        self.assertTrue(any('Sprostowanie' in s for s in e))

    def test_atomic_idempotent_ledger_and_conflict(self):
        m={'story_pages':{s['story_id']:s['page'] for s in self.issue['stories']}}
        self.assertEqual(self.store.commit(self.issue,m),1)
        self.assertEqual(self.store.commit(self.issue,m),1)
        self.assertEqual(len(self.store.read()['ledger']),1)
        self.assertTrue((self.path.parent/'state-revisions/revision-0000.json').exists())
        changed=deepcopy(self.issue);changed['surprise']='Changed after approval'
        with self.assertRaises(ValueError):
            self.store.commit(changed,m)
        self.assertEqual(self.store.read()['revision'],1)

    def test_public_projection_omits_secrets(self):
        state=self.store.read()
        state['ledger'].append({'issue_no':90,'story_ids':['TEST_FUTURE_PUBLICATION']})
        self.path.write_text(json.dumps(state))
        context=self.store.context(6)
        self.assertNotIn('TEST_ONLY_UNREVEALED_SENTINEL',json.dumps(context))
        self.assertNotIn('Synthetic test solution',json.dumps(context))
        self.assertNotIn('TEST_FUTURE_PUBLICATION',json.dumps(context))

    def test_predecessor_must_exist(self):
        i=deepcopy(self.issue)
        i['previous_issue']=5
        self.assertTrue(any('poprzedniego' in e for e in self.store.check(i)))

    def test_revision_archives_are_scoped_to_each_store(self):
        second_path=self.path.parent/'second.json'
        second_path.write_text(json.dumps(self.state))
        second=PrivateStore(second_path)
        m={'story_pages':{s['story_id']:s['page'] for s in self.issue['stories']}}
        self.store.commit(self.issue,m)
        second.commit(self.issue,m)
        self.assertTrue((self.path.parent/'state-revisions/revision-0000.json').exists())
        self.assertTrue((self.path.parent/'second-revisions/revision-0000.json').exists())

    def test_failed_build_does_not_commit_or_replace_output(self):
        i=deepcopy(self.issue)
        i['stories'][1]['paragraphs'].extend(['Dodatkowy tekst próby. '*200+str(k) for k in range(5)])
        manuscript=self.path.parent/'input.json'
        manuscript.write_text(json.dumps(i))
        output=self.path.parent/'output'
        with self.assertRaises(Overflow):
            build(manuscript,self.path,output)
        self.assertEqual(self.store.read()['revision'],0)
        self.assertFalse((output/'issue-006').exists())


class PdfGates(unittest.TestCase):
    def test_three_actual_pdf_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            for n in (6,7,8):
                i=pilot(n)
                path=Path(tmp)/f'{n}.pdf'
                m=Press(i,path).render()
                self.assertEqual(check(path,i,m)['errors'],[])
                with fitz.open(path) as d:
                    self.assertEqual(len(d),4)
                    self.assertIn('SUDOKU 9',d[3].get_text())

    def test_generic_pdf_with_large_middle_masthead_and_wrong_date_fails(self):
        i=pilot(6)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.pdf';c=canvas.Canvas(str(p),pagesize=A4)
            for n in range(4):
                c.setFont('Times-Bold',40);c.drawString(25,760,'PORANNA PRASA')
                c.setFont('Times-Roman',9);c.drawString(25,810,'NR 999 / 01.01.1999')
                c.showPage()
            c.save()
            m={'story_pages':{s['story_id']:s['page'] for s in i['stories']}}
            m['story_pages'][i['comic']['story_id']]=4
            e=check(p,i,m)['errors']
            self.assertTrue(any('winieta' in s for s in e))
            self.assertTrue(any('numer/data' in s for s in e))
            self.assertTrue(any('Komiks' in s for s in e))
            self.assertTrue(any('utracony akapit' in s for s in e))

    def test_overflow_never_silently_discards_copy(self):
        i=pilot(6)
        i['stories'][1]['paragraphs']*=10
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(Overflow):
                Press(i,Path(tmp)/'overflow.pdf').render()


class ApiGates(unittest.TestCase):
    def test_missing_key_blocks_live_instead_of_fallback(self):
        with patch.dict(os.environ,{'OPENAI_API_KEY':''}):
            with self.assertRaises(RuntimeError):
                ResponsesAuthor('explicit-model')

    def test_refusal_and_call_cap(self):
        class Response:
            status_code=200
            def json(self):return {'status':'completed','output':[{'content':[{'type':'refusal'}]}]}
        class Session:
            def post(self,*args,**kwargs):return Response()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-only-key'}):
            author=ResponsesAuthor('explicit-test-model',session=Session(),max_calls=1)
            with self.assertRaisesRegex(RuntimeError,'odmówiło'):
                author.ask('review','test',{},REVIEW_SCHEMA)
            with self.assertRaisesRegex(RuntimeError,'Limit'):
                author.ask('review','test',{},REVIEW_SCHEMA)

    def test_incomplete_response_is_rejected(self):
        class Response:
            status_code=200
            def json(self):return {'status':'incomplete','output':[]}
        class Session:
            def post(self,*args,**kwargs):return Response()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-only-key'}):
            author=ResponsesAuthor('explicit-test-model',session=Session())
            with self.assertRaisesRegex(RuntimeError,'nie zakończyło'):
                author.ask('review','test',{},REVIEW_SCHEMA)

    def test_structured_request_and_valid_response(self):
        class Response:
            status_code=200
            def json(self):return {'status':'completed','output':[{'content':[{'type':'output_text','text':'{"approved":true,"issues":[]}'}]}],
                                   'usage':{'input_tokens':12,'output_tokens':8}}
        class Session:
            def post(self,url,**kwargs):
                self.request=kwargs['json'];return Response()
        session=Session()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test-only-key'}):
            author=ResponsesAuthor('explicit-test-model',session=session)
            self.assertTrue(author.ask('review','test',{},REVIEW_SCHEMA)['approved'])
        self.assertEqual(session.request['text']['format']['type'],'json_schema')
        self.assertTrue(session.request['text']['format']['strict'])
        self.assertFalse(session.request['store'])
        self.assertEqual(author.usage,{'input_tokens':12,'output_tokens':8})


if __name__=='__main__':
    unittest.main()
