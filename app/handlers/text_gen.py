import os
from decimal import Decimal

from aiogram import F, Router
from aiogram.enums.chat_action import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

import app.keyboards as kb
from app.database import calculate, get_user
from app.generators import gen_text, gen_vision
from app.get_loggers import get_logger
from app.handlers.utils import image_download, send_message_splitting, thinking_action
from app.states import Chat

logger = get_logger(__name__)

texts = Router()


@texts.message(Command("chat"))
@texts.message(F.text.lower() == "чат")
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


@texts.message(Chat.text, F.photo)
async def chat_response_vision(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        vision_ai_model = "deepseek/deepseek-v4.1-flash"
        logger.debug(
            f"Запрос от {message.from_user.username} (ID: {message.from_user.id}): {message.text}. Модель: {vision_ai_model}"
        )
        await state.set_state(Chat.wait)
        async with ChatActionSender(
            bot=message.bot,
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            action=ChatAction.TYPING,
        ):
            await thinking_action(message=message)
            ###
            file_name = await image_download(message=message)
            response = await gen_vision(
                message.caption, f"{file_name}.jpeg", vision_ai_model
            )
            await calculate(
                response["usage"],
                vision_ai_model,
                user,
            )
            try:
                await send_message_splitting(
                    message_text=response["response"], message=message
                )
            finally:
                await state.set_state(Chat.text)
                os.remove(f"{file_name}.jpeg")
    else:
        await message.answer("Недостаточно средств на балансе")
    ###
    # response = await gpt_text(message.text, "deepseek/deepseek-v4-flash")
    # await message.answer(response)
    # await state.clear()


@texts.message(Chat.text)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        if message.text:
            text_ai_model = "inclusionai/ling-3.1-flash"
            logger.debug(
                f"Запрос от {message.from_user.username} (ID: {message.from_user.id}): {message.text}. Модель: {text_ai_model}"
            )
            await state.set_state(Chat.wait)
            async with ChatActionSender(
                bot=message.bot,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action=ChatAction.TYPING,
            ):
                await thinking_action(message=message)
                ###

                response = await gen_text(message.text, text_ai_model)
                if response["model"] is not None:
                    await calculate(
                        response["usage"],
                        text_ai_model,
                        user,
                    )
                try:
                    await send_message_splitting(
                        message_text=response["response"], message=message
                    )
                finally:
                    await state.set_state(Chat.text)
        else:
            await message.bot.send_message(
                message.chat.id,
                "Извините, запрос был утерян, не могли бы вы его перезаписать?",
                message_thread_id=message.message_thread_id,
            )
    else:
        await message.answer("Недостаточно средств на балансе")
