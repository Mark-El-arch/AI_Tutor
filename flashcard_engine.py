# flashcard_engine.py
import re


class FlashcardEngine:
    """
    Generates flashcards from section content.
    Can be rule-based or LLM-backed later.
    """

    def __init__(self, llm=None):
        self.llm = llm  # optional

    # -------------------------
    # Public API
    # -------------------------

    def generate_flashcards(self, section_title: str, section_content: str) -> list:
        """
        Returns a list of flashcards:
        [{ "front": "...", "back": "..." }]
        """

        if self.llm:
            try:
                return self._generate_with_llm(section_title, section_content)
            except Exception:
                pass  # fallback silently

        return self._generate_rule_based(section_title, section_content)

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

        # Basic patterns
        patterns = [
            (rf"What is {section_title}\??", f"{section_title} is"),
            ("In short", ""),
            ("The main idea", ""),
        ]

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
[
  {{ "front": "...", "back": "..." }}
]

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

    
