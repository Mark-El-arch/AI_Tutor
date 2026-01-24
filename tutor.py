# tutor.py

from progress_manager import ProgressManager


class Tutor:
    """
    Core tutor logic:
    - Explain sections
    - Generate quizzes
    - Run quizzes
    - Persist progress
    """

    def __init__(self, llm, quiz_engine, user_id="default"):
        self.llm = llm
        self.quiz_engine = quiz_engine
        self.progress_manager = ProgressManager(user_id=user_id)

    # -------------------------
    # Section explanation
    # -------------------------

    def explain_section(self, title: str, content: str) -> str:
        prompt = (
            f"Explain the following topic clearly and simply:\n\n"
            f"Title: {title}\n"
            f"Content: {content}"
        )
        explanation = self.llm.generate(prompt)
        print(explanation)
        return explanation

    # -------------------------
    # Quiz generation
    # -------------------------

    def generate_quiz(self, title: str, content: str) -> dict:
        """
        Simple quiz generator (v0.3).
        """
        return {
            "section": title,
            "questions": [
                {
                    "question": f"What is the main idea of {title}?",
                    "correct_answer": "classification"
                }
            ]
        }

    # -------------------------
    # Quiz execution + progress
    # -------------------------

    def take_quiz(self, quiz: dict):
        score, total = self.quiz_engine(quiz)

        self.progress_manager.update_section_progress(
            section_title=quiz["section"],
            quiz_score=score,
            quiz_total=total
        )

        print(f"Score: {score}/{total}")
        print("Progress saved.")

    # -------------------------
    # Progress queries
    # -------------------------

    def has_completed_section(self, section_title: str) -> bool:
        return self.progress_manager.is_section_completed(section_title)

    def get_progress_summary(self):
        return self.progress_manager.get_overall_progress()
