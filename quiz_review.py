from quiz_store import QuizStore
import random


class QuizReview:
    """
    Handles reviewing past quizzes outside the AI tutoring flow.
    """

    def __init__(self, user_id="default"):
        self.store = QuizStore(user_id=user_id)

    def list_sections(self):
        """
        Returns a list of sections with stored quizzes.
        """
        quizzes = self.store.list_sections()
        return list(quizzes)

    def review_section(self, section_title: str):
        """
        Review all quiz attempts for a given section.
        """
        quizzes = self.store.get_quizzes_for_section(section_title)

        if not quizzes:
            print(f"No quizzes found for section '{section_title}'.")
            return []

        print(f"\n=== Quiz Review: {section_title} ===")

        for attempt_idx, attempt in enumerate(quizzes, start=1):
            score = attempt["score"]
            total = attempt["total"]
            answers = attempt["user_answers"]

            print(f"\nAttempt {attempt_idx}: Score {score}/{total}")

            for r in answers:
                mark = "✔" if r["is_correct"] else "✘"
                print(f"{mark} {r['question']}")
                if not r["is_correct"]:
                    print(f"  Correct answer: {r['correct_answer']}")

        return quizzes

    def random_question_review(self, section_title: str, limit: int = 3):
        """
        Randomly review past questions from a section.
        """
        quizzes = self.store.get_quizzes_for_section(section_title)

        if not quizzes:
            print(f"No quizzes found for section '{section_title}'.")
            return []

        all_questions = []
        for attempt in quizzes:
            all_questions.extend(attempt["user_answers"])

        if not all_questions:
            print("No questions available.")
            return []

        random.shuffle(all_questions)
        selected = all_questions[:limit]

        print(f"\n=== Random Quiz Review: {section_title} ===")

        for idx, q in enumerate(selected, start=1):
            print(f"\nQuestion {idx}")
            print(f"Q: {q['question']}")
            input("Press Enter to reveal answer...")
            print(f"A: {q['correct_answer']}")

        return selected
