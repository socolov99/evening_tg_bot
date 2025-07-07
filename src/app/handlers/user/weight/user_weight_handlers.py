from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram3_calendar import SimpleCalendar
from aiogram.fsm.context import FSMContext
from matplotlib import pyplot as plt
import io
import src.app.keyboards.kb as kb
from src.app.handlers.common.states import WeightInput
from src.database.requests import (set_user, get_user, add_user_weight, get_user_last_15_weight_stats)

user_weight_router = Router()


@user_weight_router.callback_query(F.data == "add_weight_info")
async def user_weight(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    request_user_name = user.user_full_name if user.user_full_name is not None else user.tg_name
    await callback_query.message.answer(f"{request_user_name}, когда ты взвешивался ?",
                                        reply_markup=kb.weight_choose_day_kb)


@user_weight_router.callback_query(F.data == "add_weight_today_info")
async def user_weight_today(callback_query: CallbackQuery, state: FSMContext):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)

    await callback_query.answer()
    await state.set_state(WeightInput.waiting_for_weight)
    await state.update_data(selected_date=datetime.now(), date_chosen=True)
    await callback_query.message.answer("Пожалуйста, введи свой сегодняшний вес")


@user_weight_router.callback_query(F.data == "add_weight_date_info")
async def user_weight_date(callback: CallbackQuery, state: FSMContext):
    await set_user(callback.from_user.id, callback.from_user.username)
    weight_calendar = SimpleCalendar()
    markup = await weight_calendar.start_calendar()
    await callback.message.answer("Выбери дату взвешивания:", reply_markup=markup)
    await state.set_state(WeightInput.waiting_for_weight)
    await state.update_data(date_chosen=False)


@user_weight_router.message(F.text.regexp(r'^\d+(\.\d+)?$'))
async def weight_received(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != WeightInput.waiting_for_weight:
        return
    data = await state.get_data()
    if not data.get("date_chosen"):
        await message.answer("Сначала выберите дату через календарь.")
        return

    weight_value = float(message.text)
    selected_date = data["selected_date"]

    user = await get_user(message.from_user.id)
    await add_user_weight(user_id=user.id, action_dt=selected_date, weight_value=weight_value)

    await message.answer(f"✅ Вес {weight_value} кг на дату {selected_date.strftime('%Y-%m-%d')} записан",
                         reply_markup=kb.main)
    await state.clear()


@user_weight_router.callback_query(F.data == "user_weight_dynamics")
async def user_weight_dynamics(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    request_user_name = user.user_full_name if user.user_full_name is not None else user.tg_name
    await callback_query.message.answer(
        f"{request_user_name}, отобразить динамику твоего веса в виде таблицы или графика ?",
        reply_markup=kb.weight_stats_kb)


@user_weight_router.callback_query(F.data == "show_weight_dynamics_table")
async def show_weight_dynamics_table(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    request_user_name = user.user_full_name if user.user_full_name is not None else user.tg_name
    weights = await get_user_last_15_weight_stats(user.id)
    weights_list = list(weights)

    if len(weights_list) > 0:
        message_text = (
            f"{request_user_name}, вот твоя динамика веса в виде таблицы\n-----------------------------------\nДата;"
            f"               Вес, кг.\n-----------------------------------\n")
        for weights_stats_element in weights_list:
            message_text += f"{weights_stats_element.action_dt};   {weights_stats_element.action_value} кг.\n"
    else:
        message_text = f"{request_user_name}, о тебе нет информации. Взвесься и напиши сколько ты весишь."
    await callback_query.message.answer(message_text, reply_markup=kb.main)


@user_weight_router.callback_query(F.data == "show_weight_dynamics_diagram")
async def show_weight_dynamics_graph(callback_query: CallbackQuery):
    await set_user(callback_query.from_user.id, callback_query.from_user.username)
    user = await get_user(callback_query.from_user.id)
    request_user_name = user.user_full_name if user.user_full_name is not None else user.tg_name
    weights = await get_user_last_15_weight_stats(user.id)
    weights_list = list(weights)

    if len(weights_list) > 0:
        # 🔽 СОРТИРОВКА по дате (если вдруг они не по порядку)
        weights_list.sort(key=lambda x: x.action_dt)

        # Даты и значения
        dates = [w.action_dt.strftime("%d.%m") for w in weights_list]
        values = [w.action_value for w in weights_list]

        # График
        plt.figure(figsize=(8, 4))
        plt.plot(dates, values, marker='o', linestyle='-', color='blue')
        plt.title(f"Динамика веса      ({request_user_name})")
        plt.xlabel("Дата")
        plt.ylabel("Вес (кг)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        # Сохраняем в память
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()

        # Отправка в Telegram
        photo = BufferedInputFile(buffer.read(), filename="weight_graph.png")
        await callback_query.message.answer_photo(
            photo=photo,
            caption=f"{request_user_name}, вот твоя динамика веса в виде графика 📈",
            reply_markup=kb.main
        )
    else:
        await callback_query.message.answer(
            f"{request_user_name}, о тебе нет информации. Взвесься и напиши сколько ты весишь.",
            reply_markup=kb.main
        )
