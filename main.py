import tkinter as tk
import threading
import time
import heapq

# ===========================================================
# A* PATHFINDING
# ===========================================================
def astar(start, goal, grid):
    rows, cols = len(grid), len(grid[0])

    def neighbors(x, y):
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                yield nx, ny

    def h(x, y):
        return abs(goal[0] - x) + abs(goal[1] - y)

    pq = [(0 + h(*start), 0, start, [])]
    visited = set()

    while pq:
        _, cost, (x, y), path = heapq.heappop(pq)
        if (x, y) in visited:
            continue
        visited.add((x, y))

        if (x, y) == goal:
            return path + [(x, y)]

        for nx, ny in neighbors(x, y):
            heapq.heappush(pq, (cost + 1 + h(nx, ny), cost + 1, (nx, ny), path + [(x, y)]))

    return None


# ===========================================================
# GAME ENGINE
# ===========================================================
class PlatformerGame:
    TILE = 40
    WIDTH = 20
    HEIGHT = 12

    GRAVITY = 3
    JUMP_STRENGTH = -12
    MOVE_SPEED = 6

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Platformer with AI Pathfinding + Concurrency")

        self.canvas = tk.Canvas(self.window, width=self.TILE*self.WIDTH,
                                height=self.TILE*self.HEIGHT, bg="white")
        self.canvas.pack()

        # Level grid (1 = wall)
        self.grid = [
            [0]*20 for _ in range(12)
        ]

        # Generate platforms
        for x in range(0, 20):
            self.grid[11][x] = 1  # Ground layer

        for x in range(4, 9):
            self.grid[7][x] = 1

        for x in range(12, 16):
            self.grid[5][x] = 1

        self.draw_grid()

        # Create player and enemy
        self.player = self.create_entity(2, 9, "blue")
        self.enemy = self.create_entity(17, 9, "red")

        self.player_vy = 0
        self.enemy_path = []

        self.window.bind("<KeyPress>", self.key_down)
        self.keys = set()

        # Start AI thread
        self.running = True
        threading.Thread(target=self.ai_thread, daemon=True).start()

        self.game_loop()
        self.window.mainloop()

    # ------------------------------------------------------
    # Draw level tiles
    # ------------------------------------------------------
    def draw_grid(self):
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if self.grid[y][x] == 1:
                    self.canvas.create_rectangle(
                        x*self.TILE, y*self.TILE,
                        (x+1)*self.TILE, (y+1)*self.TILE,
                        fill="gray"
                    )

    # ------------------------------------------------------
    # Create player/enemy squares
    # ------------------------------------------------------
    def create_entity(self, gx, gy, color):
        x = gx*self.TILE+5
        y = gy*self.TILE+5
        return self.canvas.create_rectangle(x, y, x+30, y+30, fill=color)

    # ------------------------------------------------------
    # Convert pixel coords to grid
    # ------------------------------------------------------
    def to_grid(self, rect):
        x1, y1, x2, y2 = self.canvas.coords(rect)
        return (int(x1//self.TILE), int(y1//self.TILE))

    # ------------------------------------------------------
    # Player controls
    # ------------------------------------------------------
    def key_down(self, event):
        self.keys.add(event.keysym)

    # ------------------------------------------------------
    # AI thread — recalculates enemy path
    # ------------------------------------------------------
    def ai_thread(self):
        while self.running:
            time.sleep(0.5)

            ex, ey = self.to_grid(self.enemy)
            px, py = self.to_grid(self.player)

            path = astar((ex, ey), (px, py), self.grid)
            if path:
                self.enemy_path = path[1:]  # skip first (current position)

    # ------------------------------------------------------
    # Physics + movement
    # ------------------------------------------------------
    def move_entity(self, rect, dx, dy):
        self.canvas.move(rect, dx, dy)
        x1, y1, x2, y2 = self.canvas.coords(rect)

        # collision with map
        grid_x1 = int(x1 // self.TILE)
        grid_y1 = int(y1 // self.TILE)
        grid_x2 = int(x2 // self.TILE)
        grid_y2 = int(y2 // self.TILE)

        for gy in range(grid_y1, grid_y2+1):
            for gx in range(grid_x1, grid_x2+1):
                if 0 <= gx < self.WIDTH and 0 <= gy < self.HEIGHT:
                    if self.grid[gy][gx] == 1:
                        # collision detected — undo move
                        self.canvas.move(rect, -dx, -dy)
                        return False
        return True

    # ------------------------------------------------------
    # Main game loop
    # ------------------------------------------------------
    def game_loop(self):
        # PLAYER MOVEMENT
        dx = 0
        if "Left" in self.keys:
            dx -= self.MOVE_SPEED
        if "Right" in self.keys:
            dx += self.MOVE_SPEED

        # jump
        if "Up" in self.keys:
            if self.on_ground(self.player):
                self.player_vy = self.JUMP_STRENGTH

        # gravity
        self.player_vy += self.GRAVITY
        if self.player_vy > 12:
            self.player_vy = 12

        # apply horizontal & vertical movement
        self.move_entity(self.player, dx, 0)
        self.move_entity(self.player, 0, self.player_vy)

        # ENEMY AI FOLLOWING PATH
        if self.enemy_path:
            target = self.enemy_path[0]
            ex, ey = self.to_grid(self.enemy)

            if (ex, ey) == target:
                self.enemy_path.pop(0)
            else:
                tx, ty = target
                if tx > ex: self.move_entity(self.enemy, 3, 0)
                if tx < ex: self.move_entity(self.enemy, -3, 0)
                if ty > ey: self.move_entity(self.enemy, 0, 3)
                if ty < ey: self.move_entity(self.enemy, 0, -3)

        # COLLISION = GAME OVER
        if self.entity_collision(self.player, self.enemy):
            self.running = False
            self.canvas.create_text(400, 200, text="GAME OVER",
                                    fill="black", font=("Arial", 40))
            return

        self.keys.clear()
        self.window.after(30, self.game_loop)

    # ------------------------------------------------------
    def on_ground(self, rect):
        x1, y1, x2, y2 = self.canvas.coords(rect)
        grid_x = int(x1 // self.TILE)
        grid_y = int((y2 + 1) // self.TILE)

        if 0 <= grid_x < self.WIDTH and 0 <= grid_y < self.HEIGHT:
            return self.grid[grid_y][grid_x] == 1
        return False

    # ------------------------------------------------------
    def entity_collision(self, a, b):
        ax1, ay1, ax2, ay2 = self.canvas.coords(a)
        bx1, by1, bx2, by2 = self.canvas.coords(b)

        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)

# RUN GAME
if __name__ == "__main__":
    PlatformerGame()
