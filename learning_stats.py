import json
import os
from collections import defaultdict


class LearningStats:
    """
    Persistent learning analytics store.
    Tracks quiz and flashcard performance per section, per user.
    This module records facts only — no adaptivity or logic.
    """

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.base_dir = "learning_stats"
        os.makedirs(self.base_dir, exist_ok=True)
        self.file_path = os.path.join(self.base_dir, f"{user_id}.json")
        self.stats = self._load()

    # -------------------------
    # Internal helpers
    # -------------------------

    def _load(self):
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

    def _ensure_section(self, section: str):
        if section not in self.stats:
            self.stats[section] = {
                "quiz_attempts": 0,
                "quiz_correct": 0,
                "quiz_incorrect": 0,
                "flashcard_reviews": 0,
                "flashcard_good": 0,
                "flashcard_again": 0,
            }

    # -------------------------
    # Public API (contract)
    # -------------------------

    def record_quiz_result(self, section: str, correct: bool):
        self._ensure_section(section)
        self.stats[section]["quiz_attempts"] += 1
        if correct:
            self.stats[section]["quiz_correct"] += 1
        else:
            self.stats[section]["quiz_incorrect"] += 1
        self._save()

    def record_flashcard_result(self, section: str, success: bool):
        self._ensure_section(section)
        self.stats[section]["flashcard_reviews"] += 1
        if success:
            self.stats[section]["flashcard_good"] += 1
        else:
            self.stats[section]["flashcard_again"] += 1
        self._save()

    def get_section_stats(self, section: str):
        self._ensure_section(section)
        return self.stats.get(section, {})

    def get_all_stats(self):
        return self.stats
