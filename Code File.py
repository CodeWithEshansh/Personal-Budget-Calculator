import time
import json
import tkinter as tk
from tkinter import messagebox, ttk

# -------------------- MODELS -------------------- #
class Expense:
    def __init__(self, category, subcategory, amount):
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be positive")

        self.category = category
        self.subcategory = subcategory
        self.amount = amount
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "category": self.category,
            "subcategory": self.subcategory,
            "amount": self.amount,
            "timestamp": self.timestamp
        }


class BudgetManager:
    def __init__(self):
        self.expenses = []
        self.categories = {
            "Essentials": ["Groceries", "Utilities"],
            "Entertainment": ["Movies", "Games"],
            "Dining Out": ["Restaurants", "Takeout"],
            "Transportation": ["Gas", "Public Transport"],
            "Miscellaneous": ["Shopping", "Health"]
        }

        self.monthly_budget = {
            "Essentials": 1350,
            "Entertainment": 1350,
            "Dining Out": 1700,
            "Transportation": 1000,
            "Miscellaneous": 1200
        }

    def add_expense(self, category, subcategory, amount):
        if category not in self.categories:
            raise ValueError("Invalid category")
        if subcategory not in self.categories[category]:
            raise ValueError("Invalid subcategory")

        exp = Expense(category, subcategory, amount)
        self.expenses.append(exp)

    def total_expenses(self):
        return sum(e.amount for e in self.expenses)

    def remaining_budget(self):
        remaining = {}
        for cat in self.monthly_budget:
            spent = sum(e.amount for e in self.expenses if e.category == cat)
            remaining[cat] = self.monthly_budget[cat] - spent
        return remaining

    def save(self):
        with open("expenses.json", "w") as f:
            json.dump([e.to_dict() for e in self.expenses], f, indent=4)

    def load(self):
        try:
            with open("expenses.json", "r") as f:
                data = json.load(f)
                for d in data:
                    e = Expense(d["category"], d["subcategory"], d["amount"])
                    e.timestamp = d["timestamp"]
                    self.expenses.append(e)
        except:
            pass


# -------------------- GUI -------------------- #
class BudgetApp:
    def __init__(self, root):
        self.manager = BudgetManager()
        self.manager.load()

        self.root = root
        self.root.title("Personal Budget Calculator")
        self.root.geometry("450x500")
        
        # Main Container
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # --- Input Section ---
        tk.Label(main_frame, text="Category:").grid(row=0, column=0, sticky="w", pady=5)
        self.cat_combo = ttk.Combobox(main_frame, values=list(self.manager.categories.keys()), state="readonly")
        self.cat_combo.grid(row=0, column=1, pady=5, sticky="ew")
        self.cat_combo.bind("<<ComboboxSelected>>", self.update_subcategories)

        tk.Label(main_frame, text="Subcategory:").grid(row=1, column=0, sticky="w", pady=5)
        self.sub_combo = ttk.Combobox(main_frame, state="readonly")
        self.sub_combo.grid(row=1, column=1, pady=5, sticky="ew")

        tk.Label(main_frame, text="Amount (₹):").grid(row=2, column=0, sticky="w", pady=5)
        self.amt_entry = tk.Entry(main_frame)
        self.amt_entry.grid(row=2, column=1, pady=5, sticky="ew")

        # --- Button Section ---
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

        tk.Button(btn_frame, text="Add Expense", command=self.add_expense, width=15, bg="#e1f5fe").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Save Data", command=self.save_data, width=15, bg="#e8f5e9").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="View Total", command=self.show_total, width=15).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="View Remaining", command=self.show_remaining, width=15).grid(row=1, column=1, padx=5, pady=5)

        # --- Output Section ---
        self.output = tk.Text(main_frame, height=10, width=45, wrap="word", font=("Arial", 9))
        self.output.grid(row=4, column=0, columnspan=2, pady=10)

    def update_subcategories(self, event=None):
        """Updates the subcategory dropdown based on chosen category."""
        selected_cat = self.cat_combo.get()
        if selected_cat in self.manager.categories:
            self.sub_combo.config(values=self.manager.categories[selected_cat])
            self.sub_combo.set("") # Clear previous selection

    def add_expense(self):
        try:
            cat = self.cat_combo.get()
            sub = self.sub_combo.get()
            amt_str = self.amt_entry.get()
            
            if not cat or not sub or not amt_str:
                raise ValueError("All fields are required")
                
            amt = float(amt_str)
            self.manager.add_expense(cat, sub, amt)
            messagebox.showinfo("Success", f"Added ₹{amt} to {sub}")
            self.amt_entry.delete(0, tk.END)

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", "Check your inputs")

    def show_total(self):
        total = self.manager.total_expenses()
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"--- SUMMARY ---\nTotal Expenses: ₹{total:.2f}")

    def show_remaining(self):
        data = self.manager.remaining_budget()
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"{'Category':<20} | {'Remaining Budget':<15}\n")
        self.output.insert(tk.END, "-"*40 + "\n")
        for k, v in data.items():
            self.output.insert(tk.END, f"{k:<20} | ₹{v:>10.2f}\n")

    def save_data(self):
        self.manager.save()
        messagebox.showinfo("Saved", "Data saved successfully to expenses.json")


# -------------------- RUN -------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()