from datetime import datetime
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram3_calendar import SimpleCalendar
from aiogram.fsm.context import FSMContext
import src.app.keyboards.kb as kb
from src.app.handlers.common.states import DrinkInput, WeightInput
from src.database.requests import (get_user, add_user_drink)
from types import SimpleNamespace
from src.app.handlers.common.user_checks import NOT_DRINKING_TG_ID_LIST

calendar_router = Router()


def parse_calendar_callback(data_str: str):
    # Ожидаем формат: simple_calendar:act:year:month[:day]
    parts = data_str.split(':')
    if len(parts) < 4:
        return None

    # prefix = parts[0]
    act = int(parts[1])
    year = int(parts[2])
    month = int(parts[3])
    day = int(parts[4]) if len(parts) > 4 else None

    return SimpleNamespace(act=act, year=year, month=month, day=day)


@calendar_router.callback_query()
async def calendar_handler(callback_query: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    user_calendar = SimpleCalendar()

    data = parse_calendar_callback(callback_query.data)  # Парсим callback.data в объект с полями
    if not data:
        await callback_query.answer("Ошибка: неверные данные", show_alert=True)
        return

    selected_flag, selected_date = await user_calendar.process_selection(callback_query, data)

    if not selected_flag:
        # Пользователь нажал стрелочку, календарь обновлен внутри process_selection
        await callback_query.answer()
        return

    # Пользователь выбрал дату, она лежит в selected_date (datetime)
    if current_state == DrinkInput.waiting_for_date:
        user = await get_user(callback_query.from_user.id)
        if user.tg_id in NOT_DRINKING_TG_ID_LIST:
            answer_text = f"❗{user.user_full_name}, не наёбывай! Мы знаем, что ты не пил"
        else:
            if selected_date <= datetime.now():
                await add_user_drink(user_id=user.id, action_dt=selected_date)
                answer_text = (
                    f"✅ Сюююююююда!!! Правильно, {user.user_full_name}, сегодня отдыхаем"
                    if selected_date.date() == datetime.now().date()
                    else f"✅ Одобряю твой поступок, {user.user_full_name}"
                )
            else:
                answer_text = "❗Я так понимаю, ты рассказал мне о своих планах, но всё же выбери уже наступившую дату"

        await callback_query.message.answer(answer_text, reply_markup=kb.main)
        await state.clear()

    elif current_state == WeightInput.waiting_for_weight:
        if selected_date <= datetime.now():
            await state.update_data(selected_date=selected_date, date_chosen=True)
            await callback_query.message.answer(f"Напишите свой вес на {selected_date.strftime('%Y-%m-%d')}:")
            await callback_query.answer()
        else:
            await callback_query.message.answer(
                "❗Я так понимаю, ты рассказал мне о своих планах, но всё же выбери уже наступившую дату",
                reply_markup=kb.main)
            await state.clear()
    else:
        await callback_query.answer("Сначала выберите действие через меню", show_alert=True)
