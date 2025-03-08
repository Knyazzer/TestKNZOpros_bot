import logging
import json
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN, ADMIN_IDS
from admin_handlers import register_admin_handlers
from user_handlers import register_user_handlers

USER_FILE = "users.json"

def get_all_users():
    """Загружает ID пользователей из файла JSON или создаёт новый файл, если его нет."""
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", encoding="utf-8") as file:
            print(f"[LOG] Сохранение пользователей в файл: {USER_FILE}")
            json.dump([], file, ensure_ascii=False, indent=4)
        return []
    try:
        with open(USER_FILE, "r", encoding="utf-8") as file:
            users = json.load(file)
            return users if isinstance(users, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_user(user_id, username, is_admin=False):
    """Добавляет нового пользователя в список, если его там нет."""
    print(f"[LOG] Попытка сохранить пользователя: {user_id}")
    """Добавляет нового пользователя в список, если его там нет."""
    users = get_all_users()
    if not isinstance(users, list):
        users = []  # Фикс, если файл повреждён или содержит неверные данные
    
    user_data = {
        "id": user_id,
        "username": username,
        "role": "admin" if is_admin else "user",
        "timestamp": datetime.now().isoformat()
    }
    
    if not any(user["id"] == user_id for user in users):
        users.append(user_data)
        
        with open(USER_FILE, "w", encoding="utf-8") as file:
            json.dump(users, file, ensure_ascii=False, indent=4)
        print(f"[LOG] Добавлен пользователь: {user_id}, текущий список: {users}")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация обработчиков
register_admin_handlers(dp)
register_user_handlers(dp)

from datetime import datetime

async def user_registration_middleware(handler, event, data):
    from aiogram.types import Update, Message, CallbackQuery
    from aiogram.types import Message, CallbackQuery
    if isinstance(event, Update):
        if event.message:
            save_user(event.message.from_user.id, event.message.from_user.username, event.message.from_user.id in ADMIN_IDS)
        elif event.callback_query:
            save_user(event.callback_query.from_user.id, event.callback_query.from_user.username, event.callback_query.from_user.id in ADMIN_IDS)
        
    
    return await handler(event, data)

dp.update.outer_middleware(user_registration_middleware)

# Запуск бота
async def main():
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        print("[LOG] Бот остановлен вручную")
    finally:
        await bot.session.close()  # Закрываем соединение с Telegram API
        print("[LOG] Соединение с Telegram API закрыто")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[LOG] Завершение работы бота")
