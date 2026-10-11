"""Offline plan and agent work orders for Poranna Prasa 3.0.
This DOES NOT call LLMs or modify the published morning edition.
Secrets for mysteries live in private storage; never commit them here.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import date
from continuity import read_yaml, choose_rubrics

ROLE_ORDER = [
    ('editor_in_chief','Issue outline, balance, angle, word budget, source-vs-fiction labels'),
    ('archivist','Retrieve read-only canonical facts and public/editorial beliefs from PRIVATE store'),
    ('researcher','Verify source packets for nonfiction; no invented quotations'),
    ('writers','Write original fiction/nonfiction, with named mechanics, specific scenes and claims'),
    ('continuity_keeper','Detect contradictions, spoiler leaks, canon-violating character knowledge'),
    ('puzzle_master','Insert 1–3 planned clues; check sudoku uniqueness and solvability'),
    ('copy_editor','Remove filler, test specificity, natural Polish, consistent tone'),
    ('typesetter','Compose dense print layout, reserved last page, run clipping/QA and PRN')
]

def outline(catalog, history, issue_no, issue_date):
    rubrics=choose_rubrics(catalog,history,issue_no,count=7)
    return {
      'schema':1,'issue_no':issue_no,'issue_date':issue_date,
      'status':'DRAFT_NOT_APPROVED','max_pages':4,'last_page_role':'back_page',
      'news_required':False,'roles': [{'agent':n,'task':d} for n,d in ROLE_ORDER],
      'rubrics':rubrics,
      'editorial_constraints':{
          'fiction_facts_separate':True,'references_required_for_nonfiction':True,
          'story_bible_source':'PRIVATE_ONLY','print_only_when_home':'unchanged',
          'publishing_enabled':False,
          'specificity':'Every feature needs named subject, 2+ concrete examples, causal analysis'},
    }

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--rubrics',type=Path,default=Path(__file__).with_name('rubrics.yaml'))
    cli.add_argument('--issue',type=int,required=True)
    cli.add_argument('--date',default=date.today().isoformat())
    cli.add_argument('--history',type=Path)
    cli.add_argument('--output',type=Path)
    a=cli.parse_args()
    history=json.loads(a.history.read_text(encoding='utf-8'))['issues'] if a.history else []
    data=outline(read_yaml(a.rubrics),history,a.issue,a.date)
    payload=json.dumps(data,ensure_ascii=False,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(payload+'\n',encoding='utf-8')
    print(payload)
if __name__=='__main__':main()
