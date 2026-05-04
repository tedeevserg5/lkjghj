import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry


class ExpenseTrackerApp:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("900x650")

        self.data_file = "data.json"
        self.expenses = []
        self.load_data()
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="Добавление расхода", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=5)

        ttk.Label(row1, text="Сумма (₽):", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.amount_entry = ttk.Entry(row1, width=15)
        self.amount_entry.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(row1, text="Категория:", width=12).pack(side=tk.LEFT, padx=(0, 5))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(row1, textvariable=self.category_var,
                                           values=["Еда", "Транспорт", "Развлечения",
                                                   "Жильё", "Здоровье", "Образование",
                                                   "Одежда", "Другое"], width=15)
        self.category_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.category_combo.set("Еда")

        ttk.Label(row1, text="Дата:", width=8).pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry = DateEntry(row1, width=12, background='darkblue',
                                    foreground='white', borderwidth=2,
                                    date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side=tk.LEFT)

        row2 = ttk.Frame(input_frame)
        row2.pack(fill=tk.X, pady=(10, 0))

        self.add_button = ttk.Button(row2, text="Добавить расход", command=self.add_expense)
        self.add_button.pack(side=tk.LEFT)

        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        filter_row = ttk.Frame(filter_frame)
        filter_row.pack(fill=tk.X)

        ttk.Label(filter_row, text="Категория:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_category_combo = ttk.Combobox(filter_row, textvariable=self.filter_category_var,
                                                  values=["Все", "Еда", "Транспорт", "Развлечения",
                                                          "Жильё", "Здоровье", "Образование",
                                                          "Одежда", "Другое"], width=15)
        self.filter_category_combo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(filter_row, text="Дата с:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_from = DateEntry(filter_row, width=10, date_pattern='yyyy-mm-dd')
        self.date_from.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(filter_row, text="по:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_to = DateEntry(filter_row, width=10, date_pattern='yyyy-mm-dd')
        self.date_to.pack(side=tk.LEFT)

        self.filter_button = ttk.Button(filter_row, text="Применить фильтр", command=self.apply_filter)
        self.filter_button.pack(side=tk.LEFT, padx=(20, 0))

        self.reset_button = ttk.Button(filter_row, text="Сбросить", command=self.reset_filter)
        self.reset_button.pack(side=tk.LEFT, padx=(5, 0))

        sum_frame = ttk.LabelFrame(main_frame, text="Подсчёт суммы за период", padding="10")
        sum_frame.pack(fill=tk.X, pady=(0, 10))

        sum_row = ttk.Frame(sum_frame)
        sum_row.pack(fill=tk.X)

        ttk.Label(sum_row, text="с:").pack(side=tk.LEFT, padx=(0, 5))
        self.sum_date_from = DateEntry(sum_row, width=10, date_pattern='yyyy-mm-dd')
        self.sum_date_from.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(sum_row, text="по:").pack(side=tk.LEFT, padx=(0, 5))
        self.sum_date_to = DateEntry(sum_row, width=10, date_pattern='yyyy-mm-dd')
        self.sum_date_to.pack(side=tk.LEFT, padx=(0, 20))

        self.sum_button = ttk.Button(sum_row, text="Рассчитать сумму", command=self.calculate_sum)
        self.sum_button.pack(side=tk.LEFT)

        self.sum_label = ttk.Label(sum_row, text="Итого: 0.00 ₽", font=('Arial', 12, 'bold'), foreground="green")
        self.sum_label.pack(side=tk.LEFT, padx=(20, 0))

        table_frame = ttk.LabelFrame(main_frame, text="Список расходов", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Дата", "Категория", "Сумма (₽)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("ID", text="№")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Сумма (₽)", text="Сумма (₽)")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Дата", width=120, anchor="center")
        self.tree.column("Категория", width=150, anchor="center")
        self.tree.column("Сумма (₽)", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        self.delete_button = ttk.Button(control_frame, text="Удалить выбранное", command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT)

    def add_expense(self):
        try:
            amount_str = self.amount_entry.get().strip()
            category = self.category_var.get().strip()
            date = self.date_entry.get()

            if not amount_str:
                messagebox.showerror("Ошибка", "Введите сумму!")
                return

            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом!")
                return

            if not category:
                messagebox.showerror("Ошибка", "Выберите категорию!")
                return

            expense = {
                "id": len(self.expenses) + 1,
                "amount": amount,
                "category": category,
                "date": date
            }

            self.expenses.append(expense)
            self.save_data()
            self.refresh_table()
            self.amount_entry.delete(0, tk.END)
            messagebox.showinfo("Успех", f"Расход {amount:.2f} ₽ добавлен!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить запись?"):
            item = self.tree.item(selected[0])
            values = item['values']
            expense_id = values[0]

            self.expenses = [e for e in self.expenses if e["id"] != expense_id]

            for i, expense in enumerate(self.expenses, 1):
                expense["id"] = i

            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Запись удалена!")

    def refresh_table(self, expenses_list=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = expenses_list if expenses_list is not None else self.expenses

        for expense in data:
            self.tree.insert("", tk.END, values=(
                expense["id"],
                expense["date"],
                expense["category"],
                f"{expense['amount']:.2f}"
            ))

    def apply_filter(self):
        filtered = self.expenses.copy()

        category = self.filter_category_var.get()
        if category != "Все":
            filtered = [e for e in filtered if e["category"] == category]

        date_from = self.date_from.get()
        date_to = self.date_to.get()

        filtered = [e for e in filtered if date_from <= e["date"] <= date_to]

        self.refresh_table(filtered)
        messagebox.showinfo("Фильтрация", f"Найдено: {len(filtered)}")

    def reset_filter(self):
        self.filter_category_var.set("Все")
        self.refresh_table()
        messagebox.showinfo("Фильтр", "Фильтры сброшены")

    def calculate_sum(self):
        try:
            date_from = self.sum_date_from.get()
            date_to = self.sum_date_to.get()

            filtered = [e for e in self.expenses if date_from <= e["date"] <= date_to]
            total = sum(e["amount"] for e in filtered)

            self.sum_label.config(text=f"Итого: {total:.2f} ₽")

            if filtered:
                messagebox.showinfo("Статистика",
                                    f"За период {date_from} — {date_to}\n"
                                    f"Количество: {len(filtered)}\n"
                                    f"Сумма: {total:.2f} ₽\n"
                                    f"Средний: {total / len(filtered):.2f} ₽")
            else:
                messagebox.showinfo("Статистика", "Расходов не найдено")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except:
                self.expenses = []
        else:
            self.expenses = []

    def run(self):
        self.root.mainloop()