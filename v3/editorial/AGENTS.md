# Redakcja agentowa — kontrakty, nie „agent zna wszystko”

**Status:** zaprojektowana orkiestracja i walidatory, niepodłączona jeszcze do produkcyjnego API. Odpalanie na GitHub Actions wymaga klucza API, magazynu prywatnego lore i testów kosztów. Działająca gałąź `main` nie jest modyfikowana.

## Zasady nadrzędne (obowiązkowe przed każdym wydaniem)

Przed generowaniem **zawsze** przeczytaj: `../docs/KONSTYTUCJA_PORANNEJ_PRASY.md`, `../docs/FOUR_PAGE_FOLIO_CONTRACT.md`, `../docs/DZIALY_I_ROTACJA.md`, a następnie katalog `departments.yaml`. W razie sprzeczności nadrzędna jest **konstytucja**, a w sprawach paginacji kontrakt **dokładnie 4 stron A4**.

Każdy agent musi znać różnicę między działem a rubryką, bieżący zestaw tematów i źródła. **Autorytet graficzny: `../docs/BIBLIA_GRAFICZNA.md`.** Przygotuj **cztery faktyczne strony A4** w zaakceptowanym, realistycznym looku starej gazety; dopuszczalne są pełnostronicowe obrazy sklejone w PDF, jeśli tekst i łamigłówki zostaną poprawione i zweryfikowane. **Tylko s. 1 ma duże „PORANNA PRASA”. Na s. 2 i 3 tylko wąska pagina; na s. 4 również tylko drobny folio, natychmiast komiks.** Cztery obrazy mają mieć identyczny numer, datę i continuity.

## 8 ról i ścisła kolejność

| Agent | Wejście | Wyjście | Twardy warunek |
|---|---|---|---|
| 1. Redaktor prowadzący | preferencje, katalog rubryk, ostatnie 30 numerów | `issue_plan.json` (kąty, dokładnie 4 str. A4, budżety słów, rubryki) | minimum 4 rotujące rubryki, brak przymusowych newsów |
| 2. Archiwista kanonu | prywatne `canon.yaml`, `ledger.json`, `arcs.yaml`, poprzednie numery | kontekst z ID faktów, **tylko ustalone informacje** | nie pisze jeszcze tekstu, nie zmienia kanonu |
| 3. Reporter badawczy | plan tekstów realnych i źródła | `source_packets.json` z faktami i URL | wątpliwe fakty → pomiń / oznacz jako opinię; żadne wymyślone cytaty realnych ludzi |
| 4. Autorzy | plan, pakiety źródeł, oczekiwana długość | artykuły w 4 typach | 2–4 **konkretne** przykłady / nazwy / mechaniki na tekst; fikcja w stylu Puls Nocy |
| 5. Kontroler fabuły | wszystkie artykuły + kanon + graf zależności | lista błędów continuity, proponowane poprawki | nie ujawnia wiedzy z przyszłych numerów; nie naprawia sprzeczności po cichu |
| 6. Mistrz zagadek | scenariusz sezonu, lista tropów, redagowane rubryki | 1–3 dopuszczone tropy + prywatne rozwiązania | każdy trop ma ID, nośnik, późniejszy payoff i sposób sprawdzenia; brak przypadkowych szyfrów |
| 7. Redaktor językowy | kompletny numer i źródła | spójne teksty, krótkie leady, nienadmuchane akapity | wycina uogólnienia; jeden artykuł = jedna wyraźna teza / śledztwo |
| 8. Łamacz i kontroler druku | zatwierdzony pakiet artykułów | 4 grafiki A4 lub złożony PDF, kontrola typografii, finalny PDF, PRN i manifest | **wielka winieta tylko na s. 1**, 2–3 bez niej, s. 4 bez dużego nagłówka, spójne data/numer/odsyłacze, 4×A4, sudoku 9×9 o jednym rozwiązaniu, narysowany komiks |

## Rozdział prywatnej prawdy od gazety

