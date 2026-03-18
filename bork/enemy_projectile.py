"""Shared enemy/boss projectile entity."""

import arcade

from bork.constants import SCREEN_HEIGHT, SCREEN_WIDTH


class EnemyProjectile:
    """A projectile fired by enemies/bosses toward the player."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, ...],
        size: float = 5.0,
        shape: str = "diamond",
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.shape = shape  # "diamond" or "circle"

    def update(self, dt: float) -> None:
        """Move the projectile by its velocity."""
        self.x += self.vx * dt
        self.y += self.vy * dt

    def is_off_screen(self) -> bool:
        """Return True if the projectile is outside the screen bounds."""
        return (
            self.x < -self.size
            or self.x > SCREEN_WIDTH + self.size
            or self.y < -self.size
            or self.y > SCREEN_HEIGHT + self.size
        )

    def draw(self) -> None:
        """Draw the projectile as a diamond or circle."""
        s = self.size
        if self.shape == "circle":
            arcade.draw_circle_filled(self.x, self.y, s, self.color)
        else:
            # Diamond shape
            points = [
                (self.x - s, self.y),
                (self.x, self.y + s),
                (self.x + s, self.y),
                (self.x, self.y - s),
            ]
            arcade.draw_polygon_filled(points, self.color)
