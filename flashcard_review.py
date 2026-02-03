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

    def review_section(self, section_title: str, limit: int = None, review_mode: str = "all"):
        """
        Returns flashcards for a section, optionally limited.
        review_mode:
            - "all" -> show all cards
            - "due" -> show only due cards
        """
        flashcards = self.store.get_flashcards_for_section(section_title)

        if not flashcards:
            print(f"No flashcards available for section '{section_title}'.")
            return []

        # Filter by due status if needed
        if review_mode == "due":
            flashcards = [card for card in flashcards if self.is_due(card)]
            if not flashcards:
                print(f"No due flashcards in section '{section_title}'.")
                return []

        if limit:
            flashcards = flashcards[:limit]

        for idx, card in enumerate(flashcards, start=1):
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

    def review_all(self, limit_per_section: int = None, review_mode: str = "all"):
        all_flashcards = self.store.get_all_flashcards()

        if not all_flashcards:
            print("No flashcards available yet.")
            return {}

        for section, cards in all_flashcards.items():
            print(f"\n=== Section: {section} ===")
            self.review_section(section, limit=limit_per_section, review_mode=review_mode)

        return all_flashcards

    # -------------------------
    # Review helpers
    # -------------------------

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

    # -------------------------
    # Interactive loop
    # -------------------------

    def review_section_loop(self, section_title: str, limit: int = None):
        """
        Allows the user to repeatedly review a section until they choose to exit.
        Supports choosing review mode.
        """
        while True:
            print("\nChoose review mode:")
            print("1. Review all cards")
            print("2. Review only due cards")
            print("3. Exit review")
            choice = input("Select an option (1/2/3): ").strip()

            if choice == "1":
                self.review_section(section_title, limit=limit, review_mode="all")
            elif choice == "2":
                self.review_section(section_title, limit=limit, review_mode="due")
            elif choice == "3":
                print("Exiting review.\n")
                break
            else:
                print("Invalid choice. Exiting review.\n")
                break
