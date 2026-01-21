from typing import List, Dict
import json

class AITutor:
    def __init__(self, llm_client):
        self.llm = llm_client

    def section_text(self, raw_text: str) -> list:
        prompt = f"""
        You're an expect educator.
        Split the following study material into clear learning sections.
        Each section must have:
        - A short title
        - The associated content
         Return the result as valid JSON, like:
    [
        {{"title": "Title 1", "content": "Content 1"}},
        {{"title": "Title 2", "content": "Content 2"}}
    ]

        Text:
        {raw_text}
        
        # Return the result as a structured list.
        """

        response_text = self.llm.generate(prompt)
        # return response

        try:
            sections = json.loads(response_text)
        except json.JSONDecodeError:
            print("Warning: Could not parse JSON. Returning raw text as single section.")
            sections = [{"title": "Section 1", "content": response_text}]
        return sections

    def explain_section(self, section_title: str, section_content: str) -> str:
        prompt = f"""
        You're a patient AI tutor.
        
        Teach the following section clearly:
        - Explain step by step
        - Use simple language
        - Give intuitive examples
        - Assume the student may be confused
        
        Section Title: {section_title}
        Section Content: {section_content}
        """

        explanation = self.llm.generate(prompt)
        return explanation

    def answer_question(self,
                        section_title: str,
                        section_content: str,
                        student_question: str) -> str:

        prompt = f"""
        You're a supportive tutor.
        
        The student asked a question about the following section.
        Explain patiently and clearly.
        If the question shows confusion, re-explain differently.
        
        Section Title: {section_title}
        Section Content: {section_content}
        
        Student Question: {student_question}
        """

        answer = self.llm.generate(prompt)
        return answer

    def generate_quiz(self, title, content):
        """
        Generate a structured quiz for a given section.

        Returns:
            dict: {
                "quiz_title": str,
                "questions": [
                    {
                        "type": "multiple_choice" or "short_answer",
                        "question": str,
                        "options": list[str],        # Only for multiple_choice
                        "correct_answer": str,       # Only for multiple_choice
                        "expected_answer": str       # Only for short_answer
                    },
                    ...
                ]
            }
        """
        # Example static quiz (replace with LLM call for dynamic quiz later)
        quiz = {
            "quiz_title": f"Quiz for {title}",
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "What type of learning model is a Support Vector Machine (SVM)?",
                    "options": ["Unsupervised", "Supervised", "Reinforcement", "Generative"],
                    "correct_answer": "Supervised"
                },
                {
                    "type": "multiple_choice",
                    "question": "Which tasks can SVM be used for?",
                    "options": ["Classification only", "Regression only", "Both classification and regression",
                                "Clustering"],
                    "correct_answer": "Both classification and regression"
                },
                {
                    "type": "short_answer",
                    "question": "In one sentence, explain what SVM does.",
                    "expected_answer": "SVM finds the best boundary to separate data classes."
                }
            ]
        }
        return quiz