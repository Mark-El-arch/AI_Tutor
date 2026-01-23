# test_file.py
from llm import OpenAIClient
from tutor import Tutor

# Example sections
sections = [
    {
        "title": "Support Vector Machines (SVM)",
        "content": "SVMs are supervised learning models used for classification and regression."
    },
    {
        "title": "SVM Hyperplanes",
        "content": "They work by finding the optimal hyperplane that separates data points."
    }
]

def teach_section(title, content):
    tutor = Tutor(OpenAIClient())
    tutor.explain_section(title, content)
    quiz = tutor.generate_quiz(title, content)
    tutor.take_quiz(quiz)

if __name__ == "__main__":
    for section in sections:
        print("="*30)
        print(f"SECTION\n{'='*30}\n{section['title']}")
        teach_section(section["title"], section["content"])
