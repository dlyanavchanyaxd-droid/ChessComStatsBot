from aiogram.types import (
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)

def update_stats_keyboard(username: str):
    in_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔁Обновить", callback_data=f"updatestats:{username}")]
        ], resize_keyboard=True
    )
    return in_keyboard
