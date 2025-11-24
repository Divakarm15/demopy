# src/test.py
import unittest
from unittest.mock import Mock, patch, MagicMock
import random

# Import the REAL game class (not a mock version)
# This is the ONLY change you needed – we now test the actual code!
from xo_game import TicTacToe  # <-- Make sure your main file is named xo_game.py


class TestTicTacToeReal(unittest.TestCase):

    def setUp(self):
        # Patch everything that would open a real Tk window or play sound
        patcher_tk = patch('tkinter.Tk', new=MagicMock())
        patcher_msgbox = patch('tkinter.messagebox.showinfo')
        patcher_sound = patch('winsound.Beep')
        patcher_random = patch('random.choice', return_value="Great!")

        self.mock_tk = patcher_tk.start()
        self.mock_msgbox = patcher_msgbox.start()
        self.mock_sound = patcher_sound.start()
        self.mock_random = patcher_random.start()

        # Create real game instance – it will use all the mocks above
        self.game = TicTacToe()

        # Replace real buttons with MagicMock objects that behave like dicts
        self.game.buttons = [[MagicMock() for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.game.buttons[r][c].cget = lambda key, b=self.game.buttons[r][c]: b._text if key == "text" else b._state
                self.game.buttons[r][c].config = lambda **kwargs, b=self.game.buttons[r][c]: (
                    setattr(b, '_text', kwargs.get('text', b._text)),
                    setattr(b, '_state', kwargs.get('state', b._state))
                )
                self.game.buttons[r][c]._text = ""
                self.game.buttons[r][c]._state = "normal"

        # Reset scores before each test
        self.game.score_x = 0
        self.game.score_o = 0
        self.game.total_games = 0
        self.game.current_player = "X"

        # Capture messagebox calls
        self.shown_messages = []
        def capture_message(title, message):
            self.shown_messages.append(message)
        self.mock_msgbox.side_effect = capture_message

    def tearDown(self):
        patch.stopall()

    def test_initial_state(self):
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]._text, "")

    def test_place_mark(self):
        self.game.on_click(0, 0)
        self.assertEqual(self.game.buttons[0][0]._text, "X")
        self.assertEqual(self.game.current_player, "O")

        self.game.on_click(0, 1)
        self.assertEqual(self.game.buttons[0][1]._text, "O")
        self.assertEqual(self.game.current_player, "X")

    def test_cannot_place_on_occupied(self):
        self.game.on_click(1, 1)
        self.assertEqual(self.game.buttons[1][1]._text, "X")

        old_player = self.game.current_player
        self.game.on_click(1, 1)  # Try again
        self.assertEqual(self.game.buttons[1][1]._text, "X")
        self.assertEqual(self.game.current_player, old_player)

    def test_win_horizontal(self):
        moves = [(0,0), (1,0), (0,1), (1,1), (0,2)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))
        self.assertEqual(self.game.score_x, 1)
        self.assertEqual(self.game.total_games, 1)
        self.assertIn("Congratulations", self.shown_messages[-1])

    def test_win_vertical(self):
        moves = [(0,0), (0,1), (1,0), (1,1), (2,0)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_win_diagonal_main(self):
        moves = [(0,0), (0,1), (1,1), (0,2), (2,2)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_win_diagonal_anti(self):
        moves = [(0,2), (0,0), (1,1), (1,0), (2,0)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_player_o_can_win(self):
        moves = [(1,0), (0,0), (1,1), (0,1), (2,2), (0,2)]
        for i, (r, c) in enumerate(moves):
            self.game.current_player = "X" if i % 2 == 0 else "O"
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("O"))
        self.assertEqual(self.game.score_o, 1)

    def test_is_draw(self):
        draw_sequence = [
            (0,0), (0,1), (0,2), (1,1), (1,0),
            (1,2), (2,1), (2,2), (2,0)
        ]
        expected_players = ["X","O","X","O","X","O","X","O","X"]
        for i, (r, c) in enumerate(draw_sequence):
            self.game.current_player = expected_players[i]
            self.game.on_click(r, c)
        self.assertTrue(self.game.is_draw())
        self.assertEqual(self.game.total_games, 1)

    def test_reset_game(self):
        self.game.on_click(0, 0)
        self.game.score_x = 10
        self.game.reset_game()
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.score_x, 10)  # Score persists
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]._text, "")

    def test_disable_all_after_win(self):
        for r, c in [(0,0), (1,0), (0,1), (1,1), (0,2)]:
            self.game.on_click(r, c)
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]._state, "disabled")

    def test_xss_vulnerability_is_preserved(self):
        self.game.player_name_var = MagicMock()
        self.game.player_name_var.get.return_value = "<script>alert('XSS')</script>"

        # X wins on top row
        for r, c in [(0,0), (1,0), (0,1), (1,1), (0,2)]:
            self.game.on_click(r, c)

        last_message = self.shown_messages[-1]
        self.assertIn("<script>alert('XSS')</script>", last_message)
        self.assertIn("Congratulations", last_message)
        self.assertIn("You win as X", last_message)


if __name__ == '__main__':
    unittest.main(verbosity=2)
