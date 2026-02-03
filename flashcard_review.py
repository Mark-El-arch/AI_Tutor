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
            interval = card.get("interval_days", 1)
            due_label = " (Due)" if self.is_due(card) else ""

            print(f"\nFlashcard {idx}/{len(flashcards)}{due_label} [Interval: {interval}d]")
            print(f"Q: {card['front']}")
            input("Press Enter to reveal the answer...")
            print(f"A: {card['back']}")


            while True:
                choice = input("Rate your recall — (a)gain / (g)ood: ").strip().lower()
                if choice in ("a", "g"):
                    break
                print("Please enter 'a' for again or 'g' for good.")

            self.record_review(card, success=(choice == "g"))

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

    def is_due(self, card) -> bool:
        last_reviewed = card.get("last_reviewed")
        interval_days = card.get("interval_days", 1)

        if not last_reviewed:
            return True

        last = datetime.datetime.fromisoformat(last_reviewed)
        days_since = (datetime.datetime.utcnow() - last).days
        return days_since >= interval_days

    def record_review(self, card, success: bool):
        """
        Updates review data using a simple spaced repetition rule.
        """
        if success:
            # Increase interval (simple multiplier)
            current_interval = card.get("interval_days", 1)
            card["interval_days"] = min(current_interval * 2, 30)
            card["last_reviewed"] = datetime.datetime.utcnow().isoformat()
        else:
            # Reset interval on failure
            card["interval_days"] = 1
            card["last_reviewed"] = datetime.datetime.utcnow().isoformat()

    def review_section_loop(self, section_title: str, limit: int = None):
        """
        Allows the user to repeatedly review a section until they choose to exit.
        """
        while True:
            self.review_section(section_title, limit=limit)

            print("\nWhat would you like to do next?")
            print("1. Review this section again")
            print("2. Exit review")

            choice = input("Choose an option (1/2): ").strip()

            if choice == "1":
                continue
            elif choice == "2":
                print("Exiting review.\n")
                break
            else:
                print("Invalid choice. Exiting review.\n")
                break
