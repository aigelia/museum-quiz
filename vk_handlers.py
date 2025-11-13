import re
from vkbottle.bot import Message
from vkbottle import Keyboard, KeyboardButtonColor, Text

from quiz_storage import QuizStorage
from database import Database


def get_main_keyboard():
    keyboard = Keyboard(one_time=False)
    keyboard.add(Text("Новый вопрос"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("Сдаться"), color=KeyboardButtonColor.NEGATIVE)
    keyboard.row()
    keyboard.add(Text("Мой счёт"), color=KeyboardButtonColor.SECONDARY)
    return keyboard.get_json()


def normalize_answer(answer: str) -> str:
    if not answer:
        return ""
    answer = re.sub(r"\(.*?\)", "", answer)
    answer = answer.split(".")[0]
    return answer.strip().lower()


async def handle_start(message: Message):
    keyboard = get_main_keyboard()
    await message.answer("Привет! Я бот для викторин 🎯", keyboard=keyboard)


async def handle_new_question(message: Message, quiz: QuizStorage, db: Database):
    user_id = message.from_id
    question = quiz.get_random_question()
    await db.set_current_question(user_id, question)

    keyboard = get_main_keyboard()
    await message.answer(question, keyboard=keyboard)


async def handle_surrender(message: Message, quiz: QuizStorage, db: Database):
    user_id = message.from_id
    current_question = await db.get_current_question(user_id)

    if not current_question:
        keyboard = get_main_keyboard()
        await message.answer("У вас нет активного вопроса.", keyboard=keyboard)
        return

    correct_answer = quiz.get_answer(current_question)
    await db.reset_current_question(user_id)
    await message.answer(f"Правильный ответ: {correct_answer}")

    question = quiz.get_random_question()
    await db.set_current_question(user_id, question)

    keyboard = get_main_keyboard()
    await message.answer(question, keyboard=keyboard)


async def handle_score(message: Message, db: Database):
    user_id = message.from_id
    score = await db.get_score(user_id)

    keyboard = get_main_keyboard()
    await message.answer(f"Ваш счёт: {score}", keyboard=keyboard)


async def handle_answer_attempt(message: Message, quiz: QuizStorage, db: Database):
    user_id = message.from_id
    text = message.text.strip()
    current_question = await db.get_current_question(user_id)

    if not current_question:
        keyboard = get_main_keyboard()
        await message.answer(
            "Сначала запросите вопрос командой 'Новый вопрос'.",
            keyboard=keyboard
        )
        return

    correct_answer = quiz.get_answer(current_question)
    keyboard = get_main_keyboard()

    if normalize_answer(text) == normalize_answer(correct_answer):
        await db.increment_score(user_id)
        await db.reset_current_question(user_id)
        await message.answer(
            "Правильно! Поздравляю! 🎉 Для следующего вопроса нажми «Новый вопрос»",
            keyboard=keyboard
        )
    else:
        await message.answer(
            "Неверно 😔 Попробуйте ещё раз или воспользуйтесь командой 'Сдаться'.",
            keyboard=keyboard
        )
