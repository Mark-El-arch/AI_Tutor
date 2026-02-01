# # # test_file.py
# # from llm import OpenAIClient
# # from tutor import Tutor
# # from quiz_engine import run_quiz
# #
# # sections = [
# #     {
# #         "title": "Support Vector Machines (SVM)",
# #         "content": "SVMs are supervised learning models used for classification and regression."
# #     },
# #     {
# #         "title": "SVM Hyperplanes",
# #         "content": "They work by finding the optimal hyperplane that separates data points."
# #     },
# #     {
# #     "title": "Kernel Trick",
# #     "content": "The kernel trick allows SVMs to operate in higher-dimensional spaces."
# #     }
# #
# # ]
# #
# # if __name__ == "__main__":
# #     tutor = Tutor(
# #         llm=OpenAIClient(),
# #         quiz_engine=run_quiz,
# #         user_id="test_user"
# #     )
# #
# #     print("=== RESUMING SESSION ===")
# #     print("Completed sections:", tutor.get_completed_sections())
# #
# #     for section in sections:
# #         print("\n" + "=" * 40)
# #         print(f"SECTION: {section['title']}")
# #         print("=" * 40)
# #         tutor.resume_or_explain_section(
# #             section["title"],
# #             section["content"]
# #         )
# #
# #     print("\n=== FINAL PROGRESS ===")
# #     print(tutor.get_progress_summary())
#
# # test_file.py
# from llm import OpenAIClient
# from tutor import Tutor
# from quiz_engine import run_quiz
# from quiz_store import QuizStore
# from flashcard_store import FlashcardStore
# from flashcard_engine import FlashcardEngine
# from flashcard_review import FlashcardReviewer
#
# # -------------------------
# # Sample Sections
# # -------------------------
# sections = [
#     {
#         "title": "Support Vector Machines (SVM)",
#         "content": "SVMs are supervised learning models used for classification and regression."
#     },
#     {
#         "title": "SVM Hyperplanes",
#         "content": "They work by finding the optimal hyperplane that separates data points."
#     },
#     {
#         "title": "Kernel Trick",
#         "content": "The kernel trick allows SVMs to operate in higher-dimensional spaces."
#     }
# ]
#
# # -------------------------
# # AI Tutor Session
# # -------------------------
# if __name__ == "__main__":
#     tutor = Tutor(
#         llm=OpenAIClient(),
#         quiz_engine=run_quiz,
#         user_id="test_user"
#     )
#
#     print("=== RESUMING SESSION ===")
#     print("Completed sections:", tutor.get_completed_sections())
#
#     for section in sections:
#         print("\n" + "=" * 40)
#         print(f"SECTION: {section['title']}")
#         print("=" * 40)
#         tutor.resume_or_explain_section(
#             section["title"],
#             section["content"]
#         )
#
#     print("\n=== FINAL PROGRESS ===")
#     print(tutor.get_progress_summary())
#
# # -------------------------
# # QUIZ STORAGE TEST
# # -------------------------
# quiz_store = QuizStore(user_id="test_user")
#
# for section in sections:
#     # Retrieve all past quiz attempts for this section
#     attempts = quiz_store.get_quizzes_for_section(section["title"])
#     if attempts:
#         print(f"\nPast quiz attempts for '{section['title']}':")
#         for i, att in enumerate(attempts, start=1):
#             print(f" Attempt {i}: {att['score']} / {att['total']}")
#
# # -------------------------
# # FLASHCARD GENERATION & STORAGE
# # -------------------------
# flash_store = FlashcardStore(user_id="test_user")
# flash_engine = FlashcardEngine()
# reviewer = FlashcardReviewer(flash_store)
#
# # Generate flashcards from each section and store them
# for section in sections:
#     flashcards = flash_engine.generate_flashcards(section["title"], section["content"])
#     for card in flashcards:
#         flash_store.add_flashcard(section["title"], card["front"], card["back"])
#
# # -------------------------
# # FLASHCARD REVIEW (EXTERNAL FEATURE)
# # -------------------------
# print("\n=== FLASHCARD REVIEW ===")
# reviewer.review_all_sections()


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

    print("=== RESUMING SESSION ===")
    print("Completed sections:", tutor.get_completed_sections())

    # Loop through sections
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

    print("\n=== QUIZ REVIEW ===")

    sections = quiz_review.list_sections()
    sections_needing_review = []

    for section in sections:
        if QuizStore.get_incorrect_questions(section):
            sections_needing_review.append(section)

    if not sections_needing_review:
        print("No quiz mistakes to review 🎉")
    else:
        for section in sections_needing_review:
            quiz_review.review_section(section)

    # print("\n=== RANDOM QUIZ RECALL ===")
    #
    # for section in sections_with_quizzes:
    #     quiz_review.random_question_review(section, limit=2)


    # Flashcard review (consistent with current FlashcardReview class)
    print("\n=== FLASHCARD REVIEW ===")
    all_flashcards = flashcard_review.review_all()

