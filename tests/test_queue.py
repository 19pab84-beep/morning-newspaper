import hashlib,json,sys,tempfile,unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'android'))
import print_latest as phone

class Socket:
    def __init__(self):self.sent=b''
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def settimeout(self,*args):pass
    def sendall(self,data):self.sent+=data

class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.now=datetime(2026,10,14,6,35,tzinfo=ZoneInfo('Europe/Warsaw'))
        self.conf={'local_queue':str(self.root),'printer_ip':'192.168.101.9'}
        self.day=self.root/'2026-10-14';self.day.mkdir()
        self.prn=b'\0'*128+b'@PJL ENTER LANGUAGE = PCL'+b'TEST'
        self.manifest={'schema':1,'status':'ready','date':'2026-10-14','issue_id':'poranna-prasa-2026-10-14-v3-001','prn':'gazeta.prn','prn_bytes':len(self.prn),'prn_sha256':hashlib.sha256(self.prn).hexdigest(),'pages':4,'is_demo':False}
        (self.day/'gazeta.prn').write_bytes(self.prn);self.save()
    def tearDown(self):self.tmp.cleanup()
    def save(self):(self.day/'latest.json').write_text(json.dumps(self.manifest))
    def run_case(self,*,away=False,now=None):
        self.sock=Socket()
        with patch.object(phone,'home_network_available',return_value=not away),patch.object(phone,'fetch',side_effect=AssertionError('No network download')),patch.object(phone.socket,'create_connection',return_value=self.sock),patch.object(phone,'note'):
            return phone.print_configured(self.conf,now=now or self.now,state_path=self.root/'receipt.json')
    def test_sends_once_without_network_download(self):
        self.assertEqual(self.run_case(),'sent');self.assertEqual(self.sock.sent,self.prn)
        self.assertEqual(self.run_case(),'already-sent');self.assertEqual(self.sock.sent,b'')
    def test_away_and_late_never_send(self):
        self.assertEqual(self.run_case(away=True),'away');self.assertEqual(self.sock.sent,b'')
        self.assertEqual(self.run_case(now=self.now.replace(hour=7)),'late');self.assertEqual(self.sock.sent,b'')
    def test_no_future_or_stale_fallback(self):
        self.assertEqual(self.run_case(now=self.now.replace(day=13)),'not-ready')
        self.assertEqual(self.run_case(now=self.now.replace(day=15)),'not-ready')
    def test_corrupted_bytes_and_demo_rejected(self):
        (self.day/'gazeta.prn').write_bytes(self.prn+b'bad')
        with self.assertRaises(ValueError):self.run_case()
        (self.day/'gazeta.prn').write_bytes(self.prn);self.manifest['is_demo']=True;self.save()
        self.assertEqual(self.run_case(),'demo')
    def test_symlink_escape_rejected(self):
        (self.day/'gazeta.prn').unlink();outside=self.root/'other.prn';outside.write_bytes(self.prn);(self.day/'gazeta.prn').symlink_to(outside)
        with self.assertRaises(ValueError):self.run_case()
if __name__=='__main__':unittest.main()
