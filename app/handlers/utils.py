import asyncio
import logging
import uuid

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def image_download(message: Message):
    logger.info(
        f"Запрос к фотографии от {message.from_user.username} (ID: {message.from_user.id}): {message.caption}"
    )
    file = await message.bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path
    file_name = uuid.uuid4()
    await message.bot.download_file(file_path, f"{file_name}.jpeg")
    return file_name


async def message_splitting(
    message_text: str, message: Message, chunk_length: int = 80
):
    chunks = [
        message_text[i : i + chunk_length]
        for i in range(0, len(message_text), chunk_length)
    ]
    full_text = ""
    for chunk in chunks:
        full_text += str(chunk)
        try:
            await message.bot.send_message_draft(
                chat_id=message.chat.id,
                draft_id=message.message_id,
                text=full_text,
                message_thread_id=message.message_thread_id,
                parse_mode="markdown",
            )
            await asyncio.sleep(0.85)
        except TelegramRetryAfter as exc:
            logger.warning(f"Rate limit, ждём {exc.retry_after} сек")
            await asyncio.sleep(exc.retry_after)
        except TelegramBadRequest as exc:
            logger.error(exc)
        except Exception as exc:
            logger.error(f"Ошибка draft: {exc}")

    await message.answer(full_text, parse_mode="markdown")


async def thinking_action(message: Message):
    await message.bot.send_message_draft(
        chat_id=message.chat.id,
        draft_id=message.message_id,
        text="Думаю",
        message_thread_id=message.message_thread_id,
    )
