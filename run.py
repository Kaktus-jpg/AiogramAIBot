import asyncio
import logging

from aiogram import Bot, Dispatcher

from app import admin, async_main, images, texts, user
from config import TOKEN

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


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
    logging.debug("Starting bot...")


async def shutdown(dispatcher: Dispatcher):
    logging.debug("Stopping bot...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
