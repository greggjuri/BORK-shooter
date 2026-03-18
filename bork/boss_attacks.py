"""Boss attack pattern factory functions."""

import math

from bork.enemy_projectile import EnemyProjectile


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
