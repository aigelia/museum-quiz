import redis.asyncio as redis
from environs import Env
from vkbottle.bot import Bot, Message

from vk_handlers import (
    handle_start,
    handle_new_question,
    handle_surrender,
    handle_score,
    handle_answer_attempt
)
from quiz_storage import QuizStorage
from database import Database


def register_handlers(bot: Bot, quiz: QuizStorage, db: Database):
    bot.on.message(text=["Начать", "начать", "start"])(lambda msg: handle_start(msg))
    bot.on.message(text="Новый вопрос")(lambda msg: handle_new_question(msg, quiz, db))
    bot.on.message(text="Сдаться")(lambda msg: handle_surrender(msg, quiz, db))
    bot.on.message(text="Мой счёт")(lambda msg: handle_score(msg, db))
    bot.on.message()(lambda msg: handle_answer_attempt(msg, quiz, db))


def main():
    env = Env()
    env.read_env()
    vk_token = env.str("VK_TOKEN")
    redis_host = env.str("REDIS_HOST")
    redis_port = env.int("REDIS_PORT")
    redis_password = env.str("REDIS_PASSWORD", None)

    bot = Bot(token=vk_token)

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password if redis_password else None,
        decode_responses=True
    )
    quiz = QuizStorage("quiz-questions/1vs1200.txt")
    db = Database(redis_client)

    register_handlers(bot, quiz, db)
    bot.run_forever()


if __name__ == "__main__":
    main()