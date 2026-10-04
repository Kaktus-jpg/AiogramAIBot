import asyncio

from aiogram import Bot, Dispatcher

from app import admin, async_main, images, texts, user
from app.handlers.get_loggers import get_logger
from config import TOKEN

logger = get_logger(__name__)


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(user, admin)
    user.include_routers(texts, images)
    await dp.start_polling(bot)


async def on_startup(dispatcher: Dispatcher):
    await async_main()
    logger.debug("Starting bot...")


async def shutdown(dispatcher: Dispatcher):
    logger.debug("Stopping bot...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
