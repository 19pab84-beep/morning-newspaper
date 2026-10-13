"""Unique Sudoku answer for the materials promised on the printed page."""
from copy import deepcopy
from v3.editorial.production_audit import sudoku_solutions_9x9


def sudoku_answer(puzzle):
    if sudoku_solutions_9x9(puzzle)!=1:
        raise ValueError('Nie wydajemy rozwiązania niejednoznacznej planszy')
    board=deepcopy(puzzle)
    digits=set(range(1,10))

    def solve():
        choices=[]
        for row in range(9):
            for col in range(9):
                if board[row][col]:
                    continue
                box={board[r][c] for r in range(row//3*3,row//3*3+3)
                                for c in range(col//3*3,col//3*3+3)}
                options=digits-set(board[row])-{board[r][col] for r in range(9)}-box
                if not options:
                    return False
                choices.append((len(options),row,col,options))
        if not choices:
            return True
        _,row,col,options=min(choices,key=lambda x:x[0])
        for digit in sorted(options):
            board[row][col]=digit
            if solve():
                return True
        board[row][col]=0
        return False

    if not solve():
        raise ValueError('Brak rozwiązania')
    return board
