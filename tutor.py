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
        quiz = self.llm.generate_quiz(section_title, section_content)

        score, total, user_answers = self.quiz_engine(quiz)

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
