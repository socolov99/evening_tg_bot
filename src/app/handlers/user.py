from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import DialogCalendar, DialogCalendarCallback

import src.app.keyboards.kb as kb
from src.database.requests import (set_user, get_user, add_user_drink, get_user_drinks, get_drink_board,
                                   get_month_drink_stats)

from src.dicts.dict_loader import MONTH_NAMES_DICT

NOT_DRINKING_TG_ID_LIST = [5352646861]  # Вова

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id, message.from_user.username)
    user = await get_user(message.from_user.id)
    request_user_name = user.user_full_name if user.user_full_name is not None else user.tg_name
    await message.answer(f"Привет {request_user_name} !", reply_markup=kb.main)


@user_router.callback_query(F.data == "add_drink_info")
async def user_drink(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    request_user_name = user.user_full_name if user.user_full_name is not None else user.tg_name
    await callback_query.message.answer(f"{request_user_name}, когда ты пил ?", reply_markup=kb.drink)


@user_router.callback_query(F.data == "main")
async def user_drink_date(callback_query: CallbackQuery):
    await callback_query.message.answer("Главное меню", reply_markup=kb.main)


@user_router.callback_query(F.data == "add_drink_today_info")
async def user_drink_date(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    if user.tg_id in NOT_DRINKING_TG_ID_LIST:
        answer_text = f"{user.user_full_name}, не наёбывай ! Мы знаем что ты не пил"
    else:
        await add_user_drink(user_id=user.id, action_dt=datetime.now())
        answer_text = f"Сюююююююда!!! Правильно, {user.user_full_name}, сегодня отдыхаем"
    await callback_query.message.answer(answer_text, reply_markup=kb.main)


@user_router.callback_query(F.data == "add_drink_date_info")
async def user_drink_date(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    await callback_query.message.answer("Выбери дату:", reply_markup=await DialogCalendar().start_calendar())


@user_router.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
    is_selected, selected_date = await DialogCalendar().process_selection(callback_query, callback_data)
    if is_selected:
        user = await get_user(callback_query.from_user.id)
        if user.tg_id in NOT_DRINKING_TG_ID_LIST:
            answer_text = f"{user.user_full_name}, не наёбывай ! Мы знаем что ты не пил"
        else:
            if selected_date <= datetime.now():
                await add_user_drink(user_id=user.id, action_dt=selected_date)
                answer_text = (
                    f"Сюююююююда!!! Правильно, {user.user_full_name}, сегодня отдыхаем"
                    if selected_date.strftime('%Y-%m-%d') == datetime.now().strftime('%Y-%m-%d')
                    else f"Одобряю твой поступок, {user.user_full_name}"
                )
            else:
                answer_text = "Я так понимаю ты рассказал мне о своих планах, но все же выбери уже наступившую дату"
        await callback_query.message.answer(answer_text, reply_markup=kb.main)


@user_router.callback_query(F.data == "show_my_stats")
async def mystats_handler(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    drinks = await get_user_drinks(user.id)
    drink_unique_days_list = list([drink.action_dt.strftime('%Y-%m-%d') for drink in list(drinks)])
    if len(drink_unique_days_list) > 0:
        message_text = f"{user.user_full_name}, ты пил в эти даты:\n-----------------------------------\n"
        for drink_day in drink_unique_days_list:
            message_text += f"{drink_day}\n"
    else:
        message_text = 'Я не знаю когда ты пил... Пора это исправлять.\nКогда выпьешь, нажми на кнопку "Я выпил!"'
    await callback_query.message.answer(message_text, reply_markup=kb.main)


@user_router.callback_query(F.data == "show_sober_period_stats")
async def sober_stats_handler(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    stats = await get_drink_board()
    stats_list = list(stats)
    if len(stats_list) > 0:
        drunk_today_users_list = []
        message_text = "Срок трезвости\n-----------------------------------\nПользователь; Крайний раз пил; Дней трезвости\n-----------------------------------\n"
        for index, stats_element in enumerate(stats_list):
            days = stats_element.sober_time.days
            if days == 0:
                drunk_today_users_list.append(stats_element.user_name)
            message_text += f"{index + 1}) {stats_element.user_name};  {stats_element.last_drink.strftime('%Y-%m-%d')};  {days} дн.\n"
        message_text += "-----------------------------------"
        drunk_today_users_qty = len(drunk_today_users_list)
        if drunk_today_users_qty > 0:
            message_suffix_you = "ты"
            message_suffix_i = ""
            if drunk_today_users_qty > 1:
                message_suffix_you = "вы"
                message_suffix_i = "и"
            message_text += f"""\n\n{", ".join(drunk_today_users_list)} - {message_suffix_you} сегодня хорош{message_suffix_i}, так держать !!!"""
        else:
            message_text += "\nСегодня еще никто не пил ? Займитесь делом !"
        message_text += f"\n\n{stats_list[-1].user_name} занимается ерундой, пора выпить..."
    else:
        message_text = "Я пока не собрал статистику. Пьем активнее !"
    await callback_query.message.answer(message_text, reply_markup=kb.main)


@user_router.callback_query(F.data == "show_month_stats")
async def month_stats_handler(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    now = datetime.now()
    month_number = now.month
    month_day = now.day
    month_name = MONTH_NAMES_DICT.get(str(month_number))
    month_stats = await get_month_drink_stats()
    month_stats_list = list(month_stats)
    if len(month_stats_list) > 0:
        message_text = f"Статистика за {month_name} (дней: {month_day}) \n-----------------------------------\nПользователь; дней пил; %\n-----------------------------------\n"
        for index, month_stats_element in enumerate(month_stats_list):
            message_text += f"{index + 1}) {month_stats_element.user_name}; {month_stats_element.drink_days_qty} дн.; {round(100 * month_stats_element.drink_days_qty / month_day)} % \n"
    else:
        message_text = "Нет информации о пользователях"
    await callback_query.message.answer(message_text, reply_markup=kb.main)
