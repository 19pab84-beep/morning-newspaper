# Handoff do ChatGPT Work — Poranna Prasa V3.2
**Zadanie rozwojowe — nie uruchamiaj automatycznego druku w trakcie.**

Repo: https://github.com/19pab84-beep/morning-newspaper
Gałąź rozwojowa: `feature/editorial-v3-universe`
Gałąź produkcyjna: `main` — NIGDY nie nadpisuj bez wyraźnego zatwierdzenia.

## Co przeczytać na początku
1. `v3/docs/KONSTYTUCJA_PORANNEJ_PRASY.md`
2. `v3/docs/BIBLIA_GRAFICZNA.md`
3. `v3/docs/FOUR_PAGE_FOLIO_CONTRACT.md`
4. `v3/docs/DZIALY_I_ROTACJA.md`
5. `v3/editorial/AGENTS.md`
6. `v3/editorial/departments.yaml`

## Wynik, którego chcemy
Działający prototyp, który generuje **jeden pełny numer 4×A4**, w wyglądzie **zaakceptowanych fotorealistycznych, mocno gazetowych stron**, z czytelnymi polskimi artykułami, prawdziwą paginacją i obrazkowym komiksem.

**TWARDY LAYOUT:**
- Duże `PORANNA PRASA` wyłącznie na s. 1.
- s. 2 i 3 — mała, wąska pagina (strona, data, mała nazwa) bez powtórzenia dużego tytułu.
- s. 4 — bez winiety ani hasła „OSTATNIA STRONA”; po cienkim folio zaczyna się komiks.
- Wszystkie strony muszą mieć identyczny numer/data/rok; żadnych sprzecznych `NR 006`/`NR 007`.
- Minimum 300 dpi pionowo dla strony A4, czytelne polskie znaki; wynik PDF = dokładnie 4 pojedyncze strony (nie kolaż).

**TWARDY REDAKCYJNY:**
- 1 oryginalny niepokojący reportaż fikcyjny (Puls Nocy), 2–3 konkretne materiały z innych DZIAŁÓW, 5–8 rotujących RUBRYK, czasem 0 zwykłych wiadomości.
- Rotacja katalogu 32 działów/128 rubryk; sprawdzaj historię poprzednich numerów.
- Odrzucaj teksty ogólnikowe i fałszywe źródła; rzeczywistych ludzi nie cytuj fikcyjnie.
- Prywatna biblia fabularna, spoilery i rozwiązania wskazówek NIE mogą zostać umieszczone w publicznym repozytorium.
- Komiks s. 4 jako prawdziwy rysunek z 3–4 kadrami i czytelnymi dymkami; sudoku tylko 9×9, dokładnie jedno rozwiązanie.

## Plan pracy
1. Audyt starego generatora, rendererów, katalogu, testów i braków.
2. Stwórz **silnik składu/asset pipeline**; wypracuj art direction, żeby wynik papierowy wyglądał jak zaakceptowane wizualizacje, a nie biały PDF. Wybierz ścieżkę „4 obrazy + korekta typografii” lub „hybryda obrazów + prawdziwy tekst”, która spełnia obie strony wymagania. Opisz kompromisy.
3. Zbuduj mechanizm `story_id → rzeczywista_strona` i automatyczne nadawanie odsyłaczy, jednego issue_no/date i cross-page QA.
4. Zbuduj generator rubryk + testy rotacji, weryfikacji źródeł, komiksu oraz sudoku 9×9.
5. Połącz z prywatnym magazynem continuity (nie kopiuj spoilerów do publicznego repo).
6. Wygeneruj 3 różne pełne numery. **Zrenderuj i obejrzyj każdy z czterech arkuszy** i popraw wszystkie wykryte wady.
7. Wyprodukuj pliki PDF + źródłowe assety + raport QA (co przeszło, co nie). Kod zapisz na gałęzi rozwojowej; wydania, assety i raport QA na prywatnym Google Drive. Daj do akceptacji; nie merge'uj do `main` bez zgody.

## Granice
**Nie ruszaj** działającego drukowania Brother HL-1210WE: GitHub Actions, Pages, Android/Termux, Tasker, warunek domowej sieci, cel 07:00. To jest odrębny i działający system; przełączenie na V3 dopiero po fizycznym wydruku zatwierdzonego numeru.
Nie zakładaj, że agent może działać samodzielnie każdego dnia bez konfiguracji: runtime docelowy to GitHub Actions + API z sekretem, za które mogą być naliczane koszty. Work jest miejscem do realizacji projektu, nie automatycznie nowym serwerem do drukowania.

## Kryterium akceptacji
Użytkownik zestawia 4 strony nowego PDF z zaakceptowanymi wizualizacjami i mówi: **„To wygląda jak ta sama gazeta”**. Dokładnie 4 strony A4; okładka jedyna z dużą winietą; s. 3 bez wielkiego nagłówka; s. 4 bez nagłówka, z komiksem od razu u góry; treść realnie ciekawa i konkretna; wszystko spójne numerycznie i fabularnie.

## Magazyn materiałów — aktualizacja 13.10.2026

GitHub stores generator code, tests, non-secret configuration and technical documentation only.
Google Drive stores manuscripts, source/evidence packets, generated illustrations, fonts with licenses,
PDF/PNG/JPG/PRN editions, QA reports, private canon, ledger revisions and puzzle solutions.
Do not commit edition-specific text, images or reports, including text embedded in authoring scripts.
Do not upload private files as public Actions artifacts or publish them on Pages.

Extract Drive materials outside the checkout. Set `PORANNA_PRASA_ASSETS` to the extracted
`assets` directory and optionally `PORANNA_PRASA_PILOTS` to `editions` for integration tests.
`--input`, `--private-state` and `--output` must point outside the checkout.
Drive folders remain owner-private. Credentials and folder IDs are runtime configuration,
never hard-coded in public source. Sync changed canon and revisions back to the same private
Drive location after an approved run; the offline generator does not perform Drive uploads.

Production `main` and automatic printing remain unchanged pending separate acceptance.
