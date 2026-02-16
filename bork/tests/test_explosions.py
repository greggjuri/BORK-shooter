"""Tests for explosion factory functions."""

from bork.constants import (
    ENEMY_EXPLOSION_COUNT,
    PLAYER_EXPLOSION_COUNT,
    POWERUP_BURST_COUNT,
)
from bork.explosions import (
    create_enemy_explosion,
    create_player_explosion,
    create_powerup_burst,
)


def test_enemy_explosion_count_in_range() -> None:
    particles = create_enemy_explosion(100, 200)
    assert ENEMY_EXPLOSION_COUNT[0] <= len(particles) <= ENEMY_EXPLOSION_COUNT[1]


def test_enemy_explosion_position() -> None:
    particles = create_enemy_explosion(50, 75)
    for p in particles:
        assert p.x == 50
        assert p.y == 75


def test_enemy_explosion_shapes() -> None:
    particles = create_enemy_explosion(100, 200)
    for p in particles:
        assert p.shape in ("square", "triangle")


def test_player_explosion_count_in_range() -> None:
    particles = create_player_explosion(100, 200)
    assert PLAYER_EXPLOSION_COUNT[0] <= len(particles) <= PLAYER_EXPLOSION_COUNT[1]


def test_player_explosion_all_triangles() -> None:
    particles = create_player_explosion(100, 200)
    for p in particles:
        assert p.shape == "triangle"


def test_powerup_burst_count_in_range() -> None:
    particles = create_powerup_burst(100, 200, (255, 220, 0))
    assert POWERUP_BURST_COUNT[0] <= len(particles) <= POWERUP_BURST_COUNT[1]


def test_powerup_burst_all_circles() -> None:
    particles = create_powerup_burst(100, 200, (255, 220, 0))
    for p in particles:
        assert p.shape == "circle"


def test_powerup_burst_uses_provided_color() -> None:
    color = (100, 200, 50)
    particles = create_powerup_burst(100, 200, color)
    for p in particles:
        assert p.color_start == color
