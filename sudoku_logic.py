from __future__ import annotations

import random
from dataclasses import dataclass

from constants import GRID_SIZE, BOX_SIZE, DIGITS


class SudokuError(Exception):
    """Ошибки логики судоку."""


@dataclass
class Difficulty:
    name: str
    blanks: int


DIFFICULTIES = {
    "Лёгкая": Difficulty("Лёгкая", blanks=36),
    "Средняя": Difficulty("Средняя", blanks=46),
    "Сложная": Difficulty("Сложная", blanks=54),
}


def deep_copy_board(board: list[list[int]]) -> list[list[int]]:
    return [row[:] for row in board]


def find_empty(board: list[list[int]]) -> tuple[int, int] | None:
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] == 0:
                return r, c
    return None


def is_valid(board: list[list[int]], row: int, col: int, num: int) -> bool:
    if num in board[row]:
        return False

    for r in range(GRID_SIZE):
        if board[r][col] == num:
            return False

    br = (row // BOX_SIZE) * BOX_SIZE
    bc = (col // BOX_SIZE) * BOX_SIZE
    for r in range(br, br + BOX_SIZE):
        for c in range(bc, bc + BOX_SIZE):
            if board[r][c] == num:
                return False

    return True


def solve_backtracking(board: list[list[int]]) -> bool:
    empty = find_empty(board)
    if empty is None:
        return True

    row, col = empty
    nums = list(DIGITS)
    random.shuffle(nums)

    for num in nums:
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_backtracking(board):
                return True
            board[row][col] = 0

    return False


def count_solutions(board: list[list[int]], limit: int = 2) -> int:
    empty = find_empty(board)
    if empty is None:
        return 1

    row, col = empty
    total = 0

    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            total += count_solutions(board, limit=limit)
            board[row][col] = 0
            if total >= limit:
                return total

    return total


def generate_full_solution() -> list[list[int]]:
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    if not solve_backtracking(board):
        raise SudokuError("Не удалось сгенерировать решённую доску.")
    return board


def make_puzzle_from_solution(
    solution: list[list[int]],
    blanks: int,
    ensure_unique: bool = True
) -> list[list[int]]:
    puzzle = deep_copy_board(solution)

    positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    random.shuffle(positions)

    removed = 0
    attempts = 0
    max_attempts = 5000

    while removed < blanks and positions and attempts < max_attempts:
        attempts += 1
        r, c = positions.pop()
        if puzzle[r][c] == 0:
            continue

        backup = puzzle[r][c]
        puzzle[r][c] = 0

        if ensure_unique:
            test = deep_copy_board(puzzle)
            sols = count_solutions(test, limit=2)
            if sols != 1:
                puzzle[r][c] = backup
                continue

        removed += 1

    return puzzle
