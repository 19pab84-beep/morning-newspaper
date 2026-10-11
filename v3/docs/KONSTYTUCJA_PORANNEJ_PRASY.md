# KONSTYTUCJA PORANNEJ PRASY · wydanie 1.0
**Dokument nadrzędny / MASTER SPEC** · obowiązuje wszystkie nowe numery po wdrożeniu V3

**MISJA.** Poranna Prasa jest prywatnym czterostronicowym dziennikiem o fascynacjach czytelnika, który wygląda i czyta się jak prawdziwa papierowa gazeta. Ma zaskakiwać, bawić, niepokoić i nagradzać uważne czytanie. **Nie jest zbiorem najnowszych wiadomości ani streszczeniem RSS.**

## 12 nienegocjowalnych artykułów

1. **PAPIER.** Jeden numer to **dokładnie 4 osobne strony A4**, zawsze 1/2/3/4. Prawdziwy, czarno-biały wygląd starej gazety: ogromna winieta na s. 1, gęste 2–4 łamy, mała czytelna antykwa, mocne serifowe nagłówki, linie, podpisy zdjęć, tabele i gazetowa hierarchia. Bez współczesnych kart, szerokich marginesów i białych pustek. Wrażenie faktury papieru dopuszczalne, ale bez pogarszania kontrastu na laserowym Brotherze.
2. **PRAWDZIWY SKŁAD, NIE OBRAZ STRONY.** Tekst, numeracja, sudoku i odsyłacze muszą być generowane deterministycznie w składaczu PDF. Grafiki są osobnymi ilustracjami. Piękne wizualizacje generowane jako jeden obraz *nie są* drukowalnym, spójnym numerem; kontrolujemy czytelność polskich liter i dokładne rozmieszczenie.
3. **CZTERY FUNKCJE.** s. 1 = wielka okładka i temat dnia; s. 2–3 = treść główna i zmienne działy; s. 4 = **prawdziwa ostatnia strona**: komiks, ogłoszenia, listy, humor, zagadki, korekty i drobne rubryki. Nie ma piątej strony ani artykułu przeniesionego poza s. 4.
4. **PAGINACJA.** Każdy materiał ma `story_id` i faktycznie ustaloną stronę. Zapowiedź „str. N” powstaje *po* łamaniu. Nigdy nie pochodzi z tekstu AI. Spójne daty, numery, autorzy, tytuły, zwroty „ciąg dalszy” i zapowiedzi.
5. **KONKRET PONAD WODĘ.** Materiał niefikcyjny ma tezę, co najmniej **3 sprawdzalne szczegóły** (nazwa, rok, mechanika, scena, liczba, źródło) oraz wniosek; materiał fikcyjny ma zdarzenie, konsekwencję i namacalny dowód. Odrzucamy pusty, ogólnikowy akapit, powtórzenia, pseudoemocjonalne slogany i udawane statystyki.
6. **MNIEJ NEWSÓW, WIĘCEJ LEKTURY.** Zero przymusowych depesz. Zwykle: **1 autorski reportaż dziwny + 2–3 pogłębione teksty + 5–8 krótkich rubryk**. Wiadomości tylko wtedy, gdy naprawdę dotyczą zainteresowań czytelnika. Preferujemy tematy ponadczasowe i pomysły, do których warto wrócić.
7. **32 DZIAŁY / 128 FORMATÓW.** Szczegółowy katalog: `v3/editorial/departments.yaml` i `v3/docs/DZIALY_I_ROTACJA.md`. Działy to tematy, rubryki to formy. Nie drukujemy ich wszystkich. Rotacja ma zmieniać zarówno działy, jak i *sposób opowiadania*.
8. **NIESPODZIANKA JEST OBOWIĄZKOWA.** Każdy numer otrzymuje jeden nieoczywisty, wartościowy temat spoza ostatnich wydań, jeden nowy format/redakcyjny zabieg i przynajmniej jeden konkretny szczegół, którego czytelnik prawdopodobnie nie zna. Nie powtarzamy tego samego bohatera lub gry bez powodu.
9. **PULS NOCY.** Temat dnia może być fikcyjnym, niepokojącym reportażem napisanym **z całkowitą powagą lokalnej prasy**. Zwyczajne życie, delikatna anomalia, wiarygodna biurokracja, niespokojne szczegóły. Nie krzykliwe creepypasty. Prawdziwe osoby, instytucje, badania i cytaty nie mogą zostać sfabrykowane. Fikcja jest dyskretnie oznaczona w stopce.
10. **JEDNO UNIWERSUM, NIE LOSOWE STRASZAKI.** Redakcja prowadzi prywatny kanon z postaciami, miejscami, `arc_id`, `clue_id`, `introduced_in`, `payoff_due`, stanem wiedzy i historią publikacji. Maksymalnie **3 zamierzone tropy na numer** (zwykle 1 jawny + 2 dyskretne). Każda zagadka ma prywatne rozwiązanie i możliwy do odtworzenia tok dedukcji. Sprzeczności przypadkowe blokują wydanie; zaplanowane mają własny ID.
11. **KOMIKSY I ROZRYWKA SĄ PRAWDZIWE.** Komiks = **rzeczywisty obraz 3–4 kadrów** w PDF, z logicznym następstwem scen i czytelnymi, poprawnymi dymkami (skład tekstu w edytowalnej warstwie, gdy generator obrazów go zniekształca). Sudoku = pełne **9×9, dokładnie jedno rozwiązanie**; krzyżówki muszą odpowiadać hasłom. Cytaty prawdziwe z autorami/źródłami albo jawnie fikcyjne. SCP tylko z poprawną atrybucją i licencją.
12. **JAKOŚĆ PRZED WYDRUKIEM.** Osobni kontrolerzy: faktów i źródeł, stylu, continuity, ukrytych tropów, rotacji działów, łamania i druku. QA weryfikuje 4×A4, pliki obrazów stron, brak ucięć/nakładek, wszystkie odsyłacze, brak fałszywej paginacji, komiks na s. 4, walidację łamigłówek oraz PRN. Piloty nie zastępują działającej gazety na `main` bez akceptacji i fizycznego testu.

**TON REDAKCJI:** inteligentny, precyzyjny, lekko przewrotny; w fikcyjnej kronice śmiertelnie poważny. Gazeta ma po latach nadawać się do zakreślania ołówkiem i porównywania numerów.

**PRAWO REDAKTORA:** jeśli numer jest nudny, banalny, pusty lub niespójny — **nie publikujemy go; poprawiamy tekst lub zmieniamy temat**. Nie dopchamy czterech stron przypadkowymi newsami.

**STATUS:** konstytucja wersji rozwojowej. Automatyczny workflow na `main` pozostaje bez zmian do osobnej decyzji o wdrożeniu.
