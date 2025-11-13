import asyncio
from functools import partial
import re

import redis.asyncio as redis
from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from quiz_storage import QuizStorage
from database import Database


async def get_start_keyboard():
    buttons_text = [
        ["Новый вопрос", "Сдаться"],
        ["Мой счёт"]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=item) for item in row] for row in buttons_text],
        resize_keyboard=True
    )
    return keyboard


async def command_start_handler(message: Message):
    keyboard = await get_start_keyboard()
    await message.answer("Привет! Я бот для викторин 🎯", reply_markup=keyboard)


def normalize_answer(answer: str) -> str:
    if not answer:
        return ""
    answer = re.sub(r"\(.*?\)", "", answer)
    answer = answer.split(".")[0]
    return answer.strip().lower()


async def text_handler(message: Message, quiz: QuizStorage, db: Database):
    user_id = message.from_user.id
    text = message.text.strip()

    if text == "Новый вопрос":
        question = quiz.get_random_question()
        await db.set_current_question(user_id, question)
        await message.answer(question)

        correct_answer = quiz.get_answer(question)
        print(f"[DEBUG] User {user_id} получил вопрос: {question}")
        print(f"[DEBUG] Правильный ответ: {correct_answer}")

    elif text == "Сдаться":
        current_question = await db.get_current_question(user_id)
        if not current_question:
            await message.answer("У вас нет активного вопроса.")
        else:
            correct_answer = quiz.get_answer(current_question)
            await db.reset_current_question(user_id)
            await message.answer(f"Правильный ответ: {correct_answer}")

    elif text == "Мой счёт":
        score = await db.get_score(user_id)
        await message.answer(f"Ваш счёт: {score}")

    else:
        current_question = await db.get_current_question(user_id)
        if not current_question:
            await message.answer("Сначала запросите вопрос командой 'Новый вопрос'.")
            return

        correct_answer = quiz.get_answer(current_question)
        if normalize_answer(text) == normalize_answer(correct_answer):
            await db.increment_score(user_id)
            await db.reset_current_question(user_id)
            await message.answer("Правильно! Поздравляю! 🎉 Для следующего вопроса нажми «Новый вопрос»")
        else:
            await message.answer("Неверно 😔 Попробуйте ещё раз или воспользуйтесь командой 'Сдаться'.")


async def main():
    env = Env()
    env.read_env()
    tg_token = env.str("TG_TOKEN").strip()
    redis_host = env.str("REDIS_HOST").strip()
    redis_port = env.int("REDIS_PORT")
    redis_password = env.str("REDIS_PASSWORD", None)

    bot = Bot(token=tg_token)
    dp = Dispatcher()

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password if redis_password else None,
        decode_responses=True
    )

    try:
        await redis_client.ping()
        print(f"Подключаемся к Redis: host='{redis_host}', port={redis_port}, password={'set' if redis_password else 'none'}")
        print("Redis подключен ✅")
    except Exception as e:
        raise ConnectionError(f"Ошибка подключения к Redis: {e}")

    quiz = QuizStorage("quiz-questions/1vs1200.txt")
    db = Database(redis_client)

    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(partial(text_handler, quiz=quiz, db=db))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
