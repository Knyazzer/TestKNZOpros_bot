from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram import Bot
from config import API_TOKEN, ADMIN_IDS

bot = Bot(token=API_TOKEN)

async def start(message: types.Message):
    """Приветствие только для пользователей (не админов)."""
    if message.from_user.id in ADMIN_IDS:
        return  # ✅ Если админ – ничего не делаем
    
    await message.answer("Добро пожаловать! Используйте бота для взаимодействия.")

async def user_message(message: types.Message):
    """Обрабатывает обычные сообщения от пользователей."""
    if message.from_user.id in ADMIN_IDS:
        return  # ✅ Если админ – ничего не делаем

    await message.answer(f"Вы сказали: {message.text}")

def register_user_handlers(dp: Dispatcher):
    """Регистрируем обработчики ТОЛЬКО для пользователей."""
    dp.message.register(start, Command("start"))
    dp.message.register(user_message)
