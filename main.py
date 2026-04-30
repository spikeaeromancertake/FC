import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

# Файл для сохранения истории
HISTORY_FILE = "password_history.json"


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # История паролей
        self.history = self.load_history()

        # Создание интерфейса
        self.create_widgets()

        # Загрузка истории в таблицу
        self.refresh_history_table()

    def create_widgets(self):
        # Рамка для настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.password_length = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(
            settings_frame, from_=4, to=64, orient="horizontal",
            variable=self.password_length, command=self.update_length_label
        )
        self.length_scale.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)

        # Чекбоксы для выбора символов
        self.use_digits = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(
            row=1, column=0, sticky="w", pady=5
        )

        self.use_letters = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(
            row=2, column=0, sticky="w", pady=5
        )

        self.use_special = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&* etc.)", variable=self.use_special).grid(
            row=3, column=0, sticky="w", pady=5
        )

        # Кнопка генерации
        generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        generate_btn.grid(row=4, column=0, columnspan=3, pady=10)

        # Рамка для отображения пароля
        display_frame = ttk.Frame(self.root)
        display_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(display_frame, text="Сгенерированный пароль:").pack(anchor="w")
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(display_frame, textvariable=self.password_var, font=("Courier", 12), width=50)
        self.password_entry.pack(fill="x", pady=5)

        # Кнопка копирования
        copy_btn = ttk.Button(display_frame, text="Копировать в буфер", command=self.copy_to_clipboard)
        copy_btn.pack(pady=5)

        # Рамка для истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица истории
        columns = ("Дата/время", "Пароль", "Длина", "Цифры", "Буквы", "Спецсимволы")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)

        # Настройка заголовков
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)

        self.history_tree.column("Пароль", width=200)
        self.history_tree.column("Дата/время", width=120)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        history_buttons_frame = ttk.Frame(history_frame)
        history_buttons_frame.pack(fill="x", pady=5)

        ttk.Button(history_buttons_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(history_buttons_frame, text="Сохранить историю", command=self.save_history).pack(side="left", padx=5)

        # Настройка сетки для адаптивности
        settings_frame.columnconfigure(1, weight=1)
        display_frame.columnconfigure(0, weight=1)

    def update_length_label(self, value):
        """Обновление отображения длины пароля"""
        self.length_label.config(text=str(int(float(value))))

    def generate_password(self):
        """Генерация пароля на основе выбранных параметров"""
        length = self.password_length.get()

        # Проверка корректности ввода
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа")
            return
        if length > 64:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 64 символа")
            return

        # Формирование пула символов
        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_special.get():
            chars += string.punctuation

        # Проверка, что выбран хотя бы один тип символов
        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return

        # Генерация пароля
        password_chars = []
        # Обеспечиваем, чтобы пароль содержал хотя бы один символ из каждого выбранного типа
        if self.use_digits.get():
            password_chars.append(random.choice(string.digits))
        if self.use_letters.get():
            password_chars.append(random.choice(string.ascii_letters))
        if self.use_special.get():
            password_chars.append(random.choice(string.punctuation))

        # Заполняем остальные символы
        remaining_length = length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(random.choice(chars))

        # Перемешиваем пароль
        random.shuffle(password_chars)
        password = "".join(password_chars)

        # Отображаем пароль
        self.password_var.set(password)

        # Сохраняем в историю
        self.add_to_history(password)

    def add_to_history(self, password):
        """Добавление пароля в историю"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "password": password,
            "length": self.password_length.get(),
            "use_digits": self.use_digits.get(),
            "use_letters": self.use_letters.get(),
            "use_special": self.use_special.get()
        }
        self.history.append(entry)

        # Ограничиваем историю 100 записями
        if len(self.history) > 100:
            self.history = self.history[-100:]

        self.refresh_history_table()
        self.save_history()

    def refresh_history_table(self):
        """Обновление таблицы истории"""
        # Очищаем таблицу
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Добавляем записи из истории
        for entry in reversed(self.history):  # Показываем свежие сверху
            values = (
                entry["timestamp"],
                entry["password"],
                entry["length"],
                "Да" if entry["use_digits"] else "Нет",
                "Да" if entry["use_letters"] else "Нет",
                "Да" if entry["use_special"] else "Нет"
            )
            self.history_tree.insert("", "end", values=values)

    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Внимание", "Нет пароля для копирования")

    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.refresh_history_table()
            self.save_history()
            messagebox.showinfo("Успех", "История очищена")

    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")


def main():
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()