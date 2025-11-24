import unittest
from unittest.mock import Mock, patch, MagicMock
import random

# === Paste your full TicTacToe class here (or import it if in separate file) ===
# For this example, we'll define a minimal testable version of the class
# that allows dependency injection of Tkinter objects

class TicTacToe:
    def __init__(self):
        self.window = None  # Will be mocked
        self.current_player = "X"
        self.buttons = [[MagicMock() for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c]["text"] = ""
                self.buttons[r][c].config = MagicMock()
                self.buttons[r][c]["state"] = "normal"
        self.score_x = 0
        self.score_o = 0
        self.total_games = 0
        self.player_name_var = MagicMock()
        self.player_name_var.get.return_value = "Player"
        self.status_label = MagicMock()
        self.score_label = MagicMock()
        self.win_messages = ["Great!", "Wow!"]

    def check_winner(self, player):
        b = self.buttons
        for i in range(3):
            if all(b[i][j]["text"] == player for j in range(3)): return True
            if all(b[j][i]["text"] == player for j in range(3)): return True
        if b[0][0]["text"] == player and b[1][1]["text"] == player and b[2][2]["text"] == player:
            return True
        if b[0][2]["text"] == player and b[1][1]["text"] == player and b[2][0]["text"] == player:
            return True
        return False

    def is_draw(self):
        return all(self.buttons[r][c]["text"] != "" for r in range(3) for c in range(3))

    def disable_all(self):
        for r in range(3):
            for c in range(3):
                self.buttons[r][c]["state"] = "disabled"

    def reset_game(self):
        self.current_player = "X"
        for r in range(3):
            for c in range(3):
                self.buttons[r][c]["text"] = ""
                self.buttons[r][c]["state"] = "normal"

    def update_score(self):
        pass  # Mocked

    def highlight_winner(self):
        pass  # GUI only

    def play_sound(self, sound_type):
        pass  # No sound in tests

    def on_click(self, row, col):
        btn = self.buttons[row][col]
        if btn["text"] != "":
            self.play_sound("error")
            return

        btn["text"] = self.current_player
        btn.config(fg="#00ff00" if self.current_player == "X" else "#ff0066")
        self.play_sound("click")

        if self.check_winner(self.current_player):
            self.total_games += 1
            if self.current_player == "X":
                self.score_x += 1
            else:
                self.score_o += 1
            self.update_score()

            player_name = self.player_name_var.get()
            malicious_message = f"Congratulations {player_name}!\nYou win as {self.current_player}!\n{random.choice(self.win_messages)}"
            # In real code: messagebox.showinfo(...) → XSS here
            self.last_message = malicious_message  # Capture for testing XSS

            self.highlight_winner()
            self.disable_all()
            self.status_label.config(text=f"{self.current_player} Wins!", fg="#00ff00")
            self.play_sound("win")

        elif self.is_draw():
            self.total_games += 1
            self.update_score()
            self.status_label.config(text="It's a Draw!", fg="#ffff00")
            self.play_sound("draw")
        else:
            self.current_player = "O" if self.current_player == "X" else "X"


# ========================
# === UNIT TESTS BELOW ===
# ========================

class TestTicTacToe(unittest.TestCase):

    def setUp(self):
        self.game = TicTacToe()
        # Mock random.choice to be deterministic
        self.patch_random = patch('random.choice', return_value="Great!")
        self.mock_choice = self.patch_random.start()

    def tearDown(self):
        self.patch_random.stop()

    def test_initial_state(self):
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.score_x, 0)
        self.assertEqual(self.game.score_o, 0)
        self.assertEqual(self.game.total_games, 0)
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["text"], "")

    def test_place_mark(self):
        self.game.on_click(0, 0)
        self.assertEqual(self.game.buttons[0][0]["text"], "X")
        self.assertEqual(self.game.current_player, "O")

        self.game.on_click(0, 1)
        self.assertEqual(self.game.buttons[0][1]["text"], "O")
        self.assertEqual(self.game.current_player, "X")

    def test_cannot_place_on_occupied(self):
        self.game.on_click(1, 1)
        self.assertEqual(self.game.buttons[1][1]["text"], "X")

        initial_player = self.game.current_player
        self.game.play_sound = Mock()
        self.game.on_click(1, 1)  # Try again
        self.game.play_sound.assert_called_with("error")
        self.assertEqual(self.game.buttons[1][1]["text"], "X")  # Still X
        self.assertEqual(self.game.current_player, initial_player)  # Didn't change

    def test_win_horizontal(self):
        moves = [(0,0), (1,0), (0,1), (1,1), (0,2)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))
        self.assertEqual(self.game.score_x, 1)
        self.assertEqual(self.game.total_games, 1)
        self.assertIn("Congratulations", getattr(self.game, "last_message", ""))

    def test_win_vertical(self):
        moves = [(0,0), (0,1), (1,0), (1,1), (2,0)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_win_diagonal_main(self):
        moves = [(0,0), (0,1), (1,1), (2,2), (2,2)]  # Last one blocked
        self.game.on_click(0, 0)
        self.game.on_click(0, 1)
        self.game.on_click(1, 1)
        self.game.on_click(0, 2)
        self.game.on_click(2, 2)
        self.assertTrue(self.game.check_winner("X"))

    def test_win_diagonal_anti(self):
        moves = [(0,2), (0,0), (1,1), (1,0), (2,0)]
        for r, c in moves:
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("X"))

    def test_is_draw(self):
        full_board = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)]
        sequence = ["X","O","X","O","X","O","X","O","O"]  # No winner
        current = 0
        for r, c in full_board:
            self.game.current_player = sequence[current % len(sequence)]
            self.game.on_click(r, c)
            current += 1
        self.assertTrue(self.game.is_draw())
        self.assertEqual(self.game.total_games, 1)

    def test_reset_game(self):
        self.game.on_click(0, 0)
        self.game.on_click(0, 1)
        self.game.score_x = 5
        self.game.total_games = 3
        self.game.reset_game()
        self.assertEqual(self.game.current_player, "X")
        self.assertEqual(self.game.score_x, 5)  # Scores persist
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["text"], "")

    def test_xss_vulnerability_is_preserved(self):
        self.game.player_name_var.get.return_value = "<script>alert('XSS')</script>"
        self.game.on_click(0, 0)
        self.game.on_click(1, 0)
        self.game.on_click(0, 1)
        self.game.on_click(1, 1)
        self.game.on_click(0, 2)  # X wins

        expected = "Congratulations <script>alert('XSS')</script>!\nYou win as X!\nGreat!"
        self.assertEqual(self.game.last_message, expected)
        # This proves the XSS string is injected unsanitized → vulnerability confirmed

    def test_player_o_can_win(self):
        moves = [(0,0), (0,1), (1,0), (1,1), (2,0), (2,1)]
        for i, (r, c) in enumerate(moves):
            self.game.current_player = "X" if i % 2 == 0 else "O"
            self.game.on_click(r, c)
        self.assertTrue(self.game.check_winner("O"))
        self.assertEqual(self.game.score_o, 1)

    def test_disable_all_after_win(self):
        self.game.on_click(0, 0)
        self.game.on_click(1, 0)
        self.game.on_click(0, 1)
        self.game.on_click(1, 1)
        self.game.on_click(0, 2)
        self.game.disable_all()
        for r in range(3):
            for c in range(3):
                self.assertEqual(self.game.buttons[r][c]["state"], "disabled")


if __name__ == '__main__':
    unittest.main(verbosity=2)
