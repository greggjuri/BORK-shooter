"""Factory functions for creating particle burst effects."""

import math
import random

from bork.constants import (
    BOSS_EXPLOSION_LIFETIME,
    BOSS_EXPLOSION_PARTICLE_COUNT,
    BOSS_EXPLOSION_SPEED,
    BOSS_SUB_EXPLOSION_COUNT,
    BOSS_SUB_EXPLOSION_LIFETIME,
    BOSS_SUB_EXPLOSION_SPEED,
    COLOR_PLAYER,
    ENEMY_COLOR,
    ENEMY_EXPLOSION_COLOR_END,
    ENEMY_EXPLOSION_COUNT,
    ENEMY_EXPLOSION_LIFETIME,
    ENEMY_EXPLOSION_SPEED,
    PLAYER_EXPLOSION_COLOR_END,
    PLAYER_EXPLOSION_COUNT,
    PLAYER_EXPLOSION_LIFETIME,
    PLAYER_EXPLOSION_SPEED,
    POWERUP_BURST_COLOR_END,
    POWERUP_BURST_COUNT,
    POWERUP_BURST_LIFETIME,
    POWERUP_BURST_SPEED,
    SENTINEL_BODY_COLOR,
    SENTINEL_HULL_COLOR,
    SENTINEL_HULL_STROKE,
    SENTINEL_PLATE_COLOR,
)
from bork.particles import Particle


def _pick_size(small: tuple, medium: tuple, large: tuple) -> float:
    """Pick a particle size from three tiers: 60% small, 30% medium, 10% large."""
    r = random.random()
    if r < 0.6:
        return random.uniform(*small)
    elif r < 0.9:
        return random.uniform(*medium)
    return random.uniform(*large)


def create_enemy_explosion(x: float, y: float) -> list[Particle]:
    """Create a radial burst of particles for an enemy death."""
    count = random.randint(*ENEMY_EXPLOSION_COUNT)
    particles: list[Particle] = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*ENEMY_EXPLOSION_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(*ENEMY_EXPLOSION_LIFETIME)
        size_start = _pick_size((1, 2), (3, 5), (6, 8))
        particles.append(
            Particle(
                x, y, vx, vy,
                ENEMY_COLOR, ENEMY_EXPLOSION_COLOR_END,
                size_start, 0.0, lifetime, "circle",
            )
        )
    return particles


def create_player_explosion(x: float, y: float) -> list[Particle]:
    """Create a large dramatic burst for player death."""
    count = random.randint(*PLAYER_EXPLOSION_COUNT)
    particles: list[Particle] = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*PLAYER_EXPLOSION_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(*PLAYER_EXPLOSION_LIFETIME)
        size_start = _pick_size((1, 3), (4, 7), (8, 12))
        particles.append(
            Particle(
                x, y, vx, vy,
                COLOR_PLAYER, PLAYER_EXPLOSION_COLOR_END,
                size_start, 0.0, lifetime, "circle",
            )
        )
    return particles


def create_powerup_burst(
    x: float, y: float, color: tuple[int, int, int]
) -> list[Particle]:
    """Create a uniform ring burst for powerup collection."""
    count = random.randint(*POWERUP_BURST_COUNT)
    particles: list[Particle] = []
    for i in range(count):
        angle = (2 * math.pi * i) / count
        speed = random.uniform(*POWERUP_BURST_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(*POWERUP_BURST_LIFETIME)
        size_start = _pick_size((1, 2), (2, 4), (4, 6))
        particles.append(
            Particle(
                x, y, vx, vy,
                color, POWERUP_BURST_COLOR_END,
                size_start, size_start * 0.3, lifetime, "circle",
            )
        )
    return particles


# Boss explosion color palette — fire + hull debris
_BOSS_FIRE_COLORS = [
    (0, 200, 220),  # cyan
    (255, 150, 0),  # orange
    (255, 220, 80),  # yellow
    (255, 255, 255),  # white hot
    (255, 100, 20),  # deep orange
    (255, 60, 40),  # core red
]
_BOSS_DEBRIS_COLORS = [
    SENTINEL_HULL_COLOR,  # dark hull gray-blue
    SENTINEL_PLATE_COLOR,  # inner plate dark
    SENTINEL_HULL_STROKE[:3],  # light hull gray
    SENTINEL_BODY_COLOR,  # body gray
]
_BOSS_FADE_TARGETS = [
    (255, 200, 50),  # golden
    (255, 100, 0),  # deep orange
    (80, 80, 120),  # cold hull ash
]


def create_boss_explosion(x: float, y: float) -> list[Particle]:
    """Create a massive multi-layered detonation for boss death finale."""
    count = random.randint(*BOSS_EXPLOSION_PARTICLE_COUNT)
    particles: list[Particle] = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*BOSS_EXPLOSION_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(*BOSS_EXPLOSION_LIFETIME)
        size_start = _pick_size((1, 3), (4, 8), (9, 14))
        if random.random() < 0.6:
            color_start = random.choice(_BOSS_FIRE_COLORS)
        else:
            color_start = random.choice(_BOSS_DEBRIS_COLORS)
        fade_to = random.choice(_BOSS_FADE_TARGETS)
        particles.append(
            Particle(
                x, y, vx, vy,
                color_start, fade_to,
                size_start, 0.0, lifetime, "circle",
            )
        )
    return particles


def create_boss_small_explosion(x: float, y: float) -> list[Particle]:
    """Create a hefty sub-explosion for the staggered death sequence."""
    count = random.randint(*BOSS_SUB_EXPLOSION_COUNT)
    particles: list[Particle] = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*BOSS_SUB_EXPLOSION_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(*BOSS_SUB_EXPLOSION_LIFETIME)
        size_start = _pick_size((1, 2), (3, 6), (7, 10))
        if random.random() < 0.5:
            color_start = random.choice(_BOSS_FIRE_COLORS)
        else:
            color_start = random.choice(_BOSS_DEBRIS_COLORS)
        fade_to = random.choice(_BOSS_FADE_TARGETS)
        particles.append(
            Particle(
                x, y, vx, vy,
                color_start, fade_to,
                size_start, 0.0, lifetime, "circle",
            )
        )
    return particles
