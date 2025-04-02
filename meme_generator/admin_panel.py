import tkinter as tk
from tkinter import ttk, messagebox
import json
from utils.password_utils import hash_password
import datetime
import os

LOG_FILE = "logs/admin_actions.log"


class AdminPanel(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

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

        style.configure("TRadiobutton",
            font=("Times New Roman", 11),
            background="#c0f2d8",         # светло-зелёный фон
            foreground="#1e5631",         # тёмно-зелёный текст
            indicatorcolor="#1e5631",     # цвет самого индикатора (иногда работает)
            focuscolor=style.configure(".")["background"],
            relief="flat"
        )

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title("Admin panel")
        self.geometry("500x700")
        self.resizable(False, False)

        self.users_file = "auth/users.json"
        self.users = []
        self.selected_index = None

        ttk.Label(self, text="👤Users", font=("Arial", 14)).pack(pady=10)

        self.user_listbox = tk.Listbox(
            self,
            width=40,
            bg="#c0f2d8",              # светло-зелёный фон
            fg="#000000",              # чёрный текст
            font=("Times New Roman", 11),
            selectbackground="#1e5631",   # цвет выделения (тёмно-зелёный)
            selectforeground="white",     # цвет текста при выделении
            relief="groove",
            borderwidth=2
        )
        self.user_listbox.pack(pady=5)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_select)

        # Радио кнопки для ролей
        ttk.Label(self, text="Роль:").pack()
        self.role_var = tk.StringVar()
        self.radio_frame = ttk.Frame(self)
        self.radio_frame.pack(pady=5)

        ttk.Radiobutton(self.radio_frame, text="trial", variable=self.role_var, value="user").pack(anchor="w")
        ttk.Radiobutton(self.radio_frame, text="pro", variable=self.role_var, value="pro").pack(anchor="w")
        ttk.Radiobutton(self.radio_frame, text="admin", variable=self.role_var, value="admin").pack(anchor="w")


        # Кнопки действий
        ttk.Button(self, text="Save role", command=self.save_role).pack(pady=5)
        ttk.Button(self, text="Change password", command=self.change_password).pack(pady=5)
        ttk.Button(self, text="Delete user", command=self.delete_user).pack(pady=5)
        ttk.Button(self, text="➕Add user", command=self.add_user).pack(pady=5)
        ttk.Button(self, text="Close", command=self.on_close).pack(pady=10)
        ttk.Label(self, text="📝 Recent admin actions:", font=("Arial", 10)).pack(pady=(20, 0))

        self.log_display = tk.Text(
            self,
            height=5,
            width=80,
            state="disabled",
            bg="#c0f2d8",  # светло-зелёный фон
            fg="#000000",  # чёрный текст
            font=("Times New Roman", 11),
            relief="groove",
            borderwidth=2
        )
        self.log_display.pack(pady=5)
        self.load_users()
        self.load_log_entries()

    def load_log_entries(self, last_n=5):
        if not os.path.exists(LOG_FILE):
            return

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        recent = lines[-last_n:] if len(lines) >= last_n else lines

        self.log_display.config(state="normal")
        self.log_display.delete(1.0, tk.END)
        for line in recent:
            self.log_display.insert(tk.END, line)
        self.log_display.config(state="disabled")

    def load_users(self):
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                self.users = json.load(f)
            self.refresh_listbox()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users.json: {e}")

    def refresh_listbox(self):
        self.user_listbox.delete(0, tk.END)
        for user in self.users:
            self.user_listbox.insert(tk.END, f"{user['username']} ({user['role']})")

    def on_select(self, event):
        selection = self.user_listbox.curselection()
        if selection:
            self.selected_index = selection[0]
            selected_user = self.users[self.selected_index]
            self.role_var.set(selected_user['role'])

    def save_role(self):
        if self.selected_index is not None:
            new_role = self.role_var.get()
            selected_user = self.users[self.selected_index]

            if selected_user['username'] == self.master.username:
                messagebox.showwarning("Forbidden", "You cannot change your own role.")
                return

            if new_role in ["user", "pro", "admin"]:
                old_role = selected_user['role']
                selected_user['role'] = new_role
                self.save_users()
                self.refresh_listbox()
                self.load_log_entries()
                log_admin_action(f"{self.master.username} changed role {selected_user['username']} с {old_role} на {new_role}")
                messagebox.showinfo("Success", "Role updated.")


    def change_password(self):
        if self.selected_index is not None:
            user = self.users[self.selected_index]
            password_window = tk.Toplevel(self)
            password_window.title("Change password")
            password_window.geometry("300x180")
            password_window.configure(bg="#1e5631")
            password_window.resizable(False, False)

            ttk.Label(password_window, text=f"New password for {user['username']}:").pack(pady=5)
            password_entry = ttk.Entry(password_window, show="*")
            password_entry.pack(pady=5)

            ttk.Label(password_window, text="Confirm password:").pack(pady=5)
            confirm_entry = ttk.Entry(password_window, show="*")
            confirm_entry.pack(pady=5)

            def confirm():
                new_pass = password_entry.get()
                confirm_pass = confirm_entry.get()

                if not new_pass:
                    messagebox.showwarning("Error", "Password cannot be empty.")
                    return

                if new_pass != confirm_pass:
                    messagebox.showwarning("Error", "Passwords do not match.")
                    return

                user['password'] = hash_password(new_pass)
                self.save_users()
                log_admin_action(f"{self.master.username} changed passoword {user['username']}")
                self.load_log_entries()
                messagebox.showinfo("Success", "Password changed.")
                password_window.destroy()

            ttk.Button(password_window, text="Save", command=confirm).pack(pady=10)

    def delete_user(self):
        if self.selected_index is not None:
            user = self.users.pop(self.selected_index)
            log_admin_action(f"{self.master.username} deleted user {user['username']}")
            self.load_log_entries()
            self.save_users()
            self.refresh_listbox()
            self.selected_index = None
            messagebox.showinfo("Deleted", f"User {user['username']} has been deleted.")

    def on_close(self):
        self.master.deiconify()  # Показать главное окно
        self.destroy()

    def add_user(self):
        add_window = tk.Toplevel(self)
        add_window.title("Add user")
        add_window.geometry("300x300")
        add_window.configure(bg="#1e5631")
        add_window.resizable(False, False)

        ttk.Label(add_window, text="Username:").pack(pady=5)
        username_entry = ttk.Entry(add_window)
        username_entry.pack(pady=5)

        ttk.Label(add_window, text="Password:").pack(pady=5)
        password_entry = ttk.Entry(add_window, show="*")
        password_entry.pack(pady=5)

        ttk.Label(add_window, text="Re-enter password:").pack(pady=5)
        confirm_entry = ttk.Entry(add_window, show="*")
        confirm_entry.pack(pady=5)

        ttk.Label(add_window, text="Role:").pack(pady=5)
        role_var = tk.StringVar(value="user")
        role_combo = ttk.Combobox(add_window, textvariable=role_var, state="readonly")
        role_combo['values'] = ["user", "pro", "admin"]
        role_combo.current(0)
        role_combo.pack(pady=5)

        def confirm():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            confirm_password = confirm_entry.get().strip()
            role = role_var.get()

            if not username or not password:
                messagebox.showwarning("Error", "Username and password are required.")
                return

            if password != confirm_password:
                messagebox.showwarning("Error", "Passwords do not match.")
                return

            if any(u['username'] == username for u in self.users):
                messagebox.showwarning("Error", "A user with this username already exists.")
                return

            self.users.append({
                "username": username,
                "password": hash_password(password),
                "role": role
            })
            self.save_users()
            self.refresh_listbox()
            add_window.destroy()
            log_admin_action(f"{self.master.username} added user {username} ({role})")
            self.load_log_entries()
            messagebox.showinfo("Success", f"User {username} has been added.")

        ttk.Button(add_window, text="Add", command=confirm).pack(pady=10)

    def save_users(self):
        try:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save users.json: {e}")

def log_admin_action(text):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {text}\n")
