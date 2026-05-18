from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

chat_main_button = KeyboardButton(text="Чат")
main = ReplyKeyboardMarkup(
    keyboard=[
        [chat_main_button],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню.",
)
