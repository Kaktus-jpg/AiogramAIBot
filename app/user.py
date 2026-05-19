import asyncio
from asyncio.log import logger

from aiogram import Router, F

from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.states import Chat
from app.generators import gpt_text
from app.database import set_user

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id)
    await message.answer("Добро пожаловать!", reply_markup=kb.main)


@user.message(F.text == "Чат")
async def chatting(message: Message, state: FSMContext):
    await state.set_state(Chat.text)
    await message.answer("Введите ваш запрос")


@user.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    await state.set_state(Chat.wait)
    ###
    print(f"Запрос от {message.from_user.id}: {message.text}")
    response = await gpt_text(message.text)

    chunks = [response[i : i + 90] for i in range(0, len(response), 90)]
    full_text = ""

    try:
        for chunk in chunks:
            full_text += chunk
            try:
                await message.bot.send_message_draft(
                    chat_id=message.chat.id,
                    draft_id=message.message_id,
                    text=full_text,
                    message_thread_id=message.message_thread_id,
                    parse_mode="markdown",
                )
                await asyncio.sleep(0.85)
            except TelegramRetryAfter as e:
                logger.warning(f"Rate limit, ждём {e.retry_after} сек")
                await asyncio.sleep(e.retry_after)
            except Exception as e:
                logger.error(f"Ошибка draft: {e}")

        await message.answer(full_text, parse_mode="markdown")
    finally:
        await state.clear()
    ###
    # response = await gpt_text(message.text, "deepseek/deepseek-v4-flash")
    # await message.answer(response)
    # await state.clear()


@user.message(Chat.wait)
async def wait_wait(message: Message):
    await message.answer("Ваше сообщение генерируется, подождите")
