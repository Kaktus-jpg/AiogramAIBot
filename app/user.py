import logging

from aiogram import F, Router
from aiogram.enums.chat_action import ChatAction
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards as kb
from app.database import set_user
from app.states import Chat, Image

user = Router()

# Создаём логгер, используя имя модуля или __name__
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


@user.message(F.text.lower() == "отмена")
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        message_thread_id=message.message_thread_id,
        action=ChatAction.TYPING,
    )
    await message.answer(
        "Добро пожаловать!",
        reply_markup=kb.main,
    )
    await state.clear()


@user.message(Image.wait)
@user.message(Chat.wait)
async def wait_wait(message: Message):
    await message.bot.send_chat_action(
        chat_id=message.from_user.id,
        message_thread_id=message.message_thread_id,
        action=ChatAction.TYPING,
    )
    await message.answer("Ваше сообщение генерируется, подождите")
