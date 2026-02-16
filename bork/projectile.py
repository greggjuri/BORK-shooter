"""Laser projectile fired by the player."""

import arcade

from bork.constants import (
    COLOR_LASER,
    PROJECTILE_LENGTH,
    PROJECTILE_SPEED,
    PROJECTILE_WIDTH,
    SCREEN_WIDTH,
)


class Projectile:
    """A single laser projectile moving rightward."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def update(self, dt: float) -> None:
        """Move the projectile rightward."""
        self.x += PROJECTILE_SPEED * dt

    def is_off_screen(self) -> bool:
        """Return True if past the right edge of the screen."""
        return self.x > SCREEN_WIDTH + PROJECTILE_LENGTH

    def draw(self) -> None:
        """Draw the laser bolt as a small filled rectangle."""
        half_w = PROJECTILE_WIDTH / 2
        arcade.draw_lrbt_rectangle_filled(
            self.x - PROJECTILE_LENGTH / 2,
            self.x + PROJECTILE_LENGTH / 2,
            self.y - half_w,
            self.y + half_w,
            COLOR_LASER,
        )
