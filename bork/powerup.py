"""Collectible powerup that drifts leftward with a pulse animation."""

import math

import arcade

from bork.constants import (
    POWERUP_COLOR,
    POWERUP_PULSE_AMOUNT,
    POWERUP_PULSE_SPEED,
    POWERUP_SIZE,
    POWERUP_SPEED,
    POWERUP_TEXT_COLOR,
)


class Powerup:
    """A collectible powerup entity."""

    def __init__(self, x: float, y: float, kind: str) -> None:
        self.x = x
        self.y = y
        self.kind = kind  # "speed" (extensible for future types)
        self.time_alive = 0.0

    def update(self, dt: float) -> None:
        """Move leftward and advance pulse timer."""
        self.x -= POWERUP_SPEED * dt
        self.time_alive += dt

    def is_off_screen(self) -> bool:
        """Return True if past the left edge."""
        return self.x < -POWERUP_SIZE

    def draw(self) -> None:
        """Draw as a pulsing yellow circle with black letter."""
        pulse = 1.0 + POWERUP_PULSE_AMOUNT * math.sin(
            self.time_alive * POWERUP_PULSE_SPEED * 2 * math.pi
        )
        r = POWERUP_SIZE * pulse
        arcade.draw_circle_filled(self.x, self.y, r, POWERUP_COLOR)
        arcade.draw_text(
            "S",
            self.x,
            self.y,
            POWERUP_TEXT_COLOR,
            font_size=14,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
