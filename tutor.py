# tutor.py
from datetime import datetime, timedelta
from typing import Dict, List

from flashcard_engine import FlashcardEngine
from flashcard_review import FlashcardReview
from flashcard_store import FlashcardStore
from learning_stats import LearningStats
from progress_manager import ProgressManager
from quiz_store import QuizStore


class Tutor:
    """Core tutor logic for explain → quiz → persist → review."""

    MIN_PASS_RATIO = 0.7
    MIN_EASE_FACTOR = 1.3

    def __init__(self, llm=None, quiz_engine=None, user_id: str = "default"):
        if llm is None:
            from llm import OpenAIClient
            llm = OpenAIClient()
        if quiz_engine is None:
            from quiz_engine import run_quiz
            quiz_engine = run_quiz

        self.llm = llm
        self.quiz_engine = quiz_engine
        self.user_id = user_id

        self.progress_manager = ProgressManager(user_id=user_id)
        self.quiz_store = QuizStore(user_id=user_id)
        self.flashcard_store = FlashcardStore(user_id=user_id)
        self.flashcard_engine = FlashcardEngine()
        self.flashcard_review = FlashcardReview(user_id=user_id)
        self.learning_stats = LearningStats(user_id=user_id)

    def has_completed_section(self, section_title: str) -> bool:
        return self.progress_manager.is_section_completed(section_title)

    def get_completed_sections(self) -> list[str]:
        return list(self.progress_manager.progress["sections"].keys())

    def explain_section(self, title: str, content: str):
        explanation = self.llm.generate(
            "Explain this study material for a student in very simple terms. "
            "Use at least one relatable analogy, short paragraphs, and practical examples.\n\n"
            f"Title: {title}\n"
            f"Content: {content}"
        )
        print(explanation)
        return explanation

    def teach_material(self, title: str, content: str) -> dict:
        if self.has_completed_section(title):
            return {"status": "skipped", "reason": "already_completed"}

        self.explain_section(title, content)
        result = self.run_quiz_for_section(title, content)

        if result["passed"]:
            self.progress_manager.mark_section_completed(title)
            self.generate_and_store_flashcards(title, content)
            return {"status": "completed", **result}

        return {"status": "needs_retry", **result}

    def resume_or_explain_section(self, title: str, content: str):
        outcome = self.teach_material(title, content)
        if outcome["status"] == "skipped":
            print(f"Skipping '{title}' (already completed).")
        elif outcome["status"] == "needs_retry":
            print("Section not completed. Please try again later.")

    def run_quiz_for_section(self, section_title: str, section_content: str) -> dict:
        config = self.get_quiz_config(section_title)
        difficulty = self._resolve_quiz_difficulty(section_title)

        quiz = self.llm.generate_quiz(
            section_title,
            section_content,
            difficulty=difficulty,
            num_questions=config["num_questions"],
        )
        self.MIN_PASS_RATIO = config["pass_ratio"]

        score, total, user_answers = self.quiz_engine(
            quiz,
            section=section_title,
            user_id=self.user_id,
        )

        passed = total > 0 and (score / total) >= self.MIN_PASS_RATIO

        if not passed:
            print("\n--- Let's review what you missed ---")
            for r in user_answers:
                if not r["is_correct"]:
                    try:
                        explanation = self.llm.explain_mistake(
                            r["question"],
                            r["correct_answer"],
                        )
                        print("\n" + explanation)
                    except Exception:
                        print("Review unavailable (LLM offline). Please revisit the section content.")
            return {"passed": False, "score": score, "total": total}

        self.quiz_store.save_quiz_attempt(
            section_title=section_title,
            quiz=quiz,
            score=score,
            total=total,
            user_answers=user_answers,
        )
        self.progress_manager.update_section_progress(
            section_title=section_title,
            quiz_score=score,
            quiz_total=total,
        )
        print(f"\nProgress saved for '{section_title}'.")
        return {"passed": True, "score": score, "total": total}

    def generate_and_store_flashcards(self, title: str, content: str):
        existing = self.flashcard_store.get_flashcards_for_section(title)
        if existing:
            return

        flashcards = self.flashcard_engine.generate_flashcards(title, content)
        for card in flashcards:
            self.flashcard_store.add_flashcard(section=title, front=card["front"], back=card["back"])

    def get_progress_summary(self):
        return self.progress_manager.get_overall_progress()

    def get_quiz_config(self, section_title: str) -> dict:
        stats = self.learning_stats.get_section_stats(section_title)
        attempts = stats.get("quiz_attempts", 0)
        correct = stats.get("quiz_correct", 0)
        accuracy = (correct / attempts) if attempts > 0 else 1.0

        if accuracy < 0.5:
            return {"num_questions": 5, "pass_ratio": 0.8}
        if accuracy < 0.7:
            return {"num_questions": 4, "pass_ratio": 0.75}
        return {"num_questions": 3, "pass_ratio": 0.7}

    def _resolve_quiz_difficulty(self, section_title: str) -> str:
        accuracy = self.learning_stats.get_quiz_accuracy(section_title)
        if accuracy < 0.5:
            return "easy"
        if accuracy < 0.8:
            return "normal"
        return "hard"

    def review_card(self, card: Dict, quality: int) -> Dict:
        return self._apply_sm2(card, quality)

    def get_due_cards(self, cards: List[Dict]) -> List[Dict]:
        now = datetime.utcnow()
        due_cards = []
        for card in cards:
            due = card.get("due")
            if not due:
                due_cards.append(card)
                continue
            due_dt = datetime.fromisoformat(due)
            if due_dt <= now:
                due_cards.append(card)
        return sorted(due_cards, key=lambda c: c.get("due") or "")

    def _apply_sm2(self, card: Dict, quality: int) -> Dict:
        if not 0 <= quality <= 5:
            raise ValueError("Quality must be between 0 and 5")

        ef = card.get("ease_factor", 2.5)
        reps = card.get("repetitions", 0)
        interval = card.get("interval", 1)

        if quality < 3:
            reps = 0
            interval = 1
        else:
            reps += 1
            if reps == 1:
                interval = 1
            elif reps == 2:
                interval = 6
            else:
                interval = round(interval * ef)

        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ef = max(self.MIN_EASE_FACTOR, round(ef, 2))
        due_date = datetime.utcnow() + timedelta(days=interval)

        card.update({
            "repetitions": reps,
            "interval": interval,
            "ease_factor": ef,
            "due": due_date.isoformat(),
        })
        return card

    def run_daily_review(self, max_cards: int = 15):
        print("\n=== DAILY REVIEW SESSION ===")
        all_cards = self.flashcard_store.get_all_flashcards_flat()
        if not all_cards:
            print("No flashcards available.")
            return

        due_cards = self.get_due_cards(all_cards)
        if not due_cards:
            print("No cards due for review today.")
            return

        session_cards = due_cards[:max_cards]
        print(f"\nReviewing {len(session_cards)} card(s)...")

        for card in session_cards:
            print("\n--------------------------------")
            print(f"Q: {card['front']}")
            input("Press Enter to reveal answer...")
            print(f"A: {card['back']}")

            while True:
                try:
                    quality = int(input("Rate recall (0–5): "))
                    if 0 <= quality <= 5:
                        break
                except ValueError:
                    pass
                print("Enter a number between 0 and 5.")

            updated = self.review_card(card, quality)
            self.flashcard_store.update_flashcard(
                card_id=card["id"],
                updated_fields={
                    "repetitions": updated["repetitions"],
                    "interval": updated["interval"],
                    "ease_factor": updated["ease_factor"],
                    "due": updated["due"],
                },
            )
            self.learning_stats.record_flashcard_result(
                section=card.get("section", "general"),
                success=quality >= 3,
            )
