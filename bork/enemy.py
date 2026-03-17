"""Enemy entity with straight and sine-wave movement patterns."""

import math

import arcade

from bork.constants import (
    ENEMY_BATWING_BOB_PIXELS,
    ENEMY_BATWING_BOB_SPEED,
    ENEMY_BATWING_BODY_COLOR,
    ENEMY_BATWING_EYE_BRIGHT,
    ENEMY_BATWING_EYE_COLOR,
    ENEMY_BATWING_PLATE_COLOR,
    ENEMY_BATWING_STROKE_COLOR,
    ENEMY_BATWING_WOBBLE_DEGREES,
    ENEMY_BATWING_WOBBLE_SPEED,
    ENEMY_SIZE,
    ENEMY_SPEED,
    SINE_AMPLITUDE,
    SINE_FREQUENCY,
)

# Bat wing shape points
_TOP_WING = ((-6, -4), (-20, -20), (14, -16), (10, -4))
_BOT_WING = ((-6, 4), (-20, 20), (14, 16), (10, 4))
_FUSELAGE = ((-10, -4), (12, -4), (14, 0), (12, 4), (-10, 4), (-12, 0))

# Wing accent line endpoints (start, end)
_ACCENT_LINES = (((-8, -6), (-16, -16)), ((-8, 6), (-16, 16)))


def _rotate_points(
    points: tuple[tuple[int, int], ...], cx: float, cy: float, angle_rad: float
) -> list[tuple[float, float]]:
    """Rotate a set of offset points around (cx, cy)."""
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return [
        (cx + px * cos_a - py * sin_a, cy + px * sin_a + py * cos_a)
        for px, py in points
    ]


class Enemy:
    """A single enemy that moves leftward with an optional sine pattern."""

    def __init__(
        self, x: float, y: float, pattern: str, base_y: float, speed: float = 0.0
    ) -> None:
        self.x = x
        self.y = y
        self.pattern = pattern  # "straight" or "sine"
        self.base_y = base_y  # center Y for sine oscillation
        self.speed = speed if speed > 0 else ENEMY_SPEED
        self.time_alive = 0.0

    @property
    def wobble_angle(self) -> float:
        """Visual wobble rotation in radians."""
        return math.radians(
            math.sin(self.time_alive * ENEMY_BATWING_WOBBLE_SPEED * 2 * math.pi)
            * ENEMY_BATWING_WOBBLE_DEGREES
        )

    def update(self, dt: float) -> None:
        """Move leftward. Apply sine oscillation if pattern is 'sine'."""
        self.x -= self.speed * dt
        self.time_alive += dt
        if self.pattern == "sine":
            self.y = self.base_y + SINE_AMPLITUDE * math.sin(
                SINE_FREQUENCY * self.time_alive * 2 * math.pi
            )

    def is_off_screen(self) -> bool:
        """Return True if past the left edge of the screen."""
        return self.x < -ENEMY_SIZE

    @property
    def bob_offset(self) -> float:
        """Visual vertical bob offset in pixels."""
        return math.sin(self.time_alive * ENEMY_BATWING_BOB_SPEED * 2 * math.pi) * ENEMY_BATWING_BOB_PIXELS

    def draw(self) -> None:
        """Draw the enemy as a bat wing fighter with wobble and bob."""
        cx = self.x
        cy = self.y + self.bob_offset
        a = self.wobble_angle
        cos_a = math.cos(a)
        sin_a = math.sin(a)

        # Top wing
        top = _rotate_points(_TOP_WING, cx, cy, a)
        arcade.draw_polygon_filled(top, ENEMY_BATWING_BODY_COLOR)
        arcade.draw_polygon_outline(top, ENEMY_BATWING_STROKE_COLOR)

        # Bottom wing
        bot = _rotate_points(_BOT_WING, cx, cy, a)
        arcade.draw_polygon_filled(bot, ENEMY_BATWING_BODY_COLOR)
        arcade.draw_polygon_outline(bot, ENEMY_BATWING_STROKE_COLOR)

        # Center fuselage
        fuse = _rotate_points(_FUSELAGE, cx, cy, a)
        arcade.draw_polygon_filled(fuse, ENEMY_BATWING_PLATE_COLOR)
        arcade.draw_polygon_outline(fuse, ENEMY_BATWING_STROKE_COLOR)

        # Wing accent lines
        for (sx, sy), (ex, ey) in _ACCENT_LINES:
            x1 = cx + sx * cos_a - sy * sin_a
            y1 = cy + sx * sin_a + sy * cos_a
            x2 = cx + ex * cos_a - ey * sin_a
            y2 = cy + ex * sin_a + ey * cos_a
            arcade.draw_line(x1, y1, x2, y2, (255, 85, 85, 127))

        # Scanner eye
        ex = cx + 2 * cos_a
        ey = cy + 2 * sin_a
        arcade.draw_ellipse_filled(ex, ey, 6, 4, (*ENEMY_BATWING_EYE_COLOR[:3], 178))
        arcade.draw_ellipse_filled(ex, ey, 3, 2, ENEMY_BATWING_EYE_BRIGHT)
