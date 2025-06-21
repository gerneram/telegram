# 🛒 Telegram Shop Bot with Django Admin & ЮKassa

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-success?logo=django)
![PostgreSQL](https://img.shields.io/badge/Postgres-15-blue?logo=postgresql)
![Aiogram](https://img.shields.io/badge/Bot-Aiogram%203-lightgrey?logo=telegram)
![ЮKassa](https://img.shields.io/badge/ЮKassa-оплата-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)

Полнофункциональный Telegram-бот для оформления заказов с удобной админкой на Django и интеграцией с ЮKassa для онлайн-оплаты. 

## 📦 Возможности

- Каталог товаров с категориями и подкатегориями
- Добавление товаров в корзину
- Оформление заказа с указанием имени, адреса и телефона
- Генерация Excel-файла с заказами
- Оплата через ЮKassa (платёжная ссылка)
- Часто задаваемые вопросы (FAQ)
- Удобное администрирование через Django Admin

## ⚙️ Технологии

- Python 3.11
- Django 5
- PostgreSQL
- Aiogram 3
- Docker + Docker Compose
- ЮKassa
- Markdown / HTML UI для Telegram

## 📁 Структура проекта

```
project-root/
│
├── admin/                  # Django-приложение
│   ├── shop_project/       # Конфигурация Django
│   ├── store/              # Основное приложение (модели, views, urls, admin)
│   └── media/              # Медиа-файлы
│
├── bot/                    # Telegram-бот
│   ├── handlers/           # Обработчики: catalog, order, payment и т.п.
│   ├── keyboards/          # Inline-клавиатуры
│   └── main.py             # Точка входа бота
│
├── backup/                # SQL-бэкапы базы данных
├── .env                   # Переменные окружения (пример ниже)
├── docker-compose.yml     # Конфигурация Docker
├── Makefile               # Удобные команды (start, stop, logs)
├── backup.sh              # Скрипт создания бэкапа
└── restore.sh             # Скрипт восстановления бэкапа
```

## 🐳 Запуск через Docker

```bash
# Запустить контейнеры и восстановить из бэкапа
make start

# Остановить и сохранить бэкап
make stop

# Посмотреть логи бота и админки
make logs
```

## 🔐 .env (пример)

```dotenv
# Django settings
SECRET_KEY=super-secret-key
LINK=127.0.0.1

# DB
POSTGRES_DB=shopdb
POSTGRES_USER=shopuser
POSTGRES_PASSWORD=shoppass
POSTGRES_HOST=db
POSTGRES_PORT=5432

# ЮKassa
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# Для бота
BOT_TOKEN=your_telegram_bot_token
RETURN_URL=https://t.me/your_bot
```

## 📂 Бэкапы

- Скрипт `backup.sh` создаёт дамп PostgreSQL из контейнера `project-db-1` и сохраняет его в `./backup/`
- `restore.sh` внутри контейнера восстанавливает последний SQL-файл из `docker-entrypoint-initdb.d/`

## 📑 Admin панель

Доступна по адресу: `http://localhost:8000/admin/`

## 💳 Оплата

- ЮKassa генерирует ссылку для оплаты после оформления заказа
- Оплата подтверждается через `/api/payment/confirm/`

## 🧪 TODO

- Подключение webhook из ЮKassa (автоматическое подтверждение)
- Личный кабинет
- Отзывы и рейтинги

---
