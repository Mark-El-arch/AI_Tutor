# quiz_engine.py

def run_quiz(quiz: dict) -> tuple[int, int]:
    """
    Runs a quiz interactively and returns (score, total).
    """
    score = 0
    total = len(quiz["questions"])

    for q in quiz["questions"]:
        print(q["question"])
        user_answer = input("Your answer: ").strip()

        if user_answer.lower() == q["correct_answer"].lower():
            score += 1

    return score, total
