"""Collectible powerup that drifts leftward with a pulse animation."""

import math

import arcade

from bork.constants import (
    POWERUP_LABEL_COLOR,
    POWERUP_PULSE_AMOUNT,
    POWERUP_PULSE_SPEED,
    POWERUP_SIZE,
    POWERUP_SPEED,
)

# Glassy button colors
_GLOW_COLOR = (0, 200, 180, 18)
_OUTER_COLOR = (0, 180, 160, 102)  # ~0.4 opacity teal
_INNER_COLOR = (0, 220, 190, 153)  # ~0.6 opacity brighter teal
_HIGHLIGHT_COLOR = (255, 255, 255, 80)
_SPECULAR_COLOR = (255, 255, 255, 200)


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
        """Draw as a glassy pulsing button with glow and reflection."""
        pulse = 1.0 + POWERUP_PULSE_AMOUNT * math.sin(
            self.time_alive * POWERUP_PULSE_SPEED * 2 * math.pi
        )
        r = POWERUP_SIZE * pulse
        cx, cy = self.x, self.y

        # Background glow (large, very low opacity)
        arcade.draw_circle_filled(cx, cy, r * 2.0, _GLOW_COLOR)

        # Outer circle (semi-transparent teal)
        arcade.draw_circle_filled(cx, cy, r, _OUTER_COLOR)

        # Inner circle (brighter, slightly smaller for depth)
        arcade.draw_circle_filled(cx, cy, r * 0.78, _INNER_COLOR)

        # Centered letter label
        arcade.draw_text(
            "S", cx, cy, POWERUP_LABEL_COLOR,
            font_size=int(r * 0.8), bold=True,
            anchor_x="center", anchor_y="center",
        )

        # Highlight arc — ellipse in upper-left quadrant for glass reflection
        arcade.draw_ellipse_filled(
            cx - r * 0.22, cy + r * 0.25, r * 0.6, r * 0.3, _HIGHLIGHT_COLOR
        )

        # Specular dot near top
        arcade.draw_circle_filled(cx - r * 0.15, cy + r * 0.4, r * 0.1, _SPECULAR_COLOR)
