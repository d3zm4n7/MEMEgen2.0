# auth/auth_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from utils.password_utils import hash_password, check_password
from meme_generator.main_window import MainWindow

USERS_FILE = "auth/users.json"

class AuthWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MEMEgen2.0 — Login/Register")
        self.geometry("400x300")
        self.resizable(False, False)

        self.tabControl = ttk.Notebook(self)
        self.login_tab = ttk.Frame(self.tabControl)
        self.register_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.login_tab, text='Login')
        self.tabControl.add(self.register_tab, text='Register')
        self.tabControl.pack(expand=1, fill="both")

        self.create_login_tab()
        self.create_register_tab()

    def load_users(self):
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r') as f:
            return json.load(f)

    def save_users(self, users):
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

    def create_login_tab(self):
        ttk.Label(self.login_tab, text="Username:").pack(pady=5)
        self.login_username = ttk.Entry(self.login_tab)
        self.login_username.pack()

        ttk.Label(self.login_tab, text="Password:").pack(pady=5)
        self.login_password = ttk.Entry(self.login_tab, show="*")
        self.login_password.pack()

        ttk.Button(self.login_tab, text="Login", command=self.login).pack(pady=10)

    def create_register_tab(self):
        ttk.Label(self.register_tab, text="Username:").pack(pady=5)
        self.reg_username = ttk.Entry(self.register_tab)
        self.reg_username.pack()

        ttk.Label(self.register_tab, text="Password:").pack(pady=5)
        self.reg_password = ttk.Entry(self.register_tab, show="*")
        self.reg_password.pack()

        ttk.Label(self.register_tab, text="Confirm Password:").pack(pady=5)
        self.reg_confirm = ttk.Entry(self.register_tab, show="*")
        self.reg_confirm.pack()

        ttk.Label(self.register_tab, text="Role (user/pro):").pack(pady=5)
        self.reg_role = ttk.Combobox(self.register_tab, values=["user", "pro"])
        self.reg_role.pack()

        ttk.Button(self.register_tab, text="Register", command=self.register).pack(pady=10)


    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()

        users = self.load_users()
        for user in users:
            if user['username'] == username and check_password(password, user['password']):
                messagebox.showinfo("Login successful", f"Welcome {username}! Role: {user['role']}")
                self.destroy()
                main = MainWindow(username, user['role'])
                main.mainloop()  # Закрываем окно авторизации
                return
        messagebox.showerror("Login failed", "Invalid username or password")

    def register(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        role = self.reg_role.get()

        if password != confirm:
            messagebox.showerror("Error", "Пароли не совпадают!")
            return

        if role not in ['user', 'pro']:
            messagebox.showerror("Error", "Role must be 'user' or 'pro'")
            return

        users = self.load_users()
        if any(u['username'] == username for u in users):
            messagebox.showerror("Error", "Username already exists")
            return

        users.append({
            "username": username,
            "password": hash_password(password),
            "role": role
        })
        self.save_users(users)
        messagebox.showinfo("Success", "User registered!")
