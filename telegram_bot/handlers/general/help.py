from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router

# Инициализация роутера
router = Router()

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Список доступных команд:\n"
                         "/start - Зарегистрироваться/обновить данные, начать работу\n"
                         "/help - Получить помощь\n"
                         "/account - Личный веб-кабинет\n"
                         "/admin - Команды администратора")