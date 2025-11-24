# test_math_program.py
import unittest
from unittest.mock import patch, MagicMock
import builtins
import random
import sys
from io import StringIO

# Import your main program functions
# Make sure your main file is named: basic_math_program.py
from basic_math_program import generate_question, welcome, choose_operation


class TestBasicMathProgram(unittest.TestCase):

    def setUp(self):
        # Fix random seed for predictable tests
        random.seed(42)

    # Test 1: Addition questions
    def test_generate_question_addition(self):
        question, answer = generate_question("1")
        self.assertIn(" + ", question)
        a, b = map(int, question.split(" + ")[0]), int(question.split(" + ")[1].split(" =")[0])
        self.assertEqual(answer, a + b)

    # Test 2: Subtraction questions (no negative results)
    def test_generate_question_subtraction(self):
        question, answer = generate_question("2")
        self.assertIn(" - ", question)
        parts = question.split(" - ")
        a = int(parts[0])
        b = int(parts[1].split(" =")[0])
        self.assertGreaterEqual(a, b)  # Ensures no negative answers
        self.assertEqual(answer, a - b)

    # Test 3: Multiplication questions
    def test_generate_question_multiplication(self):
        question, answer = generate_question("3")
        self.assertIn(" × ", question)
        a, b = map(int, question.replace(" × ", " ").replace(" = ?", "").split())
        self.assertEqual(answer, a * b)

    # Test 4: Division questions (always exact)
    def test_generate_question_division(self):
        question, answer = generate_question("4")
        self.assertIn(" ÷ ", question)
        parts = question.split(" ÷ ")
        a = int(parts[0])
        b = int(parts[1].split(" =")[0])
        self.assertEqual(a % b, 0)  # Must be perfectly divisible
        self.assertEqual(answer, a // b)

    # Test 5: Mixed mode uses all operations
    def test_generate_question_mixed(self):
        operations_seen = set()
        for _ in range(20):  # Run 20 times to catch variety
            question, _ = generate_question("5")
            if "+" in question:
                operations_seen.add("+")
            if "-" in question:
                operations_seen.add("-")
            if "×" in question:
                operations_seen.add("×")
            if "÷" in question:
                operations_seen.add("÷")
        self.assertEqual(len(operations_seen), 4)  # Must see all 4

    # Test 6: Welcome function returns name
    @patch('builtins.input', return_value="Alice")
    def test_welcome_returns_name(self, mock_input):
        # Capture print output
        with patch('builtins.print'):
            name = welcome()
        self.assertEqual(name, "Alice")

    @patch('builtins.input', return_value="")
    def test_welcome_default_name(self, mock_input):
        with patch('builtins.print'):
            name = welcome()
        self.assertEqual(name, "Student")

    # Test 7: Choose operation validation
    @patch('builtins.input', side_effect=["99", "abc", "3"])
    def test_choose_operation_invalid_then_valid(self, mock_input):
        with patch('builtins.print'):
            result = choose_operation()
        self.assertEqual(result, "3")

    @patch('builtins.input', return_value="5")
    def test_choose_operation_mixed(self, mock_input):
        with patch('builtins.print'):
            result = choose_operation()
        self.assertEqual(result, "5")

    # Test 8: Full game flow simulation (integration test)
    @patch('builtins.input', side_effect=[
        "Bob",      # name
        "1",        # choose addition
        "5", "10", "15", "20", "25", "30", "35", "40", "45", "50",  # 10 correct answers
        "n"         # play again? no
    ])
    def test_full_game_perfect_score(self, mock_input):
        # Capture all output
        captured_output = StringIO()
        sys.stdout = captured_output

        # Run the full program
        import basic_math_program
        sys.stdout = sys.__stdout__  # restore

        output = captured_output.getvalue()
        self.assertIn("Bob", output)
        self.assertIn("100%", output)
        self.assertIn("PERFECT SCORE", output)

    # Test 9: Wrong answers reduce score
    @patch('builtins.input', side_effect=[
        "TestUser",
        "3",        # multiplication
        "12", "12", "12", "12", "12", "12", "12", "12", "12", "999",  # 9 correct, 1 wrong
        "n"
    ])
    def test_game_with_one_wrong_answer(self, mock_input):
        captured_output = StringIO()
        sys.stdout = captured_output

        import basic_math_program
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("9/10", output)
        self.assertIn("90%", output)
        self.assertIn("Excellent work", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
