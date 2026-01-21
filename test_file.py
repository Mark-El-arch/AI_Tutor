# test_tutor.py
from tutor import AITutor
from llm import OpenAIClient

# Sample text for testing
raw_text = """
Support Vector Machines (SVM) are supervised learning models used for classification and regression.
They work by finding the optimal hyperplane that separates data points.
"""

# Initialize LLM and Tutor
llm = OpenAIClient()
tutor = AITutor(llm)

# Step 1: Split text into sections
sections = tutor.section_text(raw_text)


# Step 2: Function for interactive quiz
def take_quiz(quiz):
    print(f"\n--- {quiz['quiz_title']} ---")
    score = 0
    total = len(quiz["questions"])

    for i, q in enumerate(quiz["questions"], 1):
        print(f"\nQ{i}: {q['question']}")

        if q["type"] == "multiple_choice":
            for idx, option in enumerate(q["options"], 1):
                print(f"{idx}. {option}")
            while True:
                ans = input("Your answer (type number): ").strip()
                if ans.isdigit() and 1 <= int(ans) <= len(q["options"]):
                    chosen = q["options"][int(ans) - 1]
                    break
                else:
                    print("Please enter a valid number corresponding to the options.")
            if chosen == q["correct_answer"]:
                print("Correct!")
                score += 1
            else:
                print(f"Incorrect. Correct answer: {q['correct_answer']}")

        elif q["type"] == "short_answer":
            ans = input("Your answer: ").strip()
            if ans.lower() == q["expected_answer"].lower():
                print("Correct!")
                score += 1
            else:
                print(f"Expected answer: {q['expected_answer']}")

    print(f"\nQuiz completed! Your score: {score}/{total}")


# Step 3: Teach each section with nested clarity loop
def teach_section_with_full_clarity(section):
    title = section["title"]
    content = section["content"]

    # Explain section
    print("\n--- Section Explanation ---")
    print(tutor.explain_section(title, content))

    # Layer 1: Section questions
    while True:
        has_question = input("\nDo you have any questions about this section? (Y/N): ").strip().lower()
        if has_question == "n":
            break  # No more questions, proceed to quiz
        elif has_question == "y":
            question = input("Ask your question: ")

            # Layer 2: Question clarity loop
            while True:
                answer = tutor.answer_question(title, content, question)
                print("\n--- Answer ---")
                print(answer)

                understood = input("Do you understand this answer? (Y/N): ").strip().lower()
                if understood == "y":
                    break  # Question understood, go back to section questions
                elif understood == "n":
                    question = input("Please specify what you still don't understand: ")
                else:
                    print("Please type Y for yes or N for no.")
        else:
            print("Please type Y for yes or N for no.")

    # Step 3: Generate and take quiz after all questions understood
    print("\n--- Quiz for this section ---")
    quiz = tutor.generate_quiz(title, content)
    take_quiz(quiz)


# Step 4: Loop through all sections
for sec in sections:
    teach_section_with_full_clarity(sec)
