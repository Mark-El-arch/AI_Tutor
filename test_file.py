# test_file.py
from llm import OpenAIClient
from tutor import Tutor
from quiz_engine import run_quiz
from quiz_store import QuizStore
from flashcard_review import FlashcardReview
from quiz_review import QuizReview

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
    quiz_store = QuizStore(user_id=user_id)

    print("=== RESUMING SESSION ===")
    print("Completed sections:", tutor.get_completed_sections())

    # Loop through sections for content
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

    # --- Quiz Review ---
    print("\n=== QUIZ REVIEW ===")
    all_sections = quiz_review.list_sections()
    sections_needing_review = []

    for section in all_sections:
        if quiz_store.get_incorrect_questions(section):
            sections_needing_review.append(section)

    if not sections_needing_review:
        print("No quiz mistakes to review 🎉")
    else:
        for section in sections_needing_review:
            quiz_review.review_section(section)

    # --- Flashcard Review ---
    print("\n=== FLASHCARD REVIEW ===")
    sections_with_flashcards = flashcard_review.store.list_sections()

    for section in sections_with_flashcards:
        print(f"\n--- Section: {section} ---")
        while True:
            print("\nWhat would you like to do with this section?")
            print("1. Review this section interactively (Step 5)")
            print("2. Skip section")

            choice = input("Choose an option (1/2): ").strip()

            if choice == "1":
                flashcard_review.review_section_loop(section)
                break  # exit back to main loop after review
            elif choice == "2":
                print(f"Skipping {section}.")
                break
            else:
                print("Invalid choice. Please select 1 or 2.")
