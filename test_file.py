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

if __name__ == "__main__":
    tutor = Tutor(
        llm=OpenAIClient(),
        quiz_engine=run_quiz,
        user_id="test_user"
    )

    print("=== RESUMING SESSION ===")
    print("Completed sections:", tutor.get_completed_sections())

    for section in sections:
        print("\n" + "=" * 40)
        print(f"SECTION: {section['title']}")
        print("=" * 40)
        tutor.resume_or_explain_section(
            section["title"],
            section["content"]
        )

    print("\n=== FINAL PROGRESS ===")
    print(tutor.get_progress_summary())
