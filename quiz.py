import re


def load_questions(file_path: str) -> dict:
    with open(file_path, "r", encoding="KOI8-R") as file:
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


def normalize_answer(answer: str) -> str:
    if not answer:
        return ""
    answer = re.sub(r"\(.*?\)", "", answer)
    answer = answer.split(".")[0]
    return answer.strip().lower()
