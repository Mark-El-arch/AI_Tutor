# flashcard_store.py
import json
from datetime import datetime, timedelta
from pathlib import Path


class FlashcardStore:
    """
    Persistent storage for flashcards.
    Flashcards are grouped by section and stored per user.
    """

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        base_dir = Path("data/flashcards")
        base_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = base_dir / f"{user_id}.json"
        self._load()

    def _load(self):
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"sections": {}, "next_id": 1}

        self.data.setdefault("sections", {})
        self.data.setdefault("next_id", 1)

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def _next_card_id(self) -> int:
        card_id = self.data["next_id"]
        self.data["next_id"] += 1
        return card_id

    def add_flashcard(self, section: str, front: str, back: str):
        if section not in self.data["sections"]:
            self.data["sections"][section] = []

        cards = self.data["sections"][section]

        normalized_front = front.strip().lower()
        for card in cards:
            if card["front"].strip().lower() == normalized_front:
                return

        cards.append({
            "id": self._next_card_id(),
            "section": section,
            "front": front,
            "back": back,
            "created_at": datetime.utcnow().isoformat()
        })

        self._save()

    def get_flashcards_for_section(self, section: str) -> list:
        return self.data["sections"].get(section, [])

    def get_all_flashcards(self) -> dict:
        return self.data["sections"]

    def get_all_flashcards_flat(self) -> list:
        cards = []
        for section, section_cards in self.data["sections"].items():
            for card in section_cards:
                card.setdefault("section", section)
                cards.append(card)
        return cards

    def update_flashcard(self, card_id: int, updated_fields: dict):
        for cards in self.data["sections"].values():
            for card in cards:
                if card.get("id") == card_id:
                    card.update(updated_fields)
                    self._save()
                    return True
        return False

    def list_sections(self) -> list:
        return list(self.data["sections"].keys())

    def list_decks(self) -> list:
        """Decks are section names."""
        return self.list_sections()

    def get_deck(self, deck_name: str) -> list:
        return self.get_flashcards_for_section(deck_name)

    def has_section(self, section: str) -> bool:
        return section in self.data["sections"] and len(self.data["sections"][section]) > 0

    def count_flashcards(self, section: str | None = None) -> int:
        if section:
            return len(self.data["sections"].get(section, []))
        return sum(len(cards) for cards in self.data["sections"].values())

    def clear_section(self, section: str):
        if section in self.data["sections"]:
            del self.data["sections"][section]
            self._save()

    def clear_all(self):
        self.data = {"sections": {}, "next_id": 1}
        self._save()

    def deduplicate(self, dry_run: bool = True) -> dict:
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
        card = self.data["sections"][section][card_index]

        now = datetime.utcnow()
        interval = card.get("interval", 1)
        ease = card.get("ease", 2.5)

        if rating == 1:
            interval = 1
            ease = max(1.3, ease - 0.2)
        elif rating == 2:
            interval = round(interval * ease)
        elif rating == 3:
            interval = round(interval * ease * 1.3)
            ease += 0.1

        card["last_reviewed"] = now.isoformat()
        card["interval"] = interval
        card["ease"] = round(ease, 2)
        card["next_review"] = (now + timedelta(days=interval)).isoformat()

        self._save()
