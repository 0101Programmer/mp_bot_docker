from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router

# Инициализация роутера
router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я ваш Telegram-бот.")