def run_quiz(quiz: dict) -> dict:
    results = []

    for q in quiz['questions']:
        print(q['question'])
        user_answer = input("Your answer: ").strip()
        is_correct = user_answer.lower() == q['correct_answer'].lower()
        results.append({'question': q['question'],
                        'user_answer': user_answer,
                        'correct_answer': q['correct_answer'],
                        'is_correct': is_correct})

        return results