# flashcard_store.py
import json
import os
from datetime import datetime, timedelta


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
        Prevent duplicate questions within the same section.
        """
        if section not in self.data["sections"]:
            self.data["sections"][section] = []

        cards = self.data["sections"][section]

        # Deduplicate by question text
        normalized_front = front.strip().lower()
        for card in cards:
            if card["front"].strip().lower() == normalized_front:
                return  # duplicate → do nothing

        cards.append({
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

    # -------------------------
    # v0.13 Maintenance Utility
    # -------------------------

    def deduplicate(self, dry_run: bool = True) -> dict:
        """
        Remove duplicate flashcards per section (by front text).

        - Keeps the earliest card (by created_at)
        - dry_run=True shows what would change without saving
        """

        report = {}
        changed = False

        for section, cards in self.data["sections"].items():
            seen = {}
            unique_cards = []

            for card in cards:
                key = card["front"].strip().lower()

                if key not in seen:
                    seen[key] = card
                    unique_cards.append(card)
                else:
                    changed = True

            if len(unique_cards) != len(cards):
                report[section] = {
                    "before": len(cards),
                    "after": len(unique_cards)
                }

                if not dry_run:
                    self.data["sections"][section] = unique_cards

        if changed and not dry_run:
            self._save()

        return report

    def update_review(self, section: str, card_index: int, rating: int):
        """
        Update spaced repetition metadata for a flashcard.
        rating: 1 = again, 2 = good, 3 = easy
        """
        card = self.data["sections"][section][card_index]

        now = datetime.utcnow()
        interval = card.get("interval", 1)
        ease = card.get("ease", 2.5)

        if rating == 1:  # Again
            interval = 1
            ease = max(1.3, ease - 0.2)
        elif rating == 2:  # Good
            interval = round(interval * ease)
        elif rating == 3:  # Easy
            interval = round(interval * ease * 1.3)
            ease += 0.1

        card["last_reviewed"] = now.isoformat()
        card["interval"] = interval
        card["ease"] = round(ease, 2)
        card["next_review"] = (now + timedelta(days=interval)).isoformat()

        self._save()
