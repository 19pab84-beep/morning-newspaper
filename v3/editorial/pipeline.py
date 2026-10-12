"""Offline V3 editorial planner. Never generates articles, publishes or prints.

An outline is not approval: source research and PRIVATE continuity review remain required.
"""
from __future__ import annotations
import argparse
from datetime import date
import json
from pathlib import Path
from production_audit import load_catalog, choose_plan, verify_plan

ROLE_ORDER = [
 ('editor_in_chief','Plan theme and department rotation; consult 60 issues'),
 ('archivist','Load private canon in read-only mode'),
 ('researcher','Verify every real claim and bibliography'),
 ('writers','Write original specific prose, not RSS filler'),
 ('continuity_keeper','Flag false dates, premature secrets and contradictions'),
 ('puzzle_master','Ensure solvable clues and unique 9x9 Sudoku'),
 ('copy_editor','Reject repetition, generalities and empty conclusions'),
 ('typesetter','Make actual four-page A4 PDF with illustrated last page and valid folios'),
]

def outline(catalog, history, issue_no, issue_date):
    selected=choose_plan(catalog,history,issue_no,issue_date)
    errors=verify_plan(selected,catalog)
    if errors: raise ValueError('Plan nie przeszedł kontroli: '+'; '.join(errors))
    selected['roles']=[{'agent':key,'task':task} for key,task in ROLE_ORDER]
    selected['editorial_constraints']={
        'publication_allowed':False,
        'ai_agents_executed':False,
        'private_canon_required':True,
        'source_research_required':True,
        'final_layout_qa_required':True,
        'print_only_when_home':'unchanged',
    }
    return selected


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--catalog',type=Path,default=Path(__file__).with_name('departments.yaml'))
    ap.add_argument('--issue',type=int,required=True)
    ap.add_argument('--date',default=date.today().isoformat())
    ap.add_argument('--history',type=Path)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    history=[]
    if args.history:
        history=json.loads(args.history.read_text(encoding='utf-8'))['issues']
    plan=outline(load_catalog(args.catalog),history,args.issue,args.date)
    data=json.dumps(plan,ensure_ascii=False,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data+'\n',encoding='utf-8')
    print(data)

if __name__=='__main__':main()
