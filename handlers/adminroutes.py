from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
import os
from keyboards.reply import check_stats_keyboard, admin_keyboard
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import aiosqlite
from aiogram.exceptions import TelegramForbiddenError
import asyncio
from os import getenv
load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID"))
adminrouter = Router()

class BroadcastState(StatesGroup):
    waiting_for_post = State()

DB_NAME = "ChessComStatsBot.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        full_name TEXT)
        """)
        await db.commit()

async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", (user_id, username, full_name))
        await db.commit()

async def get_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT DISTINCT username, full_name FROM users")
        result = await cursor.fetchall()
        return result

async def get_all_user_ids():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

@adminrouter.message(Command('start'))
async def start(message: Message):
    await init_db()
    await message.answer("Привет, чтобы начать нажми на кнопку ниже либо введи команду " "/stats",
                         reply_markup=check_stats_keyboard())
    await add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    if message.from_user.id == ADMIN_ID:
        await message.answer("Бот запущен", reply_markup=admin_keyboard())
    else:
        await message.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 Новый пользователь: @{message.from_user.username}")

@adminrouter.message(F.text == "Пользователи")
@adminrouter.message(Command("users"))
async def users(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    users = await get_users()
    if not users:
        await message.answer("База данных пуста")
        return
    text = "Пользователи в базе данных:\n"
    for username, full_name in users:
        text += f"{full_name}: @{username}\n"
    await message.answer(text)

@adminrouter.message(F.text == "Вещать")
@adminrouter.message(Command("broadcast"))
async def start_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await state.set_state(BroadcastState.waiting_for_post)
    await message.answer("📢 Отправь сообщение для рассылки:")


@adminrouter.message(BroadcastState.waiting_for_post)
async def process_broadcast_post(message: Message, state: FSMContext):
    await state.clear()

    user_ids = await get_all_user_ids()
    if not user_ids:
        await message.answer("❌ База данных пуста.")
        return

    status_msg = await message.answer(f"⏳ Начинаю рассылку для {len(user_ids)} пользователей...")

    success_count = 0
    blocked_count = 0

    for user_id in user_ids:
        try:
            await message.copy_to(chat_id=user_id)
            success_count += 1
            await asyncio.sleep(0.05)
        except TelegramForbiddenError:
            blocked_count += 1
        except Exception as e:
            print(f"Error:{e}")
    await status_msg.edit_text(
        f"✅ **Рассылка завершена!**\n\n"
        f"👤 Успешно доставлено: {success_count}\n"
        f"🚫 Заблокировали бота: {blocked_count}"
    )