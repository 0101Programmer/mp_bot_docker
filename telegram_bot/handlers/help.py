from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router

# Инициализация роутера
router = Router()

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Список доступных команд:\n"
                         "/start - Начать работу\n"
                         "/help - Получить помощь\n"
                         "/admin - Команды администратора")