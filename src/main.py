# basic_math_program.py
# A fun program to practice Addition, Subtraction, Multiplication & Division

import random
import time

def welcome():
    print("=" * 50)
    print("     WELCOME TO BASIC MATH PRACTICE! ")
    print("=" * 50)
    name = input("Enter your name: ").strip()
    if not name:
        name = "Student"
    print(f"\nHi {name}! Let's practice math! ")
    print("You'll get 10 questions. Try to answer fast! ")
    return name

def choose_operation():
    print("\nChoose your math operation:")
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (×)")
    print("4. Division (÷)")
    print("5. Mixed (All operations)")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice in ["1", "2", "3", "4", "5"]:
            return choice
        print("Please enter a number between 1 and 5!")

def generate_question(operation):
    if operation == "5":  # Mixed
        operation = random.choice(["+", "-", "*", "/"])
    
    if operation == "+":
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        answer = a + b
        question = f"{a} + {b} = ?"
    
    elif operation == "-":
        a = random.randint(10, 100)
        b = random.randint(1, a-1)
        answer = a - b
        question = f"{a} - {b} = ?"
    
    elif operation == "*":
        a = random.randint(2, 12)
        b = random.randint(2, 12)
        answer = a * b
        question = f"{a} × {b} = ?"
    
    elif operation == "/":
        b = random.randint(2, 10)
        answer = random.randint(2, 10)
        a = answer * b
        question = f"{a} ÷ {b} = ?"
    
    return question, answer

def play_game():
    player_name = welcome()
    choice = choose_operation()
    
    operations = {
        "1": "Addition",
        "2": "Subtraction",
        "3": "Multiplication",
        "4": "Division",
        "5": "Mixed"
    }
    
    print(f"\nStarting {operations[choice]} Practice!")
    print("You have 10 questions. Let's begin!\n")
    
    score = 0
    total_questions = 10
    
    time.sleep(1)
    
    for i in range(1, total_questions + 1):
        question, correct_answer = generate_question(choice)
        print(f"Question {i}: {question}")
        
        start_time = time.time()
        try:
            user_answer = int(input("Your answer: "))
            end_time = time.time()
            time_taken = round(end_time - start_time, 1)
        except ValueError:
            print("Please enter a number!")
            user_answer = None
            time_taken = 0
        
        if user_answer == correct_answer:
            print(f"Correct! (in {time_taken}s)")
            score += 1
        else:
            print(f"Wrong! The correct answer is {correct_answer}")
        
        print("-" * 30)
        time.sleep(0.5)
    
    # Final score
    percentage = (score / total_questions) * 100
    
    print("\n" + "=" * 50)
    print(f"      GAME OVER, {player_name.upper()}!")
    print("=" * 50)
    print(f"Score: {score}/{total_questions} ({percentage:.0f}%)")
    
    if percentage == 100:
        print("PERFECT SCORE! You're a math genius! ")
    elif percentage >= 80:
        print("Excellent work! Keep practicing! ")
    elif percentage >= 60:
        print("Good job! You're getting better! ")
    else:
        print("Keep practicing! You'll improve soon! ")
    
    print("\nThanks for playing! Run again to practice more! ")

# Start the game
if __name__ == "__main__":
    while True:
        play_game()
        again = input("\nDo you want to play again? (y/n): ").lower().strip()
        if again != "y" and again != "yes":
            print("Goodbye! Keep practicing math! ")
            break
        print("\n" + "*" * 60 + "\n")
