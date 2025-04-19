from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def generate_commissions_keyboard(commissions):
    """
    Генерирует inline-клавиатуру с кнопками для каждой комиссии.
    :param commissions: Список объектов CommissionInfo.
    :return: InlineKeyboardMarkup
    """
    keyboard = []
    for i in range(0, len(commissions), 2):  # Разбиваем на строки по 2 кнопки
        row = [
            InlineKeyboardButton(
                text=f"📋 {commissions[j].name}",
                callback_data=f"info_commission:{commissions[j].id}"
            )
            for j in range(i, min(i + 2, len(commissions)))
        ]
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)