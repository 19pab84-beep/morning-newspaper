#!/data/data/com.termux/files/usr/bin/bash
set -eu

# Usage: bash ~/morning-newspaper/android/setup.sh https://LOGIN.github.io/morning-newspaper 192.168.101.9
if [ "$#" -lt 1 ]; then
  echo "Użycie: bash android/setup.sh https://LOGIN.github.io/morning-newspaper [IP_DRUKARKI]"
  exit 1
fi
URL="${1%/}"
IP="${2:-192.168.101.9}"
case "$URL" in https://*) ;; *) echo 'Podaj adres HTTPS do GitHub Pages'; exit 1;; esac
mkdir -p "$HOME/.config/poranna-prasa" "$HOME/.termux/tasker" "$HOME/.local/state/poranna-prasa"
export URL IP
python - <<'PY'
import json, os
from pathlib import Path
Path.home().joinpath('.config/poranna-prasa/config.json').write_text(
    json.dumps({'base_url':os.environ['URL'], 'printer_ip':os.environ['IP'], 'printer_port':9100}, indent=2),
    encoding='utf-8')
PY
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cat > "$HOME/.termux/tasker/print_edition" <<'TASK' 
#!/data/data/com.termux/files/usr/bin/bash
exec /data/data/com.termux/files/usr/bin/python "__SCRIPT_PATH__"
TASK
sed -i "s|__SCRIPT_PATH__|$SCRIPT_DIR/print_latest.py|" "$HOME/.termux/tasker/print_edition"
chmod 700 "$HOME/.termux" "$HOME/.termux/tasker" "$HOME/.termux/tasker/print_edition"
echo 'OK. W Tasker -> Plugin -> Termux:Tasker -> Executable: print_edition; Background: ON.'
echo 'Ręczny test (o dowolnej porze): python ~/poranna-prasa/android/print_latest.py --force'
