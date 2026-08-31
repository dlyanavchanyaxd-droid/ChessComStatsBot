import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (Message,
                           CallbackQuery)
from aiogram.exceptions import TelegramBadRequest
from keyboards.inline import update_stats_keyboard
import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class UserStats(StatesGroup):
    waiting_for_username = State()

router = Router()


async def fetch_and_format_stats(username: str):
    try:
        stats = await get_userstats(username)
    except Exception as e:
        print(f"Error: {e}")
        return None, None

    if not stats:
        return None, None

    pfp = stats.get("avatar")
    profile_url = f"https://www.chess.com/member/{username}/"

    rapid_rating = stats.get("chess_rapid", {}).get("last", {}).get("rating", "Нет рейтинга")
    blitz_rating = stats.get("chess_blitz", {}).get("last", {}).get("rating", "Нет рейтинга")
    bullet_rating = stats.get("chess_bullet", {}).get("last", {}).get("rating", "Нет рейтинга")

    text = (
        f"📊 <b>Статистика игрока</b> <a href='{profile_url}'>{username}</a>\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"⌛ <b>Рапид:</b> <code>{rapid_rating}</code>\n"
        f"⚡ <b>Блиц:</b> <code>{blitz_rating}</code>\n"
        f"🚀 <b>Пуля:</b> <code>{bullet_rating}</code>"
    )

    return text, pfp

async def get_userstats(username):
    username = username.lower()
    headers = {
        "User-Agent": "ChessComBot/1.2 (contact: dlyanavchanyaxd@gmail.com)"
    }
    stats_url = f"https://api.chess.com/pub/player/{username}/stats"
    pfp_url = f"https://api.chess.com/pub/player/{username}/"
    async with aiohttp.ClientSession() as session:
        async with session.get(stats_url, headers=headers) as resp_stats:
            if resp_stats.status != 200:
                return None
            stats_data = await resp_stats.json()


        async with session.get(pfp_url, headers=headers) as resp_pfp:
            if resp_pfp.status != 200:
                return None
            profile_data = await resp_pfp.json()
            stats_data["avatar"] = profile_data.get("avatar")
            return stats_data


@router.callback_query(F.data.startswith("updatestats:"))
async def update_stats(callback:CallbackQuery):
    await callback.answer()
    username = callback.data.split(":")[1]
    text, pfp = await fetch_and_format_stats(username)
    if not text:
        await callback.answer("Ошибка! Не удалось обновить данные.")
        return
    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                reply_markup=update_stats_keyboard(username),
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                text=text,
                reply_markup=update_stats_keyboard(username),
                parse_mode="HTML"
            )
    except TelegramBadRequest:
        pass



@router.message(F.text == '👀Посмотреть Статистику')
@router.message(Command('stats'))
async def stats(message: Message, state: FSMContext):
    await message.answer("Введите имя пользователя:")
    await state.set_state(UserStats.waiting_for_username)

@router.message(UserStats.waiting_for_username, F.text)
async def username_procces(message: Message, state: FSMContext):
    username = message.text.strip()
    await state.clear()
    status_msg = await message.answer(f"Выдаю статистику на: {username}")
    await status_msg.edit_text(f"Выдаю статистику на: {username}.")
    await asyncio.sleep(0.4)
    await status_msg.edit_text(f"Выдаю статистику на: {username}..")
    await asyncio.sleep(0.4)
    await status_msg.edit_text(f"Выдаю статистику на: {username}...")
    await asyncio.sleep(0.4)
    await status_msg.edit_text(f"Выдаю статистику на: {username}.")
    await asyncio.sleep(0.4)
    await status_msg.edit_text(f"Выдаю статистику на: {username}..")
    await asyncio.sleep(0.4)
    await status_msg.edit_text(f"Выдаю статистику на: {username}...")
    await asyncio.sleep(0.4)
    await status_msg.delete()
    text,pfp = await fetch_and_format_stats(username)
    if not text:
        await message.answer("Ошибка! Игрок не найден.")
        return
    if pfp:
        await message.answer_photo(photo=pfp, caption=text, reply_markup=update_stats_keyboard(username), parse_mode="HTML")
    else:
        await message.answer(text=text, reply_markup=update_stats_keyboard(username), parse_mode="HTML")