"""Enemy entity with straight and sine-wave movement patterns."""

import math

import arcade

from bork.constants import (
    ENEMY_COLOR,
    ENEMY_SIZE,
    ENEMY_SPEED,
    SINE_AMPLITUDE,
    SINE_FREQUENCY,
)


class Enemy:
    """A single enemy that moves leftward with an optional sine pattern."""

    def __init__(self, x: float, y: float, pattern: str, base_y: float) -> None:
        self.x = x
        self.y = y
        self.pattern = pattern  # "straight" or "sine"
        self.base_y = base_y  # center Y for sine oscillation
        self.time_alive = 0.0

    def update(self, dt: float) -> None:
        """Move leftward. Apply sine oscillation if pattern is 'sine'."""
        self.x -= ENEMY_SPEED * dt
        self.time_alive += dt
        if self.pattern == "sine":
            self.y = self.base_y + SINE_AMPLITUDE * math.sin(
                SINE_FREQUENCY * self.time_alive * 2 * math.pi
            )

    def is_off_screen(self) -> bool:
        """Return True if past the left edge of the screen."""
        return self.x < -ENEMY_SIZE

    def draw(self) -> None:
        """Draw the enemy as a diamond shape."""
        s = ENEMY_SIZE
        points = [
            (self.x - s, self.y),  # left
            (self.x, self.y + s),  # top
            (self.x + s, self.y),  # right
            (self.x, self.y - s),  # bottom
        ]
        arcade.draw_polygon_filled(points, ENEMY_COLOR)
