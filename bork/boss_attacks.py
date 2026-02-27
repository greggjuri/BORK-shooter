"""Enemy projectiles and boss attack pattern factory functions."""

import math

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


def create_spread_shot(
    x: float,
    y: float,
    target_x: float,
    target_y: float,
    count: int,
    speed: float,
    color: tuple[int, ...],
) -> list[EnemyProjectile]:
    """Create a fan of bullets aimed toward a target."""
    projectiles: list[EnemyProjectile] = []
    base_angle = math.atan2(target_y - y, target_x - x)
    # Spread angle: 15 degrees between bullets
    spread_step = math.radians(15)
    start_angle = base_angle - spread_step * (count - 1) / 2

    for i in range(count):
        angle = start_angle + spread_step * i
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        projectiles.append(EnemyProjectile(x, y, vx, vy, color, size=5.0))
    return projectiles


def create_aimed_shot(
    x: float,
    y: float,
    target_x: float,
    target_y: float,
    speed: float,
    color: tuple[int, ...],
    size: float = 7.0,
) -> list[EnemyProjectile]:
    """Create a single fast bullet aimed at the target's current position."""
    dx = target_x - x
    dy = target_y - y
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1.0:
        dist = 1.0
    vx = (dx / dist) * speed
    vy = (dy / dist) * speed
    return [EnemyProjectile(x, y, vx, vy, color, size=size, shape="circle")]


def create_radial_burst(
    x: float,
    y: float,
    count: int,
    speed: float,
    color: tuple[int, ...],
    arc_degrees: float = 180.0,
) -> list[EnemyProjectile]:
    """Create a radial burst of bullets in a leftward-facing arc."""
    projectiles: list[EnemyProjectile] = []
    # Center the arc facing left (pi radians)
    center_angle = math.pi
    arc_rad = math.radians(arc_degrees)
    start_angle = center_angle - arc_rad / 2

    for i in range(count):
        angle = start_angle + (arc_rad / (count - 1)) * i if count > 1 else center_angle
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        projectiles.append(EnemyProjectile(x, y, vx, vy, color, size=5.0))
    return projectiles
