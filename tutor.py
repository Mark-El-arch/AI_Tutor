# tutor.py
from progress_manager import ProgressManager
from quiz_store import QuizStore
from flashcard_store import FlashcardStore
from flashcard_engine import FlashcardEngine
from flashcard_review import FlashcardReview
from learning_stats import LearningStats
from datetime import datetime, timedelta
from typing import List, Dict


class Tutor:
    """
    Core tutor logic:
    - Explain sections
    - Generate quizzes
    - Run quizzes with feedback
    - Persist and resume progress
    """

    MIN_PASS_RATIO = 0.7  # 70%
    MIN_EASE_FACTOR = 1.3

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
        self.learning_stats = LearningStats(user_id=user_id)

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
        difficulty = self._resolve_quiz_difficulty(section_title)

        quiz = self.llm.generate_quiz(
            section_title,
            section_content,
            difficulty=difficulty,
            num_questions=config["num_questions"]
        )
        difficulty = self._resolve_quiz_difficulty(section_title)

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

    def _resolve_quiz_difficulty(self, section_title: str) -> str:
            """
            Determines quiz difficulty based on historical quiz accuracy.
            """
            accuracy = self.learning_stats.get_quiz_accuracy(section_title)

            if accuracy < 0.5:
                return "easy"
            elif accuracy < 0.8:
                return "normal"
            else:
                return "hard"

            # --------------------------------------------------
            # Public Review API
            # --------------------------------------------------

    def review_card(self, card: Dict, quality: int) -> Dict:
        """
        Apply SM-2 Lite scheduling to a card.

        quality: int (0–5)
        Returns updated card.
        """
        return self._apply_sm2(card, quality)

    def get_due_cards(self, cards: List[Dict]) -> List[Dict]:
        """
        Returns cards that are due for review.
        """
        now = datetime.utcnow()

        due_cards = []
        for card in cards:
            due = card.get("due")

            if not due:
                # New cards are considered due
                due_cards.append(card)
                continue

            due_dt = datetime.fromisoformat(due)

            if due_dt <= now:
                due_cards.append(card)

        # Sort by due date (oldest first)
        return sorted(
            due_cards,
            key=lambda c: c.get("due") or ""
        )

        # --------------------------------------------------
        # SM-2 Lite Core
        # --------------------------------------------------

    def _apply_sm2(self, card: Dict, quality: int) -> Dict:
        """
        Canonical SM-2 Lite implementation.
        """

        if not 0 <= quality <= 5:
            raise ValueError("Quality must be between 0 and 5")

        ef = card.get("ease_factor", 2.5)
        reps = card.get("repetitions", 0)
        interval = card.get("interval", 1)

        # ---------- Failure ----------
        if quality < 3:
            reps = 0
            interval = 1
        else:
            # ---------- Success ----------
            reps += 1

            if reps == 1:
                interval = 1
            elif reps == 2:
                interval = 6
            else:
                interval = round(interval * ef)

        # ---------- Ease Factor Update ----------
        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ef = max(self.MIN_EASE_FACTOR, round(ef, 2))

        # ---------- Due Date ----------
        due_date = datetime.utcnow() + timedelta(days=interval)

        # ---------- Persist ----------
        card.update({
            "repetitions": reps,
            "interval": interval,
            "ease_factor": ef,
            "due": due_date.isoformat()
        })

        return card

    def run_daily_review(self, max_cards: int = 15):
        """
        Runs a daily spaced repetition review session.
        """

        print("\n=== DAILY REVIEW SESSION ===")

        # 1. Fetch all flashcards
        all_cards = self.flashcard_store.get_all_flashcards()

        if not all_cards:
            print("No flashcards available.")
            return

        # 2. Filter due cards
        due_cards = self.get_due_cards(all_cards)

        if not due_cards:
            print("No cards due for review today.")
            return

        # 3. Limit session size
        session_cards = due_cards[:max_cards]

        print(f"\nReviewing {len(session_cards)} card(s)...")

        reviewed = 0

        for card in session_cards:
            print("\n--------------------------------")
            print(f"Q: {card['front']}")
            input("Press Enter to reveal answer...")

            print(f"A: {card['back']}")

            while True:
                try:
                    quality = int(input(
                        "Rate recall (0–5): "
                        "0=complete blackout, 5=perfect recall → "
                    ))
                    if 0 <= quality <= 5:
                        break
                    else:
                        print("Enter a number between 0 and 5.")
                except ValueError:
                    print("Invalid input. Enter a number between 0 and 5.")

            # 4. Apply SM-2
            updated_card = self.review_card(card, quality)

            # 5. Persist updated card
            self.flashcard_store.update_flashcard(
                card_id=card["id"],
                updated_fields={
                    "repetitions": updated_card["repetitions"],
                    "interval": updated_card["interval"],
                    "ease_factor": updated_card["ease_factor"],
                    "due": updated_card["due"]
                }
            )

            # 6. Update learning stats
            self.learning_stats.record_flashcard_review(
                section=card.get("section"),
                quality=quality
            )

            reviewed += 1

        print("\n=== SESSION COMPLETE ===")
        print(f"Reviewed {reviewed} card(s).")
