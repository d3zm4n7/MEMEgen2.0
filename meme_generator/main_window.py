# meme_generator/main_window.py
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk, ImageFont, ImageDraw, ImageEnhance
from meme_generator.admin_panel import AdminPanel
import json
from utils.password_utils import hash_password, check_password


# Глобальный словарь шрифтов
FONT_FILES = {
    "Impact": "impact.ttf",
    "Arial": "arial.ttf",
    "Comic Sans MS": "comic.ttf",
    "Lucida Console": "lucon.ttf",
    "Times New Roman": "times.ttf"
}

class MainWindow(tk.Tk):
    def __init__(self, username, role):
        super().__init__()
        self.title(f"MEMEgen2.0 — Logged in as {username} ({role})")
        self.geometry("600x1300")
        self.resizable(False, False)

        self.username = username
        self.role = role
        self.save_count = 0

        if self.role == "user":
            self.watermark_label_var = tk.StringVar()
            self.watermark_label_var.set("💧 Осталось сохранений без watermark: 3")
            self.watermark_label = ttk.Label(self, textvariable=self.watermark_label_var, foreground="gray")
            self.watermark_label.pack(pady=5)

        # Приветствие
        ttk.Label(self, text=f"Добро пожаловать, {username}!", font=("Arial", 16)).pack(pady=10)
        ttk.Label(self, text=f"Ваша роль: {role.upper()}", font=("Arial", 12)).pack(pady=5)

        # === Создание мема ===
        ttk.Separator(self).pack(fill='x', pady=10)
        ttk.Label(self, text="🎨 Создание мема", font=("Arial", 12)).pack()

        ttk.Button(self, text="Загрузить изображение", command=self.load_image).pack(pady=5)

        self.canvas = tk.Canvas(self, width=500, height=500, bg="gray")
        self.canvas.pack(pady=5)

        # Ввод текста
        self.text_entry = ttk.Entry(self)
        self.text_entry.pack(pady=5)

        # Выбор шрифта с ограничением по роли
        ttk.Label(self, text="Шрифт:").pack()

        # Ограничения: trialuser видит только 3 шрифта, остальные — все
        if role == "user":  # trial
            available_fonts = ["Impact", "Arial", "Comic Sans MS"]
        else:  # pro и admin
            available_fonts = ["Impact", "Arial", "Comic Sans MS", "Lucida Console", "Times New Roman"]

        self.font_var = tk.StringVar()
        self.font_combo = ttk.Combobox(self, textvariable=self.font_var, state="readonly")
        self.font_combo['values'] = available_fonts
        self.font_combo.current(0)
        self.font_combo.pack()

        # Размер шрифта
        ttk.Label(self, text="Размер:").pack()
        self.font_size = tk.IntVar(value=32)
        self.font_slider = ttk.Scale(self, from_=10, to=72, orient="horizontal", variable=self.font_size)
        self.font_slider.pack()

        # Выбор положения текста
        ttk.Label(self, text="Положение текста:").pack()
        self.position_var = tk.StringVar()
        self.position_combo = ttk.Combobox(self, textvariable=self.position_var, state="readonly")
        self.position_combo['values'] = ["Верх", "Центр", "Низ"]
        self.position_combo.current(1)  # Центр по умолчанию
        self.position_combo.pack(pady=5)

        # Цвет текста и обводки (ограничение для trial)
        if self.role == "user":
            self.text_color = "white"
            self.outline_color = "black"
            ttk.Label(self, text="🎨 Цвет текста: белый").pack(pady=2)
            ttk.Label(self, text="🖌 Обводка: чёрная").pack(pady=2)
        else:
            self.text_color = "white"
            self.outline_color = "black"
            ttk.Button(self, text="🎨 Цвет текста", command=self.choose_text_color).pack(pady=2)
            ttk.Button(self, text="🖌 Цвет обводки", command=self.choose_outline_color).pack(pady=2)

        # Кнопка добавить текст (с обводкой)
        ttk.Button(self, text="Добавить текст", command=self.add_text).pack(pady=5)

        if role == "admin":
            ttk.Button(self, text="🛠 Управление пользователями", command=self.manage_users).pack(pady=10)

        ttk.Button(self, text="💾 Сохранить мем", command=self.save_meme).pack(pady=10)

        self.preview_label = ttk.Label(self)
        self.preview_label.pack(pady=10)

        ttk.Button(self, text="🔐 Сменить пароль", command=self.open_change_password).pack(pady=5)

        ttk.Button(self, text="🛠 В следующем обновлении", command=self.show_future_features).pack(pady=10)

        ttk.Button(self, text="Выйти в окно входа", command=self.logout).pack(pady=20)

        # Перетаскивание текста
        self.drag_data = {"x": 0, "y": 0}
        if self.role in ["pro", "admin"]:
            self.canvas.bind("<Button-1>", self.on_start_drag)
            self.canvas.bind("<B1-Motion>", self.on_drag)

        #preview
        self.preview_label = ttk.Label(self)
        self.preview_label.pack(pady=10)

        def show_preview_inline(self, image_path):
            img = Image.open(image_path)
            img = img.resize((300, 300))  # можно подогнать под нужный размер
            self.preview_image = ImageTk.PhotoImage(img)  # сохранить ссылку!
            self.preview_label.config(image=self.preview_image)

    def show_future_features(self):
        features = [
            "🎞 Генерация анимированных мемов (GIF)",
            "📁 История созданных мемов",
            "🔤 Новые кастомные шрифты",
            "📱 Публикация в Telegram / Discord",
            "📜 Ачивки и уровни активности", 
            "🌗 Поддержка тёмной темы",
            "🧠 Smart генератор текста для мемов",
            "🖼 Галерея мемов PRO-уровня",
            "🔁 Сравнение оригинала и результата"
        ]

        text = "\n".join(features)
        messagebox.showinfo("Скоро будет доступно", f"Вот что появится в будущем:\n\n{text}")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not file_path:
            return
        self.original_image = Image.open(file_path)
        self.original_image = self.original_image.resize((500, 500))
        self.tk_image = ImageTk.PhotoImage(self.original_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image, tags="image")

    def add_text(self):
        text = self.text_entry.get()
        if text:
            x = 250  # Центр по ширине для изображения 500x500

            pos = self.position_var.get()
            if pos == "Верх":
                y = 50
            elif pos == "Низ":
                y = 450
            else:
                y = 250  # Центр

            font_name = self.font_var.get()
            font_size = int(self.font_size.get())
            font = (font_name, font_size)

            self.canvas.delete("movable_text")

            # Обводка (рисуем несколько копий текста вокруг основного)
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        self.canvas.create_text(
                            x + dx, y + dy,
                            text=text,
                            fill=self.outline_color,
                            font=font,
                            anchor="center",
                            tags="movable_text"
                        )

            # Основной текст
            self.canvas.create_text(
                x, y,
                text=text,
                fill=self.text_color,
                font=font,
                anchor="center",
                tags="movable_text"
            )
    def open_change_password(self):
        self.withdraw()  # Прячем главное окно

        password_window = tk.Toplevel(self)
        password_window.title("Смена пароля")
        password_window.geometry("300x220")
        password_window.resizable(False, False)

    # Вернём главное окно, если пользователь закрыл окно пароля через [X]
        def on_close():
            self.deiconify()
            password_window.destroy()

        password_window.protocol("WM_DELETE_WINDOW", on_close)

        ttk.Label(password_window, text="Старый пароль:").pack(pady=5)
        old_entry = ttk.Entry(password_window, show="*")
        old_entry.pack(pady=5)

        ttk.Label(password_window, text="Новый пароль:").pack(pady=5)
        new_entry = ttk.Entry(password_window, show="*")
        new_entry.pack(pady=5)

        ttk.Label(password_window, text="Подтвердите новый пароль:").pack(pady=5)
        confirm_entry = ttk.Entry(password_window, show="*")
        confirm_entry.pack(pady=5)

        def confirm():
            old_pass = old_entry.get().strip()
            new_pass = new_entry.get().strip()
            confirm_pass = confirm_entry.get().strip()

            if not old_pass or not new_pass:
                messagebox.showwarning("Ошибка", "Все поля обязательны.")
                return

            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)

            for user in users:
                if user['username'] == self.username:
                    if not check_password(old_pass, user['password']):
                        messagebox.showerror("Ошибка", "Старый пароль неверен.")
                        return
                    if new_pass != confirm_pass:
                        messagebox.showerror("Ошибка", "Новый пароль и подтверждение не совпадают.")
                        return
                    user['password'] = hash_password(new_pass)
                    with open("users.json", "w", encoding="utf-8") as fw:
                        json.dump(users, fw, indent=4, ensure_ascii=False)
                    messagebox.showinfo("Успешно", "Пароль обновлён.")
                    password_window.destroy()
                    self.deiconify()  # Показываем главное окно обратно
                    return

            messagebox.showerror("Ошибка", "Пользователь не найден.")

        ttk.Button(password_window, text="Сменить пароль", command=confirm).pack(pady=10)

    def show_preview_inline(self, image_path):
        img = Image.open(image_path)
        img = img.resize((300, 300))  # можно 400x400 или подогнать под preview
        self.preview_image = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.preview_image)


    def on_start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move("movable_text", dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y


    def choose_text_color(self):
        color = colorchooser.askcolor(title="Выбери цвет текста")[1]
        if color:
            self.text_color = color

    def choose_outline_color(self):
        color = colorchooser.askcolor(title="Выбери цвет обводки")[1]
        if color:
            self.outline_color = color

    def generate_meme(self):
        print("Здесь будет генератор мемов")

    def pro_features(self):
        print("Здесь будут PRO-функции (шрифты, рамки, GIF и т.д.)")

    def manage_users(self):
        self.withdraw()  # Спрятать главное окно
        AdminPanel(self)

    def save_meme(self):
        if not hasattr(self, 'original_image'):
            print("Сначала загрузи изображение.")
            return

        image = self.original_image.copy()
        draw = ImageDraw.Draw(image)

        x = 250
        pos = self.position_var.get()
        if pos == "Верх":
            y = 50
        elif pos == "Низ":
            y = 450
        else:
            y = 250

        font_name = self.font_var.get()
        font_path = FONT_FILES.get(font_name, "arial.ttf")
        font_size = int(self.font_size.get())

        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"⚠️ Не удалось загрузить шрифт: {e}")
            font = ImageFont.load_default()

        text = self.text_entry.get()
        if not text:
            print("Нет текста для сохранения.")
            return

        # Обводка
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=self.outline_color, anchor="mm")
        # Основной текст
        draw.text((x, y), text, font=font, fill=self.text_color, anchor="mm")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            title="Сохранить мем"
        )

        if file_path:
            self.save_count += 1
            if self.role == "user":
                remaining = max(0, 3 - self.save_count)
                if remaining > 0:
                    self.watermark_label_var.set(f"💧 Осталось сохранений без watermark: {remaining}")
                else:
                    self.watermark_label_var.set("⚠️ Watermark активирован!")
                    self.watermark_label.config(foreground="red")

            # Конвертируем в RGBA заранее, если потребуется для watermark
            image_rgba = image.convert("RGBA")

            if self.role == "user" and self.save_count > 3:
                try:
                    watermark = Image.open("watermark.png").convert("RGBA")

                    # Если watermark больше изображения — уменьшим
                    img_width, img_height = image.size
                    wm_width, wm_height = watermark.size

                    max_wm_width = min(wm_width, img_width - 20)
                    max_wm_height = min(wm_height, img_height - 20)

                    if wm_width > max_wm_width or wm_height > max_wm_height:
                        watermark = watermark.resize((max_wm_width, max_wm_height), resample=Image.Resampling.LANCZOS)
                        wm_width, wm_height = watermark.size

                    # Прозрачность 30%
                    alpha = watermark.split()[3]
                    alpha = ImageEnhance.Brightness(alpha).enhance(0.3)
                    watermark.putalpha(alpha)

                    # Центр
                    x = (img_width - wm_width) // 2
                    y = (img_height - wm_height) // 2
                    position = (x, y)

                    # Вставляем watermark
                    image_rgba.paste(watermark, position, watermark)

                except Exception as e:
                    print("❌ Ошибка наложения watermark:", e)

        # Сохраняем
        image_rgba = image_rgba.convert("RGB")  # если был watermark, или просто сконвертируем снова
        image_rgba.save(file_path)
        print(f"✅ Мем сохранён: {file_path}")
        self.show_preview_inline(file_path)

    def logout(self):
        self.destroy()
        from auth.auth_window import AuthWindow  # импорт внутри метода
        AuthWindow().mainloop()