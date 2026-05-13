import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")
        
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "KZT"]
        self.history = self.load_history()
        self.create_widgets()
    
    def create_widgets(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        # Поле ввода суммы
        tk.Label(frame, text="Сумма:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.amount_entry = tk.Entry(frame, font=("Arial", 12), width=15)
        self.amount_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Выбор валюты "из"
        tk.Label(frame, text="Из валюты:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.from_currency = ttk.Combobox(frame, values=self.currencies, font=("Arial", 12), width=12)
        self.from_currency.grid(row=1, column=1, pady=5, padx=10)
        self.from_currency.set("USD")
        
        # Выбор валюты "в"
        tk.Label(frame, text="В валюту:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.to_currency = ttk.Combobox(frame, values=self.currencies, font=("Arial", 12), width=12)
        self.to_currency.grid(row=2, column=1, pady=5, padx=10)
        self.to_currency.set("EUR")
        
        # Кнопка конвертации
        self.convert_btn = tk.Button(frame, text="Конвертировать", font=("Arial", 12, "bold"),
                                     bg="#4CAF50", fg="white", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Результат
        self.result_label = tk.Label(frame, text="", font=("Arial", 14, "bold"), fg="blue")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Таблица истории
        tk.Label(frame, text="История конвертаций:", font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", pady=(20, 5))
        
        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        
        self.tree.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=6, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопка очистки истории
        self.clear_btn = tk.Button(frame, text="Очистить историю", font=("Arial", 10),
                                   bg="#f44336", fg="white", command=self.clear_history)
        self.clear_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.refresh_history_table()
    
    def convert(self):
        # Проверка ввода
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число!")
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        # Используем фиксированный курс (для теста без API)
        # В реальном проекте замените на API запрос
        rates = {
            "USD_EUR": 0.92,
            "EUR_USD": 1.09,
            "USD_RUB": 92.50,
            "RUB_USD": 0.0108,
            "USD_GBP": 0.79,
            "GBP_USD": 1.27,
        }
        
        rate_key = f"{from_curr}_{to_curr}"
        rate = rates.get(rate_key, 1.0)
        
        converted_amount = amount * rate
        result_text = f"{amount:.2f} {from_curr} = {converted_amount:.2f} {to_curr}"
        self.result_label.config(text=result_text)
        
        # Сохраняем в историю
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "converted_amount": converted_amount,
            "rate": rate
        }
        self.history.append(history_entry)
        self.save_history()
        self.refresh_history_table()
    
    def load_history(self):
        """Загружает историю из JSON файла"""
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Сохраняет историю в JSON файл"""
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)
    
    def refresh_history_table(self):
        """Обновляет таблицу истории"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Заполняем заново
        for entry in self.history[-20:]:  # Показываем последние 20 записей
            self.tree.insert("", "end", values=(
                entry["timestamp"],
                f"{entry['amount']:.2f}",
                entry["from_currency"],
                entry["to_currency"],
                f"{entry['converted_amount']:.2f}"
            ))
    
    def clear_history(self):
        """Очищает историю"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.refresh_history_table()
            messagebox.showinfo("Готово", "История очищена")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()