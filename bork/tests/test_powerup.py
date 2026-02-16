"""Tests for the powerup entity."""

from bork.constants import POWERUP_SIZE, SCREEN_WIDTH
from bork.powerup import Powerup

DT = 1 / 60


def test_powerup_moves_left() -> None:
    p = Powerup(SCREEN_WIDTH, 200, "speed")
    old_x = p.x
    p.update(DT)
    assert p.x < old_x


def test_powerup_off_screen_left() -> None:
    p = Powerup(-POWERUP_SIZE - 1, 200, "speed")
    assert p.is_off_screen()


def test_powerup_not_off_screen_when_visible() -> None:
    p = Powerup(SCREEN_WIDTH / 2, 200, "speed")
    assert not p.is_off_screen()


def test_powerup_pulse_changes_over_time() -> None:
    p = Powerup(400, 200, "speed")
    assert p.time_alive == 0.0
    p.update(DT)
    assert p.time_alive > 0.0


def test_powerup_kind_stored() -> None:
    p = Powerup(400, 200, "speed")
    assert p.kind == "speed"
