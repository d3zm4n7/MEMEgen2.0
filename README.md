# MEMEgen2.0 — приложение для генерации мемов

## 📄 Титульный лист

**Название проекта**: MEMEgen2.0 — приложение для генерации мемов  
**Автор**: Керя (Dez)  
**Образовательное учреждение**: *Tallinna Transpodri Kool*  
**Дата**: *02.04.2025*

---

## 📚 Содержание

1. [Введение](#введение)  
2. [Техническая часть](#техническая-часть)  
3. [Руководство пользователя](#руководство-пользователя)  
4. [Тестирование](#тестирование)  
5. [Заключение](#заключение)  
6. [Приложения](#приложения)

---

## Введение

Проект **MEMEgen2.0** — это графическое настольное приложение, разработанное на языке Python с использованием библиотеки `Tkinter`, предназначенное для создания мемов. Пользователь может загрузить изображение, ввести текст, выбрать шрифт, настроить размер, цвет и расположение текста. Также реализована система водяных знаков, история сохранений и авторизация с разграничением прав доступа.

### 🎯 Цель проекта
Создать удобное и функциональное приложение, которое позволяет пользователям различных ролей (admin, pro, trial) быстро и просто генерировать оригинальные мемы.

### 🧩 Задачи проекта
- Реализовать пользовательский интерфейс с помощью Tkinter;
- Обеспечить функциональность создания мемов;
- Внедрить авторизацию и систему ролей пользователей;
- Создать систему ограничения функций для пробных пользователей;
- Добавить возможность редактирования текста и применения водяного знака;
- Сохранение истории и логирование действий администратора.

---

## Техническая часть

### 🧪 Использованные технологии и библиотеки
- **Python 3** — основной язык программирования  
- **Tkinter / ttk** — интерфейс  
- **Pillow** — обработка изображений  
- **JSON** — хранение данных пользователей

### 🗂 Структура проекта
```
MEMEgen2.0/
├── auth/                    # Аутентификация и работа с пользователями
│   ├── auth_window.py
│   └── users.json
│
├── meme_generator/          # Генерация мемов и админ-панель
│   ├── admin_panel.py
│   └── main_window.py
│
├── utils/                   # Вспомогательные функции
│   └── password_utils.py
│
├── logs/                    # Логи действий
│   └── admin_actions.log
│
├── Шрифты: arial.ttf, comic.ttf, impact.ttf, и т.д.
├── watermark.png            # Картинка водяного знака
├── main.py                  # Главный файл запуска
└── users.json               # Файл с данными пользователей
```

### 🔍 Основные модули
- `auth_window.py` — окно авторизации, регистрация, проверка данных
- `users.json` — база данных пользователей (имя, пароль, роль)
- `main_window.py` — основное окно для генерации мемов
- `admin_panel.py` — админ-панель для управления пользователями
- `password_utils.py` — функции шифрования и проверки пароля
- `admin_actions.log` — логирование всех действий администратора

### 👥 Роли пользователей
- `admin` — полный доступ, управление пользователями, просмотр логов
- `pro` — расширенный функционал, создание мемов без ограничений
- `trial` — до 3 сохранений без водяного знака, затем watermark применяется автоматически

---

## Руководство пользователя

1. Запустите `main.py`
2. Пройдите авторизацию или зарегистрируйтесь как новый пользователь
3. Выберите изображение для мема
4. Введите верхний и нижний текст
5. Настройте шрифт, размер, цвет, положение текста
6. Отрегулируйте прозрачность водяного знака (если доступно)
7. Сохраните изображение в формате PNG или JPEG
8. Для trial-пользователей после 3 сохранений будет добавляться watermark автоматически
9. Администратор может открыть панель для управления пользователями

---

## Тестирование

Тестирование проводилось вручную, с использованием следующих сценариев:
- ✅ Авторизация пользователя с правильным и неправильным паролем
- ✅ Проверка ролей: ограничения для trial, доступ администратора
- ✅ Загрузка изображений разного формата
- ✅ Работа шрифтов (arial, comic, impact и др.)
- ✅ Сохранение изображений с текстом
- ✅ Применение водяного знака и регулировка его прозрачности
- ✅ Проверка лимита сохранений без watermark для trial
- ✅ Добавление, изменение и удаление пользователей в admin-панели

Все функции работают стабильно и соответствуют требованиям.

---

## Заключение

Проект **MEMEgen2.0** был успешно реализован в рамках учебной работы. Основные цели достигнуты, все ключевые функции работают стабильно. Реализована гибкая система прав доступа, создан интуитивно понятный интерфейс, реализована визуальная настройка текста и водяного знака.

### 💡 В будущем планируется:
- Поддержка GIF-анимации
- Интеграция с Telegram / Discord
- Система достижений и уровней активности
- Продвинутая история и галерея сохранённых мемов
- Smart-генератор текста на основе шаблонов или ИИ

---

## Приложения

### 📂 Пример users.json:
```json
[
  {
    "username": "admin",
    "password": "hash",
    "role": "admin"
  },
  {
    "username": "trialUser",
    "password": "hash",
    "role": "trial"
  }
]
```

### 🗒 Пример admin_actions.log:
```
[2025-04-03 10:15:22] admin added user: trialUser
[2025-04-03 10:17:08] admin changed password for: trialUser
[2025-04-03 10:20:44] admin deleted user: trialUser
```

---

> Документация подготовлена в рамках проекта MEMEgen2.0 — 2025.

