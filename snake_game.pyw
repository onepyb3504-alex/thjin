"""A simple Snake game that runs with Python's windowed launcher.

Double-click this file on Windows, or run it with:
    python snake_game.pyw
"""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass


CELL_SIZE = 24
GRID_WIDTH = 25
GRID_HEIGHT = 20
GAME_SPEED_MS = 110
STARTING_LENGTH = 3

BACKGROUND = "#101820"
SNAKE_HEAD = "#7CFC00"
SNAKE_BODY = "#32CD32"
FOOD_COLOR = "#FF4C4C"
TEXT_COLOR = "#F2F2F2"

DIRECTIONS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
    "w": (0, -1),
    "s": (0, 1),
    "a": (-1, 0),
    "d": (1, 0),
    "W": (0, -1),
    "S": (0, 1),
    "A": (-1, 0),
    "D": (1, 0),
}


@dataclass(frozen=True)
class Point:
    """A coordinate on the game grid."""

    x: int
    y: int

    def moved(self, direction: tuple[int, int]) -> "Point":
        dx, dy = direction
        return Point(self.x + dx, self.y + dy)


class SnakeGame:
    """Tkinter-powered Snake game with keyboard controls."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Snake Game")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg=BACKGROUND,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.score_label = tk.Label(
            root,
            text="Score: 0  |  Arrow keys/WASD to move  |  Space to restart",
            bg=BACKGROUND,
            fg=TEXT_COLOR,
            font=("Arial", 12),
            pady=8,
        )
        self.score_label.pack(fill="x")

        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.snake: list[Point] = []
        self.food = Point(0, 0)
        self.score = 0
        self.game_over = False
        self.after_id: str | None = None

        self.root.bind("<KeyPress>", self.handle_keypress)
        self.reset_game()

    def reset_game(self) -> None:
        """Start a new game from the center of the board."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        center = Point(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = [Point(center.x - offset, center.y) for offset in range(STARTING_LENGTH)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.spawn_food()
        self.update_score_label()
        self.draw()
        self.schedule_next_tick()

    def spawn_food(self) -> None:
        """Place food on a random empty cell."""
        occupied = set(self.snake)
        available_cells = [
            Point(x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if Point(x, y) not in occupied
        ]
        self.food = random.choice(available_cells)

    def handle_keypress(self, event: tk.Event) -> None:
        """Update direction or restart the game based on the pressed key."""
        if event.keysym == "space":
            self.reset_game()
            return

        requested = DIRECTIONS.get(event.keysym)
        if requested is None:
            return

        if self.direction[0] + requested[0] == 0 and self.direction[1] + requested[1] == 0:
            return
        self.next_direction = requested

    def tick(self) -> None:
        """Advance the game by one frame."""
        if self.game_over:
            return

        self.direction = self.next_direction
        new_head = self.snake[0].moved(self.direction)

        if self.hit_wall(new_head) or new_head in self.snake[:-1]:
            self.end_game()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
            self.update_score_label()
        else:
            self.snake.pop()

        self.draw()
        self.schedule_next_tick()

    def hit_wall(self, point: Point) -> bool:
        """Return whether a point is outside the board."""
        return point.x < 0 or point.x >= GRID_WIDTH or point.y < 0 or point.y >= GRID_HEIGHT

    def schedule_next_tick(self) -> None:
        self.after_id = self.root.after(GAME_SPEED_MS, self.tick)

    def update_score_label(self) -> None:
        self.score_label.config(
            text=f"Score: {self.score}  |  Arrow keys/WASD to move  |  Space to restart"
        )

    def draw(self) -> None:
        """Render the snake, food, and optional game-over text."""
        self.canvas.delete("all")
        self.draw_cell(self.food, FOOD_COLOR)
        for index, point in enumerate(self.snake):
            self.draw_cell(point, SNAKE_HEAD if index == 0 else SNAKE_BODY)

    def draw_cell(self, point: Point, color: str) -> None:
        x1 = point.x * CELL_SIZE
        y1 = point.y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=BACKGROUND)

    def end_game(self) -> None:
        self.game_over = True
        self.canvas.create_text(
            GRID_WIDTH * CELL_SIZE / 2,
            GRID_HEIGHT * CELL_SIZE / 2,
            text=f"Game Over\nScore: {self.score}\nPress Space to restart",
            fill=TEXT_COLOR,
            font=("Arial", 24, "bold"),
            justify="center",
        )


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
