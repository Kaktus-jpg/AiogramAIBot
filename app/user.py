from aiogram import Router, F
from aiogram.types import CommandStart, Message

user = Router()

@user.message(CommandStart())
async def cmd_start(message: Message):
    message.answer('Добро пожаловать!')
