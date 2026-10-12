# BIBLIA GRAFICZNA · PORANNA PRASA · V3.2
**STATUS: zatwierdzony kierunek artystyczny; obowiązuje we wszystkich nowych pilotażach. Produkcyjny `main` bez zmian.**

## WZORZEC / NIE PODLEGA DYSKUSJI
Ostatnie zaakceptowane wizualizacje użytkownika są źródłem stylu. Gazeta ma wyglądać jak **autentyczna, stara, czarno-biała gazeta**, nie jak biały raport z nagłówkami. Widoczna struktura papieru, delikatna ziarnistość rastra, odrobina zabrudzeń lub falcowania, wysoki kontrast czerni, bogaty obraz prasowy, zwięzłe śródtytuły, rytm szpalt, linie i ramki. Nie przesadzać z żółcią/sepią — końcowy odbiorca drukuje na monochromatycznym laserowym Brotherze. Artykuły muszą być nadal **czytelne**, nawet jeśli tekst ma 8–9 pt.

## ŻELAZNY ROZKŁAD 4×A4

| Strona | Winieta i pagina | Funkcja |
|---|---|---|
| **1 — OKŁADKA** | **JEDYNY** ogromny nagłówek `PORANNA PRASA`, motto, numer, data, dyskretna pogoda | Jeden mocny dziwny reportaż, główna ilustracja, trzy zapowiedzi i małe materiały |
| **2 — ŚRODEK** | **WĄSKI folio**, ok. 6–9 mm: `2 | PORANNA PRASA | DD.MM.RRRR | NR XXX`; **ŻADNEJ wielkiej winiety** | 1–2 pełne artykuły, ilustracje, dokumenty, gęsty skład |
| **3 — ŚRODEK** | **DOKŁADNIE TAK SAMO JAK S. 2**. Mała pagina, **ŻADNEGO ogromnego napisu `PORANNA PRASA`**, nawet jeśli layout graficzny kusi | Inna rotacja działów: sztuka/nauka/gry/historia/horror/muzyka, bez schematu w każdym numerze |
| **4 — OSTATNIA** | **BEZ GŁÓWNEGO NAGŁÓWKA.** U góry tylko mały numer strony + data/NR, cienka kreska. **ŻADNEGO `PORANNA PRASA — OSTATNIA STRONA`** i żadnej wielkiej winiety | Od górnej części strony zaczyna się **prawdziwy komiks 3–4 kadry**, dalej rubryki: listy, ogłoszenia, sprostowania, humor, sudoku 9×9; rotować ich układ |

Słowa `PORANNA PRASA` **wolno powtórzyć** małą czcionką tylko w paginie stron 2 i 3 (str. 4 może obyć się bez nazwy). Zawsze **dokładnie 4 strony o wymiarach A4**, nie kolaż, nie plansza „2×2 = 4 strony”.

## OBRAZY PRZEDE WSZYSTKIM — ALE Z KONTROLĄ
Użytkownik świadomie wybrał **realizm i fakturę wygenerowanych wizualizacji**, zamiast sterylnego PDF. Dopuszczamy dwie ścieżki:
1. **Grafika-first (preferowana dla kolejnego pilota):** generuj **cztery osobne pionowe strony A4** w jednym systemie estetycznym; przeprowadź kontrolę każdego tekstu, liczb, dat, autorów, literówek i odsyłaczy. Popraw błędy w osobnym składzie typografii (tekst jako osobna warstwa obrazu albo PDF). Dopiero potem sklej dokładnie cztery strony do PDF z zakotwiczoną skalą 210×297 mm. Nie zostawiaj liter generowanych przez obraz AI bez kontroli: w szczególności długie polskie akapity często są nieprawidłowe.
2. **Hybryda:** wygenerowane ilustracje, zdjęcia w stylu prasowym, tekstury papieru i ryciny + prawdziwa warstwa typograficzna w PDF. To metoda docelowa dla powtarzalnego automatycznego wydawnictwa i lepszego tekstu, ale wyglądem **musi dorównać grafice-first**.

