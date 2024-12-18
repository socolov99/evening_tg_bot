from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# main: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text="Я выпил"), KeyboardButton(text="Моя статистика")],
#     [KeyboardButton(text="Лидерборд")]
# ], resize_keyboard=True, input_field_placeholder="Выберите пункт меню")

# finish_keyboard = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')],
# ])

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я выпил!', callback_data='add_frink_info')],
    [InlineKeyboardButton(text='Моя статистика', callback_data='show_my_stats')],
    [InlineKeyboardButton(text='Месячная статистика', callback_data='show_month_stats')],
    [InlineKeyboardButton(text='Срок трезвости', callback_data='show_sober_period_stats')]
])
