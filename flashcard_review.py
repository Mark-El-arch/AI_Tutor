# # flashcard_reviewer.py
# from flashcard_store import FlashcardStore
# from flashcard_engine import FlashcardEngine
#
#
# class FlashcardReviewer:
#     """
#     Handles interactive review of flashcards for a user.
#     Works with stored flashcards and can optionally generate new ones.
#     """
#
#     def __init__(self, user_id="default", llm=None):
#         self.store = FlashcardStore(user_id=user_id)
#         self.engine = FlashcardEngine(llm=llm)
#
#     # -------------------------
#     # Generate flashcards from content and store them
#     # -------------------------
#     def generate_and_store_flashcards(self, section_title: str, section_content: str):
#         flashcards = self.engine.generate_flashcards(section_title, section_content)
#
#         for fc in flashcards:
#             self.store.add_flashcard(section_title, fc["front"], fc["back"])
#
#         print(f"Added {len(flashcards)} flashcards for '{section_title}'.")
#
#     # -------------------------
#     # Review flashcards interactively
#     # -------------------------
#     def review_section(self, section_title: str):
#         flashcards = self.store.get_flashcards_for_section(section_title)
#         if not flashcards:
#             print(f"No flashcards found for '{section_title}'.")
#             return
#
#         print(f"\nReviewing {len(flashcards)} flashcards for '{section_title}':\n")
#
#         for i, fc in enumerate(flashcards, 1):
#             print(f"Flashcard {i}: {fc['front']}")
#             input("Press Enter to see the answer...")
#             print(f"Answer: {fc['back']}\n")
#             input("Press Enter to continue...\n")
#
#         print(f"Finished reviewing flashcards for '{section_title}'.")
#
#     # -------------------------
#     # Quick review of all flashcards
#     # -------------------------
#     def review_all_sections(self):
#         all_sections = self.store.get_all_flashcards()
#         if not all_sections:
#             print("No flashcards stored yet.")
#             return
#
#         for section_title in all_sections.keys():
#             self.review_section(section_title)


# flashcard_review.py
from flashcard_store import FlashcardStore
import random


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
