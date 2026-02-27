"""Factory functions for creating particle burst effects."""

import math
import random

from bork.constants import (
    BOSS_EXPLOSION_LIFETIME,
    BOSS_EXPLOSION_PARTICLE_COUNT,
    BOSS_EXPLOSION_SIZE,
    BOSS_EXPLOSION_SPEED,
    COLOR_PLAYER,
    ENEMY_COLOR,
    ENEMY_EXPLOSION_COLOR_END,
    ENEMY_EXPLOSION_COUNT,
    ENEMY_EXPLOSION_LIFETIME,
    ENEMY_EXPLOSION_SIZE,
    ENEMY_EXPLOSION_SPEED,
    PLAYER_EXPLOSION_COLOR_END,
    PLAYER_EXPLOSION_COUNT,
    PLAYER_EXPLOSION_LIFETIME,
    PLAYER_EXPLOSION_SIZE,
    PLAYER_EXPLOSION_SPEED,
    POWERUP_BURST_COLOR_END,
    POWERUP_BURST_COUNT,
    POWERUP_BURST_LIFETIME,
    POWERUP_BURST_SIZE,
    POWERUP_BURST_SPEED,
    SENTINEL_BODY_COLOR,
    SENTINEL_CORE_COLOR,
)
from bork.particles import Particle


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
        size_start = random.uniform(*ENEMY_EXPLOSION_SIZE)
        shape = random.choice(["square", "triangle"])
        particles.append(
            Particle(
                x,
                y,
                vx,
                vy,
                ENEMY_COLOR,
                ENEMY_EXPLOSION_COLOR_END,
                size_start,
                1.0,
                lifetime,
                shape,
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
        size_start = random.uniform(*PLAYER_EXPLOSION_SIZE)
        particles.append(
            Particle(
                x,
                y,
                vx,
                vy,
                COLOR_PLAYER,
                PLAYER_EXPLOSION_COLOR_END,
                size_start,
                0.0,
                lifetime,
                "triangle",
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
        size_start = random.uniform(*POWERUP_BURST_SIZE)
        particles.append(
            Particle(
                x,
                y,
                vx,
                vy,
                color,
                POWERUP_BURST_COLOR_END,
                size_start,
                size_start * 0.5,
                lifetime,
                "circle",
            )
        )
    return particles


# Boss explosion color palette
_BOSS_COLORS = [
    (0, 200, 220),  # cyan
    (255, 150, 0),  # orange
    (255, 220, 80),  # yellow
    (255, 255, 255),  # white
]


def create_boss_explosion(x: float, y: float) -> list[Particle]:
    """Create a large dramatic burst for boss death."""
    count = random.randint(*BOSS_EXPLOSION_PARTICLE_COUNT)
    particles: list[Particle] = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*BOSS_EXPLOSION_SPEED)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(*BOSS_EXPLOSION_LIFETIME)
        size_start = random.uniform(*BOSS_EXPLOSION_SIZE)
        color_start = random.choice(_BOSS_COLORS)
        shape = random.choice(["square", "triangle", "circle"])
        particles.append(
            Particle(
                x,
                y,
                vx,
                vy,
                color_start,
                (255, 200, 50),
                size_start,
                0.0,
                lifetime,
                shape,
            )
        )
    return particles


def create_boss_small_explosion(x: float, y: float) -> list[Particle]:
    """Create a small pop for the boss dying sequence."""
    count = random.randint(8, 15)
    particles: list[Particle] = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(80, 200)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(0.2, 0.5)
        size_start = random.uniform(3, 7)
        color_start = random.choice([SENTINEL_CORE_COLOR, SENTINEL_BODY_COLOR])
        particles.append(
            Particle(
                x,
                y,
                vx,
                vy,
                color_start,
                (255, 150, 0),
                size_start,
                0.0,
                lifetime,
                random.choice(["square", "triangle"]),
            )
        )
    return particles