- `world/canon.yaml`, `world/arcs.yaml`, `world/clues.json` i `world/ledger.json` to **PRIVATE**, zawierają spoilery i nie mogą trafić do publicznego repozytorium ani GitHub Pages.
- Gazeta i PDF zawierają **prawdę redakcyjną**, która może być niepełna lub celowo błędna fabularnie, ale nie może kłamać o rzeczywistych wydarzeniach, realnych osobach czy realnych instytucjach.
- Wewnętrzne stany `secret_truth`, `editorial_belief` i `published_claim` muszą być osobnymi polami.
- Na papierze: **maksymalnie 1 jawna i 2 subtelne wskazówki**. Nie wszystkie rubryki powinny być elementami zagadki.
- Możliwa zaplanowana sprzeczność otrzymuje `contradiction_id` i wyjaśnienie w prywatnym ledgerze. Przypadkowa sprzeczność blokuje numer.
- Zawsze przechowujemy **ostatni zatwierdzony stan** i zapis każdej zmiany; agent nie może dowolnie przepisać kanonu.

## Głębokość fabuły / czytanie z ołówkiem

Każdy wątek ma: `arc_id`, pytanie główne, historię ujawnionych śladów, **prywatne rozwiązanie** (nie tylko „mroczny klimat”), planowany numer ujawnienia i sposób, w jaki czytelnik może do niego dojść wcześniej. Materiały rozkładają się na różne gatunki gazetowe: reportaż, ogłoszenie, sprostowanie, list, reklama, krzyżówka. Dwa niezależne dowody mogą łączyć się w trzecim numerze. Czytelnik zauważający sprzeczność otrzymuje przewagę, a nie karę.

**Ślad / przykład modelowy:** znak A na dokumencie w numerze X → ten sam znak na ogłoszeniu w numerze Y → potwierdzenie interpretacji w numerze Z. Prawdziwe daty ujawnień i rozwiązania są wyłącznie w prywatnym magazynie lore.

## Jakość artykułów ponad liczbę słów

Artykuł o grze musi nazwać grę, 2–3 mechaniki i konkretną decyzję dla gracza. Zamiast „roguelike uczy na błędach” napisz: „W Slay the Spire Gremlin Nob wzmacnia się po zagraniu Skill, więc Defend ma ukryty koszt; Lagavulin daje chwilę na przygotowanie; Burning Blood odzyskuje 6 HP po walce”. Analogicznie dla muzyki: nazwa zespołu, tytuł utworu, moment/technika i obserwacja. Dla horroru: tytuł filmu i konkretne rozwiązanie formalne. Bez fikcyjnych cytatów przypisywanych prawdziwym recenzentom.

**SCP dnia:** oryginalne SCP posiada licencję CC BY-SA 3.0; ewentualne adaptacje i ilustracje wymagają atrybucji autorów i licencji zgodnej z [wytycznymi SCP Wiki](https://scp-wiki.wikidot.com/licensing-guide). Jeśli tego nie możemy spełnić, nie publikujemy SCP tylko własną „Anomalię z archiwum”.

## Przed produkcją

1. Zatwierdzić ton i makietę na papierze.
2. Utworzyć **prywatny** magazyn lore (Drive folder ograniczony do właściciela, osobny token dostępu tylko do odczytu w workflow).
3. Podłączyć API, limity kosztów i model odpowiedni do każdego etapu.
4. Test 7 numerów *offline* + symulacja 60 wydań, w tym pokrycie 32 działów i uniknięcie powtórzeń: rejestrować powtórzenia, sprzeczności i nierozwiązane wskazówki.
5. Dopiero wtedy przełączyć workflow `main` i sprawdzić ponownie Brothera.

## Magazyn

Obowiązuje `../docs/STORAGE_CONTRACT.md`: repo zawiera wyłącznie kod i dokumentację techniczną. Wszystkie rękopisy, ilustracje, wydania, raporty QA, kanon i rozwiązania przechowuj na prywatnym Drive.
