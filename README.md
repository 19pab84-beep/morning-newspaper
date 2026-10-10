# PORANNA PRASA 🗞️

Automatyczna, czarno-biała gazeta A4: **GitHub Actions (RSS + opcjonalny OpenAI API) → PDF + PRN → GitHub Pages → Android/Termux/Tasker → Brother HL-1210WE**.

**Stan v0.1:** generator i konwerter działają w testach lokalnych. Użytkownik wcześniej fizycznie wydrukował pojedynczą stronę przygotowaną przez konwerter Linux oraz plik PRN wysłany przez Android. **Nie przetestowano jeszcze wielostronicowego wydruku w pełni bezobsługowego na zablokowanym Androidzie ani rzeczywistego uruchomienia workflow w GitHub.**

## Harmonogram (Europe/Warsaw)

- **05:17** – pierwsza próba przygotowania wydania w chmurze.
- **05:47** – zapasowa próba, jeśli dzisiejsze `latest.json` nie jest opublikowane.
- **06:35, 06:45, 06:55** – Android sprawdza numer; drukuje tylko raz.
- **07:00** – docelowa godzina, do której papier ma być gotowy.

GitHub Actions nie gwarantuje uruchomienia co do minuty, a Android potrafi ograniczać zadania w tle. **Nie jest to gwarancja wydruku o 07:00.** Zadania zaplanowano z zapasem; warto sprawdzić pierwsze 3–5 poranków. GitHub cron wspiera `timezone: Europe/Warsaw`, więc zmiana czasu PL jest automatyczna.

## A. Wdrożenie na GitHub

Repozytorium: **https://github.com/19pab84-beep/morning-newspaper** (publiczne).

1. Otwórz **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. (Opcjonalnie) W **Settings → Secrets and variables → Actions → New repository secret** dodaj `OPENAI_API_KEY`. Klucz API jest **płatny niezależnie** od ChatGPT; bez klucza generator działa w wersji RSS, bez redakcji AI.
3. Wejdź w **Actions → Poranna Prasa — codzienne wydanie → Run workflow** i obserwuj zadania `build` oraz `deploy`.
4. Otwórz **https://19pab84-beep.github.io/morning-newspaper/** i **https://19pab84-beep.github.io/morning-newspaper/latest.json**. Te adresy zaczną działać dopiero po pierwszym udanym wdrożeniu.
5. Jeśli użyjesz własnej domeny, ustaw Actions Variable `PRESS_BASE_URL` na jej adres bazowy i zmień konfigurację Androida.

**Prywatność:** gazeta oraz lista źródeł są dostępne publicznie przez GitHub Pages. Nie publikuj w nich danych prywatnych. GitHub Actions może uruchomić zadania z opóźnieniem albo wyłączyć harmonogram przy dłuższej bezczynności repozytorium.

## B. Android z Taskerem i Termux:Tasker