**Wartości techniczne:** pionowe A4; raster docelowo ~2480×3508 px przy 300 dpi (lub 4960×7016 px dla 600 dpi, gdy pamięć/druk pozwala). Kolor tylko jako podgląd — do druku konwersja do skali szarości. 4 osobne strony PDF, nie 4 miniatury na jednym arkuszu. Mała paginacja ma być czytelna w fizycznym A4.

## JAKI OBRAZ PASUJE?
Wolno: reporterskie zdjęcia, analogowe portrety, mapy, ryciny, reprodukcje dokumentów, historyzujące ilustracje, screentone/halftone, komiks z konsekwentną kreską.
Nie wolno: ilustracji stockowej niepasującej do gazety; losowych ślicznych grafik bez związku z artykułem; obrazów całych „stron”, w których są bełkotliwe wymyślone zdania; pseudo-źródeł lub zmyślonych przypisów, które udają fakt.

**Fotografia w fikcyjnej kronice** powinna być opisana w stopce jako ilustracja do fikcyjnego świata; nie udawać prawdziwego dokumentu autentycznej osoby czy instytucji.

## REŻIM KOMIKSU
Na **s. 4** 3–4 rysunkowe kadry jako grafika. Postacie i miejsce (np. Blok 3A) mają być rozpoznawalne w serii; co najmniej jeden żart, emocja lub subtelny trop, ale nie obowiązkowa zagadka. Dymki mają mieć poprawną polszczyznę; gdy generator grafiki popełnia literówki, nakładamy typografię osobno.

## REDAKCJA, ROTACJA I PAMIĘĆ
**32 działy i 128 rubryk** w `departments.yaml`. Numer zwykle: 1 duży osobliwy reportaż, 2–3 rzeczowe i zaskakujące artykuły, 5–8 rubryk; 0 obowiązkowych newsów; sudoku **tylko 9×9** i tylko z jednym rozwiązaniem. Utrzymywać prywatną pamięć uniwersum i historię 60 numerów. Unikać tej samej gry, bohatera, sceny lub rubryk bez nowej idei.

## BLOKADY JAKOŚCI — NIE PUBLIKUJ BEZ TEGO
- Weryfikacja 4 osobnych stron A4, w kolejności 1–4.
- **Spójna data i numer** na każdej stronie. W szczególności: **ani jednego „NR 006” na jednej i „NR 007” na innej**.
- Duża winieta tylko na s. 1; **strony 2, 3, 4 bez niej**. Strona 4 nie potrzebuje słowa „ostatnia strona”.
- Kontrola, czy każde `str. 2/3/4` naprawdę prowadzi do właściwego materiału, bez reklamowania nieistniejącego artykułu.
- Wszystkie źródła materiałów niefikcyjnych rzetelnie zweryfikowane; dla fikcyjnych cytatów czy instytucji dyskretna, uczciwa stopka.
- SUDOKU: automatycznie **jedno rozwiązanie**, prawidłowe podane cyfry, brak syntetycznie wygenerowanych przypadkowych znaków.
- Co najmniej jeden rysunkowy komiks na s. 4; poprawne dymki, zgodna postać, ciągłość fabuły.
- Brak przesuniętych kolumn, źle wyrównanych obrazów, nieczytelnych 6-pt akapitów, przepełnień, ogromnych białych przestrzeni.
- Fizyczny lub ekwiwalentny raster check: porównać ze **wzorcem zaakceptowanej gazety**, nie z poprzednim białym PDF.
- **Nie wysyłaj pilotażowych numerów do automatu Brother/Tasker.** `main` pozostaje bez zmian aż do decyzji o wdrożeniu.

## MANTRA
**„Okładka ma wielką winietę. Druga i trzecia mają wyłącznie małe paginy. Czwarta jest gazetową ostatnią stroną bez nagłówka. Wszystkie wyglądają jak stare gazety i razem tworzą jeden spójny numer.”**
