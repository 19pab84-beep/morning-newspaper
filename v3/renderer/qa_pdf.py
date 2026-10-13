"""Public CLI for the complete V3 preflight; no game-title-specific assertions."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.renderer.preflight import check as preflight


def check(path):
    path=Path(path)
    issue_file=path.parent/'issue.json'
    manifest_file=path.parent/'manifest.json'
    if not issue_file.is_file() or not manifest_file.is_file():
        return ['QA wymaga issue.json i manifest.json obok PDF; sam obraz nie dowodzi jakości']
    return preflight(path,json.loads(issue_file.read_text()),json.loads(manifest_file.read_text()))['errors']


if __name__=='__main__':
    problems=check(Path(sys.argv[1]))
    print('PASS · REVIEW ONLY' if not problems else '\n'.join(problems))
    raise SystemExit(bool(problems))
