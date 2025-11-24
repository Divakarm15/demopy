import tkinter as tk
import threading
import time
import random
import math

# ============================================================
# AI MODULE
# ============================================================

class EnemyAI:
    """
    A lightweight AI model that scores possible moves using
    a weighted "neural-like" evaluation: distance-reduction,
    prediction, and randomness.
    """

    def __init__(self):
        self.weights = {
            "distance": 1.3,
            "prediction": 1.0,
            "noise": 0.2
        }

    def choose_direction(self, enemy_pos, player_pos):
        """
        Evaluate move directions and return the best one.
        """
        directions = {
            "UP": (0, -5),
            "DOWN": (0, 5),
            "LEFT": (-5, 0),
            "RIGHT": (5, 0)
        }

        best_score = -99999
        best_move = "UP"

        for move, (dx, dy) in directions.items():
            new_enemy_x = enemy_pos[0] + dx
            new_enemy_y = enemy_pos[1] + dy

            # Distance score (AI tries to reduce distance)
            dist_before = math.dist(enemy_pos, player_pos)
            dist_after = math.dist((new_enemy_x, new_enemy_y), player_pos)
            distance_score = dist_before - dist_after

            # Prediction score (enemy predicts where player is heading)
            predicted_player = (
                player_pos[0] + random.randint(-10, 10),
                player_pos[1] + random.randint(-10, 10)
            )
            prediction_score = 1 / (math.dist((new_enemy_x, new_enemy_y), predicted_player) + 0.1)

            # Noise (adds randomness for non-linear behavior)
            noise_score = random.uniform(-1, 1)

            total_score = (
                distance_score * self.weights["distance"] +
                prediction_score * self.weights["prediction"] +
                noise_score * self.weights["noise"]
            )

            if total_score > best_score:
                best_score = total_score
                best_move = move

        return best_move


# ============================================================
# GAME ENGINE
# ============================================================

class Game:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AI + GUI + Concurrency Game")

        self.canvas = tk.Canvas(self.window, width=600, height=400, bg="white")
        self.canvas.pack()

        # Player and enemy objects
        self.player = self.canvas.create_rectangle(50, 50, 80, 80, fill="blue")
        self.enemy = self.canvas.create_rectangle(300, 200, 330, 230, fill="red")

        self.player_speed = 10
        self.enemy_speed = 5

        self.ai = EnemyAI()
        self.last_move = "UP"

        # For thread safety
        self.lock = threading.Lock()
        self.running = True

        # Movement system
        self.window.bind("<KeyPress>", self.key_pressed)

        # Start the enemy AI thread
        threading.Thread(target=self.enemy_logic_loop, daemon=True).start()

        # Game loop
        self.game_loop()

        self.window.mainloop()


    # ========================================================
    # Player controls
    # ========================================================
    def key_pressed(self, event):
        if event.keysym == "Up":
            self.move_object(self.player, 0, -self.player_speed)
        elif event.keysym == "Down":
            self.move_object(self.player, 0, self.player_speed)
        elif event.keysym == "Left":
            self.move_object(self.player, -self.player_speed, 0)
        elif event.keysym == "Right":
            self.move_object(self.player, self.player_speed, 0)

    # Safe movement inside game boundaries
    def move_object(self, obj, dx, dy):
        self.canvas.move(obj, dx, dy)
        x1, y1, x2, y2 = self.canvas.coords(obj)

        # Clamp inside canvas
        if x1 < 0: self.canvas.move(obj, -x1, 0)
        if y1 < 0: self.canvas.move(obj, 0, -y1)
        if x2 > 600: self.canvas.move(obj, 600 - x2, 0)
        if y2 > 400: self.canvas.move(obj, 0, 400 - y2)


    # ========================================================
    # ENEMY AI BACKGROUND THREAD
    # ========================================================
    def enemy_logic_loop(self):
        while self.running:
            time.sleep(0.06)  # AI thinking delay

            with self.lock:
                ex1, ey1, ex2, ey2 = self.canvas.coords(self.enemy)
                px1, py1, px2, py2 = self.canvas.coords(self.player)

                enemy_center = ((ex1 + ex2) / 2, (ey1 + ey2) / 2)
                player_center = ((px1 + px2) / 2, (py1 + py2) / 2)

                move = self.ai.choose_direction(enemy_center, player_center)
                self.last_move = move


    # ========================================================
    # GAME LOOP — runs on main Tkinter thread
    # ========================================================
    def game_loop(self):
        with self.lock:
            # Apply AI movement
            if self.last_move == "UP":
                self.move_object(self.enemy, 0, -self.enemy_speed)
            elif self.last_move == "DOWN":
                self.move_object(self.enemy, 0, self.enemy_speed)
            elif self.last_move == "LEFT":
                self.move_object(self.enemy, -self.enemy_speed, 0)
            elif self.last_move == "RIGHT":
                self.move_object(self.enemy, self.enemy_speed, 0)

            # Collision detection
            if self.check_collision():
                self.running = False
                self.canvas.create_text(
                    300, 200,
                    text="GAME OVER",
                    fill="black",
                    font=("Arial", 36)
                )
                return

        # Keep looping
        self.window.after(30, self.game_loop)


    # ========================================================
    # Collision Detection
    # ========================================================
    def check_collision(self):
        p = self.canvas.bbox(self.player)
        e = self.canvas.bbox(self.enemy)

        overlap = not (
            p[2] < e[0] or
            p[0] > e[2] or
            p[3] < e[1] or
            p[1] > e[3]
        )
        return overlap


# ============================================================
# RUN THE GAME
# ============================================================
if __name__ == "__main__":
    Game()
