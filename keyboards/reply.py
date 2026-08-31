from aiogram.types import (
                            ReplyKeyboardMarkup,
                           KeyboardButton,)

def check_stats_keyboard():
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👀Посмотреть Статистику")]
        ]
    )
    return reply_keyboard

def admin_keyboard():
    admin_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Вещать")],
            [KeyboardButton(text="Пользователи")]
        ]
    )
    return admin_keyboard