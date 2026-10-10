"""Return 1 when today's edition exists, 0 when missing or offline; GPL-2.0-or-later."""
from datetime import datetime
import sys
from zoneinfo import ZoneInfo
import requests

if __name__ == '__main__':
    url = sys.argv[1].rstrip('/') + '/latest.json'
    try:
        r = requests.get(url, timeout=12, headers={'Cache-Control': 'no-cache'},
                         params={'fresh':datetime.now(ZoneInfo('Europe/Warsaw')).strftime('%Y%m%d%H%M')})
        r.raise_for_status()
        issue = r.json()
        if issue.get('date') == datetime.now(ZoneInfo('Europe/Warsaw')).date().isoformat() and not issue.get('is_demo'):
            print('Dzisiejszy numer jest już opublikowany; pomijam.')
            sys.exit(1)
    except (requests.RequestException, ValueError):
        pass
    print('Brak dzisiejszego numeru, przygotowuję wydanie.')
    sys.exit(0)
