# quiz_engine.py

# def run_quiz(quiz: dict) -> tuple[int, int, list]:
#     """
#     Runs a quiz interactively and returns:
#     (score, total, detailed_results)
#     """
#     score = 0
#     results = []
#
#     total = len(quiz["questions"])
#
#     for q in quiz["questions"]:
#         print(q["question"])
#         user_answer = input("Your answer: ").strip()
#
#         # normalized = user_answer.lower()
#         ua = user_answer.lower()
#         ca = q["correct_answer"].lower()
#
#         invalid = ua in {"", "i forgot", "no idea", "idk"} or len(ua) < 2
#
#         is_correct = (
#             not invalid and
#             (ua in ca or ca in ua)
#             # normalized == q["correct_answer"].lower()
#         )
#
#         if is_correct:
#             score += 1
#
#         results.append({
#             "question": q["question"],
#             "user_answer": user_answer,
#             "correct_answer": q["correct_answer"],
#             "is_correct": is_correct
#         })
#
#     return score, total, results
# quiz_engine.py

def run_quiz(quiz: dict) -> tuple[int, int, list]:
    score = 0
    total = len(quiz["questions"])
    user_answers = []

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

    print("\n--- Quiz Results ---")
    print(f"Score: {score} / {total}")

    return score, total, user_answers

