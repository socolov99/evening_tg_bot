from main import EVENING_CHAT_ID
from aiogram import Bot

CHAT_ID = EVENING_CHAT_ID


async def morning_message_cron(bot: Bot):
    message_text = "Всем доброго утра !"
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")
