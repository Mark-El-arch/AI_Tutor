# llm.py
import os
import json
from openai import OpenAI


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
        section = self.generate_section(prompt)
        return section["content"]

    # -------------------------
    # Quiz generation (v0.5)
    # -------------------------

    def generate_quiz(self, section_title: str, section_content: str) -> dict:
        prompt = f"""
You are an AI tutor generating a quiz.

Create 2–3 clear, beginner-friendly questions
based ONLY on the following content.

Return STRICT JSON in the exact format below.
Do NOT include explanations, markdown, or extra text.

FORMAT:
{{
  "questions": [
    {{
      "question": "...",
      "correct_answer": "..."
    }}
  ]
}}

SECTION TITLE:
{section_title}

SECTION CONTENT:
{section_content}
"""

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
            raise ValueError(
                f"LLM returned invalid JSON for quiz:\n{raw_output}"
            )

        if "questions" not in quiz or not isinstance(quiz["questions"], list):
            raise ValueError("Quiz format invalid: missing 'questions' list")

        return quiz
