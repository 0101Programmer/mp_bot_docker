from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router, F

# Инициализация роутера
router = Router()

# Текст помощи с Markdown-форматированием и кликабельными командами
HELP_TEXT = (
    "*Список доступных команд:*\n\n"
    "• [/start](command:/start) \- Зарегистрироваться/обновить данные, начать работу\n"
    "• [/help](command:/help) \- Получить помощь\n"
    "• [/account](command:/account) \- Личный веб\-кабинет\n"
    "• [/admin](command:/admin) \- Команды администратора\n\n"
    "_Для получения дополнительной информации нажмите на соответствующую команду\._"
)

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="MarkdownV2")

# Обработчик текста "Помощь"
@router.message(F.text == "Помощь")
async def button_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="MarkdownV2")