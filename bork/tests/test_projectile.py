"""Tests for the projectile system."""

from bork.constants import PROJECTILE_LENGTH, SCREEN_WIDTH
from bork.projectile import Projectile

DT = 1 / 60


def test_projectile_initial_position() -> None:
    p = Projectile(100, 200)
    assert p.x == 100
    assert p.y == 200


def test_projectile_moves_right() -> None:
    p = Projectile(100, 200)
    old_x = p.x
    p.update(DT)
    assert p.x > old_x


def test_projectile_off_screen_detection() -> None:
    p = Projectile(SCREEN_WIDTH + PROJECTILE_LENGTH + 1, 200)
    assert p.is_off_screen()


def test_projectile_not_off_screen_when_visible() -> None:
    p = Projectile(SCREEN_WIDTH / 2, 200)
    assert not p.is_off_screen()
