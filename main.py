import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from src.app.handlers.user import user_router
from src.app.handlers.admin import admin_router
from src.database.models import async_main

"""
Telegram-бот для тестирования - @evening_tg_test_bot
"""

load_dotenv()

TOKEN = os.getenv("TOKEN")


async def on_startup(dispatcher: Dispatcher):
    await async_main()


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(user_router, admin_router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down")
