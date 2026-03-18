"""Tests for the Zone 2 Dart enemy."""

from bork.constants import (
    ENEMY_DART_SHOOT_COOLDOWN,
    ENEMY_DART_SIZE,
    SCREEN_WIDTH,
    ZONE_CONFIGS,
)
from bork.dart import Dart
from bork.wave_spawner import WaveSpawner

DT = 1 / 60


def test_dart_initial_position() -> None:
    d = Dart(500, 200, "straight", 200, 180.0)
    assert d.x == 500
    assert d.y == 200


def test_dart_moves_leftward() -> None:
    d = Dart(500, 200, "straight", 200, 180.0)
    old_x = d.x
    d.update(DT)
    assert d.x < old_x


def test_dart_off_screen() -> None:
    d = Dart(-ENEMY_DART_SIZE - 1, 200, "straight", 200, 180.0)
    assert d.is_off_screen()


def test_dart_not_off_screen_when_visible() -> None:
    d = Dart(SCREEN_WIDTH / 2, 200, "straight", 200, 180.0)
    assert not d.is_off_screen()


def test_dart_non_shooter_no_fire() -> None:
    d = Dart(500, 200, "straight", 200, 180.0, is_shooter=False)
    for _ in range(300):
        result = d.update(DT, 100, 200)
        assert result is None


def test_dart_shooter_fires_after_cooldown() -> None:
    d = Dart(500, 200, "straight", 200, 180.0, is_shooter=True)
    fired = None
    frames = int(ENEMY_DART_SHOOT_COOLDOWN * 60) + 10
    for _ in range(frames):
        result = d.update(DT, 100, 200)
        if result is not None:
            fired = result
            break
    assert fired is not None
    # Projectile should move toward player (leftward)
    assert fired.vx < 0


def test_dart_sine_pattern_oscillates() -> None:
    d = Dart(500, 270, "sine", 270, 180.0)
    for _ in range(15):
        d.update(DT)
    assert d.y != d.base_y


def test_dart_diagonal_movement() -> None:
    d = Dart(500, 200, "diagonal_cross", 200, 180.0, vy=-50.0)
    d.update(DT)
    assert d.y < 200


def test_zone2_spawns_darts() -> None:
    config = ZONE_CONFIGS[2]
    spawner = WaveSpawner(config)
    # Tick past initial delay to get first spawn
    enemies = []
    for _ in range(600):
        result = spawner.update(DT)
        if result is not None:
            enemies.append(result)
            break
    assert len(enemies) == 1
    assert isinstance(enemies[0], Dart)
