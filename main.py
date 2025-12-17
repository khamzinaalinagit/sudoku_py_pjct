import sys
from tkinter import messagebox

from app import SudokuApp


def main() -> None:
    try:
        app = SudokuApp()
        app.mainloop()
    except Exception as exc:
        messagebox.showerror("Критическая ошибка", f"Приложение завершено из-за ошибки:\n{exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
