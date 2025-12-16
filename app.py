from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox, filedialog

from constants import GRID_SIZE
from sudoku_logic import (
    SudokuError,
    DIFFICULTIES,
    generate_full_solution,
    make_puzzle_from_solution,
)
from storage import save_game, load_game


class SudokuApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Sudoku — лабораторная работа")
        self.minsize(680, 520)

        self.solution: list[list[int]] | None = None
        self.puzzle: list[list[int]] | None = None
        self.fixed: list[list[bool]] = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.show_mistakes = tk.BooleanVar(value=True)

        self._build_menu()
        self._build_layout()

        self.new_game("Средняя")
