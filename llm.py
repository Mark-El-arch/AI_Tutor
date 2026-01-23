# llm.py
import os
from openai import OpenAI

class OpenAIClient:
    def __init__(self, model="gpt-4.1-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate_section(self, topic: str) -> dict:
        """
        Generate a structured section explanation.
        Returns a dict with 'title' and 'content'.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": f"Explain {topic} clearly and simply."}
            ],
            temperature=0.4
        )

        return {
            'title': topic,
            'content': response.choices[0].message.content
        }

    def generate(self, prompt: str) -> str:
        """
        Returns a string explanation. Used by Tutor.
        """
        section = self.generate_section(prompt)
        return section['content']
