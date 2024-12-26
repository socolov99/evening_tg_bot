from main import EVENING_CHAT_ID
from aiogram import Bot
from datetime import datetime

EXACTLY = 'ровно '


def time_to_new_year() -> dict:
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


def time_to_pasha_comes() -> dict:
    """Вычисляет dict с количеством дней и часов до Пашиного прилета."""

    now = datetime.now()
    cur_year = now.year
    pasha_comes = datetime(cur_year, 12, 27, 21, 0, 0)  # Паша прилетает в 21:00:00 27го декабря
    time_difference = pasha_comes - now

    new_year_left = {
        'days': time_difference.days,
        'hours': time_difference.seconds // 3600  # Целое число часов
    }
    return new_year_left


CHAT_ID = EVENING_CHAT_ID


async def morning_message_cron(bot: Bot):
    message_text = "Всем доброго утра !"
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")


async def new_year_delta_message_cron(bot: Bot):
    days = time_to_new_year().get('days')
    hours = time_to_new_year().get('hours') + 1

    if hours == 24:
        hours = 0
        days += 1

    message_text = f"До нового года осталось {days} дн., {hours} ч."
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")


async def pasha_comes_delta_message_cron(bot: Bot):
    days = time_to_pasha_comes().get('days')
    hours = 24 * days + time_to_pasha_comes().get('hours') + 1

    message_text = f"До приезда Паши осталось {hours} ч."
    try:
        await bot.send_message(CHAT_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в чат: {e}")
