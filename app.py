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
    def _build_menu(self) -> None:
        menu = tk.Menu(self)

        game_menu = tk.Menu(menu, tearoff=False)
        game_menu.add_command(label="Новая (лёгкая)", command=lambda: self.new_game("Лёгкая"))
        game_menu.add_command(label="Новая (средняя)", command=lambda: self.new_game("Средняя"))
        game_menu.add_command(label="Новая (сложная)", command=lambda: self.new_game("Сложная"))
        game_menu.add_separator()
        game_menu.add_command(label="Проверить", command=self.check_board)
        game_menu.add_command(label="Подсказка", command=self.hint_one_cell)
        game_menu.add_command(label="Решить", command=self.solve_and_fill)
        game_menu.add_command(label="Сбросить ввод", command=self.reset_to_puzzle)
        game_menu.add_separator()
        game_menu.add_command(label="Сохранить…", command=self.ui_save)
        game_menu.add_command(label="Загрузить…", command=self.ui_load)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.safe_exit)

        options_menu = tk.Menu(menu, tearoff=False)
        options_menu.add_checkbutton(
            label="Подсвечивать ошибки",
            variable=self.show_mistakes,
            command=self.refresh_mistakes_highlight
        )

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label="О программе", command=self.about)

        menu.add_cascade(label="Игра", menu=game_menu)
        menu.add_cascade(label="Опции", menu=options_menu)
        menu.add_cascade(label="Справка", menu=help_menu)
        self.config(menu=menu)