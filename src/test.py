# src/test.py
import unittest
from unittest.mock import patch, MagicMock
import random

# Import the real game (adjust the filename if yours is different)
from xo_game import TicTacToe   # <-- make sure your game file is named xo_game.py


class TestTicTacToe(unittest.TestCase):

    def setUp(self):
        # -------------------------------
        # Patch everything that opens windows or makes sound
        # -------------------------------
        self.patcher_tk = patch("tkinter.Tk")
        self.patcher_msgbox = patch("tkinter.messagebox.showinfo")
        self.patcher_sound = patch("winsound.Beep")
        self.patcher_random = patch("random.choice", return_value="Great!")

        self.patcher_tk.start()
        self.mock_msgbox = self.patcher_msgbox.start()
        self.patcher_sound.start()
        self.patcher_random.start()

        # Create the real game instance (it will use the mocks above)
        self.game = TicTacToe()

        # Replace the real Tkinter buttons with simple dict-like objects
        self.game.buttons = [[{"text": "", "state": "normal"} for _ in range(3)] for _ in range(3)]

        # Mock the config and cget methods so the original code works unchanged
        for row in self.game.buttons:
            for btn in row:
                btn["config"] = lambda **kw, b=btn: b.update(kw)
                btn["cget"] = lambda key, b=btn: b[key]

        # Reset game state
        self.game.current_player = "X"
        self.game.score_x = self.game.score_o = self.game.total_games = 0
        self.game.player_name_var = MagicMock(get=lambda: "Player")

        # Capture messagebox calls
        self.messages = []
        self.mock_msgbox.side_effect = lambda title, msg: self.messages.append(msg)

    def tearDown(self):
        patch.stopall()

    def test_initial_state(self):
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["text"], "")

    def test_place_mark(self):
        self.game.on_click(0, 0)
        self.assertEqual(self.game.buttons[0][0]["text"], "X")
        self.assertEqual(self.game.current_player, "O")

        self.game.on_click(1, 1)
        self.assertEqual(self.game.buttons[1][1]["text"], "O")
        self.assertEqual(self.game.current_player, "X")

    def test_cannot_place_on_occupied(self):
        self.game.on_click(0, 0)
        old_player = self.game.current_player
        self.game.on_click(0, 0)          # try again
        self.assertEqual(self.game.current_player, old_player)
        self.assertEqual(self.game.buttons[0][0]["text"], "X")

    def test_win_horizontal(self):
        for r, c in [(0,0), (1,0), (0,1), (1,1), (0,2)]:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))
        self.assertEqual(self.game.score_x, 1)
        self.assertEqual(self.game.total_games, 1)
        self.assertIn("Congratulations", self.messages[-1])

    def test_win_vertical(self):
        for r, c in [(0,0), (0,1), (1,0), (1,1), (2,0)]:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_win_diagonal_main(self):
        for r, c in [(0,0), (0,1), (1,1), (1,0), (2,2)]:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_win_diagonal_anti(self):
        for r, c in [(0,2), (0,0), (1,1), (1,0), (2,0)]:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_player_o_can_win(self):
        moves = [(1,0), (0,0), (1,1), (0,1), (1,2)]
        for i, (r, c) in enumerate(moves):
            self.game.current_player = "X" if i % 2 == 0 else "O"
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("O"))
        self.assertEqual(self.game.score_o, 1)

    def test_is_draw(self):
        draw_moves = [(0,0),(0,1),(0,2),(1,1),(1,2),(1,0),(2,1),(2,2),(2,0)]
        players = ["X","O","X","O","X","O","X","O","X"]
        for (r,c), p in zip(draw_moves, players):
            self.game.current_player = p
            self.game.on_click(r, c)
        self.assertTrue(self.game.is_draw())
        self.assertEqual(self.game.total_games, 1)

    def test_reset_game(self):
        self.game.on_click(0, 0)
        self.game.score_x = 99
        self.game.reset_game()
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.score_x, 99)   # score persists
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["text"], "")

    def test_disable_all_after_win(self):
        for r, c in [(0,0), (1,0), (0,1), (1,1), (0,2)]:
            self.game.on_click(r, c)
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["state"], "disabled")

    def test_xss_vulnerability_is_preserved(self):
        self.game.player_name_var.get.return_value = "<script>alert('XSS')</script>"

        # X wins horizontally
        for r, c in [(0,0), (1,0), (0,1), (1,1), (0,2)]:
            self.game.on_click(r, c)

        last_msg = self.messages[-1]
        self.assertIn("<script>alert('XSS')</script>", last_msg)
        self.assertIn("Congratulations", last_msg)
        self.assertIn("You win as X", last_msg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
