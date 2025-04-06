from main import EVENING_CHAT_ID
from aiogram import Bot
from datetime import datetime

CHAT_ID = EVENING_CHAT_ID


async def morning_message_cron(bot: Bot):
    message_text = "Всем доброго утра !"
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")


async def demin_max_message_cron(bot: Bot):
    message_text = "Напоминаю, Дема - нерукопожатный пидорас!\n#ГЛАВШПАН"
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")
