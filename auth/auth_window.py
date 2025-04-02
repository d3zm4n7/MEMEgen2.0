# auth/auth_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from utils.password_utils import hash_password, check_password
from meme_generator.main_window import MainWindow
import webbrowser
import subprocess
import os


USERS_FILE = "auth/users.json"

class AuthWindow(tk.Tk):
    def __init__(self):
        super().__init__()

       # Тёмно-зелёная тема для Tkinter + ttk
        self.configure(bg="#1e5631")  # фон окна

        style = ttk.Style()
        style.theme_use("default")

        # Надписи
        style.configure("TLabel", font=("Times New Roman", 12),
                        background="#1e5631", foreground="white")

        # Поля ввода
        style.configure("TEntry", font=("Times New Roman", 10),
                        fieldbackground="#c0f2d8", background="white", foreground="#1e5631")

        # Кнопки
        style.configure("TButton", font=("Times New Roman", 10),
                        background="#c0f2d8", foreground="#1e5631", padding=6)
        style.map("TButton", background=[("active", "#a0e8c3")])

        # LabelFrame (рамки)
        style.configure("TLabelframe", background="#1e5631", foreground="white")
        style.configure("TLabelframe.Label", background="#1e5631", foreground="white", font=("Times New Roman", 10, "bold"))


        # Вкладки
        style.configure("TNotebook", background="#1e5631", borderwidth=0)
        style.configure("TNotebook.Tab",
            font=("Times New Roman", 10),
            padding=[10, 5],
            background="#c0f2d8",
            foreground="#1e5631"
        )
        
        style.map("TNotebook.Tab",
            background=[("selected", "#1e5631")],
            foreground=[("selected", "white")])
        
        style.configure("TCombobox",
            fieldbackground="#c0f2d8",   # фон ввода
            background="#c0f2d8",        # фон выпадающего списка
            foreground="#1e5631",        # цвет текста
            font=("Times New Roman", 11)
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", "#c0f2d8")],
            foreground=[("readonly", "#1e5631")]
        )


        self.title("MEMEgen2.0 — Login/Register")
        self.geometry("400x400")
        self.resizable(False, False)

        self.tabControl = ttk.Notebook(self)
        self.login_tab = ttk.Frame(self.tabControl)
        self.login_tab = tk.Frame(self.tabControl, bg="#1e5631")
        self.register_tab = ttk.Frame(self.tabControl)
        self.register_tab = tk.Frame(self.tabControl, bg="#1e5631")
        self.tabControl.add(self.login_tab, text='Login')
        self.tabControl.add(self.register_tab, text='Register')
        self.tabControl.pack(expand=1, fill="both")

        info_frame = ttk.LabelFrame(self, text="About MEMEgen2.0", padding=5, style="TLabelframe")
        info_frame.pack(side="bottom", pady=10, padx=10, fill="x")

        # Вставка строки с версией + кнопки справа
        ttk.Label(
            info_frame,
            text="V.2.0.0.1 | © Kerya 2025",
            font=("Times New Roman", 10, "bold"),  # <— жирность!
            foreground="white",
            background="#1e5631"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")


        ttk.Button(info_frame, text="📄 Documents", width=18,
                   command=self.open_docs).grid(row=0, column=1)

        ttk.Button(info_frame, text="🔗 GitHub", width=12,
                   command=self.open_github).grid(row=0, column=2, padx=4, pady=5)


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

        button_frame = tk.Frame(self.login_tab, bg="#1e5631")
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Log in", command=self.login).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Sign Up", command=self.show_register_tab).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Exit", command=self.quit_app).grid(row=0, column=2, padx=10)

        self.login_tab.bind_all("<Return>", lambda event: self.login())

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
        self.reg_role = ttk.Combobox(
            self.register_tab,
            values=["user", "pro"],
            state="readonly"
        )
        self.reg_role.pack()

        # Кнопки Register и Back
        button_frame = tk.Frame(self.register_tab, bg="#1e5631")
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Register", command=self.register).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=self.show_login_tab).grid(row=0, column=1, padx=10)


    def show_register_tab(self):
        self.tabControl.select(self.register_tab)

    def show_login_tab(self):
        self.tabControl.select(self.login_tab)

    def quit_app(self):
        self.destroy()



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

    def open_docs(self):
        path = "PROJECT_STRUCTURE.md"
        if os.path.exists(path):
            try:
                subprocess.Popen(["notepad", path])  # Windows
            except Exception:
                messagebox.showerror("Ошибка", "Не удалось открыть файл.")
        else:
            messagebox.showwarning("Документация", "Файл PROJECT_STRUCTURE.md не найден.")

    def open_github(self):
        webbrowser.open_new("https://github.com/d3zm4n7/MEMEgen2.0")  # Подставим, когда будет реальный URL

