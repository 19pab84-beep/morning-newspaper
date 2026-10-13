# Private local print queue

A prepared edition is downloaded from owner-private Drive to Android the evening before.
`android/install_local_queue.py` installs the dated PRN and manifest outside the checkout,
preserves printer/network settings, backs up configuration and the Tasker entrypoint,
and points `print_edition` at a local copy of the sender. Installation does not print.

The existing Tasker profile remains at 06:35/06:45/06:55 Europe/Warsaw. The sender
uses the existing date, checksum, size, LAN, 07:00 deadline and duplicate gates.
Local queue mode never falls back to the public RSS edition. A missing daily
package yields no print. This is prepared delivery, not autonomous AI generation.

The package must contain `print_latest.py`, `install_local_queue.py`, and
`queue/YYYY-MM-DD/{latest.json,gazeta.prn}`. It excludes canon and puzzle solutions.
The manifest is schema 1, status ready, is_demo false, 4 pages, a dated
`poranna-prasa-YYYY-MM-DD...` ID, byte count and SHA256 for gazeta.prn.

Install from the extracted package: `python install_local_queue.py`.
Use `python ~/.local/share/poranna-prasa/print_latest.py --check-queue`
to inspect integrity without any printer connection. Do not run `--force` to
verify installation. Normal scheduled printing refuses future or old editions.

To restore the prior source, copy `config.before-local-queue.json` over config.json
and `print_edition.before-local-queue` over print_edition in their original folders.
Restore only if those backups exist; do not delete receipt.json.

Long-term automation still needs private Drive access for Actions and Android,
API credentials, source retrieval, new illustration production and tested delivery.
No production Pages workflow is changed by this prepared-queue installation.
