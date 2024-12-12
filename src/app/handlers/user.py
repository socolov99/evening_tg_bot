from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram_calendar import DialogCalendar, DialogCalendarCallback, get_user_locale

import src.app.keyboards.kb as kb
from src.database.requests import (set_user, get_user, add_user_drink, get_user_drinks, get_drink_board)

DATE_FORMAT = "%d/%m/%Y"

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id, message.from_user.username)
    await message.answer(f"Привет {message.from_user.username} !", reply_markup=kb.main)


@user_router.message(F.text == "Я выпил")
async def user_drink(message: Message):
    await set_user(message.from_user.id, message.from_user.username)
    await message.answer("Выбери дату:", reply_markup=await DialogCalendar(locale="ru_RU").start_calendar())


@user_router.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    selected, date = await DialogCalendar(locale="ru_RU").process_selection(callback_query, callback_data)
    if selected:
        user = await get_user(callback_query.from_user.id)
        await add_user_drink(user.id, date)
        await callback_query.message.answer("Одобряю твой поступок", reply_markup=kb.main)


@user_router.message(F.text == "Моя статистика")
async def mystats_handler(message: Message):
    await set_user(message.from_user.id, message.from_user.username)
    user = await get_user(message.from_user.id)
    drinks = await get_user_drinks(user.id)
    drinks_list = list(drinks)
    if len(drinks_list) > 0:
        message_text = "Ты пил в эти даты:\n-----------------------------------\n"
        for drink in drinks_list:
            message_text += f"{drink.action_dt.strftime('%Y-%m-%d')}\n"
    else:
        message_text = 'Я не знаю когда ты пил... Пора это исправлять.\nКогда выпьешь, нажми на кнопку "Я выпил"'
    await message.answer(message_text)


@user_router.message(F.text == "Лидерборд")
async def stats_handler(message: Message):
    await set_user(message.from_user.id, message.from_user.username)
    stats = await get_drink_board()
    stats_list = list(stats)
    if len(stats_list) > 0:
        message_text = "Лидерборд\n-----------------------------------\nПользователь; Крайний раз пил; Дней трезвости\n-----------------------------------\n"
        for index, stats_element in enumerate(stats_list):
            days = stats_element.sober_time.days
            message_text += f"{index + 1}) {stats_element.tg_name};  {stats_element.last_drink.strftime('%Y-%m-%d')};  {days} дней\n"
    else:
        message_text = "Я пока не собрал статистику. Пьем активнее !"
    await message.answer(message_text)
