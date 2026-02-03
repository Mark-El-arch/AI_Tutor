import json
import os
from typing import List


class LearningStats:
    """
    Persistent learning analytics store.
    Tracks quiz and flashcard performance per section, per user.
    """

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.base_dir = "learning_stats"
        os.makedirs(self.base_dir, exist_ok=True)
        self.file_path = os.path.join(self.base_dir, f"{user_id}.json")

        # Load existing stats or initialize empty
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.stats = loaded
                    else:
                        self.stats = {}
            except json.JSONDecodeError:
                print("Warning: stats file corrupted, starting fresh.")
                self.stats = {}
        else:
            self.stats = {}

    # -------------------------
    # Internal helpers
    # -------------------------

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
    # Public API
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

    def get_weak_sections(
        self,
        quiz_threshold: float = 0.6,
        flashcard_threshold: float = 0.7
    ) -> List[str]:
        """
        Returns a list of section names the user is weak in.
        """

        weak_sections = []

        for section, data in self.stats.items():
            # --- Quiz stats ---
            quiz_attempted = data.get("quiz_attempts", 0)
            quiz_correct = data.get("quiz_correct", 0)
            quiz_accuracy = (quiz_correct / quiz_attempted) if quiz_attempted > 0 else 1.0

            # --- Flashcard stats ---
            fc_attempted = data.get("flashcard_reviews", 0)
            fc_success = data.get("flashcard_good", 0)
            flashcard_accuracy = (fc_success / fc_attempted) if fc_attempted > 0 else 1.0

            if quiz_accuracy < quiz_threshold or flashcard_accuracy < flashcard_threshold:
                weak_sections.append(section)

        return weak_sections
