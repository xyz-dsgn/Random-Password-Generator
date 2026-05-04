import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator - Генератор паролей")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Data storage
        self.history = []
        self.history_file = "password_history.json"
        
        # Load existing history
        self.load_history()
        
        # Password character sets
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Setup UI
        self.setup_ui()
        
        # Generate first password
        self.generate_password()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ==================== PASSWORD DISPLAY FRAME ====================
        display_frame = ttk.LabelFrame(main_frame, text="Сгенерированный пароль", padding="10")
        display_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(display_frame, textvariable=self.password_var, 
                                        font=("Courier", 14), width=40, state="readonly")
        self.password_entry.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.copy_button = ttk.Button(display_frame, text="Копировать", command=self.copy_to_clipboard)
        self.copy_button.grid(row=0, column=1, padx=5, pady=5)
        
        # ==================== SETTINGS FRAME ====================
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки пароля", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Length
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.length_var = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(settings_frame, from_=4, to=32, orient=tk.HORIZONTAL, 
                                       variable=self.length_var, command=self.update_length_label)
        self.length_scale.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Checkboxes
        self.use_uppercase_var = tk.BooleanVar(value=True)
        self.use_uppercase_check = ttk.Checkbutton(settings_frame, text="Заглавные буквы (A-Z)", 
                                                    variable=self.use_uppercase_var)
        self.use_uppercase_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        self.use_lowercase_var = tk.BooleanVar(value=True)
        self.use_lowercase_check = ttk.Checkbutton(settings_frame, text="Строчные буквы (a-z)", 
                                                    variable=self.use_lowercase_var)
        self.use_lowercase_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        self.use_digits_var = tk.BooleanVar(value=True)
        self.use_digits_check = ttk.Checkbutton(settings_frame, text="Цифры (0-9)", 
                                                 variable=self.use_digits_var)
        self.use_digits_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        self.use_special_var = tk.BooleanVar(value=False)
        self.use_special_check = ttk.Checkbutton(settings_frame, text="Специальные символы (!@#$%^&*)", 
                                                  variable=self.use_special_var)
        self.use_special_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Generate button
        self.generate_button = ttk.Button(settings_frame, text="Сгенерировать пароль", 
                                          command=self.generate_password)
        self.generate_button.grid(row=5, column=0, columnspan=3, pady=10)
        
        # ==================== HISTORY FRAME ====================
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding="10")
        history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create Treeview
        columns = ("Дата", "Пароль", "Длина", "Символы")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        
        # Define headings
        self.tree.heading("Дата", text="Дата и время")
        self.tree.heading("Пароль", text="Пароль")
        self.tree.heading("Длина", text="Длина")
        self.tree.heading("Символы", text="Использованные символы")
        
        # Define columns
        self.tree.column("Дата", width=150)
        self.tree.column("Пароль", width=250)
        self.tree.column("Длина", width=80)
        self.tree.column("Символы", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for table
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # ==================== BUTTONS FRAME ====================
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Clear history button
        self.clear_button = ttk.Button(buttons_frame, text="Очистить историю", command=self.clear_history)
        self.clear_button.grid(row=0, column=0, padx=5)
        
        # Save button
        self.save_button = ttk.Button(buttons_frame, text="Сохранить историю", command=self.save_history)
        self.save_button.grid(row=0, column=1, padx=5)
        
        # Load button
        self.load_button = ttk.Button(buttons_frame, text="Загрузить историю", command=self.load_history)
        self.load_button.grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        display_frame.columnconfigure(0, weight=1)
    
    def update_length_label(self, event=None):
        """Update length label when slider moves"""
        self.length_label.config(text=str(int(self.length_var.get())))
    
    def get_character_set(self):
        """Get the character set based on selected options"""
        chars = ""
        
        if self.use_lowercase_var.get():
            chars += self.lowercase
        if self.use_uppercase_var.get():
            chars += self.uppercase
        if self.use_digits_var.get():
            chars += self.digits
        if self.use_special_var.get():
            chars += self.special_chars
            
        return chars
    
    def get_selected_options(self):
        """Get string of selected character types"""
        options = []
        if self.use_lowercase_var.get():
            options.append("a-z")
        if self.use_uppercase_var.get():
            options.append("A-Z")
        if self.use_digits_var.get():
            options.append("0-9")
        if self.use_special_var.get():
            options.append("!@#$%")
        return ", ".join(options) if options else "Нет"
    
    def generate_password(self):
        """Generate a random password"""
        length = int(self.length_var.get())
        
        # Validate length
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 32 символа")
            return
        
        # Get character set
        chars = self.get_character_set()
        
        # Check if at least one character type is selected
        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return
        
        # Generate password
        password = []
        for _ in range(length):
            password.append(random.choice(chars))
        
        # Shuffle to ensure randomness
        random.shuffle(password)
        password_str = ''.join(password)
        
        # Display password
        self.password_var.set(password_str)
        
        # Add to history
        self.add_to_history(password_str, length)
    
    def add_to_history(self, password, length):
        """Add generated password to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        options = self.get_selected_options()
        
        record = {
            "timestamp": timestamp,
            "password": password,
            "length": length,
            "options": options
        }
        
        self.history.insert(0, record)  # Add to beginning
        self.refresh_history_table()
        self.save_history()
    
    def refresh_history_table(self):
        """Refresh the history table"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add history items
        for record in self.history:
            self.tree.insert("", tk.END, values=(
                record['timestamp'],
                record['password'],
                record['length'],
                record['options']
            ))
    
    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.refresh_history_table()
            self.save_history()
            messagebox.showinfo("Успех", "История очищена")
    
    def copy_to_clipboard(self):
        """Copy generated password to clipboard"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования")
    
    def save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
            return False
    
    def load_history(self):
        """Load history from JSON file"""
        if not os.path.exists(self.history_file):
            self.history = []
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
            self.refresh_history_table()
            messagebox.showinfo("Успех", f"Загружено {len(self.history)} паролей из истории")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")
            self.history = []
            return False

def main():
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()