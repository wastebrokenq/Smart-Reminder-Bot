# config.py
import os

# Получаем токен из переменной окружения или жестко кодируем (не рекомендуется для продакшена)
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_TOKEN", "6869758490:AAGufe9KTyZfYHINNo_5UPP30ZvkFbP9Azk")

# Настройки базы данных
DATABASE_URL = "sqlite:///data/reminders.db"

# Прочие параметры
TIME_ZONE = 'Europe/Moscow'
