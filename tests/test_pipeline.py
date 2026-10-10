import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
sys.path.insert(0, str(ROOT/'android'))

from news import clean, stable_id, parse_feed_xml, published_at, collect
import print_latest as phone


class DummySocket:
    def __init__(self):
        self.sent = b''
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def settimeout(self, n): pass
    def sendall(self, data): self.sent += data


class TestNews(unittest.TestCase):
    def test_rss(self):
        rss = b'<rss version="2.0"><channel><item><title>Test &amp; news</title>' \
              b'<link>https://example.com/abc</link><description>A &amp; B</description>' \
              b'<pubDate>Sat, 10 Oct 2026 05:00:00 GMT</pubDate></item></channel></rss>'
        items = parse_feed_xml(rss)
        self.assertEqual(len(items),1)
        self.assertEqual(clean(items[0]['title']), 'Test & news')
        dt = published_at(items[0], datetime.now(ZoneInfo('UTC')))
        self.assertEqual(dt.isoformat(), '2026-10-10T05:00:00+00:00')
        self.assertEqual(stable_id('a','https://x'), stable_id('b','https://x'))

    def test_atom(self):
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry>' \
               b'<title>News</title><link href="https://example.com/2"/>' \
               b'<updated>2026-10-10T06:00:00Z</updated></entry></feed>'
        self.assertEqual(parse_feed_xml(atom)[0]['link'], 'https://example.com/2')


class TestAndroid(unittest.TestCase):
    def manifest(self, today, prn):
        return {'schema':1, 'status':'ready', 'date':today,
                'issue_id':f'poranna-prasa-{today}', 'prn':'gazeta.prn',
                'prn_bytes':len(prn), 'prn_sha256':hashlib.sha256(prn).hexdigest(),
                'pages':5, 'is_demo':False}

    def run_case(self, manifest_adjust=None, date_shift=False):
        now = datetime(2026,10,10,6,40,tzinfo=ZoneInfo('Europe/Warsaw'))
        prn = b'\0'*128 + b'@PJL ENTER LANGUAGE = PCL' + b'END'
        m = self.manifest(now.date().isoformat(), prn)
        if manifest_adjust:
            m.update(manifest_adjust)
        url = 'https://example.github.io/poranna-prasa/'
        resps = [(json.dumps(m).encode(), url+'latest.json'), (prn, url+'gazeta.prn'), (json.dumps(m).encode(), url+'latest.json')]
        sock = DummySocket()
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)/'receipt.json'
            with patch.object(phone, 'fetch', side_effect=resps) as fetcher, \
                 patch.object(phone.socket, 'create_connection', return_value=sock), \
                 patch.object(phone, 'note'):
                status = phone.print_issue(url,'192.168.101.9',now=now,state_path=state)
                if status == 'sent':
                    self.assertTrue(state.exists())
                    self.assertEqual(phone.print_issue(url,'192.168.101.9',now=now,state_path=state), 'already-sent')
                else:
                    self.assertFalse(state.exists())
            return status, sock.sent

    def test_success_once(self):
        status, sent = self.run_case()
        self.assertEqual(status, 'sent')
        self.assertGreater(len(sent), 140)

    def test_old_issue(self):
        status, sent = self.run_case({'date':'2026-10-09'})
        self.assertEqual(status, 'not-ready')
        self.assertEqual(sent, b'')

    def test_demo_blocked(self):
        status, sent = self.run_case({'is_demo':True})
        self.assertEqual(status,'demo')
        self.assertEqual(sent,b'')

    def test_bad_checksum(self):
        with self.assertRaises(ValueError):
            self.run_case({'prn_sha256':'bad'})

    def test_https_required(self):
        with self.assertRaises(ValueError):
            phone.print_issue('http://insecure.example','127.0.0.1',now=datetime(2026,10,10,6,40,tzinfo=ZoneInfo('Europe/Warsaw')))

    def test_after_deadline(self):
        with patch.object(phone, 'note'):
            now = datetime(2026,10,10,7,1,tzinfo=ZoneInfo('Europe/Warsaw'))
            self.assertEqual(phone.print_issue('https://example.github.io/prasa','127.0.0.1',now=now), 'late')

if __name__=='__main__':
    unittest.main()
