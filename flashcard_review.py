# flashcard_review.py
from flashcard_store import FlashcardStore
from datetime import datetime


class FlashcardReview:
    """
    Handles reviewing flashcards outside the AI conversation.
    """

    def __init__(self, user_id="default"):
        self.store = FlashcardStore(user_id=user_id)

    def review_section(self, section_title: str, limit: int = None):
        """
        Returns flashcards for a section, optionally limited.
        """
        raw_flashcards = self.store.get_flashcards_for_section(section_title)

        # Deduplicate by question text (non-destructive)
        seen = set()
        flashcards = []
        for card in raw_flashcards:
            key = card["front"].strip().lower()
            if key not in seen:
                seen.add(key)
                flashcards.append(card)

        if not flashcards:
            print(f"No flashcards available for section '{section_title}'.")
            return []

        if limit:
            flashcards = flashcards[:limit]

        for idx, card in enumerate(flashcards, start=1):
            print(f"\nFlashcard {idx}/{len(flashcards)}")
            print(f"Q: {card['front']}")
            input("Press Enter to reveal the answer...")
            print(f"A: {card['back']}")

            print("\nHow well did you recall this?")
            print("1 = Again | 2 = Good | 3 = Easy")
            choice = input("Your choice: ").strip()

            if choice in {"1", "2", "3"}:
                self.store.update_review(
                    section_title,
                    idx - 1,
                    int(choice)
                )

        return flashcards

    def review_all(self, limit_per_section: int = None):
        """
        Review flashcards across all sections.
        """
        all_flashcards = self.store.get_all_flashcards()

        if not all_flashcards:
            print("No flashcards available yet.")
            return {}

        for section, cards in all_flashcards.items():
            print(f"\n=== Section: {section} ===")
            self.review_section(section, limit=limit_per_section)

        return all_flashcards

    def is_due(card: dict) -> bool:
        if "next_review" not in card:
            return True
        return datetime.utcnow() >= datetime.fromisoformat(card["next_review"])

