from datetime import datetime
import calendar
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram3_calendar import SimpleCalendar
from aiogram.fsm.context import FSMContext
import src.app.keyboards.kb as kb
from src.app.handlers.common.states import DrinkInput
from src.app.handlers.common.user_checks import NOT_DRINKING_TG_ID_LIST
from src.database.requests import (set_user, get_user, add_user_drink, get_user_drinks, get_drink_board,
                                   get_month_drink_stats)
from src.dicts.dict_loader import MONTH_NAMES_DICT

user_drink_router = Router()


@user_drink_router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id, message.from_user.username)
    user = await get_user(message.from_user.id)
    request_user_name = user.user_full_name if user.user_full_name is not None else user.tg_name
    await message.answer(f"Привет {request_user_name} !", reply_markup=kb.main)


@user_drink_router.callback_query(F.data == "add_drink_info")
async def user_drink(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    request_user_name = user.user_full_name if user.user_full_name is not None else user.tg_name
    await callback_query.message.answer(f"{request_user_name}, когда ты пил ?", reply_markup=kb.drink_choose_day_kb)


@user_drink_router.callback_query(F.data == "main")
async def user_drink_date(callback_query: CallbackQuery):
    await callback_query.message.answer("Главное меню", reply_markup=kb.main)


@user_drink_router.callback_query(F.data == "add_drink_today_info")
async def user_drink_today(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    if user.tg_id in NOT_DRINKING_TG_ID_LIST:
        answer_text = f"❗{user.user_full_name}, не наёбывай ! Мы знаем что ты не пил"
    else:
        await add_user_drink(user_id=user.id, action_dt=datetime.now())
        answer_text = f"✅ Сюююююююда!!! Правильно, {user.user_full_name}, сегодня отдыхаем"
    await callback_query.message.answer(answer_text, reply_markup=kb.main)


@user_drink_router.callback_query(F.data == "add_drink_date_info")
async def user_drink_date(callback: CallbackQuery, state: FSMContext):
    await set_user(callback.from_user.id, callback.from_user.username)
    drink_calendar = SimpleCalendar()
    markup = await drink_calendar.start_calendar()
    await callback.message.answer("Выбери дату:", reply_markup=markup)
    await state.set_state(DrinkInput.waiting_for_date)


@user_drink_router.callback_query(F.data == "show_my_stats")
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


@user_drink_router.callback_query(F.data == "show_sober_period_stats")
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
    else:
        message_text = "Я пока не собрал статистику. Пьем активнее !"
    await callback_query.message.answer(message_text, reply_markup=kb.main)


# Обработчик нажатия на "Месячная статистика" — показывает клавиатуру с месяцами
@user_drink_router.callback_query(F.data == "show_month_stats")
async def show_months_keyboard(callback_query: CallbackQuery):
    now = datetime.now()
    current_month = now.month

    # Формируем список месяцев от текущего к январю (по убыванию)
    months_buttons = []
    for month in range(current_month, 0, -1):
        month_name = MONTH_NAMES_DICT.get(str(month), str(month))
        # callback_data с номером месяца, например, "show_month_stats_7"
        button = InlineKeyboardButton(
            text=month_name,
            callback_data=f"show_month_stats_{month}"
        )
        months_buttons.append([button])  # по одному в строке

    months_kb = InlineKeyboardMarkup(inline_keyboard=months_buttons)

    await callback_query.message.answer("Выбери месяц для просмотра статистики:", reply_markup=months_kb)
    await callback_query.answer()  # чтобы убрать "часики" на кнопке


@user_drink_router.callback_query(lambda c: c.data and c.data.startswith("show_month_stats"))
async def month_stats_handler(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)

    data = callback_query.data  # например, "show_month_stats" или "show_month_stats_5"
    parts = data.split('_')

    # Получаем номер месяца из callback data или текущий месяц
    if len(parts) == 4 and parts[3].isdigit():
        month_number = int(parts[3])
        if not 1 <= month_number <= 12:
            month_number = datetime.now().month
    else:
        month_number = datetime.now().month

    current_year = datetime.now().year
    # Получаем точное количество дней в заданном месяце текущего года
    month_day = calendar.monthrange(current_year, month_number)[1]

    month_name = MONTH_NAMES_DICT.get(str(month_number), "Неизвестный месяц")

    # Вызов функции с передачей номера месяца
    month_stats = await get_month_drink_stats(month=month_number)
    month_stats_list = list(month_stats)

    if len(month_stats_list) > 0:
        message_text = f"Статистика за {month_name} (дней: {month_day}) \n-----------------------------------\nПользователь; дней пил; %\n-----------------------------------\n"
        for index, month_stats_element in enumerate(month_stats_list):
            percent = round(100 * month_stats_element.drink_days_qty / month_day) if month_day else 0
            message_text += f"{index + 1}) {month_stats_element.user_name}; {month_stats_element.drink_days_qty} дн.; {percent} % \n"
    else:
        message_text = "Нет информации о пользователях"

    await callback_query.message.answer(message_text, reply_markup=kb.main)
