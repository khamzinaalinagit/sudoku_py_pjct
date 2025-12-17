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

    def _validate_digit(self, proposed: str, action: str) -> bool:
        try:
            if action == "0":
                return True
            if proposed == "":
                return True
            if len(proposed) > 1:
                return False
            return proposed.isdigit() and 1 <= int(proposed) <= 9
        except Exception:
            return False

    def _on_cell_changed(self, _r: int, _c: int) -> None:
        if self.show_mistakes.get():
            self.refresh_mistakes_highlight()
    def _on_resize(self, _event: tk.Event) -> None:
        try:
            w = max(self.winfo_width(), 520)
            h = max(self.winfo_height(), 520)
            cell_px = min((w - 220) // 9, (h - 120) // 9)
            size = max(14, min(28, cell_px // 2))
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    self.cells[r][c].config(font=("Segoe UI", size))
        except Exception:
            pass

    def _apply_board(self, board: list[list[int]]) -> None:
         for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                e = self.cells[r][c]
                e.config(state="normal")
                e.delete(0, tk.END)
                if board[r][c] != 0:
                    e.insert(0, str(board[r][c]))

    def _lock_fixed_cells(self, puzzle: list[list[int]]) -> None:
        self.fixed = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                e = self.cells[r][c]
                if puzzle[r][c] != 0:
                    self.fixed[r][c] = True
                    e.config(disabledforeground="black")
                    e.config(state="disabled")
                else:
                     e.config(state="normal")
        self.refresh_mistakes_highlight()
    def get_user_board(self) -> list[list[int]]:
        board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                t = self.cells[r][c].get().strip()
                board[r][c] = int(t) if t else 0
        return board

    def new_game(self, difficulty_name: str) -> None:
        try:
            diff = DIFFICULTIES.get(difficulty_name, DIFFICULTIES["Средняя"])
            self.status.set(f"Генерация: {diff.name}…")

            sol = generate_full_solution()
            puz = make_puzzle_from_solution(sol, blanks=diff.blanks, ensure_unique=True)

            self.solution = sol
            self.puzzle = puz
            self._apply_board(puz)
            self._lock_fixed_cells(puz)

            self.status.set(f"Новая игра: {diff.name}")
        except Exception as exc:
            self.status.set("Ошибка генерации.")
            messagebox.showerror("Ошибка", f"Не удалось создать игру:\n{exc}")

    def reset_to_puzzle(self) -> None:
        try:
            if self.puzzle is None:
                raise SudokuError("Нет активной игры.")
            self._apply_board(self.puzzle)
            self._lock_fixed_cells(self.puzzle)
            self.status.set("Сброс выполнен.")
        except Exception as exc:
            messagebox.showwarning("Предупреждение", str(exc))

    def refresh_mistakes_highlight(self) -> None:
        try:
            for r in range(9):
                for c in range(9):
                    self.cells[r][c].config(bg="white")

            if not self.show_mistakes.get() or self.solution is None:
                return

            user = self.get_user_board()
            for r in range(9):
                for c in range(9):
                    v = user[r][c]
                    if v != 0 and v != self.solution[r][c] and not self.fixed[r][c]:
                        self.cells[r][c].config(bg="#ffd6d6")
        except Exception:
            pass

    def check_board(self) -> None:
        try:
            if self.solution is None:
                raise SudokuError("Нет активной игры.")
            user = self.get_user_board()

            empties = sum(1 for r in range(9) for c in range(9) if user[r][c] == 0)
            wrong = sum(
                1 for r in range(9) for c in range(9)
                if user[r][c] != 0 and user[r][c] != self.solution[r][c]
            )

            self.refresh_mistakes_highlight()

            if wrong == 0 and empties == 0:
                self.status.set("Готово! Решение верное.")
                messagebox.showinfo("Sudoku", "Верно! Судоку решено.")
            elif wrong == 0:
                self.status.set(f"Ошибок нет, пустых: {empties}.")
                messagebox.showinfo("Sudoku", f"Пока верно. Осталось: {empties}.")
            else:
                self.status.set(f"Ошибок: {wrong}.")
                messagebox.showwarning("Sudoku", f"Найдено ошибок: {wrong}.")
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Проверка не выполнена:\n{exc}")

    def hint_one_cell(self) -> None:
        try:
            if self.solution is None:
                raise SudokuError("Нет активной игры.")

            user = self.get_user_board()
            empties = [(r, c) for r in range(9) for c in range(9) if user[r][c] == 0 and not self.fixed[r][c]]
            if not empties:
                messagebox.showinfo("Sudoku", "Нет пустых клеток для подсказки.")
                return

            r, c = random.choice(empties)
            self.cells[r][c].delete(0, tk.END)
            self.cells[r][c].insert(0, str(self.solution[r][c]))
            self.status.set(f"Подсказка: клетка ({r + 1}, {c + 1}).")
            self.refresh_mistakes_highlight()
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Подсказка не выполнена:\n{exc}")

    def solve_and_fill(self) -> None:
        try:
            if self.solution is None:
                raise SudokuError("Нет активной игры.")
            if not messagebox.askyesno("Sudoku", "Показать решение?"):
                return
            self._apply_board(self.solution)
            self._lock_fixed_cells(self.solution)
            self.status.set("Решение показано.")
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Решение не показано:\n{exc}")

    def ui_save(self) -> None:
        try:
            if self.solution is None or self.puzzle is None:
                raise SudokuError("Нечего сохранять: нет активной игры.")
            path = filedialog.asksaveasfilename(
                title="Сохранить игру",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if not path:
                return
            user = self.get_user_board()
            save_game(path, self.puzzle, self.solution, user)
            self.status.set(f"Сохранено: {path}")
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{exc}")
 def ui_load(self) -> None:
        try:
            path = filedialog.askopenfilename(
                title="Загрузить игру",
                filetypes=[("Text files", "*.txt")]
            )
            if not path:
                return
            puzzle, solution, user = load_game(path)
            self.puzzle, self.solution = puzzle, solution
            self._apply_board(user)
            self._lock_fixed_cells(puzzle)
            self.status.set(f"Загружено: {path}")
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Не удалось загрузить:\n{exc}")
