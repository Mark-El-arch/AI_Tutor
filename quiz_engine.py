from learning_stats import LearningStats

def run_quiz(quiz: dict, *, section: str, user_id: str = "user_id") -> tuple[int, int, list]:
    score = 0
    total = len(quiz["questions"])
    user_answers = []

    stats = LearningStats(user_id=user_id)


    for q in quiz["questions"]:
        print(q["question"])
        answer = input("Your answer: ").strip()

        correct = answer.lower() == q["correct_answer"].lower()
        if correct:
            score += 1

        user_answers.append({
            "question": q["question"],
            "answer": answer,
            "correct_answer": q["correct_answer"],
            "is_correct": correct
        })

        # ✅ Step 2 instrumentation
        stats.record_quiz_result(
            section=section,
            correct=correct
        )

    print("\n--- Quiz Results ---")
    print(f"Score: {score} / {total}")

    return score, total, user_answers

