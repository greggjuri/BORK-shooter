"""Zone 2 Dart enemy — small, fast, green arrow that may shoot."""

import math

import arcade

from bork.constants import (
    ENEMY_DART_ACCENT_COLOR,
    ENEMY_DART_BODY_COLOR,
    ENEMY_DART_PROJECTILE_COLOR,
    ENEMY_DART_PROJECTILE_SPEED,
    ENEMY_DART_SCANNER_COLOR,
    ENEMY_DART_SHOOT_COOLDOWN,
    ENEMY_DART_SIZE,
    SINE_AMPLITUDE,
    SINE_FREQUENCY,
)
from bork.enemy_projectile import EnemyProjectile

# Dart arrow geometry (facing left, smaller than bat wing)
_DART_BODY = ((-8, 0), (6, -5), (6, 5))
_DART_FIN_TOP = ((2, -5), (6, -8), (6, -4))
_DART_FIN_BOT = ((2, 5), (6, 8), (6, 4))


class Dart:
    """Zone 2 fast enemy — small green arrow that may shoot aimed projectiles."""

    def __init__(
        self,
        x: float,
        y: float,
        pattern: str,
        base_y: float,
        speed: float,
        vy: float = 0.0,
        is_shooter: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.pattern = pattern
        self.base_y = base_y
        self.speed = speed
        self.vy = vy
        self.is_shooter = is_shooter
        self.shoot_timer: float = ENEMY_DART_SHOOT_COOLDOWN
        self.time_alive = 0.0

    def update(
        self, dt: float, player_x: float = 0.0, player_y: float = 0.0
    ) -> EnemyProjectile | None:
        """Move and optionally fire at the player. Returns projectile or None."""
        self.x -= self.speed * dt
        self.time_alive += dt

        if self.pattern == "sine":
            self.y = self.base_y + SINE_AMPLITUDE * math.sin(
                SINE_FREQUENCY * self.time_alive * 2 * math.pi
            )
        elif self.vy != 0.0:
            self.y += self.vy * dt

        # Shooting logic
        if self.is_shooter:
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.shoot_timer = ENEMY_DART_SHOOT_COOLDOWN
                return self._fire_at(player_x, player_y)
        return None

    def _fire_at(self, px: float, py: float) -> EnemyProjectile:
        """Create an aimed projectile toward the player."""
        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1.0:
            dist = 1.0
        vx = (dx / dist) * ENEMY_DART_PROJECTILE_SPEED
        vy = (dy / dist) * ENEMY_DART_PROJECTILE_SPEED
        return EnemyProjectile(
            self.x, self.y, vx, vy, ENEMY_DART_PROJECTILE_COLOR, size=4.0, shape="circle"
        )

    def is_off_screen(self) -> bool:
        """Return True if past the left edge of the screen."""
        return self.x < -ENEMY_DART_SIZE

    def draw(self) -> None:
        """Draw as a small green arrow with scanner eye."""
        cx, cy = self.x, self.y

        # Main body triangle
        body = [(cx + ox, cy + oy) for ox, oy in _DART_BODY]
        arcade.draw_polygon_filled(body, ENEMY_DART_BODY_COLOR)
        arcade.draw_polygon_outline(body, ENEMY_DART_ACCENT_COLOR)

        # Top fin
        fin_t = [(cx + ox, cy + oy) for ox, oy in _DART_FIN_TOP]
        arcade.draw_polygon_filled(fin_t, ENEMY_DART_BODY_COLOR)
        arcade.draw_polygon_outline(fin_t, ENEMY_DART_ACCENT_COLOR)

        # Bottom fin
        fin_b = [(cx + ox, cy + oy) for ox, oy in _DART_FIN_BOT]
        arcade.draw_polygon_filled(fin_b, ENEMY_DART_BODY_COLOR)
        arcade.draw_polygon_outline(fin_b, ENEMY_DART_ACCENT_COLOR)

        # Scanner eye glow
        arcade.draw_circle_filled(cx, cy, 2.5, ENEMY_DART_SCANNER_COLOR)
