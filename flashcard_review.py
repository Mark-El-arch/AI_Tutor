from flashcard_store import FlashcardStore
from learning_stats import LearningStats
import datetime


class FlashcardReview:
    """
    Handles reviewing flashcards outside the AI conversation.
    Adds due-card status, quiz mistakes integration, and spaced repetition.
    """

    def __init__(self, user_id="default"):
        self.store = FlashcardStore(user_id=user_id)
        self.stats = LearningStats(user_id=user_id)

    # -------------------------
    # Single section review
    # -------------------------
    def review_section(self, section_title: str, limit: int = None, review_mode: str = "all"):
        """
        Review flashcards for a section.
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

        # Count due cards upfront
        due_count = sum(1 for c in flashcards if self.is_due(c))
        total_due = due_count
        print(f"\n--- Section: {section_title} ---")
        print(f"Total flashcards: {len(flashcards)} | Due: {total_due}")

        for idx, card in enumerate(flashcards, start=1):
            interval = card.get("interval_days", 1)
            due_label = " (Due)" if self.is_due(card) else ""
            print(f"\nFlashcard {idx}/{len(flashcards)}{due_label} [Interval: {interval}d]")
            print(f"Q: {card['front']}")
            input("Press Enter to reveal the answer...")
            print(f"A: {card['back']}")

            # Rate recall
            while True:
                choice = input("Rate your recall — (a)gain / (g)ood: ").strip().lower()
                if choice in ("a", "g"):
                    break
                print("Please enter 'a' for again or 'g' for good.")

            self.record_review(card, success=(choice == "g"))
            self.stats.record_flashcard_result(
                section=section_title,
                success=(choice == "g")
            )

        # Save updated timestamps
        self.store._save()

        # Section summary
        again_count = sum(1 for c in flashcards if c.get("interval_days", 1) == 1)
        good_count = len(flashcards) - again_count
        print(f"\nReview summary for '{section_title}': {good_count} good, {again_count} again.")

        return flashcards

    # -------------------------
    # Review all sections
    # -------------------------
    def review_all(self, limit_per_section: int = None, review_mode: str = "all"):
        all_flashcards = self.store.get_all_flashcards()
        if not all_flashcards:
            print("No flashcards available yet.")
            return {}

        for section, cards in all_flashcards.items():
            self.review_section(section, limit=limit_per_section, review_mode=review_mode)

        return all_flashcards

    # -------------------------
    # Helpers
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
            # Double interval, max 30 days
            current_interval = card.get("interval_days", 1)
            card["interval_days"] = min(current_interval * 2, 30)
            card["last_reviewed"] = datetime.datetime.utcnow().isoformat()
        else:
            # Reset interval
            card["interval_days"] = 1
            card["last_reviewed"] = datetime.datetime.utcnow().isoformat()

    # -------------------------
    # Interactive loop
    # -------------------------
    def review_section_loop(self, section_title: str, limit: int = None):
        """
        Repeatedly review a section until the user exits.
        Supports switching review modes.
        """
        while True:
            print("\nWhat would you like to do with this section?")
            print("1. Review this section interactively")
            print("2. Skip section")
            choice = input("Choose an option (1/2): ").strip()

            if choice == "1":
                while True:
                    print("\nChoose review mode:")
                    print("1. Review all cards")
                    print("2. Review only due cards")
                    print("3. Exit review")
                    mode_choice = input("Select an option (1/2/3): ").strip()
                    if mode_choice == "1":
                        self.review_section(section_title, limit=limit, review_mode="all")
                    elif mode_choice == "2":
                        self.review_section(section_title, limit=limit, review_mode="due")
                    elif mode_choice == "3":
                        print("Exiting review.\n")
                        break
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3.")
                break
            elif choice == "2":
                print(f"Skipping {section_title}.")
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
