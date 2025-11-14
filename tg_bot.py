import asyncio
import redis.asyncio as redis
from aiogram.filters import CommandStart
from environs import Env
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage

from tg_handlers import (
    command_start_handler,
    handle_new_question,
    handle_surrender,
    handle_score,
    handle_solution_attempt,
    QuizStates
)
from quiz import load_questions


def register_handlers(dp: Dispatcher, redis_client: redis.Redis, questions: dict):
    from functools import partial

    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(
        partial(handle_new_question, redis_client=redis_client, questions=questions),
        F.text == "Новый вопрос"
    )
    dp.message.register(
        partial(handle_surrender, redis_client=redis_client, questions=questions),
        F.text == "Сдаться"
    )
    dp.message.register(
        partial(handle_score, redis_client=redis_client),
        F.text == "Мой счёт"
    )
    dp.message.register(
        partial(handle_solution_attempt, redis_client=redis_client, questions=questions),
        QuizStates.waiting_for_answer
    )


async def main():
    env = Env()
    env.read_env()
    tg_token = env.str("TG_TOKEN")
    redis_host = env.str("REDIS_HOST")
    redis_port = env.int("REDIS_PORT")
    redis_password = env.str("REDIS_PASSWORD", None)

    storage = MemoryStorage()
    bot = Bot(token=tg_token)
    dp = Dispatcher(storage=storage)

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password if redis_password else None,
        decode_responses=True
    )

    try:
        await redis_client.ping()
    except Exception as e:
        raise ConnectionError(f"Ошибка подключения к Redis: {e}")

    questions = load_questions("quiz-questions/1vs1200.txt")

    register_handlers(dp, redis_client, questions)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
