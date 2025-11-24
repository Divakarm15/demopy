import tkinter as tk
from tkinter import messagebox, ttk, font
import random
import winsound  # Windows only, remove or replace on other OS
import time

class TicTacToe:
    def __init__(self):
        # ============================
        # === MAIN WINDOW SETUP ===
        # ============================
        self.window = tk.Tk()
        self.window.title("XO Game (Tic Tac Toe) - Ultimate Edition")
        self.window.geometry("600x700")
        self.window.resizable(False, False)
        self.window.configure(bg="#1e1e1e")

        # ============================
        # === GAME STATE VARIABLES ===
        # ============================
        self.current_player = "X"
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.score_x = 0
        self.score_o = 0
        self.total_games = 0
        self.theme = "dark"  # dark / light
        self.sound_enabled = True

        # ============================
        # === PLAYER NAME INPUT (XSS VULNERABLE) ===
        # ============================
        # === INTRODUCED XSS VULNERABILITY START ===
        self.player_name_var = tk.StringVar(value="Player")
        name_frame = tk.Frame(self.window, bg="#1e1e1e")
        name_frame.pack(pady=10)
        tk.Label(name_frame, text="Your name:", font=("Helvetica", 12), fg="cyan", bg="#1e1e1e").pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame, textvariable=self.player_name_var, width=20, font=("Helvetica", 11), bg="#333", fg="white", insertbackground="white")
        self.name_entry.pack(side=tk.LEFT, padx=8)
        # === XSS VULNERABILITY END ===

        # ============================
        # === SCOREBOARD ===
        # ============================
        score_frame = tk.Frame(self.window, bg="#1e1e1e")
        score_frame.pack(pady=10)
        self.score_label = tk.Label(score_frame, text=f"X: {self.score_x}   |   O: {self.score_o}   |   Games: {self.total_games}",
                                    font=("Courier", 14, "bold"), fg="#00ff00", bg="#1e1e1e")
        self.score_label.pack()

        # ============================
        # === CREATE BOARD ===
        # ============================
        self.create_board()

        # ============================
        # === CONTROL BUTTONS ===
        # ============================
        control_frame = tk.Frame(self.window, bg="#1e1e1e")
        control_frame.pack(pady=15)

        reset_btn = tk.Button(control_frame, text="New Game", font=("Arial", 12, "bold"), bg="#ff4444", fg="white",
                              activebackground="#ff6666", command=self.reset_game, width=12, height=2)
        reset_btn.grid(row=0, column=0, padx=10)

        theme_btn = tk.Button(control_frame, text="Toggle Theme", font=("Arial", 12), bg="#4444aa", fg="white",
                              activebackground="#6666cc", command=self.toggle_theme, width=12, height=2)
        theme_btn.grid(row=0, column=1, padx=10)

        sound_btn = tk.Button(control_frame, text="Sound: ON", font=("Arial", 12), bg="#44aa44", fg="white",
                              activebackground="#66cc66", command=self.toggle_sound, width=12, height=2)
        sound_btn.grid(row=0, column=2, padx=10)

        # ============================
        # === STATUS LABEL ===
        # ============================
        self.status_label = tk.Label(self.window, text=f"Player {self.current_player}'s turn",
                                     font=("Helvetica", 16, "bold"), fg="#ffff00", bg="#1e1e1e")
        self.status_label.pack(pady=10)

        # ============================
        # === FUN MESSAGES LIST ===
        # ============================
        self.win_messages = [
            "Amazing skills!",
            "Unbelievable move!",
            "You're on fire!",
            "Champion of XO!",
            "Master strategist!",
            "None can defeat you!"
        ]

        self.play_sound("start")
        self.window.mainloop()

    def create_board(self):
        frame = tk.Frame(self.window, bg="#1e1e1e")
        frame.pack(pady=20)

        button_style = {
            "font": ("Arial", 36, "bold"),
            "width": 5,
            "height": 2,
            "relief": "raised",
            "bd": 5,
            "bg": "#333333",
            "fg": "white",
            "activebackground": "#555555"
        }

        for row in range(3):
            for col in range(3):
                btn = tk.Button(
                    frame,
                    text="",
                    command=lambda r=row, c=col: self.on_click(r, c),
                    **button_style
                )
                btn.grid(row=row, column=col, padx=5, pady=5)
                self.buttons[row][col] = btn

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

            # === XSS TRIGGER (UNCHANGED FROM ORIGINAL) ===
            player_name = self.player_name_var.get()                     # User-controlled input
            malicious_message = f"Congratulations {player_name}!\nYou win as {self.current_player}!\n{random.choice(self.win_messages)}"
            messagebox.showinfo("Game Over", malicious_message)         # Direct insertion → XSS
            # === END OF XSS ===

            self.highlight_winner()
            self.disable_all()
            self.status_label.config(text=f"{self.current_player} Wins!", fg="#00ff00")
            self.play_sound("win")

        elif self.is_draw():
            self.total_games += 1
            self.update_score()
            messagebox.showinfo("Game Over", "It's a draw!\nGood game!")
            self.status_label.config(text="It's a Draw!", fg="#ffff00")
            self.play_sound("draw")
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.status_label.config(text=f"Player {self.current_player}'s turn", fg="#ff0066" if self.current_player == "O" else "#00ff00")

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
                btn = self.buttons[r][c]
                btn["text"] = ""
                btn["state"] = "normal"
                btn.config(bg="#333333", fg="white")
        self.status_label.config(text=f"Player {self.current_player}'s turn", fg="#00ff00")
        self.play_sound("start")

    def update_score(self):
        self.score_label.config(text=f"X: {self.score_x}   |   O: {self.score_o}   |   Games: {self.total_games}")

    def highlight_winner(self):
        winner = self.current_player
        b = self.buttons
        lines = [
            [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
        ]
        for line in lines:
            if all(b[r][c]["text"] == winner for r, c in line):
                for r, c in line:
                    b[r][c].config(bg="#00ff00", fg="black")
                break

    def toggle_theme(self):
        if self.theme == "dark":
            self.theme = "light"
            bg = "white"
            fg = "black"
            btn_bg = "#f0f0f0"
        else:
            self.theme = "dark"
            bg = "#1e1e1e"
            fg = "white"
            btn_bg = "#333333"

        self.window.config(bg=bg)
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=bg)
                for child in widget.winfo_children():
                    if isinstance(child, (tk.Label, tk.Button)):
                        child.config(bg=bg, fg=fg)
                    if isinstance(child, tk.Button) and child not in [self.buttons[r][c] for r in range(3) for c in range(3)]:
                        child.config(bg="#888888" if self.theme == "light" else "#444444")
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(bg=btn_bg)

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        # Find and update the sound button text
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button) and "Sound" in child.cget("text"):
                        child.config(text=f"Sound: {'ON' if self.sound_enabled else 'OFF'}")

    def play_sound(self, sound_type):
        if not self.sound_enabled:
            return
        try:
            freq = 440
            dur = 150
            if sound_type == "click":
                winsound.Beep(600, 100)
            elif sound_type == "win":
                winsound.Beep(800, 200)
                winsound.Beep(1000, 200)
                winsound.Beep(1200, 300)
            elif sound_type == "draw":
                winsound.Beep(400, 300)
                winsound.Beep(300, 300)
            elif sound_type == "error":
                winsound.Beep(200, 400)
            elif sound_type == "start":
                winsound.Beep(500, 100)
                winsound.Beep(700, 100)
        except:
            pass  # Ignore sound errors on non-Windows


if __name__ == "__main__":
    TicTacToe()
