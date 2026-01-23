# tutor.py
import ast

class Tutor:
    def __init__(self, llm):
        self.llm = llm

    def _generate(self, prompt: str) -> str:
        if hasattr(self.llm, "generate"):
            return self.llm.generate(prompt)
        raise RuntimeError("LLM does not have a generate() method")

    def explain_section(self, title: str, content: str):
        prompt = f"Explain this section clearly and simply:\nTitle: {title}\nContent: {content}"
        explanation = self._generate(prompt).strip()
        print(f"--- Section Explanation ---\n{explanation}")

        # Ask user if they have questions
        user_input = input("Do you have any questions about this section? (Y/N): >? ").strip().lower()
        if user_input == "y":
            question = input("Ask your question: >? ").strip()
            answer = self._generate(question)
            print(f"--- Answer ---\n{answer}")
            understood = input("Do you understand this answer? (Y/N): >? ").strip().lower()
            if understood != "y":
                print("You can ask again or move to the quiz.")

    def generate_quiz(self, title: str, content: str) -> dict:
        """
        Generate a short quiz with 2-3 questions.
        Returns a dictionary structured for interactive quizzes.
        """
        prompt = f"""
        Generate a short quiz for this section:
        Title: {title}
        Content: {content}
        Include 2-3 questions. Each question should be multiple choice or short answer.
        Return a Python dict like this:
        {{
            'title': str,
            'questions': [
                {{
                    'type': 'multiple_choice'|'short_answer',
                    'question': str,
                    'options': [str],
                    'correct_answer': str,
                    'expected_answer': str
                }}
            ]
        }}
        """

        response = self._generate(prompt)

        try:
            # Remove any markdown/code block formatting
            response_clean = response.strip("```").strip()
            quiz_dict = ast.literal_eval(response_clean)
            return quiz_dict
        except Exception as e:
            print("Error parsing quiz from LLM:", e)
            return {"title": title, "questions": []}

    def take_quiz(self, quiz: dict):
        if not quiz or not quiz.get("questions"):
            print("No quiz questions available for this section.")
            return

        print("--- Section Quiz ---")
        score = 0
        total = len(quiz["questions"])

        for idx, q in enumerate(quiz["questions"], 1):
            print(f"Question {idx}: {q['question']}")
            if q['type'] == "multiple_choice" and q.get('options'):
                for i, option in enumerate(q['options'], 1):
                    print(f"{i}. {option}")
                ans = input("Your answer (number): >? ").strip()
                try:
                    if q['options'][int(ans)-1].lower() == q['correct_answer'].lower():
                        score += 1
                except:
                    pass
            elif q['type'] == "short_answer":
                ans = input("Your answer: >? ").strip()
                if ans.lower() == q['correct_answer'].lower():
                    score += 1

        print(f"Quiz completed! Your score: {score}/{total}")
