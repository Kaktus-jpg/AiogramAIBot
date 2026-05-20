import asyncio
from aiogram import Bot, Dispatcher

from config import TOKEN

from app import admin, user, async_main


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(user, admin)
    await dp.start_polling(bot)


async def on_startup(dispatcher: Dispatcher):
    await async_main()
    print("Starting bot...")


async def shutdown(dispatcher: Dispatcher):
    print("Stopping bot...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
