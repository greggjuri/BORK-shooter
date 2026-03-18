"""Player ship with momentum-based 8-directional movement."""

import math

import arcade

from bork.constants import (
    EXHAUST_LAYERS,
    FIRE_RATE_LEVELS,
    INVULNERABLE_BLINK_RATE,
    PLAYER_SHIP_SIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIP_ACCENT_COLOR,
    SHIP_BODY_COLOR,
    SHIP_COCKPIT_COLOR,
    SHIP_DARK_COLOR,
    SHIP_OUTLINE_COLOR,
    SPEED_LEVELS,
)


class Player:
    """Player ship with momentum-based 8-directional movement."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.shoot_timer = 0.0
        self.speed_level: int = 1
        self.fire_rate_level: int = 1
        self.invulnerable_timer: float = 0.0

    @property
    def is_invulnerable(self) -> bool:
        """Return True if player is in invulnerability period."""
        return self.invulnerable_timer > 0.0

    def update(self, dt: float, keys_pressed: set[int]) -> None:
        """Update position based on input, friction, and bounds."""
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer < 0:
                self.invulnerable_timer = 0.0

        # Determine direction from input
        dx = 0.0
        dy = 0.0
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            dx += 1.0
        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            dx -= 1.0
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            dy += 1.0
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            dy -= 1.0

        # Normalize diagonal so it doesn't exceed max speed
        if dx != 0.0 and dy != 0.0:
            factor = 1.0 / math.sqrt(2.0)
            dx *= factor
            dy *= factor

        # Set velocity instantly to tier max speed in input direction
        max_speed = SPEED_LEVELS[self.speed_level - 1]
        self.vx = dx * max_speed
        self.vy = dy * max_speed

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Clamp to screen bounds (accounting for ship size)
        self.x = max(PLAYER_SHIP_SIZE, min(SCREEN_WIDTH - PLAYER_SHIP_SIZE, self.x))
        self.y = max(PLAYER_SHIP_SIZE, min(SCREEN_HEIGHT - PLAYER_SHIP_SIZE, self.y))

    def draw(self) -> None:
        """Draw the ship as a multi-polygon geometric dart."""
        if self.is_invulnerable:
            if int(self.invulnerable_timer * INVULNERABLE_BLINK_RATE * 2) % 2 == 0:
                return

        cx, cy = self.x, self.y

        # Engine exhaust glow (smooth red-to-orange gradient, outer to inner)
        for ox, w, h, r, g, b, a in EXHAUST_LAYERS:
            arcade.draw_ellipse_filled(cx + ox, cy, w, h, (r, g, b, a))

        # Engine block (small rect at rear)
        arcade.draw_lbwh_rectangle_filled(cx - 33, cy - 10, 6, 20, SHIP_ACCENT_COLOR)
        arcade.draw_lbwh_rectangle_outline(cx - 33, cy - 10, 6, 20, SHIP_OUTLINE_COLOR)

        # Engine nozzle lines (3 short lines extending left)
        for offset in (-6, 0, 6):
            arcade.draw_line(
                cx - 33, cy + offset, cx - 38, cy + offset, SHIP_OUTLINE_COLOR
            )

        # Main body
        body = [
            (cx + 40, cy),
            (cx - 10, cy - 14),
            (cx - 30, cy - 16),
            (cx - 30, cy + 16),
            (cx - 10, cy + 14),
        ]
        arcade.draw_polygon_filled(body, SHIP_BODY_COLOR)
        arcade.draw_polygon_outline(body, SHIP_OUTLINE_COLOR)

        # Top wing fin
        top_fin = [(cx - 5, cy - 14), (cx - 30, cy - 28), (cx - 30, cy - 16)]
        arcade.draw_polygon_filled(top_fin, SHIP_DARK_COLOR)
        arcade.draw_polygon_outline(top_fin, SHIP_OUTLINE_COLOR)

        # Bottom wing fin
        bot_fin = [(cx - 5, cy + 14), (cx - 30, cy + 28), (cx - 30, cy + 16)]
        arcade.draw_polygon_filled(bot_fin, SHIP_DARK_COLOR)
        arcade.draw_polygon_outline(bot_fin, SHIP_OUTLINE_COLOR)

        # Center stripe (faint horizontal line along fuselage)
        arcade.draw_line(cx + 38, cy, cx - 30, cy, (*SHIP_OUTLINE_COLOR[:3], 102))

        # Cockpit accent
        cockpit = [(cx + 40, cy), (cx + 10, cy - 5), (cx + 10, cy + 5)]
        arcade.draw_polygon_filled(cockpit, SHIP_COCKPIT_COLOR)
        arcade.draw_polygon_outline(cockpit, SHIP_OUTLINE_COLOR)

    def can_shoot(self) -> bool:
        """Return True if shoot cooldown has elapsed."""
        return self.shoot_timer <= 0.0

    def reset_shoot_timer(self) -> None:
        """Reset the shoot cooldown based on fire rate tier."""
        self.shoot_timer = FIRE_RATE_LEVELS[self.fire_rate_level - 1]

    def downgrade_on_death(self) -> None:
        """Drop both tier levels by 1 on death (min 1)."""
        self.speed_level = max(1, self.speed_level - 1)
        self.fire_rate_level = max(1, self.fire_rate_level - 1)
