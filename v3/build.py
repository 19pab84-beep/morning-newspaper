"""Build an offline REVIEW issue. This command has no publisher or printer."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from v3.editorial.authoring import ResponsesAuthor
from v3.editorial.private_state import PrivateStore
from v3.editorial.puzzles import sudoku_answer
from v3.editorial.production_audit import load_catalog
from v3.editorial.quality import validate,PRIVATE_KEYS,walk
from v3.renderer.press import Press
from v3.renderer.preflight import check

ROOT=Path(__file__).resolve().parent


def build(input_path, private_state, output, *, live=False, model=None, prn=False):
    input_path=Path(input_path).resolve()
    out=Path(output).resolve()
    for path in (input_path, out):
        if path.is_relative_to(ROOT.parent):
            raise ValueError('Manuscripts and generated editions must be outside the repository')
    issue=json.loads(input_path.read_text(encoding='utf-8'))
    if PRIVATE_KEYS.intersection(walk(issue)):
        raise ValueError('Prywatne pola w publicznym przydziale; nie wysłano ich do AI')
    store=PrivateStore(private_state)
    state=store.read()
    number=issue['issue_no']
    if state['ledger'] and number<max(h['issue_no'] for h in state['ledger']):
        if not any(h['issue_no']==number for h in state['ledger']):
            raise ValueError('Nie można wstawić wcześniejszego numeru do istniejącego ledgeru')
    history=[h for h in state['ledger'][-60:] if h['issue_no']<number]
    roles=[{'role':'editor_in_chief','executed':'catalog and history validation'},
           {'role':'archivist','executed':'private store, safe public projection'}]
    if live:
        issue=ResponsesAuthor(model).rewrite(issue,store.context(number))
    roles.extend([{'role':'researcher','executed':'source packet evidence/attestation gates; no automatic live browsing'},
                  {'role':'writers','executed':'Responses API' if live else issue.get('provenance',{}).get('mode','original ChatGPT Work manuscripts')}])
    errors=validate(issue,load_catalog(ROOT/'editorial/departments.yaml'),history)
    errors+=store.check(issue)
    if errors:
        raise ValueError('Numer odrzucony:\n - '+'\n - '.join(errors))
    roles.extend([{'role':'continuity_keeper','executed':'claims, clues, corrections, embargo gates'},
                  {'role':'puzzle_master','executed':'clue schedule + unique 9×9 solution'},
                  {'role':'copy_editor','executed':issue['editorial_review']['reviewer']}])
    out=Path(output).resolve()
    out.mkdir(parents=True,exist_ok=True)
    dest=out/f'issue-{number:03d}'
    with tempfile.TemporaryDirectory(dir=out,prefix='.staging-') as tmp:
        stage=Path(tmp)
        pdf=stage/f'poranna_prasa_nr{number:03d}.pdf'
        manifest=Press(issue,pdf).render()
        qa=check(pdf,issue,manifest,raster_dir=stage/'pages')
        if qa['errors']:
            raise ValueError('Preflight odrzucił numer: '+'; '.join(qa['errors']))
        roles.append({'role':'typesetter','executed':'hybrid PDF + actual PDF preflight + 300 dpi raster'})
        qa['editorial_review']=issue['editorial_review']
        qa['continuity']='PASS: external private canon; no private data in public output'
        qa['rotation']='PASS: manuscript departments/formats/topics against previous 60 ledger entries'
        qa['sudoku_solutions']=1
        qa['roles']=roles
        qa['visual_review']='PENDING'
        qa['physical_print']='NOT_PERFORMED'
        if prn:
            # Reuse the existing encoder read-only, generating a local file only.
            # The production script, workflow and device configuration remain unchanged.
            from v3.renderer.prn import build as encode_prn
            stream=stage/f'poranna_prasa_nr{number:03d}.prn'
            encode_prn(pdf,stream)
            data=stream.read_bytes()
            sheets=data.count(b'@PJL SET PAPER = A4')
            if sheets!=4 or data.count(b'1030M\x0c')!=4:
                raise ValueError('PRN: błędna liczba stron')
            qa['prn']={'status':'STRUCTURAL_PASS','pages':sheets,'dpi':600,
                       'sent_to_printer':False,'physical_compatibility':'NOT_TESTED'}
        manifest['pdf_sha256']=hashlib.sha256(pdf.read_bytes()).hexdigest()
        manifest['provenance']=issue['provenance']
        for name,data in [('manifest.json',manifest),('qa.json',qa),('issue.json',issue)]:
            (stage/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        bibliography='\n\n'.join(f"{sid}: {s['publisher']} · {s['title']}\n{s['url']}\n{s['print_note']}"
                                  + ('\nDostępna dokumentacja: '+s['secondary_locator'] if s.get('secondary_locator') else '')
                                  + ('\nDostęp: '+s['access_note'] if s.get('access_note') else '')
                                  for sid,s in issue['sources'].items())
        (stage/'sources.txt').write_text(bibliography+'\n',encoding='utf-8')
        answer=sudoku_answer(issue['sudoku'])
        (stage/'sudoku-answer.txt').write_text('\n'.join(' '.join(map(str,row)) for row in answer)+'\n',encoding='utf-8')
        # The old output is retained until the complete candidate is validated.
        backup=out/f'.previous-{number:03d}'
        if backup.exists():
            raise ValueError('Istnieje nierozstrzygnięty poprzedni zapis numeru')
        if dest.exists():
            dest.rename(backup)
        try:
            shutil.copytree(stage,dest)
            store.commit(issue,manifest)
        except Exception:
            if dest.exists():
                shutil.rmtree(dest)
            if backup.exists():
                backup.rename(dest)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    return dest


def main():
    ap=argparse.ArgumentParser(description='Poranna Prasa V3 · offline REVIEW generator')
    ap.add_argument('--input',type=Path,required=True,help='public manuscript/assignment JSON')
    ap.add_argument('--private-state',type=Path,required=True,help='external PRIVATE JSON canon, never inside the checkout')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--live',action='store_true',help='explicit paid Responses API authoring')
    ap.add_argument('--model',help='explicit model for live mode; no hidden default')
    ap.add_argument('--prn',action='store_true',help='local 600 dpi stream only; does not send anything')
    args=ap.parse_args()
    if args.model and not args.live:
        ap.error('--model requires --live')
    try:
        dest=build(args.input,args.private_state,args.output,live=args.live,model=args.model,prn=args.prn)
    except (ValueError,RuntimeError) as error:
        ap.exit(1,str(error)+'\n')
    print('VALIDATED LOCAL OUTPUT: '+str(dest))


if __name__=='__main__':
    main()
