# # tutor.py
# from progress_manager import ProgressManager
# from quiz_store import QuizStore
# from flashcard_store import FlashcardStore
# from flashcard_engine import FlashcardEngine
# from quiz_store import QuizStore
#
#
# class Tutor:
#     """
#     Core tutor logic:
#     - Explain sections
#     - Generate LLM-powered quizzes
#     - Run quizzes with feedback
#     - Persist and resume progress
#     """
#
#     MIN_PASS_RATIO = 0.7  # 70%
#
#     def __init__(self, llm, quiz_engine, user_id="default"):
#         self.llm = llm
#         self.quiz_engine = quiz_engine
#         self.user_id = user_id
#         self.progress_manager = ProgressManager(user_id=user_id)
#         self.quiz_store = QuizStore(user_id=user_id)
#         self.flashcard_store = FlashcardStore(user_id=user_id)
#         self.flashcard_engine = FlashcardEngine()
#
#     # -------------------------
#     # Session resumption
#     # -------------------------
#
#     def has_completed_section(self, section_title: str) -> bool:
#         return self.progress_manager.is_section_completed(section_title)
#
#     def get_completed_sections(self):
#         return list(self.progress_manager.progress["sections"].keys())
#
#     # -------------------------
#     # Teaching
#     # -------------------------
#
#     def explain_section(self, title: str, content: str):
#         explanation = self.llm.generate(
#             f"Explain the following topic clearly and simply:\n\n"
#             f"Title: {title}\n"
#             f"Content: {content}"
#         )
#         print(explanation)
#         return explanation
#
#     def resume_or_explain_section(self, title: str, content: str):
#         if self.has_completed_section(title):
#             print(f"Skipping '{title}' (already completed).")
#             return
#
#         self.explain_section(title, content)
#
#         passed = self.run_quiz_for_section(title, content)
#
#         if passed:
#             self.progress_manager.mark_section_completed(title)
#             self.generate_and_store_flashcards(title, content)
#
#     # -------------------------
#     # Quiz logic
#     # -------------------------
#
#     def run_quiz_for_section(self, section_title: str, section_content: str):
#         quiz = self.llm.generate_quiz(section_title, section_content)
#
#         score, total, user_answers = self.quiz_engine(quiz)
#
#         print("\n--- Quiz Results ---")
#         for r in user_answers:
#             mark = "✔" if r["is_correct"] else "✘"
#             print(f"{mark} {r['question']}")
#             if not r["is_correct"]:
#                 print(f"  Correct answer: {r['correct_answer']}")
#
#         if score < total:
#             print("\nSection not completed. Please try again later.")
#             return False  # ❌ not mastered
#
#         self.quiz_store.save_quiz_attempt(
#             section_title=section_title,
#             quiz=quiz,
#             score=score,
#             total=total,
#             user_answers=user_answers
#         )
#
#         self.progress_manager.update_section_progress(
#             section_title=section_title,
#             quiz_score=score,
#             quiz_total=total
#         )
#
#         print(f"\nProgress saved for '{section_title}'.")
#         return True  # ✅ mastered
#
#     # -------------------------
#     # Progress reporting
#     # -------------------------
#
#     def get_progress_summary(self):
#         return self.progress_manager.get_overall_progress()
#
#     def generate_and_store_flashcards(self, title: str, content: str):
#         existing = self.flashcard_store.get_flashcards_for_section(title)
#         if existing:
#             return  # prevent duplicates
#
#         flashcards = self.flashcard_engine.generate_flashcards(title, content)
#
#         for card in flashcards:
#             self.flashcard_store.add_flashcard(
#                 section=title,
#                 front=card["front"],
#                 back=card["back"]
#             )

# tutor.py
from progress_manager import ProgressManager
from quiz_store import QuizStore
from flashcard_store import FlashcardStore
from flashcard_engine import FlashcardEngine
from flashcard_review import FlashcardReview
from learning_stats import LearningStats


