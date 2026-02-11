# llm.py
import os
import json
from openai import OpenAI, RateLimitError


class OpenAIClient:
    def __init__(self, model="gpt-4.1-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    # -------------------------
    # Section explanation
    # -------------------------

    def generate_section(self, topic: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": f"Explain {topic} clearly and simply."}
            ],
            temperature=0.4
        )

        return {
            "title": topic,
            "content": response.choices[0].message.content
        }

    def generate(self, prompt: str) -> str:
        try:
            section = self.generate_section(prompt)
            return section["content"]
        except RateLimitError:
            return (
                "LLM unavailable due to quota limits\n"
                "Please review the material manually or try again later."
            )

    # -------------------------
    # Quiz generation (v0.17)
    # -------------------------

    def generate_quiz(
        self,
        section_title: str,
        section_content: str,
        difficulty: str = "normal",
        num_questions: int = 3
    ) -> dict:
        """
        Generate a quiz for a section with optional difficulty.
        Returns a dict:
        {
            "questions": [
                {"question": "...", "correct_answer": "..."}
            ]
        }
        """

        # Difficulty guidelines
        difficulty_guidelines = {
            "easy": (
                "Use simple, direct questions. "
                "Focus on definitions and basic recall. "
                "Avoid tricky wording or close distractors."
            ),
            "normal": (
                "Use standard conceptual questions. "
                "Test understanding, not memorization. "
                "Include reasonable distractors."
            ),
            "hard": (
                "Use challenging questions. "
                "Test edge cases, misconceptions, and deeper reasoning. "
                "Use subtle distractors and application-based questions."
            )
        }

        difficulty_instruction = difficulty_guidelines.get(
            difficulty, difficulty_guidelines["normal"]
        )

        prompt = f"""
You are an AI tutor generating a quiz.

Section Title: {section_title}

Section Content:
{section_content}

Difficulty Level: {difficulty.upper()}
Guidelines: {difficulty_instruction}

Rules:
- Generate {num_questions} clear, independent questions
- Each question must have exactly one correct answer
- Return STRICT JSON in this format only:
{{
  "questions": [
    {{"question": "...", "correct_answer": "..."}}
  ]
}}
Do NOT include explanations, markdown, or extra text.
"""

        try:
            print(f"[LLM] Generating {difficulty} quiz for '{section_title}'")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You generate valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            raw_output = response.choices[0].message.content.strip()

            try:
                quiz = json.loads(raw_output)
            except json.JSONDecodeError:
                raise ValueError(f"LLM returned invalid JSON for quiz:\n{raw_output}")

            if "questions" not in quiz or not isinstance(quiz["questions"], list):
                raise ValueError("Quiz format invalid: missing 'questions' list")

            return quiz

        except RateLimitError:
            # fallback quiz
            return {
                "questions": [
                    {
                        "question": f"What is the main idea of {section_title}?",
                        "correct_answer": "definition"
                    }
                ]
            }

    # -------------------------
    # Mistake explanation
    # -------------------------

    def explain_mistake(self, question: str, correct_answer: str) -> str:
        prompt = f"""
A learner answered a question incorrectly.

QUESTION:
{question}

CORRECT ANSWER:
{correct_answer}

Explain the concept clearly and simply so the learner understands.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a patient AI tutor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        return response.choices[0].message.content
