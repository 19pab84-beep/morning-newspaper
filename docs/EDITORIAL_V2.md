# PORANNA PRASA 2.0 — redakcja i projekt wydania

**Status:** projekt redakcyjny do akceptacji, osobna gałąź `feature/editorial-v2`. Żaden plik tego planu nie zmienia produkcyjnego harmonogramu na `main`.

## Koncepcja

Prawdziwa **w formie** gazeta drukowana codziennie rano: A4, monochromatyczna, data, numer, numeracja stron, tytuły, zajawki, autorzy, dział ogłoszeń, stopka redakcyjna. Nie kolejny wydruk RSS. Głos redakcji: rzeczowy, oszczędny, lekko ironiczny, z wyczuwalną osobowością.

Inspiracja: wcześniejszy projekt **Puls Nocy**. Niepokojące i niemożliwe zdarzenia opisywane z powagą miejskiej kroniki i z dyskretnym, narastającym absurdem. Nie horror wprost ani creepypasta rozpoznawalna po pierwszym zdaniu. Fikcyjne teksty należy oznaczać jako fikcję w małej stopce redakcyjnej i metadanych numeru. Nie przypisywać wypowiedzi prawdziwym osobom ani instytucjom.

## Mieszanka treści i priorytety

- **1 główny reportaż fikcyjny / Puls Nocy**, 450–800 słów, na okładce; temat „dziwny” i niepokojący. Oryginalny tekst codziennie, a nie odświeżany szablon.
- **2–3 artykuły autorskie, ponadczasowe**, 250–500 słów: horror, liminalność, stare technologie, zjawiska i ciekawostki, konstrukcja gier, Nintendo, solo RPG i planszówki, ciężka muzyka i kultura alternatywna. Najważniejszy jest interesujący kąt i dobra narracja, nie lista linków.
- **0–2 krótkie aktualności** wyłącznie przy naprawdę istotnych wydarzeniach z zainteresowań czytelnika (premiery, nowe gry, odkrycia). Nie ma obowiązkowego przeglądu polityki czy wiadomości ze świata.
- **Ostatnia strona obowiązkowo rezerwowana od początku składu**: ogłoszenia drobne, prawdziwa łamigłówka z jednym rozwiązaniem, listy do redakcji, sprostowania, ogłoszenie/reklama z diegetycznym żartem, mini rubryki. To NIE jest strona, na którą przenosi się resztę artykułów.

## Zasady generowania przez AI

Generowanie wymaga `OPENAI_API_KEY` w GitHub Secrets (oddzielne opłaty API). Wersja RSS-only nie realizuje tej koncepcji i **nie powinna jej imitować**. Zanim przełączymy codzienną produkcję na V2, trzeba sprawdzić obecność klucza, koszty, retencję pamięci tematów i fizyczny wydruk próbny.

Redakcja odbywa się etapami:
1. **Planer numeru:** wybiera różne tematy i kąty, bierze pod uwagę historię poprzednich 30 numerów, unika tej samej osi tematycznej co wczoraj i czuwa nad różnorodnością. Zapisuje w JSON plan działów, typ materiałów i budżet słów.
2. **Research** (tylko dla non-fiction i newsów): zbiera źródła, daty i potwierdzone fakty. Jeśli nie ma dostatecznej podstawy, zmienia tekst w esej/opinię lub pomija temat; nie fabrykuje faktów, dat, cytatów ani linków.
3. **Autorzy:** piszą wieloakapitowe teksty i leady, nie streszczenia RSS. Każdy materiał otrzymuje typ `fiction | essay | sourced_feature | brief`. Fikcja musi używać fikcyjnych nazw, cytatów i zdarzeń.
4. **Redaktor:** wymaga jasnego początku, konkretu, sensownego zakończenia, naturalnego polskiego, różnej długości zdań, braku pustego AI-style; kontroluje niepowtarzalność, spójność, źródła, rozdzielenie faktów od fikcji.
5. **Łamacz:** nadaje tekstom wagę graficzną, pilnuje dowiązania sekcji i rezerwuje stronę ostatnią. Puste strony/kolumny, samotne nagłówki, mikroskopijne fonty i tekst poza marginesem są błędem wydania.
6. **Kontrola druku:** PDF render → test wizualny → PRN Brother → manifest SHA-256 → dopiero publikacja. Skrypt Android/Termux/Tasker i warunek obecności w domu pozostają bez zmian.

## Zasady reportażu Puls Nocy

- Wyjściowa anomalia zakorzeniona w zwykłej sprawie: administracja, rodzina, praca, sklep, transport.
- Najpierw normalne obserwacje i społeczne konsekwencje, nie nadprzyrodzona ekspozycja.
- Cytaty mogą pochodzić wyłącznie od **wymyślonych** świadków i fikcyjnych urzędników.
- Stopniowanie szczegółów, rzeczowy ton, suchy humor biurokratyczny.
- Nierozwiązana ostatnia scena, którą czytelnik sam dopowiada.
- Nieliczne nawiązania między wydaniami: wspólne motywy i drobne anomalie w ogłoszeniach. Nie wolno robić wyłącznie klonów tej samej historii.
- Nie udajemy rzeczywistego reportażu w metadanych; dyskretny imprint w numerze objaśnia jego charakter.

## Format próbny (4 strony A4)

1. Pierwsza strona: masthead, wydanie i data, **Puls Nocy** — okładkowy reportaż, zapowiedzi reszty numeru, krótki list redakcji.
2. Artykuł główny: pogłębiony tekst o liminalności i mechanizmie horroru, niżej dossier / notatnik redakcyjny.
3. Kultura: rogaliki zamiast rolodexu — gry, solo RPG, muzyka eksperymentalna, technika; kilka dobrze napisanych tekstów.
4. **Ostatnia strona**: ogłoszenia, sudoku 4×4 (jedno rozwiązanie), prognoza nastroju, sprostowanie, fikcyjna reklama, mała stopka o konwencji literackiej.

Docelowo możliwość 4–6 stron, ale bez sztucznego dopychania przypadkowymi newsami. Przy większej objętości ostatnia strona zawsze pozostaje ostatnią.

## Blokery wdrożenia na main

- Sprawdzone klucz API i koszty / limit miesięczny.
- Generator V2, selekcja i pamięć tematów.
- Layout z oddzielnym szablonem ostatniej strony i kontrolą składu.
- Render/przegląd kilku próbnych wydań i druk jednej pełnej makiety.
- Jasne rozróżnienie twórczej fikcji od faktów, zwłaszcza w publikacji WWW.

Makieta PDF powstaje poza repo i **nie uruchamia żadnego drukowania**.
