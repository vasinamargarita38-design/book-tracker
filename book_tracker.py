import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("750x500")
        self.root.resizable(False, False)

        # Данные
        self.books = []
        self.load_data()

        # Поля ввода
        self.create_input_fields()
        # Таблица
        self.create_table()
        # Фильтры
        self.create_filters()
        # Обновить отображение
        self.refresh_table()

    def create_input_fields(self):
        frame = tk.LabelFrame(self.root, text="Добавить книгу", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Название
        tk.Label(frame, text="Название:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_entry = tk.Entry(frame, width=25)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Автор
        tk.Label(frame, text="Автор:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.author_entry = tk.Entry(frame, width=25)
        self.author_entry.grid(row=0, column=3, padx=5, pady=5)

        # Жанр
        tk.Label(frame, text="Жанр:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.genre_var = tk.StringVar()
        genres = ["Роман", "Детектив", "Фантастика", "Научная", "Поэзия", "Другое"]
        self.genre_combo = ttk.Combobox(frame, textvariable=self.genre_var, values=genres, width=22)
        self.genre_combo.grid(row=1, column=1, padx=5, pady=5)
        self.genre_combo.current(0)

        # Количество страниц
        tk.Label(frame, text="Страниц:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.pages_entry = tk.Entry(frame, width=25)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=5)

        # Кнопка добавления
        btn_add = tk.Button(frame, text="Добавить книгу", command=self.add_book, bg="lightgreen")
        btn_add.grid(row=2, column=0, columnspan=4, pady=10)

    def create_table(self):
        frame = tk.LabelFrame(self.root, text="Список книг", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "title", "author", "genre", "pages")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        self.tree.column("id", width=40)
        self.tree.column("title", width=180)
        self.tree.column("author", width=150)
        self.tree.column("genre", width=100)
        self.tree.column("pages", width=70)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_filters(self):
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Жанр:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.filter_genre = tk.StringVar(value="Все")
        genres_all = ["Все", "Роман", "Детектив", "Фантастика", "Научная", "Поэзия", "Другое"]
        genre_filter_combo = ttk.Combobox(frame, textvariable=self.filter_genre, values=genres_all, width=15)
        genre_filter_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Страниц больше:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.filter_pages = tk.Entry(frame, width=10)
        self.filter_pages.grid(row=0, column=3, padx=5, pady=5)

        btn_filter = tk.Button(frame, text="Применить фильтр", command=self.refresh_table)
        btn_filter.grid(row=0, column=4, padx=10, pady=5)

        btn_reset = tk.Button(frame, text="Сбросить фильтр", command=self.reset_filters)
        btn_reset.grid(row=0, column=5, padx=5, pady=5)

    def reset_filters(self):
        self.filter_genre.set("Все")
        self.filter_pages.delete(0, tk.END)
        self.refresh_table()

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_var.get().strip()
        pages_str = self.pages_entry.get().strip()

        # Валидация
        if not title or not author or not genre:
            messagebox.showerror("Ошибка", "Заполните название и автора")
            return
        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError("Количество страниц должно быть положительным")
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым положительным числом")
            return

        new_id = max([b["id"] for b in self.books], default=0) + 1
        self.books.append({
            "id": new_id,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        })
        self.save_data()
        self.clear_inputs()
        self.refresh_table()
        messagebox.showinfo("Успех", "Книга добавлена")

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)
        self.genre_combo.current(0)

    def refresh_table(self):
        # Очистить таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)

        genre_filter = self.filter_genre.get()
        pages_filter_str = self.filter_pages.get().strip()

        filtered = self.books[:]
        if genre_filter != "Все":
            filtered = [b for b in filtered if b["genre"] == genre_filter]
        if pages_filter_str:
            try:
                pages_min = int(pages_filter_str)
                filtered = [b for b in filtered if b["pages"] > pages_min]
            except ValueError:
                pass  # игнорируем некорректный ввод

        for b in filtered:
            self.tree.insert("", tk.END, values=(b["id"], b["title"], b["author"], b["genre"], b["pages"]))

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
        else:
            self.books = []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()