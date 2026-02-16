"""Tests for the enemy entity."""

from bork.constants import ENEMY_SIZE, SCREEN_WIDTH
from bork.enemy import Enemy

DT = 1 / 60


def test_enemy_moves_left() -> None:
    e = Enemy(SCREEN_WIDTH, 200, "straight", 200)
    old_x = e.x
    e.update(DT)
    assert e.x < old_x


def test_enemy_straight_pattern_constant_y() -> None:
    e = Enemy(SCREEN_WIDTH, 200, "straight", 200)
    for _ in range(60):
        e.update(DT)
    assert e.y == 200


def test_enemy_sine_pattern_oscillates() -> None:
    e = Enemy(SCREEN_WIDTH, 270, "sine", 270)
    # After some time, sine should push y away from base_y
    for _ in range(15):
        e.update(DT)
    assert e.y != e.base_y


def test_enemy_off_screen_left() -> None:
    e = Enemy(-ENEMY_SIZE - 1, 200, "straight", 200)
    assert e.is_off_screen()


def test_enemy_not_off_screen_when_visible() -> None:
    e = Enemy(SCREEN_WIDTH / 2, 200, "straight", 200)
    assert not e.is_off_screen()
