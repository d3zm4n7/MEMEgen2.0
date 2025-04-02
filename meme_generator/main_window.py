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

        self.title(f"MEMEgen2.0 — Logged in as {username} ({role})")
        self.geometry("810x700")
        self.configure(bg="#1e5631")
        self.username = username
        self.role = role
        self.text_color = "white"
        self.outline_color = "black"
        self.save_count = 0

        # Верхняя часть (приветствие)
        top_frame = tk.Frame(self, bg="#1e5631")
        top_frame.grid(row=0, column=0, columnspan=3, pady=(10, 0), sticky="ew")

        ttk.Label(top_frame, text=f"Welcome, {username}!", font=("Times New Roman", 12)).grid(row=0, column=0, padx=10)
        ttk.Button(top_frame, text="🔐Change password", command=self.open_change_password).grid(row=0, column=1, columnspan=2, pady=5)
        
        ttk.Label(top_frame, text=f"Your role: {role.upper()}", font=("Times New Roman", 12)).grid(row=0, column=3, padx=10)
        if self.role == "admin":
            ttk.Button(top_frame, text="🛠Users", command=self.manage_users).grid(row=0, column=4, columnspan=2, pady=5)




        # Основной контейнер
        main_frame = tk.Frame(self, bg="#1e5631")
        main_frame.grid(row=1, column=0, padx=10, pady=10)

        # Центр — Canvas
        center_frame = tk.Frame(main_frame, bg="#1e5631")
        center_frame.grid(row=0, column=0, sticky="n")

        self.canvas = tk.Canvas(center_frame, width=500, height=500, bg="gray")
        self.canvas.grid(row=0, column=0, columnspan=2, sticky="w")

        if self.role == "user":
            self.watermark_label_var = tk.StringVar()
            self.watermark_label_var.set("💧Saves left without watermark: 3")
            self.watermark_label = ttk.Label(center_frame, textvariable=self.watermark_label_var, foreground="gray", font=("Times New Roman", 10))
            self.watermark_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Button(center_frame, text="🛠Coming up features...", command=self.show_future_features).grid(row=2, column=1, columnspan=2, sticky="w", pady=5)
        

        
        # Правая панель (настройки)
        right_frame = tk.Frame(main_frame, bg="#1e5631")
        right_frame.grid(row=0, column=1, rowspan=2, padx=20, sticky="n")

        row = 0
        meme_frame = ttk.LabelFrame(right_frame, text="🎨 MEME creation", padding=10)
        meme_frame.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1

        ttk.Label(meme_frame, text="Insert picture:").grid(row=row, column=0, sticky="w")
        ttk.Button(meme_frame, text="Browse", command=self.load_image).grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        ttk.Label(meme_frame, text="Text:").grid(row=row, column=0, sticky="w")
        self.text_entry = ttk.Entry(meme_frame)
        self.text_entry.grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        fonts = ["Impact", "Arial", "Comic Sans MS", "Lucida Console", "Times New Roman"]
        if self.role == "user":
            fonts = fonts[:3]
        self.font_var = tk.StringVar()
        ttk.Label(meme_frame, text="Font:").grid(row=row, column=0, sticky="w")
        self.font_combo = ttk.Combobox(meme_frame, textvariable=self.font_var, values=fonts, state="readonly")
        self.font_combo.current(0)
        self.font_combo.grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        ttk.Label(meme_frame, text="Font size:").grid(row=row, column=0, sticky="w")
        self.font_size = tk.IntVar(value=32)
        self.font_slider = ttk.Scale(meme_frame, from_=10, to=100, orient="horizontal", command=self.update_font_size)
        self.font_slider.grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        ttk.Label(meme_frame, text="Allocation:").grid(row=row, column=0, sticky="w")
        self.position_var = tk.StringVar()
        self.position_combo = ttk.Combobox(meme_frame, textvariable=self.position_var, values=["Top", "Center", "Bottom"], state="readonly")
        self.position_combo.current(1)
        self.position_combo.grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        if self.role == "user":
            ttk.Label(meme_frame, text="Font color: white").grid(row=row, column=0, columnspan=2)
            ttk.Label(meme_frame, text="Outline: black").grid(row=row, column=2, columnspan=2)
        else:
            ttk.Button(meme_frame, text="🎨Font color", command=self.choose_text_color).grid(row=row, column=0)
            ttk.Button(meme_frame, text="🖌Outline", command=self.choose_outline_color).grid(row=row, column=2)
        row += 1

        ttk.Button(meme_frame, text="Add text", command=self.add_text).grid(row=row, column=0, columnspan=4, pady=5)

        ttk.Button(right_frame, text="💾Save MEME", command=self.save_meme).grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(right_frame, text="Log Out", command=self.logout).grid(row=2, column=0, columnspan=2 )


 # Перетаскивание текста
        self.drag_data = {"x": 0, "y": 0}
        if self.role in ["pro", "admin"]:
            self.canvas.bind("<Button-1>", self.on_start_drag)
            self.canvas.bind("<B1-Motion>", self.on_drag)

        #preview
        self.preview_frame = tk.Frame(self, bg="#1e5631")
        self.preview_frame.grid(row=2, column=1, pady=10)

        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.grid()

        def show_preview_inline(self, image_path):
            img = Image.open(image_path)
            img = img.resize((300, 300))  # можно подогнать под нужный размер
            self.preview_image = ImageTk.PhotoImage(img)  # сохранить ссылку!
            self.preview_label.config(image=self.preview_image)

    def show_future_features(self):
        features = [
            "🎞 Animated meme generation (GIF)",
            "📁 Meme creation history",
            "🔤 New custom fonts",
            "📱 Posting to Telegram / Discord",
            "📜 Achievements and activity levels",
            "🌗 Dark theme support",
            "🧠 Smart meme text generator",
            "🖼 PRO-level meme gallery",
            "🔁 Original vs result comparison",
            "🖼 PRO subscription reliese"
        ]

        text = "\n".join(features)
        messagebox.showinfo("Coming Soon", f"Here’s what’s coming in the future:\n\n{text}")

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
            if pos == "Top":
                y = 50
            elif pos == "Bottom":
                y = 450
            else:
                y = 250  #  Center

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
    def update_font_size(self, event=None):
        self.font_size.set(int(float(self.font_slider.get())))

    def open_change_password(self):
        self.withdraw()  # Прячем главное окно

        password_window = tk.Toplevel(self)
        password_window.title("Password change")
        password_window.geometry("350x275")
        password_window.configure(bg="#1e5631")
        password_window.resizable(False, False)



    # Вернём главное окно, если пользователь закрыл окно пароля через [X]
        def on_close():
            self.deiconify()
            password_window.destroy()

        password_window.protocol("WM_DELETE_WINDOW", on_close)

        ttk.Label(password_window, text="Old password:").pack(pady=5)
        old_entry = ttk.Entry(password_window, show="*")
        old_entry.pack(pady=5)

        ttk.Label(password_window, text="New password:").pack(pady=5)
        new_entry = ttk.Entry(password_window, show="*")
        new_entry.pack(pady=5)

        ttk.Label(password_window, text="Re-enter new password:").pack(pady=5)
        confirm_entry = ttk.Entry(password_window, show="*")
        confirm_entry.pack(pady=5)

        def confirm():
            old_pass = old_entry.get().strip()
            new_pass = new_entry.get().strip()
            confirm_pass = confirm_entry.get().strip()

            if not old_pass or not new_pass:
                messagebox.showwarning("Error", "All fields are required.")
                return

            with open("users.json", "r", encoding="utf-8") as f:
                users = json.load(f)

            for user in users:
                if user['username'] == self.username:
                    if not check_password(old_pass, user['password']):
                        messagebox.showerror("Error", "The old password is incorrect.")
                        return
                    if new_pass != confirm_pass:
                        messagebox.showerror("Error", "The new password and confirmation do not match.")
                        return
                    user['password'] = hash_password(new_pass)
                    with open("users.json", "w", encoding="utf-8") as fw:
                        json.dump(users, fw, indent=4, ensure_ascii=False)
                    messagebox.showinfo("Success", "Password updated.")
                    password_window.destroy()
                    self.deiconify()  # Показываем главное окно обратно
                    return

            messagebox.showerror("Error", "User not found.")

        ttk.Button(password_window, text="Change password", command=confirm).pack(pady=10)

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
        color = colorchooser.askcolor(title="Choose text color")[1]
        if color:
            self.text_color = color

    def choose_outline_color(self):
        color = colorchooser.askcolor(title="Choose outline color")[1]
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
            print("Please upload an image first.")
            return

        image = self.original_image.copy()
        draw = ImageDraw.Draw(image)

        x = 250
        pos = self.position_var.get()
        if pos == "Top":
            y = 50
        elif pos == "Bottom":
            y = 450
        else:
            y = 250

        font_name = self.font_var.get()
        font_path = FONT_FILES.get(font_name, "arial.ttf")
        font_size = int(self.font_size.get())

        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"⚠️Failed to load font: {e}")
            font = ImageFont.load_default()

        text = self.text_entry.get()
        if not text:
            print("No text to save.")
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
            title="Save MEME"
        )

        if file_path:
            self.save_count += 1
            if self.role == "user":
                remaining = max(0, 3 - self.save_count)
                if remaining > 0:
                    self.watermark_label_var.set(f"💧Saves left without watermark: {remaining}")
                else:
                    self.watermark_label_var.set("⚠️ Watermark activate!")
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
                    print("❌ Error applying watermark:", e)

        # Сохраняем
        image_rgba = image_rgba.convert("RGB")  # если был watermark, или просто сконвертируем снова
        image_rgba.save(file_path)
        print(f"✅ Meme saved: {file_path}")
        self.show_preview_inline(file_path)

    def logout(self):
        self.destroy()
        from auth.auth_window import AuthWindow  # импорт внутри метода
        AuthWindow().mainloop()