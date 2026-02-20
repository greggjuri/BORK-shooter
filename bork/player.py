"""Player ship with momentum-based 8-directional movement."""

import math

import arcade

from bork.constants import (
    COLOR_PLAYER,
    INVULNERABLE_BLINK_RATE,
    PLAYER_ACCELERATION,
    PLAYER_FRICTION,
    PLAYER_MAX_SPEED,
    PLAYER_SHIP_SIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOOT_COOLDOWN,
    TARGET_FPS,
)


class Player:
    """Player ship with momentum-based 8-directional movement."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.shoot_timer = 0.0
        self.speed_multiplier = 1.0
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

        # Apply acceleration from input
        ax = 0.0
        ay = 0.0
        if arcade.key.RIGHT in keys_pressed or arcade.key.D in keys_pressed:
            ax += PLAYER_ACCELERATION
        if arcade.key.LEFT in keys_pressed or arcade.key.A in keys_pressed:
            ax -= PLAYER_ACCELERATION
        if arcade.key.UP in keys_pressed or arcade.key.W in keys_pressed:
            ay += PLAYER_ACCELERATION
        if arcade.key.DOWN in keys_pressed or arcade.key.S in keys_pressed:
            ay -= PLAYER_ACCELERATION

        # Normalize diagonal input so it doesn't exceed acceleration magnitude
        if ax != 0.0 and ay != 0.0:
            factor = 1.0 / math.sqrt(2.0)
            ax *= factor
            ay *= factor

        self.vx += ax * self.speed_multiplier * dt
        self.vy += ay * self.speed_multiplier * dt

        # Apply friction (frame-rate independent)
        friction = PLAYER_FRICTION ** (dt * TARGET_FPS)
        self.vx *= friction
        self.vy *= friction

        # Clamp to max speed (adjusted by powerup multiplier)
        max_speed = PLAYER_MAX_SPEED * self.speed_multiplier
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > max_speed:
            scale = max_speed / speed
            self.vx *= scale
            self.vy *= scale

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Clamp to screen bounds (accounting for ship size)
        self.x = max(PLAYER_SHIP_SIZE, min(SCREEN_WIDTH - PLAYER_SHIP_SIZE, self.x))
        self.y = max(PLAYER_SHIP_SIZE, min(SCREEN_HEIGHT - PLAYER_SHIP_SIZE, self.y))

    def draw(self) -> None:
        """Draw the ship as a right-pointing triangle."""
        if self.is_invulnerable:
            if int(self.invulnerable_timer * INVULNERABLE_BLINK_RATE * 2) % 2 == 0:
                return
        s = PLAYER_SHIP_SIZE
        arcade.draw_triangle_filled(
            self.x + s,
            self.y,  # nose (right)
            self.x - s,
            self.y + s * 0.7,  # top-left
            self.x - s,
            self.y - s * 0.7,  # bottom-left
            COLOR_PLAYER,
        )

    def can_shoot(self) -> bool:
        """Return True if shoot cooldown has elapsed."""
        return self.shoot_timer <= 0.0

    def reset_shoot_timer(self) -> None:
        """Reset the shoot cooldown timer."""
        self.shoot_timer = SHOOT_COOLDOWN
