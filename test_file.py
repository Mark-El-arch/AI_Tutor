# test_file.py

from llm import OpenAIClient
from tutor import Tutor
from quiz_engine import run_quiz

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


def teach_section(tutor, title, content):
    print("\n--- Explanation ---")
    tutor.explain_section(title, content)

    print("\n--- Quiz ---")
    quiz = tutor.generate_quiz(title, content)
    tutor.take_quiz(quiz)

    print("\n--- Progress Snapshot ---")
    print(tutor.get_progress_summary())


if __name__ == "__main__":
    tutor = Tutor(
        llm=OpenAIClient(),
        quiz_engine=run_quiz,
        user_id="test_user"
    )

    for section in sections:
        print("\n" + "=" * 40)
        print(f"SECTION: {section['title']}")
        print("=" * 40)
        teach_section(tutor, section["title"], section["content"])
