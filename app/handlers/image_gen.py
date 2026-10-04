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
from app.generators import gen_image, gen_vision_image
from app.handlers.get_loggers import get_logger
from app.handlers.utils import image_download, thinking_action
from app.states import Image

images = Router()


logger = get_logger(__name__)


@images.message(Command("image_gen"))
@images.message(F.text.lower() == "генерация картинок")
async def chatting(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        await state.set_state(Image.text)
        await message.bot.send_chat_action(
            chat_id=message.from_user.id,
            message_thread_id=message.message_thread_id,
            action=ChatAction.TYPING,
        )
        await message.answer(
            "Введите ваш запрос для генерации изображения", reply_markup=kb.cancel
        )
    else:
        await message.answer("Недостаточно средств на балансе")


@images.message(Image.text, F.photo)
async def chat_image_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        if message.caption:
            image_gen_ai_model = "bytedance-seed/seedream-5-0-flash"

            logger.debug(
                f"Запрос от {message.from_user.username} (ID: {message.from_user.id}): {message.text}. Модель: {image_gen_ai_model}"
            )
            await state.set_state(Image.wait)
            async with ChatActionSender(
                bot=message.bot,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action=ChatAction.TYPING,
            ):
                await thinking_action(message=message)
            async with ChatActionSender(
                bot=message.bot,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action=ChatAction.UPLOAD_PHOTO,
            ):
                file_name = await image_download(message=message)
                response = await gen_vision_image(
                    req=message.caption,
                    file=f"{file_name}.jpeg",
                    model=image_gen_ai_model,
                )
                await calculate(
                    response["usage"],
                    image_gen_ai_model,
                    user,
                )

                await message.answer_photo(photo=response["image"])
                await state.set_state(Image.text)
                os.remove(f"{file_name}.jpeg")
        else:
            await message.answer(
                "Ошибка: к фото обязательно должен быть приложен текст"
            )
    else:
        await message.answer("Недостаточно средств на балансе")


@images.message(Image.text)
async def chat_response(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if Decimal(user.balance) > 0:
        if message.text:
            image_gen_ai_model = "recraft/recraft-v4.1-flash"

            logger.debug(
                f"Запрос от {message.from_user.username} (ID: {message.from_user.id}): {message.text}. Модель: {image_gen_ai_model}"
            )
            await state.set_state(Image.wait)
            async with ChatActionSender(
                bot=message.bot,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action=ChatAction.TYPING,
            ):
                await thinking_action(message=message)
            async with ChatActionSender(
                bot=message.bot,
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                action=ChatAction.UPLOAD_PHOTO,
            ):
                response = await gen_image(message.text, image_gen_ai_model)
                await calculate(
                    response["usage"],
                    image_gen_ai_model,
                    user,
                )

                await message.answer_photo(photo=response["image"])
                await state.set_state(Image.text)
        else:
            await message.bot.send_message(
                message.chat.id,
                "Извините, запрос для генерации изображения был утерян.\nНе могли бы вы его перезаписать?",
                message_thread_id=message.message_thread_id,
            )
    else:
        await message.answer("Недостаточно средств на балансе")
