import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from environs import Env


async def command_start_handler(message: Message):
    await message.answer("Здравствуйте!")


async def text_handler(message: Message, bot: Bot):
    await message.answer(message.text)


async def main():
    env = Env()
    env.read_env()

    tg_token = env.str("TG_TOKEN")
    bot = Bot(token=tg_token)
    dp = Dispatcher()

    dp.message.register(
        command_start_handler,
        CommandStart()
    )
    dp.message.register(text_handler)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())