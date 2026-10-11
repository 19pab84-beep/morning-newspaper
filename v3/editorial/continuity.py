"""Redakcyjny walidator i rotator rubryk. Nie publikuje niczego sam.
Prywatne lore powinno być dostarczone z prywatnego magazynu, NIGDY z GitHub Pages.
"""
from __future__ import annotations
import json
import random
from pathlib import Path
from collections import Counter
import yaml


def read_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def choose_rubrics(catalog: dict, history: list[dict], issue_no: int, count: int = 7) -> list[str]:
    """Stable rotation with cooldown and weighted overdue rubric priority.
    Forced front/back slots are not counted against rotation count.
    """
    cfg = catalog['rules']
    candidates = [r for r in catalog['rubrics'] if r['id'] not in cfg['regular_front'] + cfg['fixed_back']]
    rng = random.Random(issue_no)
    eligible = []
    for entry in candidates:
        past = [i['issue_no'] for i in history if entry['id'] in i.get('rubrics',[])]
        distance = issue_no - max(past) if past else issue_no + 4
        # Hard rule: no repeat in the previous two issues. Longer rubric
        # cooldowns are soft preferences, otherwise 60-day rotation deadlocks.
        if distance <= cfg.get('avoid_repeat_last_issues', 2):
            continue
        desired = entry.get('cooldown_issues', 2)
        cooldown_penalty = 50 * max(0, desired - distance)
        eligible.append((distance * entry['weight'] - cooldown_penalty + rng.random(), entry['id']))
    eligible.sort(reverse=True)
    selected = [rubric for _,rubric in eligible[:count]]
    if len(selected) < min(count, cfg.get('min_rotating_per_issue', 4)):
        raise ValueError('Za mało rubryk spełnia okres karencji; nie forsuj powtórek')
    return list(cfg['regular_front']) + selected + list(cfg['fixed_back'])


def sudoku_solution_count(puzzle: list[list[int]], *, limit: int = 2) -> int:
    """4x4 classic sudoku with 2x2 subgrids. Counts up to `limit`."""
    if len(puzzle)!=4 or any(len(row)!=4 for row in puzzle):
        raise ValueError('Sudoku musi mieć 4x4')
    grid = [row[:] for row in puzzle]
    if any(not isinstance(n,int) or n not in (0,1,2,3,4) for row in grid for n in row):
        raise ValueError('Sudoku: znaki spoza 0–4')
    def valid(r,c,n):
        return (n not in grid[r] and all(grid[i][c]!=n for i in range(4))
                and all(grid[i][j]!=n for i in range(r//2*2,r//2*2+2)
                        for j in range(c//2*2,c//2*2+2)))
    # Existing duplicate givens fail before search.
    for r in range(4):
        for c in range(4):
            n=grid[r][c]
            if n:
                grid[r][c]=0
                if not valid(r,c,n):return 0
                grid[r][c]=n
    result=0
    def solve():
        nonlocal result
        if result>=limit:return
        choices=[]
        for r in range(4):
            for c in range(4):
                if grid[r][c]==0:
                    opts=[n for n in range(1,5) if valid(r,c,n)]
                    if not opts:return
                    choices.append((len(opts),r,c,opts))
        if not choices:
            result+=1;return
        _,r,c,opts=min(choices)
        for n in opts:
            grid[r][c]=n;solve();grid[r][c]=0
    solve();return result


def validate_issue(issue: dict, canon: dict, clues: dict, history: list[dict]) -> list[str]:
    """Machine-checkable hard gates. Semantic fact-check remains a separate step."""
    errors=[]
    number=issue.get('issue_no')
    if not isinstance(number,int) or number<=0:errors.append('Brak poprawnego issue_no');return errors
    if any(item.get('issue_no')==number and item.get('status')=='published' for item in history):
        errors.append('Nie wolno ponownie opublikować numeru')
    if issue.get('backpage_index') != issue.get('page_count'):
        errors.append('Ostatnia strona nie jest ostatnią stroną PDF')
    if issue.get('page_count',0) not in range(4,7):
        errors.append('Wydanie powinno mieć 4–6 stron')
    if issue.get('fiction_disclaimer') is not True:
        errors.append('Brak dyskretnej, prawdziwej stopki fikcyjności')
    facts={x['id']:x for x in canon['facts']}
    ids={x['id']:x for x in clues['clues']}
    attached=issue.get('clues',[])
    if not 1 <= len(attached) <= 3:
        errors.append('Kontrola tempa narracji: 1–3 tropy w numerze')
    if len(attached)!=len(set(attached)):
        errors.append('Ten sam trop powtórzony w obrębie wydania')
    for cid in attached:
        clue=ids.get(cid)
        if not clue:errors.append(f'Nieznana wskazówka {cid}');continue
        if clue['introduced_issue']!=number:
            errors.append(f'{cid} przypisana do innego numeru')
        if clue['canonical_ref'] not in facts:
            errors.append(f'{cid}: brak odniesienia do kanonu')
        if number>=clue['payoff_target_issue'] and clue['state'] not in ('resolved','revealed'):
            errors.append(f'{cid}: przekroczona data rozwiązania')
    for article in issue.get('articles',[]):
        if article['type'] not in ('fiction','essay','sourced_feature','brief'):
            errors.append(f'{article.get("id")}: nieznany typ artykułu');continue
        if article['type'] in ('sourced_feature','brief') and not article.get('source_urls'):
            errors.append(f'{article.get("id")}: potrzebne źródła dla prawdziwych twierdzeń')
        if article['type']=='fiction' and article.get('source_urls'):
            errors.append(f'{article.get("id")}: fikcji nie podpisuj linkami do rzekomej dokumentacji')
        if article.get('word_count',0)<100 and article.get('role')=='feature':
            errors.append(f'{article.get("id")}: główny artykuł jest zbyt ogólny/krótki')
        for ref in article.get('canon_refs',[]):
            if ref not in facts:
                errors.append(f'{article.get("id")}: nieznany element kanonu: {ref}')
            elif facts[ref]['reveal_min_issue']>number:
                errors.append(f'{article.get("id")}: nieplanowane wczesne ujawnienie {ref}')
    return errors


def ensure_safe(issue,canon,clues,history):
    problems=validate_issue(issue,canon,clues,history)
    if problems:raise ValueError('Publikacja zablokowana:\n - '+'\n - '.join(problems))
    return True
