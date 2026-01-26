# tutor.py
from progress_manager import ProgressManager


class Tutor:
    """
    Core tutor logic:
    - Explain sections
    - Generate LLM-powered quizzes
    - Run quizzes with feedback
    - Persist and resume progress
    """

    MIN_PASS_RATIO = 0.7  # 70%

    def __init__(self, llm, quiz_engine, user_id="default"):
        self.llm = llm
        self.quiz_engine = quiz_engine
        self.progress_manager = ProgressManager(user_id=user_id)

    # -------------------------
    # Session resumption
    # -------------------------

    def has_completed_section(self, section_title: str) -> bool:
        return self.progress_manager.is_section_completed(section_title)

    def get_completed_sections(self):
        return list(self.progress_manager.progress["sections"].keys())

    # -------------------------
    # Teaching
    # -------------------------

    def explain_section(self, title: str, content: str):
        prompt = (
            f"Explain the following topic clearly and simply:\n\n"
            f"Title: {title}\n"
            f"Content: {content}"
        )
        explanation = self.llm.generate(prompt)
        print(explanation)

    def resume_or_explain_section(self, title: str, content: str):
        if self.has_completed_section(title):
            print(f"Skipping '{title}' (already completed).")
            return

        self.explain_section(title, content)
        self.run_quiz_for_section(title, content)

    # -------------------------
    # Quiz logic
    # -------------------------

    def run_quiz_for_section(self, section_title: str, section_content: str):
        quiz = self.llm.generate_quiz(section_title, section_content)

        score, total, results = self.quiz_engine(quiz)

        print("\n--- Quiz Results ---")
        for r in results:
            if r["is_correct"]:
                print(f"✔ {r['question']}")
            else:
                print(f"✘ {r['question']}")
                print(f"  Correct answer: {r['correct_answer']}")

        print(f"\nScore: {score} / {total}")

        pass_ratio = score / total if total > 0 else 0

        if pass_ratio >= self.MIN_PASS_RATIO:
            self.progress_manager.update_section_progress(
                section_title=section_title,
                quiz_score=score,
                quiz_total=total
            )
            print(f"Progress saved for '{section_title}'.")
        else:
            print(
                f"Section '{section_title}' not completed. "
                f"Please review and try again."
            )

    # -------------------------
    # Progress reporting
    # -------------------------

    def get_progress_summary(self):
        return self.progress_manager.get_overall_progress()
