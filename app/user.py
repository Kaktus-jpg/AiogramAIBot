import asyncio
import logging
from decimal import Decimal

from aiogram import F, Router
from aiogram.enums.chat_action import ChatAction
from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

import app.keyboards as kb
from app.database import calculate, get_user, set_user
from app.generators import gpt_text
from app.states import Chat

user = Router()

# Создаём логгер, используя имя модуля или __name__
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@user.message(F.text == "Отмена")
@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await set_user(message.from_user.id)
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        message_thread_id=message.message_thread_id,
        action=ChatAction.TYPING,
    )
    await message.answer("Добро пожаловать!", reply_markup=kb.main)
    await state.clear()


@user.message(F.text == "Чат")
async def chatting(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        await state.set_state(Chat.text)
        await message.bot.send_chat_action(
            chat_id=message.from_user.id,
            message_thread_id=message.message_thread_id,
            action=ChatAction.TYPING,
        )
        await message.answer("Введите ваш запрос", reply_markup=kb.cancel)
    else:
        await message.answer("Недостаточно средств на балансе")


@user.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        await state.set_state(Chat.wait)
        async with ChatActionSender(
            bot=message.bot,
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            action=ChatAction.TYPING,
        ):
            await message.bot.send_message_draft(
                chat_id=message.chat.id,
                draft_id=message.message_id,
                text="Думаю",
                message_thread_id=message.message_thread_id,
            )
            ###
            logger.info(
                f"Запрос от {message.from_user.username} (ID: {message.from_user.id}): {message.text}"
            )
            response = await gpt_text(message.text)
            await calculate(
                message.from_user.id,
                response["usage"],
                "deepseek/deepseek-v4-flash",
                user,
            )
            chunks = [
                response["response"][i : i + 90]
                for i in range(0, len(response["response"]), 90)
            ]
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
                await state.set_state(Chat.text)
    else:
        await message.answer("Недостаточно средств на балансе")
    ###
    # response = await gpt_text(message.text, "deepseek/deepseek-v4-flash")
    # await message.answer(response)
    # await state.clear()


@user.message(Chat.wait)
async def wait_wait(message: Message):
    await message.bot.send_chat_action(
        chat_id=message.from_user.id,
        message_thread_id=message.message_thread_id,
        action=ChatAction.TYPING,
    )
    await message.answer("Ваше сообщение генерируется, подождите")
