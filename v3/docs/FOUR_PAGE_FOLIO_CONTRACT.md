# Kontrakt czterech stron A4 — Poranna Prasa

## Wymóg redakcyjny

Jeden numer = **dokładnie 4 osobne strony formatu A4** (595.28 × 841.89 pt). Dwustronicowe ilustracje przedstawiające czterostronicową makietę nie są gotowym numerem i nie mogą zostać opublikowane jako PDF gazety.

- **Strona 1:** **jedyny duży masthead „PORANNA PRASA”**, data, numer wydania, reportaż dnia, zajawki; prowadzą tylko do faktycznie istniejących materiałów na stronach 2, 3 i 4.
- **Strona 2:** **tylko wąska pagina** (mały „PORANNA PRASA”, strona 2, data, numer), bez wielkiego nagłówka, pełne teksty z rotujących działów. Zajawka „str. 2” musi tu mieć odpowiadający jej artykuł.
- **Strona 3:** **tak samo jak s. 2 — bez dużej winiety**, jedynie mały pasek folio. Artykuły i działy ROTUJĄ, nie zawsze horror i gry; odsyłacze z okładki muszą być prawdziwe.
- **Strona 4:** **bez wielkiej winiety i bez nagłówka „PORANNA PRASA — OSTATNIA STRONA”**. U góry najwyżej **cieniutka pagina** zawierająca numer strony, datę i numer wydania; zaraz pod nią **obrazkowy komiks**, listy, ogłoszenia, korekty, sudoku 9×9 i inne rotujące rubryki. Brak przypadkowych kontynuacji artykułów.

## Ścisłe reguły składu

1. Najpierw zaplanuj wszystkie materiały wraz z unikalnymi `story_id`, dopiero potem składaj strony i generuj odniesienia.
2. Numer strony nie może pochodzić bezpośrednio z tekstu AI. Powinien być nadawany przez silnik składu na podstawie faktycznej strony `story_id`.
3. Walidator sprawdza: dokładnie 4 strony, wszystkie A4, numeracja 1–4, **jednakowy numer i data na wszystkich czterech stronach** (niedopuszczalne np. Nr 007 na okładce i Nr 006 w środku), **duża winieta WYŁĄCZNIE na s. 1**, na 2–4 tylko mała pagina, istnienie każdego zapowiadanego tekstu, prawidłowe numery stron, obecność narysowanego komiksu na s. 4, brak literówek AI i tekstu poza marginesami.
4. Fikcyjne dane lokalne (adresy, numery protokołów, rozkłady, cytaty) muszą być sprawdzane z prywatną biblią kanonu. Data artykułu nie może przeczyć dacie wydania; sprostowania mogą odnosić się tylko do istniejących wcześniejszych publikacji (w tym ulotek zapowiadających numer).
5. Zagadki muszą mieć sprawdzone rozwiązanie, a sudoku dokładnie jedno rozwiązanie.
6. **Najpierw cztery osobne, zaakceptowane graficznie strony A4, potem jeden czterostronicowy PDF.** Pełne renderingi stron z image generation mogą być bazą, jeżeli ręcznie lub deterministycznie skontrolowano i naprawiono tekst, numerację, odsyłacze, ilustracje oraz zagadki; finalny PDF może składać się z czterech obrazów. Potwierdź skalę i kontrast wydruku na Brotherze. Sam atrakcyjny kolaż czterech miniaturek nie jest numerem.
7. Drukowanie Brothera oraz odbiór przez Androida to odrębny etap. Nie wdrażaj prototypu bez fizycznego testu czterech stron.
8. W stopce oznacz literacką fikcję w sposób niewybijający z konwencji gazetowej. Prawdziwych cytatów i wydarzeń nie wolno wymyślać.

## Numer demonstracyjny 001 (11.10.2026)

| Materiał | Strona |
|---|---|
| Lokatorzy słyszą pukanie z własnych mieszkań | 1 |
| Gremlin Nob / Slay the Spire | 2 |
| Samotne RPG i Exit 8 | 2 |
| Archiwum, liczenie domów od końca ulicy | 3 |
| Warsztat pisania i Skyward Sword HD | 3 |
| Blok 3A (rysunkowy komiks), listy, ogłoszenia, sudoku | 4 |

Motywy `Brzozowa 17`, `3A`, `03:17`, `autobus 44`, `A-017`, `4519` powinny zachować spójność w obrębie numeru i między wydaniami. Rozwiązania tych tropów pozostają w prywatnym rejestrze kanonu, nie w publicznych plikach.

**Status:** prototyp redakcyjny, nie część produkcyjnego pipeline na `main`.
