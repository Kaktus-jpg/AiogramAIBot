import asyncio

from aiogram import Router, F
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import logger

import app.keyboards as kb
from app.states import Chat
from app.generators import gpt_text

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать!", reply_markup=kb.main)
    

@user.message(Command('test'))
async def cmd_test(message: Message):
    full_text = 'Прлпдвлпдададмбалатсдчостчлслсьсдаьааоласлтсвлдвосьслсладсювдаоашалсталссл'
    await message.bot.send_message_draft(
                    chat_id=message.chat.id,
                    draft_id=message.message_id,
                    text=full_text,
                    message_thread_id=message.message_thread_id,
                )


@user.message(F.text == "Чат")
async def chatting(message: Message, state: FSMContext):
    await state.set_state(Chat.text)
    await message.answer("Введите ваш запрос")


@user.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    await state.set_state(Chat.wait)
    ###
    # logger.info(f"Запрос от {message.from_user.id}: {message.text}")
    # full_text = ""
    #
    # try:
    #     async for chunk in gpt_text(message.text):
    #         full_text += chunk
    #         try:
    #             await message.bot.send_message_draft(
    #                 chat_id=message.chat.id,
    #                 draft_id=message.message_id,
    #                 text=full_text,
    #                 message_thread_id=message.message_thread_id,
    #             )
    #             await asyncio.sleep(0.1)
    #         except TelegramRetryAfter as e:
    #             logger.warning(f"Rate limit, ждём {e.retry_after} сек")
    #             await asyncio.sleep(e.retry_after)
    #         except Exception as e:
    #             logger.error(f"Ошибка draft: {e}")
    #
    #     await message.answer(full_text)
    # finally:
    #     await state.clear()
    ###
    response = await gpt_text(message.text, "deepseek/deepseek-v4-flash")
    await message.answer(response)
    await state.clear()


@user.message(Chat.wait)
async def wait_wait(message: Message):
    await message.answer("Ваше сообщение генерируется, подождите")
