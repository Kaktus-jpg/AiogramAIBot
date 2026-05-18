import asyncio
from aiogram import Bot, Dispatcher

from config import TOKEN

from app import admin, user


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(user, admin)
    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    print("Starting bot...")


async def shutdown(dispatcher: Dispatcher):
    print("Stopping bot...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
