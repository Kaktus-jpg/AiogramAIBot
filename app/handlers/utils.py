import asyncio
import uuid

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import InputRichMessage, Message

from app.get_loggers import get_logger

logger = get_logger(__name__)


async def image_download(message: Message):
    logger.info(
        f"Запрос к фотографии от {message.from_user.username} (ID: {message.from_user.id}): {message.caption}"
    )
    file = await message.bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path
    file_name = uuid.uuid4()
    await message.bot.download_file(file_path, f"{file_name}.jpeg")
    return file_name


async def send_message_splitting(
    message_text: str, message: Message, chunk_length: int = 80
):
    draft_failed = False

    chunks = [
        message_text[i : i + chunk_length]
        for i in range(0, len(message_text), chunk_length)
    ]
    full_text = ""

    iterator = iter(chunks)

    for chunk in iterator:
        full_text += str(chunk)
        try:
            await message.bot.send_rich_message_draft(
                chat_id=message.chat.id,
                draft_id=message.message_id,
                rich_message=InputRichMessage(
                    markdown=full_text,
                    skip_entity_detection=False,
                ),
                message_thread_id=message.message_thread_id,
            )
        except TelegramBadRequest as exc:
            logger.warning(
                "Черновик отклонён на длине %s: %s",
                len(full_text),
                exc.message,
            )
            draft_failed = True
            break  # Не отправляем остальные ошибочные промежуточные варианты
        except TelegramRetryAfter as exc:
            logger.warning("Лимит Telegram: %s сек.", exc.retry_after)
            await asyncio.sleep(exc.retry_after)
        except Exception as exc:
            logger.error(f"Ошибка draft: {exc}")
        else:
            await asyncio.sleep(0.85)

    if draft_failed:
        # Используем весь исходный ответ, а не full_text:
        # цикл мог остановиться посередине сообщения.

        for chunk in iterator:
            full_text += str(chunk)
            try:
                await message.bot.send_message_draft(
                    chat_id=message.chat.id,
                    draft_id=message.message_id,
                    text=full_text,
                    message_thread_id=message.message_thread_id,
                    parse_mode="markdown",
                )
            except TelegramBadRequest as exc:
                logger.warning(
                    "Черновик отклонён на длине %s: %s",
                    len(full_text),
                    exc.message,
                )
            except TelegramRetryAfter as exc:
                logger.warning("Лимит Telegram: %s сек.", exc.retry_after)
                await asyncio.sleep(exc.retry_after)
            except Exception as exc:
                logger.error(f"Ошибка draft: {exc}")
            else:
                await asyncio.sleep(0.85)

        await message.answer(text=message_text)

    else:
        await message.answer_rich(
            rich_message=InputRichMessage(
                markdown=message_text,
                skip_entity_detection=False,
            )
        )


async def thinking_action(message: Message):
    await message.bot.send_message_draft(
        chat_id=message.chat.id,
        draft_id=message.message_id,
        text="Думаю",
        message_thread_id=message.message_thread_id,
    )
