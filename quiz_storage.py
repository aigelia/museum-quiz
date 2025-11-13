import random
import re

from environs import Env


class QuizStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.questions = self._load_questions()

    def _load_questions(self) -> dict:
        with open(self.file_path, "r", encoding="KOI8-R") as file:
            raw_content = file.read()

        raw_content = raw_content.split('\n\n')
        questions, answers = [], []

        for line in raw_content:
            line = line.replace('\n', ' ')
            if 'Вопрос' in line:
                line = re.sub(r"Вопрос\s*\d+\s*:\s*", "", line)
                questions.append(line.strip())
            elif 'Ответ' in line:
                line = line.replace("Ответ: ", "")
                answers.append(line.strip())

        return dict(zip(questions, answers))

    def get_random_question(self) -> str:
        return random.choice(list(self.questions.keys()))

    def get_answer(self, question: str) -> str:
        return self.questions.get(question, "")
