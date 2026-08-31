from os import getenv
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.adminroutes import adminrouter
from handlers.routes import router
import asyncio


load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

dp.include_routers(router, adminrouter)


async def main():
    bot = Bot(token=TOKEN)
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())