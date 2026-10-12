"""Offline editorial checks and rotation prototype for Poranna Prasa V3.

No AI, publication, printer access or private canon. No facts are fabricated.
An audit cannot replace semantic fact checking or continuity review.
"""
from __future__ import annotations
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
import hashlib
import json
import re

COVER_ANGLES = [
    'księga/adres', 'transport', 'korespondencja', 'świadectwo',
    'plan budynku', 'głos/radio', 'urzędowy komunikat', 'fotografia',
    'sprostowanie', 'ogłoszenie', 'pamięć świadka', 'księga zgonów',
]


def load_catalog(path):
    """The currently stored departments.yaml is JSON, a YAML-compatible subset."""
    return json.loads(Path(path).read_text(encoding='utf-8'))


def validate_catalog(catalog):
    problems = []
    depts = catalog.get('departments', [])
    ids = [d.get('id') for d in depts]
    all_formats = [f.get('id') for d in depts for f in d.get('formats', [])]
    if len(depts) != 32 or len(set(ids)) != len(ids):
        problems.append('Katalog: oczekiwano 32 unikalnych działów')
    if len(all_formats) != 128 or len(set(all_formats)) != len(all_formats):
        problems.append('Katalog: oczekiwano 128 unikalnych formatów')
    if catalog.get('policy', {}).get('issue_pages') != 4:
        problems.append('Katalog: 4 strony A4 są wymagane')
    for d in depts:
        if len(d.get('formats', [])) != 4:
            problems.append(f"Dział {d.get('id')} nie ma czterech formatów")
        for f in d.get('formats', []):
            if not f.get('title'):
                problems.append('Pusty tytuł formatu')
    return problems


def _key(id_, n):
    return int.from_bytes(hashlib.sha256(f'{n}|{id_}'.encode()).digest()[:8], 'big')


def _pick(pool, history, number, selected, last_two=True):
    selected_ids = set(selected)
    eligible = []
    for d, f in pool:
        fid = f['id'] if f else d['id']
        if fid in selected_ids:
            continue
        past = [h['issue_no'] for h in history if fid in (h['formats'] if f else h['main_departments'])]
        if last_two and past and number - max(past) <= (2 if f else 3):
            continue
        use = len(past)
        # Prefer rare and long-absent items. Stable tie break is seeded by issue number.
        last = number - max(past) if past else number + 12
        eligible.append((use, -last, _key(fid, number), d, f))
    if not eligible:
        raise ValueError('Brak dopuszczalnego formatu/działu bez zbyt wczesnych powtórzeń')
    *_, d, f = min(eligible, key=lambda x:x[:3])
    return d, f


def choose_plan(catalog, history, issue_no, issue_date):
    problems = validate_catalog(catalog)
    if problems:
        raise ValueError('; '.join(problems))
    depts = catalog['departments']
    main_pool = [(d, None) for d in depts if d['desk_code'] not in ('U','O')]
    main = []
    main_desks = []
    for _ in range(2):
        possible = [(d, f) for d,f in main_pool if d['desk_code'] not in main_desks]
        d, _ = _pick(possible, history, issue_no, [x['id'] for x in main])
        main.append(d);main_desks.append(d['desk_code'])
    used_formats = []
    back_pool = [(d, f) for d in depts if d['desk_code']=='O' for f in d['formats']]
    inside_pool = [(d, f) for d in depts if d['desk_code']!='O' and d['id'] not in {m['id'] for m in main} for f in d['formats']]
    shorts = []
    for pool, target in [(back_pool,3),(inside_pool,3)]:
        for _ in range(target):
            d, f = _pick(pool, history, issue_no, used_formats)
            used_formats.append(f['id'])
            shorts.append({'department_id':d['id'],'desk':d['desk_code'],'format_id':f['id'],
                           'title':f['title'],'page':4 if target==3 and pool is back_pool else 2+(len(shorts)%2)})
    story_pages = {f'feature_{i+1}':2+i for i in range(2)}
    story_pages['backpage']=4
    return {'schema':3,'status':'DRAFT_OFFLINE_ONLY','issue_no':issue_no,'date':issue_date,
            'pages':4,'cover':{'type':'fiction','angle':COVER_ANGLES[(issue_no-1)%len(COVER_ANGLES)],'page':1},
            'main_departments':[d['id'] for d in main], 'main_desks':main_desks,
            'formats':used_formats,'shorts':shorts,'teasers':[
                {'story_id':x,'page':p} for x,p in story_pages.items()],
            'backpage_reserved':True,'comic_image_required':True,'sudoku_size':9,
            'canon_check':'NOT_DONE','source_verification':'NOT_DONE','article_generation':'NOT_DONE'}


def verify_plan(plan, catalog):
    problems = []
    all_depts = {d['id']:d for d in catalog['departments']}
    all_formats = {f['id']:f for d in catalog['departments'] for f in d['formats']}
    if plan.get('pages') != 4: problems.append('Nie ma dokładnie czterech stron')
    if plan.get('cover',{}).get('type') != 'fiction': problems.append('Brak fikcyjnego reportażu okładkowego')
    main = plan.get('main_departments',[])
    if len(main) not in (2,3) or len(main)!=len(set(main)):problems.append('Artykuły główne: potrzebne 2–3 różne działy')
    if any(x not in all_depts for x in main):problems.append('Nieznany dział główny')
    formats = plan.get('formats',[])
    if not 5 <= len(formats) <= 8 or len(formats)!=len(set(formats)):
        problems.append('W numerze musi być 5–8 unikatowych krótkich rubryk')
    if any(x not in all_formats for x in formats):problems.append('Nieznany format rubryki')
    if not plan.get('backpage_reserved'):problems.append('Nie zarezerwowano strony czwartej')
    if not plan.get('comic_image_required'):problems.append('Komiks musi być obrazem')
    if plan.get('sudoku_size') != 9:problems.append('Sudoku musi być 9x9')
    if any(t.get('page') not in (2,3,4) for t in plan.get('teasers',[])):
        problems.append('Fałszywe odsyłacze do nieistniejących stron')
    if any(s.get('page') not in (2,3,4) for s in plan.get('shorts',[])):
        problems.append('Rubryka nie mieści się w 4 stronach')
    return problems


