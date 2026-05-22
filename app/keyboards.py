from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


chat_main_button = KeyboardButton(text="Чат")
image_main_button = KeyboardButton(text="Генерация картинок")
main = ReplyKeyboardMarkup(
    keyboard=[
        [chat_main_button],
        [image_main_button],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите пункт меню.",
)


cancel_button = KeyboardButton(text="Отмена")
cancel = ReplyKeyboardMarkup(
    keyboard=[
        [cancel_button],
    ],
    resize_keyboard=True,
)
