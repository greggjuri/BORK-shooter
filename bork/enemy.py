"""Enemy entity with straight and sine-wave movement patterns."""

import math

import arcade

from bork.constants import (
    ENEMY_BODY_COLOR,
    ENEMY_EYE_BRIGHT,
    ENEMY_EYE_COLOR,
    ENEMY_HULL_COLOR,
    ENEMY_PLATE_COLOR,
    ENEMY_SIZE,
    ENEMY_SPEED,
    ENEMY_STROKE_COLOR,
    ENEMY_WOBBLE_DEGREES,
    ENEMY_WOBBLE_SPEED,
    SINE_AMPLITUDE,
    SINE_FREQUENCY,
)

# Crescent body points (reversed-C, arms sweep back/left)
_CRESCENT_POINTS = (
    (-2, -8), (-14, -12), (-22, -18), (-28, -28), (-32, -30),
    (-26, -28), (-24, -22), (-18, -16), (-8, -12), (6, -10),
    (14, -5), (14, 5), (6, 10), (-8, 12), (-18, 16),
    (-24, 22), (-26, 28), (-32, 30), (-28, 28), (-22, 18),
    (-14, 12), (-2, 8),
)

# Top armor plate points
_TOP_PLATE_POINTS = ((-16, -13), (-22, -18), (-26, -24), (-24, -20), (-18, -15))

# Bottom armor plate points (mirror of top)
_BOT_PLATE_POINTS = ((-16, 13), (-22, 18), (-26, 24), (-24, 20), (-18, 15))

# Center hull plate points
_HULL_POINTS = ((0, -6), (10, -4), (12, 0), (10, 4), (0, 6), (-4, 0))


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

    def __init__(self, x: float, y: float, pattern: str, base_y: float) -> None:
        self.x = x
        self.y = y
        self.pattern = pattern  # "straight" or "sine"
        self.base_y = base_y  # center Y for sine oscillation
        self.time_alive = 0.0

    @property
    def wobble_angle(self) -> float:
        """Visual wobble rotation in radians."""
        return math.radians(
            math.sin(self.time_alive * ENEMY_WOBBLE_SPEED * 2 * math.pi)
            * ENEMY_WOBBLE_DEGREES
        )

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
        """Draw the enemy as a crescent raider with wobble."""
        cx, cy = self.x, self.y
        a = self.wobble_angle

        # Main crescent body
        body = _rotate_points(_CRESCENT_POINTS, cx, cy, a)
        arcade.draw_polygon_filled(body, ENEMY_BODY_COLOR)
        arcade.draw_polygon_outline(body, ENEMY_STROKE_COLOR)

        # Top armor plate
        top_plate = _rotate_points(_TOP_PLATE_POINTS, cx, cy, a)
        arcade.draw_polygon_filled(top_plate, ENEMY_PLATE_COLOR)
        arcade.draw_polygon_outline(top_plate, ENEMY_STROKE_COLOR)

        # Bottom armor plate
        bot_plate = _rotate_points(_BOT_PLATE_POINTS, cx, cy, a)
        arcade.draw_polygon_filled(bot_plate, ENEMY_PLATE_COLOR)
        arcade.draw_polygon_outline(bot_plate, ENEMY_STROKE_COLOR)

        # Center hull plate
        hull = _rotate_points(_HULL_POINTS, cx, cy, a)
        arcade.draw_polygon_filled(hull, ENEMY_HULL_COLOR)
        arcade.draw_polygon_outline(hull, (*ENEMY_STROKE_COLOR[:3], 102))

        # Arm tip glows
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        for ox, oy in ((-29, -27), (-29, 27)):
            gx = cx + ox * cos_a - oy * sin_a
            gy = cy + ox * sin_a + oy * cos_a
            arcade.draw_circle_filled(gx, gy, 1.5, (*ENEMY_STROKE_COLOR[:3], 127))

        # Scanner eye (two layered ellipses at center-right)
        arcade.draw_ellipse_filled(cx, cy, 10, 6, (*ENEMY_EYE_COLOR[:3], 153))
        arcade.draw_ellipse_filled(cx, cy, 6, 3, (*ENEMY_EYE_BRIGHT[:3], 229))
