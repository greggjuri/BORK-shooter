"""Tests for the player ship."""

import arcade

from bork.constants import (
    FIRE_RATE_LEVELS,
    PLAYER_MAX_SPEED,
    PLAYER_SHIP_SIZE,
    PLAYER_START_X,
    PLAYER_START_Y,
    RESPAWN_INVULNERABLE_TIME,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHOOT_COOLDOWN,
    SPEED_LEVELS,
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


def test_player_stops_without_input() -> None:
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    p.update(DT, {arcade.key.RIGHT})
    assert p.vx > 0
    p.update(DT, set())
    assert p.vx == 0.0
    assert p.vy == 0.0


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


def test_player_moves_at_max_speed() -> None:
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    p.update(DT, {arcade.key.RIGHT})
    assert abs(p.vx - PLAYER_MAX_SPEED) < 0.01
    assert p.vy == 0.0


def test_player_shoot_cooldown() -> None:
    p = Player(100, 100)
    assert p.can_shoot()
    p.reset_shoot_timer()
    assert not p.can_shoot()
    assert p.shoot_timer == FIRE_RATE_LEVELS[0]
    # Simulate enough time passing
    p.shoot_timer = 0.0
    assert p.can_shoot()


def test_player_diagonal_movement() -> None:
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    keys = {arcade.key.RIGHT, arcade.key.UP}
    p.update(DT, keys)
    assert p.vx > 0
    assert p.vy > 0


def test_player_speed_level_default() -> None:
    p = Player(100, 100)
    assert p.speed_level == 1
    assert p.fire_rate_level == 1


def test_player_speed_level_increases_max_speed() -> None:
    p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    p.speed_level = 2
    p.update(DT, {arcade.key.RIGHT})
    assert abs(p.vx - SPEED_LEVELS[1]) < 0.01
    assert p.vx > SPEED_LEVELS[0]


def test_player_max_speed_at_each_tier() -> None:
    for level in (1, 2, 3):
        p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        p.speed_level = level
        p.update(DT, {arcade.key.RIGHT})
        assert abs(p.vx - SPEED_LEVELS[level - 1]) < 0.01


def test_player_shoot_cooldown_at_each_tier() -> None:
    for level in (1, 2, 3):
        p = Player(100, 100)
        p.fire_rate_level = level
        p.reset_shoot_timer()
        assert p.shoot_timer == FIRE_RATE_LEVELS[level - 1]


def test_downgrade_on_death_decrements_levels() -> None:
    p = Player(100, 100)
    p.speed_level = 3
    p.fire_rate_level = 2
    p.downgrade_on_death()
    assert p.speed_level == 2
    assert p.fire_rate_level == 1


def test_downgrade_on_death_floors_at_1() -> None:
    p = Player(100, 100)
    p.speed_level = 1
    p.fire_rate_level = 1
    p.downgrade_on_death()
    assert p.speed_level == 1
    assert p.fire_rate_level == 1


def test_constants_consistency() -> None:
    assert SPEED_LEVELS[0] == PLAYER_MAX_SPEED
    assert FIRE_RATE_LEVELS[0] == SHOOT_COOLDOWN


def test_player_not_invulnerable_initially() -> None:
    p = Player(100, 100)
    assert p.is_invulnerable is False


def test_player_invulnerable_when_timer_set() -> None:
    p = Player(100, 100)
    p.invulnerable_timer = RESPAWN_INVULNERABLE_TIME
    assert p.is_invulnerable is True


def test_invulnerable_timer_decrements() -> None:
    p = Player(100, 100)
    p.invulnerable_timer = 1.0
    p.update(DT, set())
    assert p.invulnerable_timer < 1.0


def test_invulnerable_ends_at_zero() -> None:
    p = Player(100, 100)
    p.invulnerable_timer = 0.05
    # Tick enough to expire
    for _ in range(10):
        p.update(DT, set())
    assert p.is_invulnerable is False
    assert p.invulnerable_timer == 0.0
