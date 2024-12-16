from main import EVENING_CHAT_ID
from aiogram import Bot

CHAT_ID = EVENING_CHAT_ID


async def morning_message_cron(bot: Bot):
    message_text = "Всем доброго утра !\nАнтон, ты уже на РАБоте ? Раб, трудись усерднее, а вечером так и быть можешь побаловаться пивом..."
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")
