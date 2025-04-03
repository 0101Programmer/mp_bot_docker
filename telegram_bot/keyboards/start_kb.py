from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Создаем клавиатуру
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Написать обращение")],
        [KeyboardButton(text="Описание комиссий")],
        [KeyboardButton(text="Отследить статус обращения")],
        [KeyboardButton(text="Помощь")],
    ],
    resize_keyboard=True,
)