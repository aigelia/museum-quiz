import random
import redis.asyncio as redis
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from quiz import normalize_answer


class QuizStates(StatesGroup):
    waiting_for_answer = State()


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


async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    keyboard = await get_start_keyboard()
    await message.answer("Привет! Я бот для викторин 🎯", reply_markup=keyboard)


async def handle_new_question(message: Message, redis_client: redis.Redis, questions: dict, state: FSMContext):
    user_id = message.from_user.id
    question = random.choice(list(questions.keys()))
    await redis_client.set(f"user:{user_id}:current_question", question)
    await state.set_state(QuizStates.waiting_for_answer)
    await message.answer(question)


async def handle_solution_attempt(message: Message, redis_client: redis.Redis, questions: dict, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()
    current_question = await redis_client.get(f"user:{user_id}:current_question")

    if not current_question:
        await message.answer("Сначала запросите вопрос командой 'Новый вопрос'.")
        await state.clear()
        return

    correct_answer = questions.get(current_question, "")
    if normalize_answer(text) == normalize_answer(correct_answer):
        await redis_client.incr(f"user:{user_id}:score")
        await redis_client.delete(f"user:{user_id}:current_question")
        await message.answer("Правильно! Поздравляю! 🎉 Для следующего вопроса нажми «Новый вопрос»")
        await state.clear()
    else:
        await message.answer("Неверно 😔 Попробуйте ещё раз или воспользуйтесь командой 'Сдаться'.")


async def handle_surrender(message: Message, redis_client: redis.Redis, questions: dict, state: FSMContext):
    user_id = message.from_user.id
    current_question = await redis_client.get(f"user:{user_id}:current_question")

    if not current_question:
        await message.answer("У вас нет активного вопроса.")
        return

    correct_answer = questions.get(current_question, "")
    await redis_client.delete(f"user:{user_id}:current_question")
    await message.answer(f"Правильный ответ: {correct_answer}")

    question = random.choice(list(questions.keys()))
    await redis_client.set(f"user:{user_id}:current_question", question)
    await state.set_state(QuizStates.waiting_for_answer)
    await message.answer(question)


async def handle_score(message: Message, redis_client: redis.Redis):
    user_id = message.from_user.id
    score = await redis_client.get(f"user:{user_id}:score")
    score = int(score) if score else 0
    await message.answer(f"Ваш счёт: {score}")
