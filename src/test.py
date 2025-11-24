# src/test.py
import unittest
from unittest.mock import patch
import random

# Now imports work perfectly!
from basic_math_program import generate_question, welcome, choose_operation


class TestBasicMathProgram(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_generate_question_addition(self):
        q, a = generate_question("1")
        self.assertIn(" + ", q)
        x, y = map(int, [part for part in q.split() if part.isdigit()])
        self.assertEqual(a, x + y)

    def test_generate_question_subtraction(self):
        q, a = generate_question("2")
        self.assertIn(" - ", q)
        parts = q.replace(" =", "").split()
        x, y = int(parts[0]), int(parts[2])
        self.assertGreaterEqual(x, y)
        self.assertEqual(a, x - y)

    def test_generate_question_multiplication(self):
        q, a = generate_question("3")
        self.assertIn(" × ", q)
        parts = q.replace(" × ", " ").replace(" = ?", "").split()
        x, y = int(parts[0]), int(parts[1])
        self.assertEqual(a, x * y)

    def test_generate_question_division(self):
        q, a = generate_question("4")
        self.assertIn(" ÷ ", q)
        parts = q.split(" ÷ ")
        x = int(parts[0])
        y = int(parts[1].split()[0])
        self.assertEqual(x % y, 0)
        self.assertEqual(a, x // y)

    def test_mixed_mode(self):
        ops = set()
        for _ in range(30):
            q, _ = generate_question("5")
            for op in ["+", "-", "×", "÷"]:
                if op in q:
                    ops.add(op)
        self.assertEqual(len(ops), 4)

    @patch('builtins.input', side_effect=["Alice", "1", "10", "20", "30", "n"])
    @patch('builtins.print')
    def test_full_game_flow(self, mock_print, mock_input):
        from basic_math_program import play_game
        play_game()  # Should run without errors


if __name__ == "__main__":
    unittest.main(verbosity=2)
