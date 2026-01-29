# flashcard_store.py
import json
import os
from datetime import datetime


class FlashcardStore:
    """
    Persistent storage for flashcards.
    Flashcards are grouped by section and stored per user.
    """

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.file_path = f"flashcards_{user_id}.json"
        self._load()

    # -------------------------
    # Internal helpers
    # -------------------------

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"sections": {}}

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # -------------------------
    # Public API
    # -------------------------

    def add_flashcard(self, section: str, front: str, back: str):
        """
        Add a flashcard to a section.
        """
        if section not in self.data["sections"]:
            self.data["sections"][section] = []

        self.data["sections"][section].append({
            "front": front,
            "back": back,
            "created_at": datetime.utcnow().isoformat()
        })

        self._save()

    def get_flashcards_for_section(self, section: str) -> list:
        """
        Retrieve all flashcards for a section.
        """
        return self.data["sections"].get(section, [])

    def get_all_flashcards(self) -> dict:
        """
        Retrieve all flashcards grouped by section.
        """
        return self.data["sections"]

    # -------------------------
    # Step 3: Access & Management Helpers
    # -------------------------

    def list_sections(self) -> list:
        """
        Return a list of section names that have flashcards.
        """
        return list(self.data["sections"].keys())

    def has_section(self, section: str) -> bool:
        """
        Check if a section has any flashcards.
        """
        return section in self.data["sections"] and len(self.data["sections"][section]) > 0

    def count_flashcards(self, section: str | None = None) -> int:
        """
        Count flashcards.
        - If section is provided, count only that section
        - Otherwise, count all flashcards
        """
        if section:
            return len(self.data["sections"].get(section, []))

        return sum(len(cards) for cards in self.data["sections"].values())

    def clear_section(self, section: str):
        """
        Delete all flashcards for a specific section.
        """
        if section in self.data["sections"]:
            del self.data["sections"][section]
            self._save()

    def clear_all(self):
        """
        Delete all flashcards for all sections.
        """
        self.data = {"sections": {}}
        self._save()

