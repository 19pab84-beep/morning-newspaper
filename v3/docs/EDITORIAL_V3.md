# PORANNA PRASA 3.0 — nowy layout, selekcja, ciągłość

**Etap:** prototyp. Codzienna produkcja na `main`, GitHub Pages i Termux/Tasker nadal pozostaje nietknięta.

> **Aktualny standard V3:** [KONSTYTUCJA_PORANNEJ_PRASY.md](KONSTYTUCJA_PORANNEJ_PRASY.md), [DZIALY_I_ROTACJA.md](DZIALY_I_ROTACJA.md) oraz [FOUR_PAGE_FOLIO_CONTRACT.md](FOUR_PAGE_FOLIO_CONTRACT.md). Dawne 30 rubryk pozostaje historycznym prototypem; nowy katalog to **32 działy / 128 formatów**, z rotacją i twardym limitem **4 A4**. Fotorealistyczna szata graficzna zaakceptowanych wizualizacji jest teraz wzorcem produktu.

## Zmiana kierunku

Codzienna gazeta **o czymś**, a nie 27 krótkich depesz. Jeden mocny reportaż z fikcyjnego świata Pulsu Nocy, 2–3 konkretne artykuły o horrorze, Nintendo, roguelike’ach, grach solo i planszówkach, muzyce i technologii, następnie kilka rotujących rubryk. Prawdziwe wiadomości tylko wtedy, gdy mają rzeczywistą wartość dla czytelnika; liczba może wynieść zero. Informacja o fikcyjności jest dyskretna, ale rzeczywista. Zmyślonych słów nie przypisujemy realnym osobom.

## Zasady składu

- Format: A4, **trzy łamy**, 29 pt marginesu, odstęp 12 pt, ok. 8,25 pt font podstawowy / 10,45 pt interlinia, serify w tekstach, sans w metadanych.
- Pierwsza strona: pełny winietowy tytuł gazety **tylko na pierwszej stronie**, temat główny i reportaż w łamach.
- Artykuły nie mogą być ogólnymi refleksjami: **przedmiot + mechanika/przypadek + konsekwencja**. Źródła przy analizach niefikcyjnych.
- Ostatnia strona fizycznie ostatnia: ogłoszenia, korespondencja, sprostowanie, łamigłówka, reklama fikcyjna i komiks (w rotacji).
- Układ próbny renderujemy osobno. Przed wdrożeniem w generator planuj dynamiczny page balancing i unikaj łamania nagłówków. Brak mechanicznego dopełniania losowymi wiadomościami.
- Nowe numery V3 zawsze **dokładnie 4 strony A4**, niezależnie od wcześniejszego limitu testowego w produkcyjnym pipeline. Zmiana docelowych limitów wymaga osobnego testu Brothera.

## Wcześniejszy katalog 30 rubryk (wersja historyczna)

Pełna specyfikacja w `editorial/rubrics.yaml`: 30 identyfikatorów ze slotami, wagami i karencją. Obejmuje: temat Puls Nocy, lokalne ostrzeżenia, listy, ogłoszenia, cytaty, żarty, trzykadrowy komiks, SCP dnia (prawidłowa licencja!), recenzję opowiadania, „tego dnia”, mechaniki gier, Nintendo, solo RPG, planszówki, metal, archiwum technologii, naukę, psychologię niepokoju, anomalię redakcyjną, fotografię z archiwum, rozkład jazdy, sudoku, krzyżówkę, nekrologi, transkrypcje, przepisy itd.

## Kontrola ciągłości

- Oddziel prywatną rzeczywistość świata od tego, co gazetowi reporterzy uważają za fakt.
- Zaszywaj ślady w wielu typach materiałów; nie więcej niż trzy ślady na numer.
- Każda wskazówka ma ID, pierwsze wystąpienie i prywatne rozwiązanie. Agent `continuity_keeper` odrzuca przypadkowe sprzeczności; `puzzle_master` odrzuca zagadki bez jednoznacznego rozwiązania.
- Pamięć to **pliki i walidator**, a nie domniemana pamięć jednej sesji AI. Prywatne lore nigdy nie jest publikowane w repozytorium publicznym.

## Demo

`renderer/render_dense.py` + `renderer/sample_content.py` generują PDF **bez PRN** i bez publikowania do Pages. Testowane na czterech stronach. Sudoku sprawdzono na jedno rozwiązanie. To przykładowy numer, nie pełen autoprodukcyjny pipeline.

## Kolejne kroki przed zamianą porannego generatora

1. Zatwierdzenie makiety po wydruku.
2. Prywatny magazyn lore (np. prywatny Drive folder lub prywatne repo). Nie publiczny GitHub.
3. Wybór modelu i podpięcie API; limity kosztu na numer, jawna informacja o brakującym kluczu.
4. Uruchomienie ośmiu ról, odrzucanie nudnych tekstów i konfliktów kanonu.
5. Symulacja 30–60 wydań z kontrolą zdradzonych sekretów, powtórek, karencji i ciągłości postaci.
6. Dopiero później przełączenie codziennego workflow i test wydruku z zablokowanym Androidem.
