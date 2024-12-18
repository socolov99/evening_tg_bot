from main import EVENING_CHAT_ID
from aiogram import Bot
from datetime import datetime

EXACTLY = 'ровно '


def days_hours_to_new_year() -> dict:
    """Вычисляет dict с количеством дней и часов до Нового года."""

    now = datetime.now()
    next_year = now.year + 1
    new_year = datetime(next_year, 1, 1, 0, 0, 0)  # Новый год в 00:00:00
    time_difference = new_year - now

    new_year_left = {
        'days': time_difference.days,
        'hours': time_difference.seconds // 3600  # Целое число часов
    }
    return new_year_left


CHAT_ID = EVENING_CHAT_ID


async def morning_message_cron(bot: Bot):
    message_text = "Всем доброго утра !\nАнтон, ты членосос, завтра пиздуй на работу, хватит бухать"
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")


async def new_year_delta_message_cron(bot: Bot):
    days = days_hours_to_new_year().get('days')
    hours = days_hours_to_new_year().get('hours')
    if hours == 0:
        exactly_word = 'EXACTLY'
        addition_str = ''
    else:
        exactly_word = ''
        addition_str = f" и {hours} часов"
    message_text = f"До нового года осталось {exactly_word}{days} дн.{addition_str}"
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")
