"""Tests for the player ship."""

import math

import arcade

from bork.constants import (
    PLAYER_MAX_SPEED,
    PLAYER_SHIP_SIZE,
    PLAYER_START_X,
    PLAYER_START_Y,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOOT_COOLDOWN,
    SPEED_BOOST_MULTIPLIER,
)
from bork.player import Player

DT = 1 / 60


def test_player_initial_position() -> None:
    p = Player(PLAYER_START_X, PLAYER_START_Y)
    assert p.x == PLAYER_START_X
    assert p.y == PLAYER_START_Y
    assert p.vx == 0.0
    assert p.vy == 0.0


def test_player_accelerates_right() -> None:
    p = Player(100, 100)
    keys = {arcade.key.RIGHT}
    p.update(DT, keys)
    assert p.vx > 0


def test_player_accelerates_left() -> None:
    p = Player(100, 100)
    keys = {arcade.key.LEFT}
    p.update(DT, keys)
    assert p.vx < 0


def test_player_accelerates_up() -> None:
    p = Player(100, 100)
    keys = {arcade.key.UP}
    p.update(DT, keys)
    assert p.vy > 0


def test_player_accelerates_with_wasd() -> None:
    p = Player(100, 100)
    keys = {arcade.key.D}
    p.update(DT, keys)
    assert p.vx > 0


def test_player_decelerates_without_input() -> None:
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    p.vx = 200.0
    p.vy = 100.0
    p.update(DT, set())
    assert abs(p.vx) < 200.0
    assert abs(p.vy) < 100.0


def test_player_clamped_to_screen_bounds() -> None:
    # Test right bound
    p = Player(SCREEN_WIDTH + 100, SCREEN_HEIGHT / 2)
    p.update(DT, set())
    assert p.x <= SCREEN_WIDTH - PLAYER_SHIP_SIZE

    # Test left bound
    p = Player(-100, SCREEN_HEIGHT / 2)
    p.update(DT, set())
    assert p.x >= PLAYER_SHIP_SIZE

    # Test top bound
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT + 100)
    p.update(DT, set())
    assert p.y <= SCREEN_HEIGHT - PLAYER_SHIP_SIZE

    # Test bottom bound
    p = Player(SCREEN_WIDTH / 2, -100)
    p.update(DT, set())
    assert p.y >= PLAYER_SHIP_SIZE


def test_player_max_speed_clamped() -> None:
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    p.vx = 9999.0
    p.vy = 9999.0
    p.update(DT, set())
    speed = math.sqrt(p.vx**2 + p.vy**2)
    assert speed <= PLAYER_MAX_SPEED + 0.01


def test_player_shoot_cooldown() -> None:
    p = Player(100, 100)
    assert p.can_shoot()
    p.reset_shoot_timer()
    assert not p.can_shoot()
    assert p.shoot_timer == SHOOT_COOLDOWN
    # Simulate enough time passing
    p.shoot_timer = 0.0
    assert p.can_shoot()


def test_player_diagonal_movement() -> None:
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    keys = {arcade.key.RIGHT, arcade.key.UP}
    p.update(DT, keys)
    assert p.vx > 0
    assert p.vy > 0


def test_player_speed_multiplier_default() -> None:
    p = Player(100, 100)
    assert p.speed_multiplier == 1.0


def test_player_speed_multiplier_increases_max_speed() -> None:
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    p.speed_multiplier = SPEED_BOOST_MULTIPLIER
    p.vx = 9999.0
    p.vy = 0.0
    p.update(DT, set())
    boosted_max = PLAYER_MAX_SPEED * SPEED_BOOST_MULTIPLIER
    assert abs(p.vx) <= boosted_max + 0.01
    assert abs(p.vx) > PLAYER_MAX_SPEED