def simulate(catalog, n=60, start=date(2026,10,12)):
    history=[];issues=[]
    for i in range(1,n+1):
        plan=choose_plan(catalog,history,i,(start+timedelta(days=i-1)).isoformat())
        errors=verify_plan(plan,catalog)
        if errors:raise AssertionError(f'Numer {i}: {errors}')
        issues.append(plan)
        history.append({'issue_no':i,'formats':plan['formats'],'main_departments':plan['main_departments']})
    per7=[len(set(d for issue in issues[a:a+7] for d in issue['main_departments'] + [x['department_id'] for x in issue['shorts']])) for a in range(n-6)]
    per14=[len(set(d for issue in issues[a:a+14] for d in issue['main_departments'] + [x['department_id'] for x in issue['shorts']])) for a in range(n-13)]
    repeat=[]
    for i, p in enumerate(issues):
        for prior in issues[max(0,i-2):i]:
            if set(p['formats']) & set(prior['formats']):repeat.append([p['issue_no'],prior['issue_no']])
    return {'issues':n,'unique_departments':len(set(d for i in issues for d in i['main_departments']+[r['department_id'] for r in i['shorts']])),
            'unique_formats':len(set(f for i in issues for f in i['formats'])),
            'min_departments_per_7_issues':min(per7),'min_departments_per_14_issues':min(per14),
            'repeat_formats_within_previous_2_issues':repeat,
            'different_main_desks_every_issue':all(len(set(i['main_desks']))==2 for i in issues),
            'series':issues}


def sudoku_solutions_9x9(puzzle, limit=2):
    """Check Sudoku givens for inconsistencies; count solutions up to two (MRV)."""
    if len(puzzle)!=9 or any(len(r)!=9 for r in puzzle):
        raise ValueError('Sudoku musi mieć 9×9')
    if any(type(x) is not int or x<0 or x>9 for row in puzzle for x in row):
        raise ValueError('Wartości sudoku muszą być 0..9')
    board=[r[:] for r in puzzle]
    rows=[set() for _ in range(9)];cols=[set() for _ in range(9)];boxes=[set() for _ in range(9)]
    empty=[]
    for r in range(9):
        for c in range(9):
            x=board[r][c];b=r//3*3+c//3
            if not x:empty.append((r,c));continue
            if x in rows[r] or x in cols[c] or x in boxes[b]:return 0
            rows[r].add(x);cols[c].add(x);boxes[b].add(x)
    found=0
    digits=set(range(1,10))
    def solve(remaining):
        nonlocal found
        if found>=limit:return
        if not remaining:found+=1;return
        choices=[]
        for r,c in remaining:
            b=r//3*3+c//3
            opts=digits-rows[r]-cols[c]-boxes[b]
            if not opts:return
            choices.append((len(opts),r,c,opts))
        _,r,c,opts=min(choices, key=lambda z:z[0])
        b=r//3*3+c//3
        left=[p for p in remaining if p!=(r,c)]
        for x in sorted(opts):
            rows[r].add(x);cols[c].add(x);boxes[b].add(x)
            solve(left)
            rows[r].remove(x);cols[c].remove(x);boxes[b].remove(x)
            if found>=limit:return
    solve(empty)
    return found


def audit_pdf(path):
    """Physical PDF preflight, not semantic truth or layout aesthetic approval."""
    import fitz
    d=fitz.open(path)
    errors=[];stats=[]
    if len(d)!=4:errors.append(f'Oczekiwano 4 stron A4, jest {len(d)}')
    for i,page in enumerate(d):
        w,h=page.rect.width,page.rect.height
        if abs(w-595.2756)>1 or abs(h-841.8898)>1:
            errors.append(f'Strona {i+1}: zły format {w:.1f}×{h:.1f} pt')
        text=page.get_text()
        images=len(page.get_images(full=True))
        if not text.strip():errors.append(f'Strona {i+1}: brak czytelnej warstwy tekstowej')
        if i==3 and images==0:errors.append('Strona 4: nie ma osadzonego obrazkowego komiksu/ilustracji')
        rect=page.rect
        outside=sum(1 for block in page.get_text('blocks') if block[6]==0 and (block[0]<6 or block[1]<5 or block[2]>w-6 or block[3]>h-5))
        if outside:errors.append(f'Strona {i+1}: {outside} bloki tekstu przycięte lub poza marginesem')
        stats.append({'page':i+1,'size_pt':[round(w,1),round(h,1)],'words':len(page.get_text('words')),'images':images,'outside_blocks':outside})
    if len(d)==4:
        cover=d[0].get_text()
        for pageid in re.findall(r'\bSTR\.\s*(\d+)\b',cover,flags=re.I):
            if int(pageid) not in (2,3,4):errors.append(f'Okładka odsyła do str. {pageid}')
    return {'status':'PASS' if not errors else 'FAIL','errors':errors,'pages':stats}
