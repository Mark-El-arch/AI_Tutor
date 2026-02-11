# flashcard_engine.py
import re
from datetime import datetime, timedelta


class FlashcardEngine:
    """
    Generates flashcards from section content.
    Supports SM-2 Lite adaptive scheduling for review.
    """

    def __init__(self, llm=None):
        self.llm = llm  # optional

    # -------------------------
    # Public API
    # -------------------------

    def generate_flashcards(self, section_title: str, section_content: str) -> list:
        """
        Returns a list of flashcards:
        [{ "front": "...", "back": "...", "repetition": 0, "interval": 1, "next_review": date }]
        """
        if self.llm:
            try:
                flashcards = self._generate_with_llm(section_title, section_content)
            except Exception:
                flashcards = self._generate_rule_based(section_title, section_content)
        else:
            flashcards = self._generate_rule_based(section_title, section_content)

        # Initialize SM-2 Lite fields
        today = datetime.today().date()
        for card in flashcards:
            card.setdefault("repetition", 0)
            card.setdefault("interval", 1)  # in days
            card.setdefault("next_review", str(today))

        return flashcards

    # -------------------------
    # Rule-based fallback
    # -------------------------

    def _generate_rule_based(self, section_title: str, content: str) -> list:
        """
        Simple extraction-based flashcards.
        """
        flashcards = []

        # Clean content
        text = re.sub(r"\n+", " ", content)
        sentences = [s.strip() for s in re.split(r"\. ", text) if len(s) > 40]

        if sentences:
            flashcards.append({
                "front": f"What is {section_title}?",
                "back": sentences[0]
            })

        if len(sentences) > 1:
            flashcards.append({
                "front": f"Why is {section_title} important?",
                "back": sentences[1]
            })

        return flashcards

    # -------------------------
    # LLM-powered generation
    # -------------------------

    def _generate_with_llm(self, section_title: str, section_content: str) -> list:
        """
        Uses LLM to generate flashcards (JSON-only).
        """
        prompt = f"""
Generate 3 concise flashcards for revision.

Rules:
- Beginner-friendly
- Question-answer format
- No markdown
- No explanations
- STRICT JSON only

FORMAT:
[{{ "front": "...", "back": "..." }}]

SECTION TITLE:
{section_title}

SECTION CONTENT:
{section_content}
"""
        response = self.llm.client.chat.completions.create(
            model=self.llm.model,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        import json
        output = response.choices[0].message.content.strip()
        flashcards = json.loads(output)

        if not isinstance(flashcards, list):
            raise ValueError("Invalid flashcard format")

        return flashcards

    # -------------------------
    # SM-2 Lite adaptive review
    # -------------------------

    @staticmethod
    def review_card(card: dict, response: str):
        """
        Update flashcard scheduling using SM-2 Lite.

        response: 'g' (good) or 'a' (again)
        """
        today = datetime.today().date()

        if response == "a":  # Again
            card["repetition"] = 0
            card["interval"] = 1
        elif response == "g":  # Good
            card["repetition"] += 1
            if card["repetition"] == 1:
                card["interval"] = 1
            elif card["repetition"] == 2:
                card["interval"] = 6
            else:
                card["interval"] *= 2

        # Update next review date
        card["next_review"] = str(today + timedelta(days=card["interval"]))

