# quiz_store.py
import json
from pathlib import Path
from datetime import datetime


class QuizStore:
    def __init__(self, user_id="default"):
        self.base_path = Path("data/quizzes")
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.file_path = self.base_path / f"{user_id}_quizzes.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def save_quiz_attempt(
        self,
        section_title: str,
        quiz: dict,
        score: int,
        total: int,
        user_answers: list
    ):
        attempt = {
            "timestamp": datetime.utcnow().isoformat(),
            "score": score,
            "total": total,
            "questions": quiz["questions"],
            "user_answers": user_answers
        }

        self.data.setdefault(section_title, []).append(attempt)
        self._save()

    def get_quizzes_for_section(self, section_title: str):
        return self.data.get(section_title, [])

    # -------------------------
    # Step 4: Review & Access Helpers
    # -------------------------

    def list_sections(self) -> list:
        """
        Return all sections that have quiz attempts.
        """
        return list(self.data.keys())

    def has_section(self, section_title: str) -> bool:
        """
        Check if a section has any quiz attempts.
        """
        return section_title in self.data and len(self.data[section_title]) > 0

    def get_latest_attempt(self, section_title: str):
        """
        Return the most recent quiz attempt for a section.
        """
        attempts = self.data.get(section_title, [])
        return attempts[-1] if attempts else None

    def get_attempt_count(self, section_title: str | None = None) -> int:
        """
        Count quiz attempts.
        - Per section if provided
        - Total otherwise
        """
        if section_title:
            return len(self.data.get(section_title, []))

        return sum(len(attempts) for attempts in self.data.values())

    def get_incorrect_questions(self, section_title: str) -> list:
        """
        Return incorrectly answered questions from the latest attempt.
        """
        latest = self.get_latest_attempt(section_title)
        if not latest:
            return []

        incorrect = []
        for q, ua in zip(latest["questions"], latest["user_answers"]):
            if ua.lower() != q["correct_answer"].lower():
                incorrect.append({
                    "question": q["question"],
                    "your_answer": ua,
                    "correct_answer": q["correct_answer"]
                })

        return incorrect

    def clear_section(self, section_title: str):
        """
        Delete all quiz attempts for a section.
        """
        if section_title in self.data:
            del self.data[section_title]
            self._save()

    def clear_all(self):
        """
        Delete all quiz history.
        """
        self.data = {}
        self._save()

