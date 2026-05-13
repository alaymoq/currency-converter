import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# Конфигурация
API_KEY = "5629257a47806ee961dd03a2"
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"

HISTORY_FILE = "history.json"

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Загрузка доступных валют (заглушка, позже обновим из API)
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "KZT", "UAH", "TRY"]
        
        # Загрузка истории из файла
        self.history = self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление списка валют из API
        self.update_currency_list()
    
    def create_widgets(self):
        # Рамка для конвертации
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
        
        # Создаём таблицу (Treeview)
        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        
        self.tree.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=6, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки управления историей
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Очистить историю", command=self.clear_history, bg="#f44336", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Обновить курс валют", command=self.update_currency_list, bg="#2196F3", fg="white").pack(side="left", padx=5)
        
        # Загрузка истории в таблицу
        self.refresh_history_table()
    
    def update_currency_list(self):
        """Получает список доступных валют из API"""
        try:
            response = requests.get(BASE_URL + "USD", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["result"] == "success":
                    currencies = list(data["conversion_rates"].keys())
                    self.currencies = sorted(currencies)
                    
                    # Обновляем значения в Combobox
                    self.from_currency['values'] = self.currencies
                    self.to_currency['values'] = self.currencies
                    messagebox.showinfo("Успех", f"Загружено {len(self.currencies)} валют")
            else:
                messagebox.showwarning("Предупреждение", "Не удалось загрузить список валют. Используются стандартные.")
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Ошибка загрузки валют: {e}")
    
    def convert(self):
        """Конвертирует валюту и сохраняет в историю"""
        # Проверка корректности ввода суммы
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число в поле суммы!")
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        if not from_curr or not to_curr:
            messagebox.showerror("Ошибка", "Выберите обе валюты!")
            return
        
        # Получение курса из API
        try:
            url = BASE_URL + from_curr
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data["result"] == "success":
                rate = data["conversion_rates"].get(to_curr)
                if rate:
                    converted_amount = amount * rate
                    result_text = f"{amount:.2f} {from_curr} = {converted_amount:.2f} {to_curr} (курс: {rate:.4f})"
                    self.result_label.config(text=result_text)
                    
                    # Сохранение в историю
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
                else:
                    messagebox.showerror("Ошибка", f"Валюта {to_curr} не найдена")
            else:
                messagebox.showerror("Ошибка", "Не удалось получить курс. Проверьте API-ключ или интернет-соединение.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения с API: {e}")
    
    def load_history(self):
        """Загружает историю из JSON файла"""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Сохраняет историю в JSON файл"""
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
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

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()