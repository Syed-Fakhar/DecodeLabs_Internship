import customtkinter as ctk
from tkinter import messagebox
import json
import os

class ExpenseTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Modern Expense Tracker (PKR)")
        self.geometry("500x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Allow table to expand
        
        # Data Persistence
        self.db_file = "expenses.json"
        self.total_spent = 0.0
        self.expenses = []
        self.load_data()
        
        # UI Elements
        self.setup_ui()
        self.refresh_table()
        self.update_total_display()

    def setup_ui(self):
        # Header
        self.header_label = ctk.CTkLabel(
            self, 
            text="Expense Tracker", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # Appearance Mode Toggle
        self.appearance_mode_label = ctk.CTkLabel(self, text="Appearance Mode:", font=ctk.CTkFont(size=12))
        self.appearance_mode_label.grid(row=1, column=0, padx=20, pady=(0, 5))
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self, 
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode
        )
        self.appearance_mode_optionemenu.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.description_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Expense description (e.g. Rent, Fee)",
            height=40
        )
        self.description_entry.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="ew")

        self.amount_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Enter amount (e.g. 50.00)",
            height=40
        )
        self.amount_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.add_button = ctk.CTkButton(
            self.input_frame, 
            text="Add Expense", 
            command=self.add_expense,
            font=ctk.CTkFont(weight="bold"),
            height=40,
            fg_color="#1f538d",
            hover_color="#14375e"
        )
        self.add_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Expense Table Section
        self.table_label = ctk.CTkLabel(self, text="Expense History", font=ctk.CTkFont(size=16, weight="bold"))
        self.table_label.grid(row=4, column=0, padx=20, pady=(20, 5), sticky="w")

        self.table_frame = ctk.CTkScrollableFrame(self, height=200)
        self.table_frame.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=3)
        self.table_frame.grid_columnconfigure(1, weight=1)

        # Total Display Frame
        self.total_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.total_frame.grid(row=6, column=0, padx=20, pady=10, sticky="nsew")
        self.total_frame.grid_columnconfigure(0, weight=1)

        self.total_label_title = ctk.CTkLabel(
            self.total_frame, 
            text="Total Spent", 
            font=ctk.CTkFont(size=14)
        )
        self.total_label_title.grid(row=0, column=0, padx=20, pady=(5, 0))

        self.total_label_value = ctk.CTkLabel(
            self.total_frame, 
            text="PKR 0.00", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#2fa572"
        )
        self.total_label_value.grid(row=1, column=0, padx=20, pady=(0, 5))

        # Reset Button
        self.reset_button = ctk.CTkButton(
            self, 
            text="Reset All Data", 
            command=self.reset_tracker,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            hover_color=("gray70", "gray30")
        )
        self.reset_button.grid(row=7, column=0, padx=20, pady=(10, 20))

    def add_expense(self):
        description = self.description_entry.get().strip()
        amount_str = self.amount_entry.get()
        
        if not description:
            messagebox.showwarning("Missing Info", "Please enter a description for the expense.")
            return

        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError("Negative value")
            
            # Accumulator Logic: total = total + new_expense
            self.total_spent += amount
            self.expenses.append({
                "amount": amount,
                "description": description
            })
            self.save_data()
            self.update_total_display()
            self.refresh_table()
            
            # Clear fields
            self.amount_entry.delete(0, 'end')
            self.description_entry.delete(0, 'end')
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for the amount.")
            self.amount_entry.delete(0, 'end')

    def update_total_display(self):
        self.total_label_value.configure(text=f"PKR {self.total_spent:,.2f}")

    def reset_tracker(self):
        if messagebox.askyesno("Reset", "Are you sure you want to clear all expenses?"):
            self.total_spent = 0.0
            self.expenses = []
            self.save_data()
            self.update_total_display()
            self.refresh_table()
            self.amount_entry.delete(0, 'end')
            self.description_entry.delete(0, 'end')

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def refresh_table(self):
        """Clears and repopulates the expense table."""
        # Clear existing rows
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Add headers
        header_font = ctk.CTkFont(weight="bold")
        ctk.CTkLabel(self.table_frame, text="Description", font=header_font).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(self.table_frame, text="Amount (PKR)", font=header_font).grid(row=0, column=1, sticky="e", padx=10, pady=5)

        # Add data rows
        for i, expense in enumerate(self.expenses, start=1):
            ctk.CTkLabel(self.table_frame, text=expense["description"]).grid(row=i, column=0, sticky="w", padx=10, pady=2)
            ctk.CTkLabel(self.table_frame, text=f"{expense['amount']:,.2f}").grid(row=i, column=1, sticky="e", padx=10, pady=2)

    def load_data(self):
        """Loads expense data from a JSON file."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    data = json.load(f)
                    self.total_spent = data.get("total_spent", 0.0)
                    self.expenses = data.get("expenses", [])
            except (json.JSONDecodeError, IOError):
                # If file is corrupt or unreadable, start fresh
                self.total_spent = 0.0
                self.expenses = []

    def save_data(self):
        """Saves current expense data to a JSON file."""
        data = {
            "total_spent": self.total_spent,
            "expenses": self.expenses
        }
        try:
            with open(self.db_file, "w") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # Default mode
    ctk.set_default_color_theme("blue")
    
    app = ExpenseTrackerApp()
    app.mainloop()
