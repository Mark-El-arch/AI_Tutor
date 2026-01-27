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
        explanation = self.llm.generate(
            f"Explain the following topic clearly and simply:\n\n"
            f"Title: {title}\n"
            f"Content: {content}"
        )
        print(explanation)
        return explanation

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
            mark = "✔" if r["is_correct"] else "✘"
            print(f"{mark} {r['question']}")
            if not r["is_correct"]:
                print(f"  Correct answer: {r['correct_answer']}")

        if score < total:
            print("\n--- Let's review what you missed ---")

            for r in results:
                if not r["is_correct"]:
                    explanation = self.llm.explain_mistake(
                        r["question"],
                        r["correct_answer"]
                    )
                    print("\n" + explanation)

            print("\nSection not completed. Please try again later.")
            return  # ❌ Do NOT mark progress yet

        # ✅ Mastery achieved
        self.progress_manager.update_section_progress(
            section_title=section_title,
            quiz_score=score,
            quiz_total=total
        )

        print(f"\nProgress saved for '{section_title}'.")

    # -------------------------
    # Progress reporting
    # -------------------------

    def get_progress_summary(self):
        return self.progress_manager.get_overall_progress()
