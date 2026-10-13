# Poranna Prasa V3 — generator do oceny

Hybrydowy skład czterech A4: duża winieta wyłącznie na okładce, małe paginy
stron 2–3, komiks pod cienkim folio strony 4. Tekst, dymki, sudoku i odsyłacze
są deterministyczną warstwą PDF. Generator nie publikuje ani nie drukuje.

## Materiały z Drive

Repo zawiera wyłącznie kod, testy i dokumentację techniczną. Rozpakuj materiały
z prywatnego Drive poza checkoutem: `assets/`, `editions/`, osobny kanon.
Ilustracje i fonty Liberation (z licencją) są w pakiecie materiałów.
Pełne zasady: [STORAGE_CONTRACT.md](docs/STORAGE_CONTRACT.md).

```bash
python -m pip install -r v3/requirements.txt
export PORANNA_PRASA_ASSETS=/PRIVATE/materials/assets
python -m v3.build --input /PRIVATE/materials/editions/006.json \
  --private-state /PRIVATE/private-state-ordered-pilots.json \
  --output /PRIVATE/output --prn
```

Powtórz dla kolejnych numerów w kolejności; ledger wymaga poprzedników.
Wyjście zawiera PDF, cztery rastry 300 dpi, bibliografię, manifest, QA,
rękopis i rozwiązanie sudoku oraz opcjonalny PRN 600 dpi. Wszystkie pozostają
poza repo i są przeznaczone do prywatnego Drive. Synchronizacja Drive nie jest
automatyczna; zapis i wersjonowanie kanonu odbywa się lokalnie atomowo.

## AI i prywatna ciągłość

Piloty napisano w ChatGPT Work; `provenance` opisuje pochodzenie. Jawny tryb
`--live --model WYBRANY_MODEL` używa Responses API, wymaga `OPENAI_API_KEY`
i podlega opłatom. Model dostaje bezpieczną projekcję kanonu oraz pakiety
zweryfikowanych źródeł. Rozwiązania i przyszłe ujawnienia pozostają prywatne.
Odmowa, niepełna odpowiedź, naruszenie jakości lub brak klucza blokują numer.
Limit: 16 wywołań i 6000 tokenów wyjścia na wywołanie. Prawdziwy tryb API
nie został jeszcze przetestowany. Nie ma podłączonego harmonogramu.

Planer obejmuje 32 działy/128 formatów. `PrivateStore` weryfikuje deklarowane
fakty, tropy i sprostowania, utrzymuje historię i blokuje konflikt numeru.
Testy i walidatory nie zastępują redakcyjnej oceny tekstów oraz continuity.

## Testy

```bash
PYTHONPATH=.:v3/editorial python -m unittest discover -s v3/tests -v
PYTHONPATH=.:v3/editorial python -m unittest discover -s v3/editorial -p 'test*.py' -v
# Pełny test trzech rzeczywistych wydań z prywatnymi materiałami:
export PORANNA_PRASA_PILOTS=/PRIVATE/materials/editions
export PORANNA_PRASA_ASSETS=/PRIVATE/materials/assets
PYTHONPATH=.:v3/editorial python -m unittest discover -s v3/tests -v
```

Bez pakietu Drive testy integracyjne pilotów są jawnie pomijane. Publiczne
kontrole katalogu, sudoku, kontraktów API i granic magazynu działają bez niego.
Preflight sprawdza rzeczywisty PDF: 4×A4, daty, paginację, odsyłacze, akapity,
komiks, dymki, marginesy i nakładanie wierszy. Potrzebna pozostaje wizualna
akceptacja i fizyczny test wydruku; PRN sprawdzono tylko strukturalnie.

`main`, workflow, Pages i automatyczne drukowanie pozostają bez zmian.
Nie uruchamiaj pilotażowych wydań w automacie Brother/Tasker.

## Prywatne drukowanie przygotowanego numeru

[PRIVATE_PRINT_QUEUE.md](docs/PRIVATE_PRINT_QUEUE.md) opisuje pakiet wieczorny dla istniejącego Taskera. Tryb lokalnej kolejki nie wymaga API ani dostępu do Drive na telefonie; instalator nie drukuje. Brak pakietu na dany dzień oznacza brak druku.
