from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from aiogram import Bot
from config import API_TOKEN

bot = Bot(token=API_TOKEN)

class AdminMessageState(StatesGroup):
    waiting_for_message = State()

async def admin_start(message: types.Message):
    """Приветственное сообщение для админов с кнопкой."""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📩 Отправить сообщение пользователям")]],
        resize_keyboard=True
    )
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Вы администратор. Используйте кнопку ниже для отправки сообщений пользователям.", reply_markup=keyboard)

async def send_message_to_users(message: types.Message, state: FSMContext):
    """Админ отправляет сообщение пользователям."""
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Введите сообщение или отправьте файл для рассылки пользователям.")
        await state.set_state(AdminMessageState.waiting_for_message)

async def distribute_message(message: types.Message, state: FSMContext):
    """Бот рассылает сообщение или файл всем пользователям."""
    from main import get_all_users  # Импортируем здесь, чтобы избежать циклического импорта
    users = [user for user in get_all_users() if user["id"] not in ADMIN_IDS]
    await state.clear()

    # Определяем, что отправил админ
    if message.text and not (message.document or message.photo or message.video):
        text = message.text
        for user in users:
            try:
                await bot.send_message(chat_id=user["id"], text=text)
            except Exception as e:
                print(f"[ERROR] Ошибка отправки сообщения пользователю {user['id']}: {e}")
        await message.answer("Текстовое сообщение отправлено всем пользователям.")

    elif message.document:
        file_id = message.document.file_id
        for user in users:
            try:
                await bot.send_document(chat_id=user["id"], document=file_id, caption=message.caption or "Файл от администратора")
            except Exception as e:
                print(f"[ERROR] Ошибка отправки документа пользователю {user['id']}: {e}")
        await message.answer("Документ отправлен всем пользователям.")

    elif message.photo:
        file_id = message.photo[-1].file_id
        for user in users:
            try:
                await bot.send_photo(chat_id=user["id"], photo=file_id, caption=message.caption or "Изображение от администратора")
            except Exception as e:
                print(f"[ERROR] Ошибка отправки фото пользователю {user['id']}: {e}")
        await message.answer("Фото отправлено всем пользователям.")

    elif message.video:
        file_id = message.video.file_id
        for user in users:
            try:
                await bot.send_video(chat_id=user["id"], video=file_id, caption=message.caption or "Видео от администратора")
            except Exception as e:
                print(f"[ERROR] Ошибка отправки видео пользователю {user['id']}: {e}")
        await message.answer("Видео отправлено всем пользователям.")

    else:
        await message.answer("Неизвестный формат. Отправьте текст, документ, фото или видео.")

def register_admin_handlers(dp: Dispatcher):
    dp.message.register(admin_start, Command("start"))
    dp.message.register(send_message_to_users, lambda message: message.text == "📩 Отправить сообщение пользователям")
    dp.message.register(send_message_to_users, Command("send"))
    dp.message.register(distribute_message, AdminMessageState.waiting_for_message)
