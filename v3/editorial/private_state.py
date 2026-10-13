"""Versioned private continuity, immutable public projection, transactional ledger.

The path must be outside the checkout. No private fixture lives in this module.
On Unix a flock protects read-modify-write; atomic replace prevents partial JSON.
"""
from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile

REPO = Path(__file__).resolve().parents[2]


def private_path(path):
    p = Path(path).resolve()
    if p == REPO or REPO in p.parents:
        raise ValueError('Prywatny kanon musi być poza repozytorium')
    return p


class PrivateStore:
    def __init__(self, path):
        self.path = private_path(path)

    @contextmanager
    def locked(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock = self.path.with_suffix('.lock')
        with lock.open('a') as stream:
            os.chmod(lock, 0o600)
            fcntl.flock(stream, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)

    def read(self):
        state = json.loads(self.path.read_text(encoding='utf-8'))
        for key in ('facts', 'arcs', 'clues', 'ledger', 'revision'):
            if key not in state:
                raise ValueError('Niekompletny prywatny kanon: ' + key)
        return state

    def context(self, number):
        """Safe author-facing view; never sends future solutions to the author."""
        s = self.read()
        facts = [dict(id=f['id'], published_claim=f['published_claim'])
                 for f in s['facts'] if f['reveal_min_issue'] <= number]
        clues = [dict(id=c['id'], carrier=c['carrier'], public_text=c['public_text'])
                 for c in s['clues'] if c['introduced_in'] == number]
        return {'facts': facts, 'clues': clues,
                'previous_publications': [h for h in s['ledger'] if h['issue_no']<number][-60:]}

    def check(self, issue):
        """Check claims, corrections, clue scheduling and unrevealed strings."""
        s = self.read()
        n = issue['issue_no']
        facts = {f['id']: f for f in s['facts']}
        clues = {c['id']: c for c in s['clues']}
        errors = []
        previous=issue.get('previous_issue')
        if previous and not any(h['issue_no']==previous for h in s['ledger']):
            errors.append('Brak zatwierdzonego poprzedniego numeru')
        if previous and any(h['issue_no']==previous and h['date']>issue['date'] for h in s['ledger']):
            errors.append('Data numeru jest wcześniejsza niż jego poprzednika')
        all_stories = issue['stories'] + [issue['comic']]
        public_text = json.dumps(issue, ensure_ascii=False).casefold()
        clue_ids = issue.get('clue_ids', [])
        if not 1 <= len(clue_ids) <= 3 or len(set(clue_ids)) != len(clue_ids):
            errors.append('Wymagane 1–3 różne tropy')
        visibility = []
        for cid in clue_ids:
            clue = clues.get(cid)
            if not clue or clue['introduced_in'] != n:
                errors.append('Nieznany lub przedwczesny trop: ' + cid)
                continue
            visibility.append(clue['visibility'])
            carriers = [a for a in all_stories if a['story_id'] == clue['carrier']]
            if not carriers or clue['public_text'] not in json.dumps(carriers, ensure_ascii=False):
                errors.append('Trop nie znajduje się w swoim materiale: ' + cid)
            if not clue.get('solution') or not clue.get('deduction') or clue['payoff_due'] < n:
                errors.append('Trop bez rozwiązania lub po terminie: ' + cid)
        if visibility.count('explicit') > 1 or visibility.count('subtle') > 2:
            errors.append('Przekroczono 1 jawny + 2 subtelne tropy')
        for arc in s['arcs']:
            if n < arc['payoff_due'] and arc['secret_truth'].casefold() in public_text:
                errors.append('Przedwczesne ujawnienie rozwiązania')
        for story in all_stories:
            for claim in story.get('canon_claims', []):
                fact = facts.get(claim['id'])
                if not fact or fact['reveal_min_issue'] > n:
                    errors.append('Nieznany/przedwczesny fakt: ' + claim['id'])
                elif claim['value'] != fact['published_claim']:
                    allowed = [c for c in s.get('contradictions', [])
                               if c['id'] == claim.get('contradiction_id')
                               and c['issue_no'] == n and c['fact_id'] == claim['id']
                               and c['published_claim'] == claim['value']]
                    if not allowed:
                        errors.append('Sprzeczność kanonu: ' + claim['id'])
            for ref in story.get('correction_refs', []):
                if not any(h['issue_no'] < n and ref in h['story_ids'] for h in s['ledger']):
                    errors.append('Sprostowanie nieistniejącego tekstu: ' + ref)
        return errors

    def commit(self, issue, manifest):
        """Record a validated REVIEW pilot, not a production publication."""
        with self.locked():
            s = self.read()
            n = issue['issue_no']
            digest = hashlib.sha256(json.dumps(issue, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            existing = [x for x in s['ledger'] if x['issue_no'] == n]
            if existing:
                if existing[0]['content_sha256'] != digest:
                    raise ValueError('Numer istnieje z inną treścią; użyj nowego numeru')
                return s['revision']
            if s['ledger'] and n <= max(x['issue_no'] for x in s['ledger']):
                raise ValueError('Ledger przyjmuje numery w kolejności')
            errors = self.check(issue)
            if errors:
                raise ValueError('; '.join(errors))
            old = deepcopy(s)
            s['ledger'].append({'issue_no': n, 'date': issue['date'],
                'status': 'REVIEW_PILOT', 'content_sha256': digest,
                'story_ids': list(manifest['story_pages']),
                'formats': [a['format_id'] for a in issue['stories'] if a['role'] == 'short'],
                'main_departments': [a['department_id'] for a in issue['stories'] if a['role'] == 'feature'],
                'topics': [a['topic'] for a in issue['stories']],
                'cover_angle': issue['cover_angle']})
            s['revision'] += 1
            archive = self.path.parent / (self.path.stem+'-revisions')
            archive.mkdir(exist_ok=True, mode=0o700)
            snapshot = archive / f"revision-{old['revision']:04d}.json"
            if not snapshot.exists():
                snapshot.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding='utf-8')
                os.chmod(snapshot, 0o600)
            fd, name = tempfile.mkstemp(dir=self.path.parent, prefix='.canon-')
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                    json.dump(s, stream, ensure_ascii=False, indent=2)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(name, self.path)
            finally:
                if os.path.exists(name):
                    os.unlink(name)
            return s['revision']
