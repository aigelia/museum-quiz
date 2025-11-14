import redis.asyncio as redis
from environs import Env
from vkbottle.bot import Bot

import vk_handlers
from quiz import load_questions


def register_handlers(bot: Bot, redis_client: redis.Redis, questions: dict):
    bot.on.message(text=["Начать", "начать", "start"])(
        lambda msg: vk_handlers.handle_start(msg)
    )
    bot.on.message(text="Новый вопрос")(
        lambda msg: vk_handlers.handle_new_question(msg, redis_client, questions)
    )
    bot.on.message(text="Сдаться")(
        lambda msg: vk_handlers.handle_surrender(msg, redis_client, questions)
    )
    bot.on.message(text="Мой счёт")(
        lambda msg: vk_handlers.handle_score(msg, redis_client)
    )
    bot.on.message()(
        lambda msg: vk_handlers.handle_answer_attempt(msg, redis_client, questions)
    )


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

    questions = load_questions("quiz-questions/1vs1200.txt")

    register_handlers(bot, redis_client, questions)
    bot.run_forever()


if __name__ == "__main__":
    main()
