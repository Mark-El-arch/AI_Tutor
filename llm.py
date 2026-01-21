# llm.py
import os
from openai import OpenAI


class OpenAIClient:
    def __init__(self, model="gpt-4.1-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        return response.choices[0].message.content
