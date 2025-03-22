from aiogram.types import Message
from aiogram import Router

# Инициализация роутера
router = Router()

# Обработчик текстовых сообщений
@router.message()
async def echo(message: Message):
    await message.answer(f"Вы сказали: {message.text}")