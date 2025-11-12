import re

def main():
    with open("quiz-questions/1vs1200.txt", "r", encoding="KOI8-R") as file:
        raw_content = file.read()

    raw_content = raw_content.split(sep='\n\n')
    questions = []
    answers = []

    for line in raw_content:
        line = line.replace('\n', ' ')
        if 'Вопрос' in line:
            line = re.sub(r"Вопрос\s*\d+\s*:\s*", "", line)
            questions.append(line.strip())
        elif 'Ответ' in line:
            line = line.replace("Ответ: ", "")
            answers.append(line.strip())

    result = dict(zip(questions, answers))
    print(result)

if __name__ == "__main__":
    main()
