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
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title("Панель администратора")
        self.geometry("500x700")
        self.resizable(False, False)

        self.users_file = "auth/users.json"
        self.users = []
        self.selected_index = None

        ttk.Label(self, text="👤 Пользователи", font=("Arial", 14)).pack(pady=10)

        self.user_listbox = tk.Listbox(self, width=40)
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
        ttk.Button(self, text="Сохранить роль", command=self.save_role).pack(pady=5)
        ttk.Button(self, text="Сменить пароль", command=self.change_password).pack(pady=5)
        ttk.Button(self, text="Удалить пользователя", command=self.delete_user).pack(pady=5)
        ttk.Button(self, text="➕ Добавить пользователя", command=self.add_user).pack(pady=5)
        ttk.Button(self, text="Закрыть", command=self.on_close).pack(pady=10)
        ttk.Label(self, text="📝 Последние действия администратора:", font=("Arial", 10)).pack(pady=(20, 0))

        self.log_display = tk.Text(self, height=5, width=80, state="disabled", bg="#f5f5f5", relief="groove")
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
            messagebox.showerror("Ошибка", f"Не удалось загрузить users.json: {e}")

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
                messagebox.showwarning("Запрещено", "Вы не можете изменить свою собственную роль.")
                return

            if new_role in ["user", "pro", "admin"]:
                old_role = selected_user['role']
                selected_user['role'] = new_role
                self.save_users()
                self.refresh_listbox()
                self.load_log_entries()
                log_admin_action(f"{self.master.username} изменил роль {selected_user['username']} с {old_role} на {new_role}")
                messagebox.showinfo("Успешно", "Роль обновлена.")


    def change_password(self):
        if self.selected_index is not None:
            user = self.users[self.selected_index]
            password_window = tk.Toplevel(self)
            password_window.title("Смена пароля")
            password_window.geometry("300x180")
            password_window.resizable(False, False)

            ttk.Label(password_window, text=f"Новый пароль для {user['username']}:").pack(pady=5)
            password_entry = ttk.Entry(password_window, show="*")
            password_entry.pack(pady=5)

            ttk.Label(password_window, text="Подтвердите пароль:").pack(pady=5)
            confirm_entry = ttk.Entry(password_window, show="*")
            confirm_entry.pack(pady=5)

            def confirm():
                new_pass = password_entry.get()
                confirm_pass = confirm_entry.get()

                if not new_pass:
                    messagebox.showwarning("Ошибка", "Пароль не может быть пустым.")
                    return

                if new_pass != confirm_pass:
                    messagebox.showwarning("Ошибка", "Пароли не совпадают.")
                    return

                user['password'] = hash_password(new_pass)
                self.save_users()
                log_admin_action(f"{self.master.username} сменил пароль {user['username']}")
                self.load_log_entries()
                messagebox.showinfo("Успешно", "Пароль изменён.")
                password_window.destroy()

            ttk.Button(password_window, text="Сохранить", command=confirm).pack(pady=10)

    def delete_user(self):
        if self.selected_index is not None:
            user = self.users.pop(self.selected_index)
            log_admin_action(f"{self.master.username} удалил пользователя {user['username']}")
            self.load_log_entries()
            self.save_users()
            self.refresh_listbox()
            self.selected_index = None
            messagebox.showinfo("Удалено", f"Пользователь {user['username']} удалён.")

    def on_close(self):
        self.master.deiconify()  # Показать главное окно
        self.destroy()

    def add_user(self):
        add_window = tk.Toplevel(self)
        add_window.title("Добавить пользователя")
        add_window.geometry("300x300")
        add_window.resizable(False, False)

        ttk.Label(add_window, text="Имя пользователя:").pack(pady=5)
        username_entry = ttk.Entry(add_window)
        username_entry.pack(pady=5)

        ttk.Label(add_window, text="Пароль:").pack(pady=5)
        password_entry = ttk.Entry(add_window, show="*")
        password_entry.pack(pady=5)

        ttk.Label(add_window, text="Подтвердите пароль:").pack(pady=5)
        confirm_entry = ttk.Entry(add_window, show="*")
        confirm_entry.pack(pady=5)

        ttk.Label(add_window, text="Роль:").pack(pady=5)
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
                messagebox.showwarning("Ошибка", "Имя пользователя и пароль обязательны.")
                return

            if password != confirm_password:
                messagebox.showwarning("Ошибка", "Пароли не совпадают.")
                return

            if any(u['username'] == username for u in self.users):
                messagebox.showwarning("Ошибка", "Пользователь с таким именем уже существует.")
                return

            self.users.append({
                "username": username,
                "password": hash_password(password),
                "role": role
            })
            self.save_users()
            self.refresh_listbox()
            add_window.destroy()
            log_admin_action(f"{self.master.username} добавил пользователя {username} ({role})")
            self.load_log_entries()
            messagebox.showinfo("Успешно", f"Пользователь {username} добавлен.")

        ttk.Button(add_window, text="Добавить", command=confirm).pack(pady=10)

    def save_users(self):
        try:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить users.json: {e}")

def log_admin_action(text):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {text}\n")
