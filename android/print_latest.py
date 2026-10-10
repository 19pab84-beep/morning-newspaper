#!/usr/bin/env python3
"""Android/Termux fetch+TCP sender; refuses stale/demo/duplicate issues.
Uses only Python stdlib. GPL-2.0-or-later.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import socket
import sys
from datetime import datetime, time
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

HOME = Path.home()
CONFIG = HOME / '.config/poranna-prasa/config.json'
STATE = HOME / '.local/state/poranna-prasa/receipt.json'
LOG = HOME / '.local/state/poranna-prasa/print.log'
MAX_PRN = 20_000_000


def note(message):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    record = f'{datetime.now().astimezone().isoformat(timespec="seconds")}  {message}'
    print(record, flush=True)
    with LOG.open('a', encoding='utf-8') as fh:
        fh.write(record + '\n')


def fetch(url: str, *, limit: int):
    req = Request(url, headers={'User-Agent':'PorannaPrasa-Android/0.1',
                                 'Cache-Control':'no-cache', 'Pragma':'no-cache'})
    with urlopen(req, timeout=20) as response:
        resolved = response.geturl()
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Plik przekracza dozwolony limit rozmiaru')
    return data, resolved


def same_host(base: str, final: str) -> bool:
    a, b = urlsplit(base), urlsplit(final)
    return (a.scheme == 'https' and b.scheme == 'https' and
            a.hostname == b.hostname)


def print_issue(base_url: str, printer_ip: str, port: int=9100, *,
                allow_demo=False, force=False, now=None,
                state_path=STATE) -> str:
    now = now or datetime.now(ZoneInfo('Europe/Warsaw'))
    day = now.date().isoformat()
    if not force and now.timetz().replace(tzinfo=None) >= time(7, 0):
        note('PO TERMINIE: po 07:00 nie drukuję automatycznie.')
        return 'late'
    base = base_url.rstrip('/') + '/'
    if not urlsplit(base).scheme == 'https':
        raise ValueError('Adres wydania musi używać HTTPS')

    raw, resolved = fetch(base + 'latest.json?ts=' + now.strftime('%Y%m%d%H%M'), limit=200_000)
    if not same_host(base, resolved):
        raise ValueError('Manifest przekierowano poza zaufaną domenę')
    manifest = json.loads(raw)
    if manifest.get('schema') != 1 or manifest.get('status') != 'ready':
        raise ValueError('Manifest wydania jest niekompletny')
    if manifest.get('date') != day or not manifest.get('issue_id', '').startswith(f'poranna-prasa-{day}'):
        note(f'BRAK NOWEGO WYDANIA: manifest={manifest.get("date")}, dzisiaj={day}')
        return 'not-ready'
    if manifest.get('is_demo') and not allow_demo:
        note('ODMOWA: manifest dotyczy wydania DEMO')
        return 'demo'
    issue_id = manifest['issue_id']
    state_path.parent.mkdir(parents=True, exist_ok=True)
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding='utf-8'))
            if state.get('issue_id') == issue_id and not force:
                note(f'POMINIĘTO DUPLIKAT: {issue_id}')
                return 'already-sent'
        except json.JSONDecodeError:
            pass

    filename = manifest.get('prn')
    if filename != 'gazeta.prn':
        raise ValueError('Nieoczekiwana nazwa PRN w manifeście')
    file_url = urljoin(base, filename) + '?ts=' + now.strftime('%Y%m%d%H%M')
    data, resolved = fetch(file_url, limit=MAX_PRN)
    if not same_host(base, resolved):
        raise ValueError('PRN przekierowano poza zaufaną domenę')
    if len(data) != manifest.get('prn_bytes'):
        raise ValueError('Nie zgadza się długość pliku PRN')
    digest = hashlib.sha256(data).hexdigest()
    if digest != manifest.get('prn_sha256'):
        raise ValueError('Niezgodna suma SHA256, odmawiam wydruku')
    if not data.startswith(b'\0' * 128) or b'@PJL ENTER LANGUAGE = PCL' not in data[:1000]:
        raise ValueError('Plik PRN nie wygląda na testowany format Brother')
    if not (1 <= int(manifest.get('pages', 0)) <= 8):
        raise ValueError('Niebezpieczna liczba stron')

    # A successful socket send proves delivery of bytes into TCP, NOT paper output.
    note(f'WYSYŁANIE: {issue_id}, stron={manifest["pages"]}, bytes={len(data)}')
    with socket.create_connection((printer_ip, port), timeout=9) as conn:
        conn.settimeout(25)
        conn.sendall(data)
    receipt = {'issue_id': issue_id, 'date': day, 'prn_sha256': digest,
               'sent_at': now.isoformat(), 'printer': printer_ip,
               'result': 'sent-to-tcp-not-physically-confirmed'}
    tmp = state_path.with_suffix('.tmp')
    tmp.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, state_path)
    note(f'OK: strumień wysłany do {printer_ip}:{port}; brak potwierdzenia fizycznego wydruku')
    return 'sent'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=CONFIG)
    parser.add_argument('--allow-demo', action='store_true')
    parser.add_argument('--force', action='store_true', help='For manual testing only; may reprint')
    args = parser.parse_args()
    if not args.config.exists():
        print(f'Brakuje konfiguracji: {args.config}', file=sys.stderr)
        return 2
    conf = json.loads(args.config.read_text(encoding='utf-8'))
    lockfile = STATE.parent / 'print.lock'
    lockfile.parent.mkdir(parents=True, exist_ok=True)
    try:
        with lockfile.open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            print_issue(conf['base_url'], conf['printer_ip'], conf.get('printer_port', 9100),
                        allow_demo=args.allow_demo, force=args.force)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as e:
        note(f'BŁĄD: {type(e).__name__}: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
