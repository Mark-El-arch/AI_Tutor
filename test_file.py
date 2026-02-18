# test_file.py
from llm import OpenAIClient
from tutor import Tutor
from quiz_engine import run_quiz
from quiz_store import QuizStore
from flashcard_review import FlashcardReview
from quiz_review import QuizReview
from learning_stats import LearningStats

sections = [
    {
        "title": "Support Vector Machines (SVM)",
        "content": "SVMs are supervised learning models used for classification and regression."
    },
    {
        "title": "SVM Hyperplanes",
        "content": "They work by finding the optimal hyperplane that separates data points."
    },
    {
        "title": "Kernel Trick",
        "content": "The kernel trick allows SVMs to operate in higher-dimensional spaces."
    }
]

if __name__ == "__main__":
    user_id = "test_user"

    # Initialize components
    tutor = Tutor(
        llm=OpenAIClient(),
        quiz_engine=run_quiz,
        user_id=user_id
    )

    flashcard_review = FlashcardReview(user_id=user_id)
    quiz_review = QuizReview(user_id=user_id)

    print("=== RESUMING SESSION ===")
    print("Completed sections:", tutor.get_completed_sections())

    # Loop through sections
    # for section in sections:
    #     print("\n" + "=" * 40)
    #     print(f"SECTION: {section['title']}")
    #     print("=" * 40)
    #     tutor.resume_or_explain_section(
    #         section["title"],
    #         section["content"]
    #     )

    ordered_titles = tutor.get_next_sections(
        [s["title"] for s in sections]
    )

    for title in ordered_titles:
        section = next(s for s in sections if s["title"] == title)
        tutor.resume_or_explain_section(section["title"], section["content"])

    print("\n=== FINAL PROGRESS ===")
    print(tutor.get_progress_summary())

    # -------------------------
    # Quiz review (Step 7 prep)
    # -------------------------
    print("\n=== QUIZ REVIEW ===")
    sections_with_mistakes = []
    all_sections = quiz_review.list_sections()
    for section in all_sections:
        if quiz_review.store.get_incorrect_questions(section):
            sections_with_mistakes.append(section)

    if not sections_with_mistakes:
        print("No quiz mistakes to review 🎉")
    else:
        for section in sections_with_mistakes:
            print(f"\nReviewing quiz mistakes for section '{section}':")
            quiz_review.review_section(section)

    # -------------------------
    # Flashcard review (Step 5–8)
    # -------------------------
    print("\n=== FLASHCARD REVIEW ===")
    all_flashcards = flashcard_review.review_all()

    # Interactive loop for each section
    for section in all_flashcards.keys():
        flashcard_review.review_section_loop(section)

    stats = LearningStats(user_id=user_id)
    weak = stats.get_weak_sections()
    print("Weak sections:", weak)

    tutor.report_weak_sections()
