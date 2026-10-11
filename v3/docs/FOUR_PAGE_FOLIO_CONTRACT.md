# Kontrakt czterech stron A4 — Poranna Prasa

## Wymóg redakcyjny

Jeden numer = **dokładnie 4 osobne strony formatu A4** (595.28 × 841.89 pt). Dwustronicowe ilustracje przedstawiające czterostronicową makietę nie są gotowym numerem i nie mogą zostać opublikowane jako PDF gazety.

- **Strona 1:** pierwsza strona, masthead, data, numer wydania, reportaż dnia, trzy zajawki; prowadzą tylko do stron 2, 3 i 4.
- **Strona 2:** pełne teksty o grach, mechanikach i innych zainteresowaniach. Każdy lead ze strony 1, który wskazuje „str. 2”, musi mieć tutaj odpowiadający mu artykuł.
- **Strona 3:** archiwum uniwersum + pełne artykuły kulturalne/techniczne. Odsyłacze z pierwszej strony mają odpowiadać rzeczywistej paginacji.
- **Strona 4:** osobny typ strony: **obrazkowy komiks jako faktyczny asset graficzny**, listy do redakcji, sprostowania, ogłoszenia drobne, łamigłówki. Nie ma tu miejsca na przypadkowe kontynuacje artykułów.

## Ścisłe reguły składu

1. Najpierw zaplanuj wszystkie materiały wraz z unikalnymi `story_id`, dopiero potem składaj strony i generuj odniesienia.
2. Numer strony nie może pochodzić bezpośrednio z tekstu AI. Powinien być nadawany przez silnik składu na podstawie faktycznej strony `story_id`.
3. Walidator sprawdza: dokładnie 4 strony, wszystkie A4, numeracja 1–4, tożsamość daty/numeru, brak referencji do stron poza 1–4, istnienie każdego zapowiadanego tekstu, obecność bitmapowego komiksu na stronie 4, brak tekstu poza marginesami.
4. Fikcyjne dane lokalne (adresy, numery protokołów, rozkłady, cytaty) muszą być sprawdzane z prywatną biblią kanonu. Data artykułu nie może przeczyć dacie wydania; sprostowania mogą odnosić się tylko do istniejących wcześniejszych publikacji (w tym ulotek zapowiadających numer).
5. Zagadki muszą mieć sprawdzone rozwiązanie, a sudoku dokładnie jedno rozwiązanie.
6. PDF musi być renderowany do czterech osobnych obrazów w QA; poprawność kodu bez podglądu nie wystarcza.
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
