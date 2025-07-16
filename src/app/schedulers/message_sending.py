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


async def demin_max_message_cron_16_30(bot: Bot):
    message_text = "Я вновь всем напоминаю, Дема - нерукопожатный пидорас! Не забывайте об этом.\n#ГЛАВШПАН"
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")

async def demin_max_message_cron_20_00(bot: Bot):
    message_text = "Дема может отсосать хуй, обращайтесь, он любит делать приятно пацанам.\n#ГЛАВШПАН"
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")