#!/usr/bin/env python3
"""Android/Termux fetch+TCP sender; refuses stale/demo/duplicate issues.
Uses only Python stdlib. GPL-2.0-or-later.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import ipaddress
import json
import os
import socket
import sys
from datetime import datetime, time
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

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


def home_network_available(printer_ip: str, port: int = 9100, home_subnet: str | None = None) -> bool:
    """Require a locally routed IPv4 address in the home subnet AND a reachable printer.

    The UDP connect only inspects the chosen local route; it sends no data.
    A TCP connect is then used as a short reachability check (no print data).
    This deliberately fails closed on mobile data or other Wi-Fi networks.
    """
    net = ipaddress.ip_network(home_subnet or f'{printer_ip}/24', strict=False)
    ip = ipaddress.ip_address(printer_ip)
    if net.version != 4 or ip not in net:
        raise ValueError('Adres drukarki nie nalezy do skonfigurowanej sieci domowej')

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as route:
            route.connect((printer_ip, port))
            local_ip = ipaddress.ip_address(route.getsockname()[0])
        if local_ip not in net:
            return False
        with socket.create_connection((printer_ip, port), timeout=3):
            return True
    except (OSError, ValueError):
        return False


def print_issue(base_url: str, printer_ip: str, port: int=9100, *,
                allow_demo=False, force=False, now=None,
                state_path=STATE, home_subnet=None, fetcher=None) -> str:
    if now is None:
        try:
            now = datetime.now(ZoneInfo('Europe/Warsaw'))
        except ZoneInfoNotFoundError as exc:
            raise ValueError('Brak bazy stref czasowych w Termuxie. Uruchom: python -m pip install tzdata') from exc
    fetcher = fetcher or fetch
    day = now.date().isoformat()
    if not force and now.timetz().replace(tzinfo=None) >= time(7, 0):
        note('PO TERMINIE: po 07:00 nie drukuję automatycznie.')
        return 'late'
    base = base_url.rstrip('/') + '/'
    if not urlsplit(base).scheme == 'https':
        raise ValueError('Adres wydania musi używać HTTPS')

    # No download, no connection and no print outside the home LAN.
    # --force does NOT override this restriction.
    if not home_network_available(printer_ip, port, home_subnet):
        note('POZA DOMEM: brak lokalnego polaczenia z drukarka; pomijam wydruk.')
        return 'away'

    raw, resolved = fetcher(base + 'latest.json?ts=' + now.strftime('%Y%m%d%H%M'), limit=200_000)
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
    data, resolved = fetcher(file_url, limit=MAX_PRN)
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


def local_queue_fetch(folder):
    """Read only the two expected files; keep the same manifest/PRN validation."""
    folder = Path(folder).resolve()
    def read(url, *, limit):
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.netloc != 'local-queue.invalid':
            raise ValueError('Nieprawidłowy adres kolejki')
        name = parsed.path.lstrip('/')
        if name not in ('latest.json', 'gazeta.prn'):
            raise ValueError('Nieoczekiwany plik kolejki')
        path = (folder / name).resolve()
        if path.parent != folder:
            raise ValueError('Plik kolejki wychodzi poza katalog')
        with path.open('rb') as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError('Plik przekracza dozwolony limit rozmiaru')
        return data, url
    return read


def print_configured(conf, *, allow_demo=False, force=False, now=None, state_path=STATE):
    """Private local queue mode does not fall back to the public RSS edition."""
    if 'local_queue' not in conf:
        return print_issue(conf['base_url'], conf['printer_ip'], conf.get('printer_port', 9100),
                           allow_demo=allow_demo, force=force, now=now, state_path=state_path,
                           home_subnet=conf.get('home_subnet'))
    now = now or datetime.now(ZoneInfo('Europe/Warsaw'))
    folder = Path(conf['local_queue']) / now.date().isoformat()
    if not (folder/'latest.json').is_file():
        note('BRAK NOWEGO WYDANIA: prywatna kolejka nie zawiera dzisiejszego numeru.')
        return 'not-ready'
    return print_issue('https://local-queue.invalid', conf['printer_ip'], conf.get('printer_port', 9100),
                       allow_demo=allow_demo, force=force, now=now, state_path=state_path,
                       home_subnet=conf.get('home_subnet'), fetcher=local_queue_fetch(folder))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=CONFIG)
    parser.add_argument('--allow-demo', action='store_true')
    parser.add_argument('--force', action='store_true', help='For manual testing only; may reprint')
    parser.add_argument('--check-queue', action='store_true', help='Verify queued manifest and SHA256 without printer connection')
    args = parser.parse_args()
    if not args.config.exists():
        print(f'Brakuje konfiguracji: {args.config}', file=sys.stderr)
        return 2
    conf = json.loads(args.config.read_text(encoding='utf-8'))
    if args.check_queue:
        folder=Path(conf['local_queue'])
        for manifest_path in sorted(folder.glob('*/latest.json')):
            m=json.loads(manifest_path.read_text())
            data=(manifest_path.parent/'gazeta.prn').read_bytes()
            if m.get('schema')!=1 or m.get('status')!='ready' or m.get('is_demo') or m.get('pages')!=4:
                raise ValueError('Nieprawidłowy manifest kolejki')
            if m['date']!=manifest_path.parent.name or not m['issue_id'].startswith('poranna-prasa-'+m['date']):
                raise ValueError('Nieprawidłowa data kolejki')
            if len(data)>MAX_PRN or len(data)!=m['prn_bytes'] or hashlib.sha256(data).hexdigest()!=m['prn_sha256']:
                raise ValueError('Nieprawidłowy PRN kolejki')
            print('GOTOWE:',m['date'],'4 strony; SHA256 OK; niczego nie wysłano do drukarki')
        return 0
    lockfile = STATE.parent / 'print.lock'
    lockfile.parent.mkdir(parents=True, exist_ok=True)
    try:
        with lockfile.open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            print_configured(conf, allow_demo=args.allow_demo, force=args.force)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as e:
        note(f'BŁĄD: {type(e).__name__}: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
