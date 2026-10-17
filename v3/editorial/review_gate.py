"""Validate review evidence, not literary quality. Never auto-score prose."""
import hashlib
from pathlib import Path

REQUIRED = {'logic', 'specificity', 'repetition', 'visual', 'continuity', 'sources', 'canon'}

def review_errors(report, pdf):
    errors = []
    if report.get('pdf_sha256') != hashlib.sha256(Path(pdf).read_bytes()).hexdigest():
        errors.append('Review does not describe the current PDF')
    if report.get('pages_inspected') != [1, 2, 3, 4]:
        errors.append('Inspect all four rendered pages')
    checks = report.get('editorial_checks', {})
    if REQUIRED - checks.keys() or any(not str(checks.get(k, '')).strip() for k in REQUIRED):
        errors.append('Missing editorial review evidence')
    if report.get('technical_errors') != []:
        errors.append('Technical preflight missing or failed')
    if not isinstance(report.get('defects'), list):
        errors.append('Missing defect register')
    for defect in report.get('defects', []):
        if defect.get('status') == 'fixed' and not defect.get('verification'):
            errors.append('Fix has no verification evidence')
        if defect.get('severity') in ('critical', 'major') and defect.get('status') != 'fixed':
            errors.append('Unresolved publication blocker: '+defect.get('description', '?'))
    if not report.get('limitations'):
        errors.append('Missing assessment limitations')
    return errors

if __name__ == '__main__':
    import argparse
    import json
    parser=argparse.ArgumentParser(description='Check review evidence against the exact final PDF')
    parser.add_argument('report',type=Path)
    parser.add_argument('pdf',type=Path)
    args=parser.parse_args()
    errors=review_errors(json.loads(args.report.read_text()),args.pdf)
    print(json.dumps({'status':'BLOCKED' if errors else 'REVIEW_COMPLETE','errors':errors}))
    raise SystemExit(bool(errors))
