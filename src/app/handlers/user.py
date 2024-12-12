from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import src.app.keyboards.kb as kb
from src.database.requests import (set_user, get_user, add_user_drink, get_user_drinks, get_drink_board)

user_router = Router()


@user_router.message(F.text == "Отмена")
@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id, message.from_user.username)
    await message.answer(f"Привет {message.from_user.username} !", reply_markup=kb.main)


@user_router.message(F.text == "Я выпил")
async def user_drink(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    await add_user_drink(user.id)
    await message.answer("Одобряю твой поступок")


@user_router.message(F.text == "Моя статистика")
async def mystats_handler(message: Message):
    user = await get_user(message.from_user.id)
    drinks = await get_user_drinks(user.id)

    if drinks:
        message_text = "Ты пил в эти даты:\n"
        for drink in drinks:
            message_text += f"- {drink.action_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
    else:
        message_text = "Я не знаю когда ты пил... Пора это исправлять.\nКогда выпьешь, напиши команду /drink"
    await message.answer(message_text)


@user_router.message(F.text == "Лидерборд")
async def stats_handler(message: Message):
    stats = await get_drink_board()

    if stats:
        message_text = "Лидерборд\n-----------------------------------\nПользователь; Крайний раз пил; Дней трезвости\n-----------------------------------\n"
        for index, stats_element in enumerate(stats):
            days = stats_element.sober_time.days
            message_text += f"{index + 1}) {stats_element.tg_name};  {stats_element.last_drink.strftime('%Y-%m-%d')};  {days} дней\n"
    else:
        message_text = "Я пока не собрал статистику. Пьем активнее !"
    await message.answer(message_text)
