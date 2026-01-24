# progress_manager.py
import json
import os
from datetime import datetime
from typing import Dict


class ProgressManager:
    """
    Handles loading, updating, and saving learner progress
    to persistent storage (JSON file).
    """

    def __init__(self, file_path: str = "progress.json", user_id: str = "default"):
        self.file_path = file_path
        self.user_id = user_id
        self.progress = self._load_progress()

    # -------------------------
    # Core persistence methods
    # -------------------------

    def _load_progress(self) -> Dict:
        """Load progress from disk or initialize a new structure."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Corrupted file fallback
                return self._empty_progress()
        else:
            return self._empty_progress()

    def _empty_progress(self) -> Dict:
        """Initial empty progress structure."""
        return {
            "user_id": self.user_id,
            "sections": {}
        }

    def save_progress(self) -> None:
        """Persist progress to disk."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.progress, f, indent=2)

    # -------------------------
    # Section-level operations
    # -------------------------

    def is_section_completed(self, section_title: str) -> bool:
        """Check if a section has been completed."""
        section = self.progress["sections"].get(section_title)
        return bool(section and section.get("completed", False))

    def update_section_progress(
        self,
        section_title: str,
        quiz_score: int,
        quiz_total: int
    ) -> None:
        """
        Update progress for a section after quiz completion.
        """
        self.progress["sections"][section_title] = {
            "completed": True,
            "quiz_score": quiz_score,
            "quiz_total": quiz_total,
            "last_attempt": datetime.utcnow().isoformat()
        }
        self.save_progress()

    def get_section_progress(self, section_title: str) -> Dict:
        """Retrieve stored progress for a specific section."""
        return self.progress["sections"].get(section_title, {})

    # -------------------------
    # Reporting / summaries
    # -------------------------

    def get_overall_progress(self) -> Dict:
        """Return a summary of overall learning progress."""
        sections = self.progress["sections"]
        total_sections = len(sections)
        completed_sections = sum(
            1 for s in sections.values() if s.get("completed")
        )

        return {
            "total_sections": total_sections,
            "completed_sections": completed_sections,
            "completion_percentage": (
                round((completed_sections / total_sections) * 100, 2)
                if total_sections > 0 else 0.0
            )
        }
