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

    def _build_layout(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main = tk.Frame(self)
        self.main.grid(row=0, column=0, sticky="nsew")
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_columnconfigure(1, weight=0)

        self.board_frame = tk.Frame(self.main, padx=10, pady=10)
        self.board_frame.grid(row=0, column=0, sticky="nsew")

        self.side = tk.Frame(self.main, padx=10, pady=10)
        self.side.grid(row=0, column=1, sticky="ns")

        tk.Label(self.side, text="Действия", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))
        tk.Button(self.side, text="Проверить", command=self.check_board, width=16).pack(pady=4)
        tk.Button(self.side, text="Подсказка", command=self.hint_one_cell, width=16).pack(pady=4)
        tk.Button(self.side, text="Решить", command=self.solve_and_fill, width=16).pack(pady=4)
        tk.Button(self.side, text="Сбросить", command=self.reset_to_puzzle, width=16).pack(pady=4)

        tk.Label(self.side, text="Сложность", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(16, 8))
        tk.Button(self.side, text="Лёгкая", command=lambda: self.new_game("Лёгкая"), width=16).pack(pady=4)
        tk.Button(self.side, text="Средняя", command=lambda: self.new_game("Средняя"), width=16).pack(pady=4)
        tk.Button(self.side, text="Сложная", command=lambda: self.new_game("Сложная"), width=16).pack(pady=4)

        self.status = tk.StringVar(value="Готово")
        tk.Label(self, textvariable=self.status, anchor="w", padx=10).grid(row=1, column=0, sticky="ew")

        self.cells: list[list[tk.Entry]] = []
        for r in range(GRID_SIZE):
            row_cells = []
            for c in range(GRID_SIZE):
                vcmd = (self.register(self._validate_digit), "%P", "%d")
                e = tk.Entry(
                    self.board_frame,
                    justify="center",
                    font=("Segoe UI", 18),
                    width=2,
                    validate="key",
                    validatecommand=vcmd
                )
                e.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                e.bind("<FocusOut>", lambda _ev, rr=r, cc=c: self._on_cell_changed(rr, cc))
                row_cells.append(e)
            self.cells.append(row_cells)

        for i in range(GRID_SIZE):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)

        self.bind("<Configure>", self._on_resize)
