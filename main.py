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
    scheduler.add_job(message_sending.morning_message_cron, trigger='cron', hour=6, minute=15,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Утреннее сообщение Антону

    scheduler.add_job(message_sending.anton_start_working_message_cron, trigger='cron', hour=8, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Антон приехал на работу
    scheduler.add_job(message_sending.anton_eating_message_cron, trigger='cron', hour=12, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Антон в обед
    scheduler.add_job(message_sending.anton_working_message_cron, trigger='cron', hour=14, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Антон день

    scheduler.add_job(message_sending.new_year_delta_message_cron, trigger='cron', hour=12, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Предновогоднее сообщение
    scheduler.add_job(message_sending.new_year_delta_message_cron, trigger='cron', hour=0, minute=0,
                      start_date=datetime.now(), kwargs={'bot': bot})  # Предновогоднее сообщение

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
