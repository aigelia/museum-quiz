import random
import redis.asyncio as redis
from vkbottle.bot import Message
from vkbottle import Keyboard, KeyboardButtonColor, Text

from quiz import normalize_answer


def get_main_keyboard():
    keyboard = Keyboard(one_time=False)
    keyboard.add(Text("Новый вопрос"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("Сдаться"), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Text("Мой счёт"), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


async def handle_start(message: Message):
    keyboard = get_main_keyboard()
    await message.answer("Привет! Я бот для викторин 🎯", keyboard=keyboard)


async def handle_new_question(message: Message, redis_client: redis.Redis, questions: dict):
    user_id = message.from_id
    question = random.choice(list(questions.keys()))
    await redis_client.set(f"user:{user_id}:current_question", question)

    keyboard = get_main_keyboard()
    await message.answer(question, keyboard=keyboard)


async def handle_surrender(message: Message, redis_client: redis.Redis, questions: dict):
    user_id = message.from_id
    current_question = await redis_client.get(f"user:{user_id}:current_question")

    if not current_question:
        keyboard = get_main_keyboard()
        await message.answer("У вас нет активного вопроса.", keyboard=keyboard)
        return

    correct_answer = questions.get(current_question, "")
    await redis_client.delete(f"user:{user_id}:current_question")
    await message.answer(f"Правильный ответ: {correct_answer}")

    question = random.choice(list(questions.keys()))
    await redis_client.set(f"user:{user_id}:current_question", question)

    keyboard = get_main_keyboard()
    await message.answer(question, keyboard=keyboard)


async def handle_score(message: Message, redis_client: redis.Redis):
    user_id = message.from_id
    score = await redis_client.get(f"user:{user_id}:score")
    score = int(score) if score else 0

    keyboard = get_main_keyboard()
    await message.answer(f"Ваш счёт: {score}", keyboard=keyboard)


async def handle_answer_attempt(message: Message, redis_client: redis.Redis, questions: dict):
    user_id = message.from_id
    text = message.text.strip()
    current_question = await redis_client.get(f"user:{user_id}:current_question")

    if not current_question:
        keyboard = get_main_keyboard()
        await message.answer(
            "Сначала запросите вопрос командой 'Новый вопрос'.",
            keyboard=keyboard
        )
        return

    correct_answer = questions.get(current_question, "")
    keyboard = get_main_keyboard()

    if normalize_answer(text) == normalize_answer(correct_answer):
        await redis_client.incr(f"user:{user_id}:score")
        await redis_client.delete(f"user:{user_id}:current_question")
        await message.answer(
            "Правильно! Поздравляю! 🎉 Для следующего вопроса нажми «Новый вопрос»",
            keyboard=keyboard
        )
    else:
        await message.answer(
            "Неверно 😔 Попробуйте ещё раз или воспользуйтесь командой 'Сдаться'.",
            keyboard=keyboard
        )
