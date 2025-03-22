from aiogram.types import Message
from aiogram import Router

# Инициализация роутера
router = Router()

# Обработчик просто текстовых сообщений
@router.message()
async def all_messages(message: Message):
    await message.answer(f"Команда не распознана, пожалуйста, введите /help для получения более детальной информации")