import re

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from quiz_storage import QuizStorage
from database import Database


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


def normalize_answer(answer: str) -> str:
    if not answer:
        return ""
    answer = re.sub(r"\(.*?\)", "", answer)
    answer = answer.split(".")[0]
    return answer.strip().lower()


async def handle_new_question(message: Message, quiz: QuizStorage, db: Database, state: FSMContext):
    user_id = message.from_user.id
    question = quiz.get_random_question()
    await db.set_current_question(user_id, question)
    await state.set_state(QuizStates.waiting_for_answer)

    await message.answer(question)

    correct_answer = quiz.get_answer(question)
    print(f"[DEBUG] User {user_id} получил вопрос: {question}")
    print(f"[DEBUG] Правильный ответ: {correct_answer}")


async def handle_solution_attempt(message: Message, quiz: QuizStorage, db: Database, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip()
    current_question = await db.get_current_question(user_id)

    if not current_question:
        await message.answer("Сначала запросите вопрос командой 'Новый вопрос'.")
        await state.clear()
        return

    correct_answer = quiz.get_answer(current_question)
    if normalize_answer(text) == normalize_answer(correct_answer):
        await db.increment_score(user_id)
        await db.reset_current_question(user_id)
        await message.answer("Правильно! Поздравляю! 🎉 Для следующего вопроса нажми «Новый вопрос»")
        await state.clear()
    else:
        await message.answer("Неверно 😔 Попробуйте ещё раз или воспользуйтесь командой 'Сдаться'.")


async def handle_surrender(
        message: Message,
        quiz: QuizStorage,
        db: Database,
        state: FSMContext
):
    user_id = message.from_user.id
    current_question = await db.get_current_question(user_id)

    if not current_question:
        await message.answer("У вас нет активного вопроса.")
        return

    # Показываем правильный ответ
    correct_answer = quiz.get_answer(current_question)
    await db.reset_current_question(user_id)
    await message.answer(f"Правильный ответ: {correct_answer}")

    # Сразу отправляем новый вопрос
    question = quiz.get_random_question()
    await db.set_current_question(user_id, question)
    await state.set_state(QuizStates.waiting_for_answer)
    await message.answer(question)

    print(f"[DEBUG] User {user_id} получил вопрос: {question}")
    print(f"[DEBUG] Правильный ответ: {quiz.get_answer(question)}")


async def handle_score(message: Message, db: Database):
    user_id = message.from_user.id
    score = await db.get_score(user_id)
    await message.answer(f"Ваш счёт: {score}")
