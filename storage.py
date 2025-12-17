from __future__ import annotations

from sudoku_logic import SudokuError


def write_board(f, board: list[list[int]]) -> None:
    for r in range(9):
        f.write(" ".join(str(board[r][c]) for c in range(9)) + "\n")


def read_board_block(lines: list[str], header: str) -> list[list[int]]:
    if header not in lines:
        raise SudokuError(f"В файле отсутствует блок: {header}")
    idx = lines.index(header) + 1
    block = lines[idx:idx + 9]
    if len(block) != 9:
        raise SudokuError(f"Блок {header} повреждён (нужно 9 строк).")

    board: list[list[int]] = []
    for line in block:
        parts = line.split()
        if len(parts) != 9:
            raise SudokuError(f"Блок {header} повреждён (строка: {line})")
        row: list[int] = []
        for p in parts:
            if not p.isdigit():
                raise SudokuError(f"Некорректное значение в {header}: {p}")
            v = int(p)
            if v < 0 or v > 9:
                raise SudokuError(f"Значение вне диапазона 0..9 в {header}: {v}")
            row.append(v)
        board.append(row)
    return board


def save_game(path: str, puzzle: list[list[int]], solution: list[list[int]], user: list[list[int]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Sudoku save\n")
        f.write("PUZZLE\n")
        write_board(f, puzzle)
        f.write("SOLUTION\n")
        write_board(f, solution)
        f.write("USER\n")
        write_board(f, user)


def load_game(path: str) -> tuple[list[list[int]], list[list[int]], list[list[int]]]:
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]

    puzzle = read_board_block(lines, "PUZZLE")
    solution = read_board_block(lines, "SOLUTION")
    user = read_board_block(lines, "USER")
    return puzzle, solution, user
