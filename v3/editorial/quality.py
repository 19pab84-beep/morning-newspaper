"""Hard editorial gates; source attestation and semantics are explicitly separate."""
from __future__ import annotations
from datetime import date
import re
from urllib.parse import urlparse
from v3.editorial.production_audit import sudoku_solutions_9x9

PRIVATE_KEYS={'secret_truth','editorial_belief','solution','deduction','arcs','ledger','private_context'}


def walk(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            yield k
            yield from walk(v)
    elif isinstance(obj,list):
        for v in obj:
            yield from walk(v)


def validate(issue,catalog,history):
    errors=[]
    if PRIVATE_KEYS.intersection(walk(issue)):
        errors.append('Prywatne pola w pakiecie publicznym')
    try:
        date.fromisoformat(issue['date'])
    except (KeyError,ValueError,TypeError):
        errors.append('Zła data numeru')
    if type(issue.get('issue_no')) is not int or issue['issue_no']<1:
        errors.append('Zły numer wydania')
    if issue.get('pages')!=4:
        errors.append('Wymagane cztery strony')
    stories=issue.get('stories',[])
    depts={d['id']:d for d in catalog['departments']}
    formats={f['id']:d['id'] for d in catalog['departments'] for f in d['formats']}
    ids=[s.get('story_id') for s in stories]+[issue.get('comic',{}).get('story_id')]
    if len(ids)!=len(set(ids)) or None in ids:
        errors.append('story_id muszą być obecne i unikalne')
    features=[s for s in stories if s['role']=='feature']
    shorts=[s for s in stories if s['role']=='short']
    if len(features) not in (2,3) or len({s['department_id'] for s in features})!=len(features):
        errors.append('Wymagane 2–3 artykuły z różnych działów')
    if len([s for s in stories if s['role']=='cover' and s['type']=='fiction' and s['page']==1])!=1:
        errors.append('Wymagany jeden reportaż fikcyjny na okładce')
    if not 5<=len(shorts)<=8:
        errors.append('Wymagane 5–8 krótkich rubryk')
    if issue.get('news_count')!=0:
        errors.append('Piloty bez przymusowych wiadomości')
    if not issue.get('surprise') or not issue.get('new_format'):
        errors.append('Brak niespodzianki / nowego formatu')
    recent=history[-2:]
    forbidden_formats={f for h in recent for f in h.get('formats',[])}
    used=[]
    for s in stories:
        sid=s['story_id']
        if s['page'] not in (1,2,3,4):
            errors.append(sid+': strona poza zakresem')
        if s['department_id'] not in depts:
            errors.append(sid+': nieznany dział')
        if s['role']=='short':
            fid=s['format_id'];used.append(fid)
            if formats.get(fid)!=s['department_id']:
                errors.append(sid+': format z innego działu')
            if fid in forbidden_formats:
                errors.append(sid+': za wczesne powtórzenie rubryki')
        text=' '.join(s['paragraphs'])
        words=len(text.split())
        minimum=320 if s['role']=='feature' else 200 if s['role']=='cover' else 50
        if words<minimum:
            errors.append(sid+': za mało konkretnego materiału')
        if len(set(s['paragraphs']))!=len(s['paragraphs']):
            errors.append(sid+': powtórzony akapit')
        if re.search(r'\b(?:str\.|strona)\s*\d',text,re.I):
            errors.append(sid+': AI nie może nadawać odsyłaczy')
        if re.search(r'\b(?:lorem ipsum|TODO|TBD|placeholder)\b',text,re.I):
            errors.append(sid+': niedokończona treść')
        specifics=s.get('specifics',[])
        if len(specifics)<3 or any(v.casefold() not in text.casefold() for v in specifics):
            errors.append(sid+': brak trzech deklarowanych konkretów w tekście')
        if s['type']=='fiction' and (s.get('source_ids') or s.get('claims')):
            errors.append(sid+': fikcja z udawanym źródłem')
        if s['type']=='sourced_feature':
            if not s.get('source_ids') or not s.get('claims'):
                errors.append(sid+': brak źródeł i twierdzeń')
            for claim in s.get('claims',[]):
                if claim['source_id'] not in s.get('source_ids',[]):
                    errors.append(sid+': źródło twierdzenia nie znajduje się w bibliografii materiału')
                source=issue['sources'].get(claim['source_id'])
                if not source or claim['evidence_id'] not in source.get('evidence',{}):
                    errors.append(sid+': twierdzenie bez dowodu')
            for source_id in s.get('source_ids',[]):
                source=issue['sources'].get(source_id)
                if not source:
                    errors.append(sid+': nieznane źródło');continue
                u=urlparse(source['url'])
                if u.scheme!='https' or not u.netloc or u.netloc.endswith('.invalid'):
                    errors.append(sid+': niewiarygodny URL')
                if not source.get('reviewed_at') or not source.get('evidence') or not source.get('reviewer'):
                    errors.append(sid+': źródło niezweryfikowane')
        topic=re.sub(r'^\d+-','',s['topic']).casefold()
        if s['role']!='cover' and any(topic==re.sub(r'^\d+-','',t).casefold()
                                     for h in history[-21:] for t in h.get('topics',[])):
            errors.append(sid+': powtórzony temat bez nowej perspektywy')
    if len(used)!=len(set(used)):
        errors.append('Powtórzony format w numerze')
    for s in features:
        if any(s['department_id'] in h.get('main_departments',[]) for h in history[-3:]):
            errors.append('Za wczesne powtórzenie głównego działu')
    if any(h.get('cover_angle')==issue['cover_angle'] for h in history[-4:]):
        errors.append('Za wczesne powtórzenie mechanizmu okładki')
    comic=issue.get('comic',{})
    if comic.get('panels') not in (3,4) or len(comic.get('balloons',[]))!=comic.get('panels'):
        errors.append('Wymagane 3–4 kadry z dymkami')
    if not comic.get('image') or not comic.get('sequence'):
        errors.append('Komiks nie ma rysunku lub następstwa scen')
    if any(t['story_id'] not in ids for t in issue.get('teasers',[])):
        errors.append('Zapowiedź nieistniejącego tekstu')
    try:
        if sudoku_solutions_9x9(issue['sudoku'])!=1:
            errors.append('Sudoku nie ma dokładnie jednego rozwiązania')
    except (KeyError,ValueError):
        errors.append('Sudoku musi być 9 × 9')
    if issue.get('editorial_review',{}).get('status')not in ('APPROVED_FOR_PILOT','APPROVED_FOR_PRINT'):
        errors.append('Brak oceny redakcyjnej dla pilota')
    return errors
