# src/test.py
import unittest
from unittest.mock import patch, MagicMock

# Import your actual game class
# Make sure your main game file is named xo_game.py in src/
from xo_game import TicTacToe


class TestTicTacToeGame(unittest.TestCase):

    def setUp(self):
        # Prevent any real window from opening
        self.patcher_tk = patch("tkinter.Tk")
        self.patcher_msg = patch("tkinter.messagebox.showinfo")
        self.patcher_sound = patch("winsound.Beep", return_value=None)

        self.patcher_tk.start()
        self.mock_msgbox = self.patcher_msg.start()
        self.patcher_sound.start()

        # Create real game instance (it will use mocks)
        self.game = TicTacToe()

        # Replace real Tkinter buttons with simple dictionaries
        self.game.buttons = [
            [{"text": "", "state": "normal"} for _ in range(3)]
            for _ in range(3)
        ]

        # Add .config() and .cget() methods to make original code work
        for row in self.game.buttons:
            for btn in row:
                btn["config"] = lambda **kwargs, b=btn: b.update(kwargs)
                btn["cget"] = lambda key, b=btn: b[key]

        # Reset game state
        self.game.current_player = "X"
        self.game.score_x = 0
        self.game.score_o = 0
        self.game.total_games = 0

        # Mock player name (safe by default)
        self.game.player_name_var = MagicMock()
        self.game.player_name_var.get.return_value = "Player"

        # Capture all messagebox calls
        self.shown_messages = []
        self.mock_msgbox.side_effect = lambda title, msg: self.shown_messages.append(msg)

    def tearDown(self):
        patch.stopall()

    def test_initial_board_is_empty(self):
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["text"], "")

    def test_x_places_mark_correctly(self):
        self.game.on_click(0, 0)
        self.assertEqual(self.game.buttons[0][0]["text"], "X")
        self.assertEqual(self.game.current_player, "O")

    def test_o_places_mark_correctly(self):
        self.game.current_player = "O"
        self.game.on_click(1, 1)
        self.assertEqual(self.game.buttons[1][1]["text"], "O")
        self.assertEqual(self.game.current_player, "X")

    def test_cannot_place_on_occupied_cell(self):
        self.game.on_click(0, 0)  # X
        current = self.game.current_player
        self.game.on_click(0, 0)  # Try again
        self.assertEqual(self.game.buttons[0][0]["text"], "X")
        self.assertEqual(self.game.current_player, current)  # Didn't change

    def test_x_wins_horizontal(self):
        moves = [(0,0), (1,0), (0,1), (1,1), (0,2)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))
        self.assertEqual(self.game.score_x, 1)
        self.assertEqual(self.game.total_games, 1)

    def test_x_wins_vertical(self):
        moves = [(0,0), (0,1), (1,0), (1,1), (2,0)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_x_wins_diagonal_main(self):
        moves = [(0,0), (0,1), (1,1), (0,2), (2,2)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_x_wins_diagonal_anti(self):
        moves = [(0,2), (0,0), (1,1), (1,0), (2,0)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_o_can_win(self):
        moves = [(1,0), (0,0), (1,1), (0,1), (1,2)]  # O wins column 1
        for i, (r, c) in enumerate(moves):
            self.game.current_player = "X" if i % 2 == 0 else "O"
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("O"))
        self.assertEqual(self.game.score_o, 1)

    def test_draw_game(self):
        moves = [(0,0),(0,1),(0,2),(1,1),(1,2),(1,0),(2,1),(2,2),(2,0)]
        players = ["X","O","X","O","X","O","X","O","X"]
        for (r,c), p in zip(moves, players):
            self.game.current_player = p
            self.game.on_click(r, c)
        self.assertTrue(self.game.is_draw())
        self.assertEqual(self.game.total_games, 1)

    def test_buttons_disabled_after_win(self):
        for r, c in [(0,0), (1,0), (0,1), (1,1), (0,2)]:
            self.game.on_click(r, c)
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["state"], "disabled")

    def test_reset_clears_board_but_keeps_score(self):
        self.game.on_click(0, 0)
        self.game.score_x = 5
        self.game.reset_game()
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.score_x, 5)
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["text"], "")

    def test_xss_vulnerability_exists_intentionally(self):
        # This test PROVES the XSS bug is present (as requested)
        malicious_name = "<script>alert('XSS')</script>"
        self.game.player_name_var.get.return_value = malicious_name

        # X wins
        for r, c in [(0,0), (1,0), (0,1), (1,1), (0,2)]:
            self.game.on_click(r, c)

        last_message = self.shown_messages[-1]
        self.assertIn(malicious_name, last_message)
        self.assertIn("Congratulations", last_message)
        self.assertIn("You win as X", last_message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
