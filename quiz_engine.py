# quiz_engine.py

def run_quiz(quiz: dict) -> tuple[int, int, list]:
    """
    Runs a quiz interactively and returns:
    (score, total, detailed_results)
    """
    score = 0
    results = []

    total = len(quiz["questions"])

    for q in quiz["questions"]:
        print(q["question"])
        user_answer = input("Your answer: ").strip()

        normalized = user_answer.lower()
        invalid = (
            normalized in {"", "i forgot", "no idea", "idk"} or
            len(normalized) < 2
        )

        is_correct = (
            not invalid and
            normalized == q["correct_answer"].lower()
        )

        if is_correct:
            score += 1

        results.append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": q["correct_answer"],
            "is_correct": is_correct
        })

    return score, total, results
