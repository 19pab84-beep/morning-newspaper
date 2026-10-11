# Gęsty skład + 30 rotujących rubryk

`rubrics.yaml`: 30 rubryk, wagi, miejsce w gazecie, typ i okres karencji. Każde wydanie: 1 reportaż fikcyjny z Pulsu Nocy, 4–9 rubryk rotujących, stała strona ostatnia z listami i ogłoszeniami. Świeżych newsów może być **zero**.

`continuity.py`: deterministyczny rotator i twarde walidacje prywatnego kanonu, dat ujawnień, tropów, źródeł realnych materiałów, sudoku.

`AGENTS.md`: plan ośmiu agentów, kontrakty i bramki jakości. Bez podłączonego API nie udajemy, że agenci już codziennie pracują.

Fizyczny wydruk próbny: `renderer/render_dense.py` w paczce lokalnej. **Nie przekierowuje nic na drukarkę**; wyłącznie PDF testowy.
