#!/usr/bin/env python3
"""Install a private dated queue alongside the existing Termux/Tasker setup.
This installer never sends print bytes. The package contains no private canon.
"""
from pathlib import Path
import hashlib,json,os,shlex,shutil,sys

def install(package,task_home):
    package=Path(package).resolve();task_home=Path(task_home).resolve()
    confpath=task_home/'.config/poranna-prasa/config.json'
    if not confpath.is_file():
        raise ValueError('Brak istniejącej konfiguracji Porannej Prasy w Termuxie')
    conf=json.loads(confpath.read_text())
    if not conf.get('printer_ip'):
        raise ValueError('Brak adresu drukarki w istniejącej konfiguracji')
    days=list((package/'queue').glob('*/latest.json'))
    if not days:raise ValueError('Pakiet nie zawiera numeru gazety')
    for mp in days:
        m=json.loads(mp.read_text());data=(mp.parent/'gazeta.prn').read_bytes()
        if m.get('schema')!=1 or m.get('status')!='ready' or m.get('is_demo') or m.get('pages')!=4:
            raise ValueError('Nieprawidłowy manifest numeru')
        if mp.parent.name!=m.get('date') or m.get('prn')!='gazeta.prn' or not m.get('issue_id','').startswith('poranna-prasa-'+m['date']):
            raise ValueError('Nieprawidłowa data lub identyfikator numeru')
        if len(data)>20_000_000 or len(data)!=m['prn_bytes'] or hashlib.sha256(data).hexdigest()!=m['prn_sha256']:
            raise ValueError('Pakiet PRN jest uszkodzony')
    backup=confpath.with_name('config.before-local-queue.json')
    if not backup.exists():shutil.copy2(confpath,backup)
    queue=task_home/'.local/share/poranna-prasa/queue';queue.mkdir(parents=True,exist_ok=True)
    for mp in days:
        dest=queue/mp.parent.name;dest.mkdir(exist_ok=True)
        for name in ('gazeta.prn','latest.json'):
            target=dest/name
            if target.exists() and target.read_bytes()!=(mp.parent/name).read_bytes():
                raise ValueError('Istnieje inny numer z tą datą; nie zastępuję go automatycznie')
            shutil.copy2(mp.parent/name,target);target.chmod(0o600)
    code=queue.parent/'print_latest.py';shutil.copy2(package/'print_latest.py',code);code.chmod(0o600)
    conf['local_queue']=str(queue)
    confpath.write_text(json.dumps(conf,ensure_ascii=False,indent=2)+'\n');confpath.chmod(0o600)
    task=task_home/'.termux/tasker/print_edition';task.parent.mkdir(parents=True,exist_ok=True)
    task_backup=task.with_name('print_edition.before-local-queue')
    if task.exists() and not task_backup.exists():shutil.copy2(task,task_backup)
    task.write_text('#!'+str(Path(sys.executable).parent/'bash')+'\nexec '+shlex.quote(sys.executable)+' '+shlex.quote(str(code))+' "$@"\n');task.chmod(0o700)
    print('KOLEJKA GOTOWA:',', '.join(mp.parent.name for mp in days))
    print('Tasker nadal używa print_edition. Nie uruchomiono drukowania.')
    print('Tryb kolejki: brak dzisiejszego pakietu oznacza brak wydruku; nie wraca do RSS.')
    print('Sprawdzenie bez druku: python '+shlex.quote(str(code))+' --check-queue')

if __name__=='__main__':
    try:install(Path(__file__).resolve().parent,Path.home())
    except (OSError,ValueError,KeyError) as error:sys.exit(str(error))
