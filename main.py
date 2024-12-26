import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from src.app.handlers.user import user_router
from src.app.handlers.admin import admin_router
from src.database.models import async_main
from src.app.schedulers import message_sending

load_dotenv()

TOKEN = os.getenv("TOKEN")
EVENING_CHAT_ID = os.getenv("EVENING_CHAT_ID")
ADMIN_TG_ID = os.getenv("ADMIN_TG_ID")


def start_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(message_sending.morning_message_cron, trigger='cron', hour=8, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Утреннее сообщение

    scheduler.add_job(message_sending.pasha_comes_delta_message_cron, trigger='cron', hour=15, minute=38,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Приезд Паши
    scheduler.add_job(message_sending.pasha_comes_delta_message_cron, trigger='cron', hour=21, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Приезд Паши
    scheduler.add_job(message_sending.pasha_comes_delta_message_cron, trigger='cron', hour=0, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Приезд Паши
    scheduler.add_job(message_sending.pasha_comes_delta_message_cron, trigger='cron', hour=10, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Приезд Паши
    scheduler.add_job(message_sending.pasha_comes_delta_message_cron, trigger='cron', hour=17, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Приезд Паши


    scheduler.start()


async def on_startup(dispatcher: Dispatcher):
    await async_main()


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    start_scheduler(bot)
    dp.include_routers(user_router, admin_router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down")