Przyjmujemy, że Termux i Python masz już z testów komunikacji z drukarką. **W Termuxie Python może nie znaleźć `Europe/Warsaw`; `android/setup.sh` automatycznie instaluje pakiet `tzdata`, który rozwiązuje ten problem.** Jeśli instalacja była wykonana przed tą poprawką, uruchom `python -m pip install tzdata` i ponów test drukowania. Instaluj **Termux:Tasker z tego samego źródła co Termux** (F-Droid z F-Droid; nie mieszaj podpisów APK). Przyda się [Tasker](https://tasker.joaoapps.com/) (płatny) oraz [Termux:Tasker](https://f-droid.org/packages/com.termux.tasker/).

1. Zainstaluj **Termux:Tasker**, **Tasker** i nadaj uprawnienia opisane poniżej.
2. W Termux sklonuj repozytorium:

   ```bash
   pkg install python git
   cd ~
   git clone https://github.com/19pab84-beep/morning-newspaper.git
   bash ~/morning-newspaper/android/setup.sh "https://19pab84-beep.github.io/morning-newspaper" 192.168.101.9
   ```

3. Android → Ustawienia → Aplikacje → **Tasker → Uprawnienia → Dodatkowe uprawnienia → Run commands in Termux environment**. Zapewnij Termux i Tasker uprawnienia pracy w tle; nie wyłączaj automatyzacji oszczędzaniem baterii.
4. Tasker → **Profiles → + → Time**, utwórz **3 osobne zadania** uruchamiane o **06:35, 06:45 i 06:55**, codziennie. W zadaniu: **Plugin → Termux:Tasker → Executable: `print_edition` → Execute in a terminal session: OFF** (działanie w tle). Dla czasu ustaw start równy godzinie zadania lub użyj zdarzenia uruchamiającego o wskazanej godzinie w swojej wersji Taskera.
5. Przetestuj ręcznie (po publikacji pierwszego aktualnego numeru):

   ```bash
   python ~/morning-newspaper/android/print_latest.py --force
   ```

   `--force` służy **tylko do ręcznego testowania**; może wydrukować duplikat. Normalny harmonogram go nie używa.
6. Zablokuj ekran i ręcznie uruchom zadanie w Taskerze. Powtórz test w kolejne poranki. W przypadku zmiany IP drukarki edytuj `~/.config/poranna-prasa/config.json` (albo ponownie uruchom `setup.sh`). Rozważ rezerwację IP `192.168.101.9` w DHCP routera.

Wynik i błędy zapisują się w `~/.local/state/poranna-prasa/print.log`; informacja o ostatnim wysłanym wydaniu w `receipt.json`. Potwierdzenie oznacza **wysłanie do TCP 9100**, a nie fizyczne potwierdzenie papieru w zasobniku.

**Ważne:** Telefon musi być w zasięgu domowego Wi‑Fi, mieć dostęp do GitHub Pages, a drukarka musi być włączona i mieć papier/toner. Jeśli o 06:55 nie ma jeszcze aktualnego wydania, telefon go nie wydrukuje — nie drukuje automatycznie po 07:00.

## C. Zasady redakcyjne

- `config.yaml` – źródła RSS, rubryki, limity wiadomości, model AI.
- `src/news.py` – RSS, weryfikacja dat, selekcja, eliminacja powtórek na podstawie ID ostatnich 120 artykułów.
- `src/layout.py` – dwukolumnowy układ A4 bez kolorowego tła.
- `src/build_prn.py` – konwersja PDF → PBM/600 DPI → rastrowy strumień do Brothera, zgodny z **wcześniej sprawdzonym jednostronicowym testem**; do testowania przy druku wielostronicowym.
- `src/build.py` – całościowa produkcja PDF, PRN, `latest.json` i strony źródeł.
- `.github/workflows/daily.yml` – harmonogram publikowania.
- `android/print_latest.py` – HTTPS, SHA-256, limit 20 MB, bieżąca data, blokada demo i duplikatów.

Generator nie publikuje wydania, jeśli zbierze mniej niż **9 aktualnych** tematów, nie pozwala przekroczyć **8 stron** i nie podszywa się pod wiadomości w trybie demo. Źródła są wydrukowane przy każdym artykule i klikane w PDF/na stronie WWW. AI parafrazuje **wyłącznie** otrzymane streszczenia RSS; to nie jest pełny fact-check oryginalnych artykułów. Jeśli temat jest ważny, sprawdź oryginalny materiał.

Uwaga: nie każda wiadomość ma RSS z wiarygodną datą. Takie pozycje są pomijane. Nie wszystkie zewnętrzne kanały RSS gwarantują trwałość adresów; błędy widać w logach GitHub Actions.

## D. Lokalne testy generatora

Ubuntu/Linux, Python 3.12+, Ghostscript (`gs`), `fonts-dejavu-core`:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/build.py --demo --date 2026-10-10 --output demo/public
# prawdziwy numer (RSS; z AI jeśli ustawiono OPENAI_API_KEY):
python src/build.py --output public
```

**Nie publikuj plików z `--demo` jako bieżącej gazety.** Android z harmonogramu i tak odrzuci taki manifest.

## Co dalej po MVP

- Archiwum PDF na Drive / prywatnym magazynie (v0.1 publikuje **tylko aktualne wydanie**).
- Dziennik dostarczenia i powiadomienie o awarii zadania.
- Wyrównanie objętości do stałych 4–6 stron i bogatsza oprawa redakcyjna.
- Kuracja tematów na podstawie Twojej oceny każdego numeru.

## Licencja

Kod w projekcie GPL-2.0-or-later, ponieważ konwerter interpretuje format z projektu [brlaser](https://github.com/pdewacht/brlaser) (GPL). Dane ze źródeł RSS należą do odpowiednich wydawców; generator używa krótkich opisów / własnych streszczeń, nie pełnych tekstów artykułów.
