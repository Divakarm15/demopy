import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("XO Game (Tic Tac Toe)")

        self.current_player = "X"
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        self.create_board()

        self.window.mainloop()

    def create_board(self):
        frame = tk.Frame(self.window)
        frame.pack()

        for row in range(3):
            for col in range(3):
                btn = tk.Button(
                    frame,
                    text="",
                    font=("Arial", 30),
                    width=5,
                    height=2,
                    command=lambda r=row, c=col: self.on_click(r, c)
                )
                btn.grid(row=row, column=col)
                self.buttons[row][col] = btn

        reset_btn = tk.Button(
            self.window,
            text="Reset",
            font=("Arial", 14),
            command=self.reset_game
        )
        reset_btn.pack(pady=10)

    def on_click(self, row, col):
        btn = self.buttons[row][col]

        # Ignore move if button occupied
        if btn["text"] != "":
            return

        btn["text"] = self.current_player

        if self.check_winner(self.current_player):
            messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
            self.disable_all()
        elif self.is_draw():
            messagebox.showinfo("Game Over", "It's a draw!")
        else:
            # Switch player
            self.current_player = "O" if self.current_player == "X" else "X"

    def check_winner(self, player):
        b = self.buttons

        # Rows, columns, diagonals
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
                btn = self.buttons[r][c]
                btn["text"] = ""
                btn["state"] = "normal"


if __name__ == "__main__":
    TicTacToe()
