from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Я выпил"), KeyboardButton(text="Моя статистика")],
    [KeyboardButton(text="Лидерборд")]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню")

cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True)
