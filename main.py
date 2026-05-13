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
        
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY"]
        self.history = self.load_history()
        self.create_widgets()
    
    def create_widgets(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Сумма:").grid(row=0, column=0, pady=5)
        self.amount_entry = tk.Entry(frame, width=15)
        self.amount_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(frame, text="Из валюты:").grid(row=1, column=0, pady=5)
        self.from_currency = ttk.Combobox(frame, values=self.currencies, width=12)
        self.from_currency.grid(row=1, column=1, pady=5)
        self.from_currency.set("USD")
        
        tk.Label(frame, text="В валюту:").grid(row=2, column=0, pady=5)
        self.to_currency = ttk.Combobox(frame, values=self.currencies, width=12)
        self.to_currency.grid(row=2, column=1, pady=5)
        self.to_currency.set("EUR")
        
        self.convert_btn = tk.Button(frame, text="Конвертировать", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.result_label = tk.Label(frame, text="", font=("Arial", 12, "bold"), fg="blue")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        tk.Label(frame, text="История конвертаций:").grid(row=5, column=0, columnspan=2, pady=5)
        
        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        
        self.tree.grid(row=6, column=0, columnspan=2, pady=5)
        
        self.clear_btn = tk.Button(frame, text="Очистить историю", command=self.clear_history)
        self.clear_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.refresh_history_table()
    
    def convert(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительной")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        # Временный фиктивный курс
        rate = 1.1
        converted = amount * rate
        
        self.result_label.config(text=f"{amount:.2f} {from_curr} = {converted:.2f} {to_curr}")
        
        self.history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "converted": converted
        })
        self.save_history()
        self.refresh_history_table()
    
    def load_history(self):
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)
    
    def refresh_history_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        for entry in self.history[-20:]:
            self.tree.insert("", "end", values=(
                entry["timestamp"],
                entry["amount"],
                entry["from_currency"],
                entry["to_currency"],
                f"{entry['converted']:.2f}"
            ))
    
    def clear_history(self):
        self.history = []
        self.save_history()
        self.refresh_history_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()