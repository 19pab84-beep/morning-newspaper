"""Build daily issue: RSS -> AI edit -> A4 PDF -> tested raster Brother PRN -> static Pages manifest.
GPL-2.0-or-later.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests
import yaml
from build_prn import build as pdf_to_prn
from layout import create_pdf
from news import collect, edit_with_ai


def today_local(tz='Europe/Warsaw'):
    return datetime.now(ZoneInfo(tz))


def manifest_history(base_url):
    if not base_url:
        return []
    try:
        url = base_url.rstrip('/') + '/latest.json'
        r = requests.get(url, timeout=12, headers={'Cache-Control':'no-cache'})
        r.raise_for_status()
        data = r.json()
        return data.get('seen_ids', [])[:120]
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_html(issue_date, stories, ai=False, demo=False):
    lis = []
    for story in stories:
        link = html.escape(story.get('link',''), quote=True)
        caption = html.escape(story['headline'])
        lis.append(f'<li><strong>{caption}</strong> – {html.escape(story["section"])} '
                   + (f'(<a href="{link}" target="_blank" rel="noopener noreferrer">źródło</a>)' if link else '')
                   + '</li>')
    notice = ('DEMO: wymyślone treści, nie są aktualnymi wiadomościami' if demo else
              ('Wersja AI: streszczenia wygenerowane z danych RSS' if ai else 'Wersja RSS: bez redakcji AI'))
    return (f'<!doctype html><html lang="pl"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Poranna Prasa — {issue_date}</title>'
            '<style>body{max-width:770px;margin:5vh auto;padding:0 18px;color:#181818;'
            'font:17px/1.6 Georgia,serif}h1{font-size:38px}li{margin:12px 0}'
            'a{color:#333}.meta{font:13px Arial,sans-serif;color:#555}</style></head><body>'
            f'<p class="meta">{issue_date} • {notice}</p><h1>PORANNA PRASA</h1>'
            f'<p><a href="gazeta.pdf">Pobierz PDF</a></p><h2>Źródła wydania</h2>'
            f'<ol>{"".join(lis)}</ol></body></html>')


def mock_items(now):
    cats = ['POLSKA', 'ŚWIAT', 'TECHNOLOGIA I AI', 'NAUKA', 'KULTURA, FILM I GRY', 'MUZYKA I INNE ODKRYCIA']
    motifs = ['Jak powstaje gazeta na zamówienie', 'Rozwiązania, które ułatwiają codzienność',
              'Historia pewnego nietypowego wynalazku', 'Zaskakujące sposoby na zwykłe problemy',
              'Dlaczego dobrze sprawdzać źródła wiadomości']
    body = ('To jest wyłącznie próbny, wymyślony tekst służący sprawdzeniu układu gazety i poprawnego wydruku. '
            'Na tej podstawie oceniamy, czy kolumny są czytelne, polskie litery dobrze złożone, '
            'a kontrast odpowiedni dla monochromatycznej drukarki laserowej. '
            'W prawdziwym wydaniu ten fragment zostanie zastąpiony krótkim artykułem '
            'opartym na aktualnych źródłach, z datą publikacji i odnośnikiem do materiału. '
            'Mechanizm ma odrzucać przestarzałe informacje i chronić przed wielokrotnym drukowaniem tego samego numeru.')
    out = []
    for i in range(24):
        out.append({'id':f'demo-{i}', 'section':cats[i//4], 'title':motifs[i%5],
                    'headline': motifs[i%5], 'body':body, 'source':'DEMO — BRAK ŹRÓDŁA',
                    'link':'', 'published':now.date().isoformat()})
    return out


def generate(config: dict, outdir: Path, *, demo=False, base_url='', forced_date='') -> dict:
    tz = config['publication']['timezone']
    now = today_local(tz)
    day = forced_date or now.date().isoformat()
    history = manifest_history(base_url) if not demo else []
    if demo:
        stories = mock_items(now)
        warnings = []
    else:
        stories, warnings = collect(config, history=history)
        stories = edit_with_ai(stories, config['publication']['ai_model'],
                               os.environ.get('OPENAI_API_KEY', ''))
    for warning in warnings:
        print('OSTRZEŻENIE:', warning, file=sys.stderr)
    outdir.mkdir(parents=True, exist_ok=True)
    pdf = outdir/'gazeta.pdf'
    prn = outdir/'gazeta.prn'
    pages = create_pdf(stories, pdf, issue_date=day,
                       title=config['publication']['title'], demo=demo,
                       ai=bool(os.environ.get('OPENAI_API_KEY')) and not demo)
    if pages > 8 and not demo:
        raise RuntimeError(f'Wydanie ma {pages} stron (limit bezpieczeństwa 8), wstrzymano publikację')
    pdf_to_prn(pdf, prn)
    manifest = {
        'schema': 1, 'status': 'ready', 'issue_id': f'poranna-prasa-{day}' + ('-demo' if demo else ''),
        'date': day, 'time_zone': tz, 'generated_at': now.isoformat(),
        'pdf': 'gazeta.pdf', 'prn': 'gazeta.prn',
        'prn_sha256': sha(prn), 'pdf_sha256': sha(pdf), 'prn_bytes': prn.stat().st_size,
        'pages': pages, 'stories': len(stories), 'is_demo': demo,
        'ai_edited': bool(os.environ.get('OPENAI_API_KEY')) and not demo,
        'seen_ids': list(dict.fromkeys([a['id'] for a in stories] + history))[:120],
    }
    (outdir/'latest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (outdir/'index.html').write_text(index_html(day, stories, manifest['ai_edited'], demo), encoding='utf-8')
    (outdir/'.nojekyll').write_text('', encoding='utf-8')
    (outdir/'sources.json').write_text(json.dumps([{
        'headline': a['headline'], 'section': a['section'], 'source': a['source'],
        'link': a['link'], 'published': a['published']} for a in stories], indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ['date','pages','stories','prn_bytes','is_demo']}, ensure_ascii=False))
    return manifest


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, default=Path('config.yaml'))
    ap.add_argument('--output', type=Path, default=Path('public'))
    ap.add_argument('--base-url', default=os.environ.get('PRESS_BASE_URL', ''))
    ap.add_argument('--demo', action='store_true', help='NEVER publish as a real issue')
    ap.add_argument('--date', default='', help='Only for reproducible offline tests')
    args = ap.parse_args()
    with args.config.open(encoding='utf-8') as f:
        config = yaml.safe_load(f)
    generate(config, args.output, demo=args.demo, base_url=args.base_url,
             forced_date=args.date)
