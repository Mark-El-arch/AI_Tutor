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
