import time

questions = [
    {
        "question": "Which number completes the pattern?\n2, 4, 8, 16, ?",
        "options": ["20", "24", "32", "34"],
        "answer": "32"
    },
    {
        "question": "Which shape has the fewest sides?\n",
        "options": ["Pentagon", "Triangle", "Hexagon", "Square"],
        "answer": "Triangle"
    },
    {
        "question": "Find the odd one out:\nDog, Cat, Snake, Horse",
        "options": ["Dog", "Cat", "Snake", "Horse"],
        "answer": "Snake"
    },
    {
        "question": "What comes next?\nA, C, E, G, ?",
        "options": ["H", "I", "J", "K"],
        "answer": "I"
    },
    {
        "question": "If ALL Bloops are Razzies, and ALL Razzies are Lazzies,\nare ALL Bloops definitely Lazzies?",
        "options": ["Yes", "No"],
        "answer": "Yes"
    }
]

def run_iq_test():
    print("==== SIMPLE IQ-STYLE QUIZ ====")
    print("Answer the following reasoning questions.\n")
    time.sleep(1)

    score = 0

    for i, q in enumerate(questions):
        print(f"Question {i+1}:")
        print(q["question"])
        for idx, opt in enumerate(q["options"], start=1):
            print(f"{idx}. {opt}")

        user_answer = input("Your answer: ").strip()

        # Convert index to option text if numeric
        if user_answer.isdigit():
            index = int(user_answer) - 1
            if 0 <= index < len(q["options"]):
                user_answer = q["options"][index]

        if user_answer.lower() == q["answer"].lower():
            score += 1
            print("Correct!\n")
        else:
            print(f"Wrong. Correct answer is: {q['answer']}\n")

        time.sleep(0.5)

    print("==== RESULTS ====")
    print(f"Your Score: {score} / {len(questions)}")

    # Provide a playful summary (not real IQ)
    if score == 5:
        print("Excellent reasoning ability!")
    elif score >= 3:
        print("Good reasoning skills.")
    else:
        print("Keep practicing your logic and pattern skills!")

if __name__ == "__main__":
    run_iq_test()
