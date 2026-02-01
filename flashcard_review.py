from flashcard_store import FlashcardStore
import datetime


class FlashcardReview:
    """
    Handles reviewing flashcards outside the AI conversation.
    Adds due-card status for revision.
    """

    def __init__(self, user_id="default"):
        self.store = FlashcardStore(user_id=user_id)

    # -------------------------
    # Single section review
    # -------------------------

    def review_section(self, section_title: str, limit: int = None):
        """
        Returns flashcards for a section, optionally limited.
        Marks due status but still shows all cards.
        """
        flashcards = self.store.get_flashcards_for_section(section_title)

        if not flashcards:
            print(f"No flashcards available for section '{section_title}'.")
            return []

        if limit:
            flashcards = flashcards[:limit]

        for idx, card in enumerate(flashcards, start=1):
            # Determine due status
            last_reviewed = card.get("last_reviewed")
            if last_reviewed:
                last = datetime.datetime.fromisoformat(last_reviewed)
                days_since = (datetime.datetime.utcnow() - last).days
                due_label = " (Due)" if days_since >= 1 else ""
            else:
                due_label = " (Due)"

            print(f"\nFlashcard {idx}/{len(flashcards)}{due_label}")
            print(f"Q: {card['front']}")
            input("Press Enter to reveal the answer...")
            print(f"A: {card['back']}")

            # Update last reviewed timestamp
            card["last_reviewed"] = datetime.datetime.utcnow().isoformat()

        # Save updated timestamps
        self.store._save()

        return flashcards

    # -------------------------
    # Review across all sections
    # -------------------------

    def review_all(self, limit_per_section: int = None):
        """
        Review flashcards across all sections.
        Shows due status for each card.
        """
        all_flashcards = self.store.get_all_flashcards()

        if not all_flashcards:
            print("No flashcards available yet.")
            return {}

        for section, cards in all_flashcards.items():
            print(f"\n=== Section: {section} ===")
            self.review_section(section, limit=limit_per_section)

        return all_flashcards