class Tutor:
    """
    Core tutor logic:
    - Explain sections
    - Generate quizzes
    - Run quizzes with feedback
    - Persist and resume progress
    """

    MIN_PASS_RATIO = 0.7  # 70%

    def __init__(self, llm, quiz_engine, user_id="default"):
        self.llm = llm
        self.quiz_engine = quiz_engine
        self.user_id = user_id

        self.progress_manager = ProgressManager(user_id=user_id)
        self.quiz_store = QuizStore(user_id=user_id)
        self.flashcard_store = FlashcardStore(user_id=user_id)
        self.flashcard_engine = FlashcardEngine()

        self.stats = LearningStats(user_id=user_id)
        self.flashcard_review = FlashcardReview(user_id=user_id)

    # -------------------------
    # Session helpers
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

        result = self.run_quiz_for_section(title, content)

        if result["passed"]:
            self.progress_manager.mark_section_completed(title)
            self.generate_and_store_flashcards(title, content)
        else:
            print("Section not completed. Please try again later.")

    # -------------------------
    # Quiz logic
    # -------------------------

    def run_quiz_for_section(self, section_title: str, section_content: str) -> dict:
        # quiz = self.llm.generate_quiz(section_title, section_content)
        config = self.get_quiz_config(section_title)

        quiz = self.llm.generate_quiz(
            section_title,
            section_content,
            num_questions=config["num_questions"]
        )

        self.MIN_PASS_RATIO = config["pass_ratio"]

        score, total, user_answers = self.quiz_engine(
            quiz,
            section = section_title,
            user_id = self.user_id)

        print("\n--- Quiz Results ---")
        for r in user_answers:
            mark = "✔" if r["is_correct"] else "✘"
            print(f"{mark} {r['question']}")
            if not r["is_correct"]:
                print(f"  Correct answer: {r['correct_answer']}")

        passed = (score / total) >= self.MIN_PASS_RATIO

        if not passed:
            print("\n--- Let's review what you missed ---")
            for r in user_answers:
                if not r["is_correct"]:
                    try:
                        explanation = self.llm.explain_mistake(
                            r["question"],
                            r["correct_answer"]
                        )
                        print("\n" + explanation)
                    except Exception:
                        print("Review unavailable (LLM offline). Please revisit the section content.")

            return {
                "passed": False,
                "score": score,
                "total": total
            }

        # Save successful attempt
        self.quiz_store.save_quiz_attempt(
            section_title=section_title,
            quiz=quiz,
            score=score,
            total=total,
            user_answers=user_answers
        )

        self.progress_manager.update_section_progress(
            section_title=section_title,
            quiz_score=score,
            quiz_total=total
        )

        print(f"\nProgress saved for '{section_title}'.")

        return {
            "passed": True,
            "score": score,
            "total": total
        }

    # -------------------------
    # Flashcards
    # -------------------------

    def generate_and_store_flashcards(self, title: str, content: str):
        existing = self.flashcard_store.get_flashcards_for_section(title)
        if existing:
            return  # prevent duplicates

        flashcards = self.flashcard_engine.generate_flashcards(title, content)

        for card in flashcards:
            self.flashcard_store.add_flashcard(
                section=title,
                front=card["front"],
                back=card["back"]
            )

    # -------------------------
    # Progress reporting
    # -------------------------

    def get_progress_summary(self):
        return self.progress_manager.get_overall_progress()

    # -------------------------
    # STEP 4 — Weak section report
    # -------------------------

    def report_weak_sections(self):
        weak_sections = self.stats.get_weak_sections()

        print("\n=== PERFORMANCE ANALYSIS ===")

        if not weak_sections:
            print("Great work! No weak sections detected 🎉")
            return

        print("Based on your quiz and flashcard performance, you should review:")
        for section in weak_sections:
            print(f" - {section}")

        while True:
            choice = input("\nWould you like to review these sections now? (y/n): ").strip().lower()
            if choice == "y":
                for section in weak_sections:
                    print(f"\n--- Reviewing weak section: {section} ---")
                    self.flashcard_review.review_section_loop(section)
                break
            elif choice == "n":
                print("Okay. You can revisit them later.")
                break
            else:
                print("Please enter 'y' or 'n'.")

    # -------------------------
    # STEP 5 — Adaptive routing
    # -------------------------

    def get_next_sections(self, all_sections: list[str]) -> list[str]:
        """
        Returns sections ordered by learning priority:
        1. Weak sections (not yet completed)
        2. Remaining uncompleted sections
        """

        completed = set(self.get_completed_sections())
        weak_sections = set(self.stats.get_weak_sections())

        # Remove completed sections
        weak_sections = [s for s in weak_sections if s not in completed]

        remaining = [
            s for s in all_sections
            if s not in completed and s not in weak_sections
        ]

        ordered = weak_sections + remaining

        return ordered

    # -------------------------
    # STEP 6 — Adaptive quiz difficulty
    # -------------------------

    def get_quiz_config(self, section_title: str) -> dict:
        stats = self.stats.get_section_stats(section_title)

        attempts = stats.get("quiz_attempts", 0)
        correct = stats.get("quiz_correct", 0)

        accuracy = (correct / attempts) if attempts > 0 else 1.0

        if accuracy < 0.5:
            return {"num_questions": 5, "pass_ratio": 0.8}
        elif accuracy < 0.7:
            return {"num_questions": 4, "pass_ratio": 0.75}
        else:
            return {"num_questions": 3, "pass_ratio": 0.7}

    def session_summary(self):
        progress = self.progress_manager.get_overall_progress()
        weak_sections = self.learning_stats.get_weak_sections()

        print("\n=== SESSION SUMMARY ===")
        print(f"Total sections: {progress['total_sections']}")
        print(f"Completed sections: {progress['completed_sections']}")
        print(f"Completion: {progress['completion_percentage']}%")

        if weak_sections:
            print("\nNeeds reinforcement:")
            for section in weak_sections:
                print(f" - {section}")
        else:
            print("\nAll sections are currently strong. Well done!")

        print("\nNext step recommendation:")
        if weak_sections:
            print(f"→ Review flashcards for: {weak_sections[0]}")
        else:
            print("→ Move on to the next topic.")
