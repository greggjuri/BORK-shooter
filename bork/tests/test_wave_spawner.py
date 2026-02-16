"""Tests for the wave spawner."""

from bork.constants import (
    ENEMIES_PER_WAVE,
    ENEMY_SPAWN_SPACING,
    SCREEN_HEIGHT,
    WAVE_BOTTOM_Y,
    WAVE_CENTER_Y,
    WAVE_PAUSE,
    WAVE_START_DELAY,
    WAVE_TOP_Y,
)
from bork.wave_spawner import WaveSpawner

DT = 1 / 60


def _tick(spawner: WaveSpawner, seconds: float) -> list:
    """Advance spawner by the given duration, collecting spawned enemies."""
    enemies = []
    frames = int(seconds * 60)
    for _ in range(frames):
        result = spawner.update(DT)
        if result is not None:
            enemies.append(result)
    return enemies


def test_no_spawn_during_initial_delay() -> None:
    s = WaveSpawner()
    enemies = _tick(s, WAVE_START_DELAY - 0.1)
    assert len(enemies) == 0


def test_first_spawn_after_delay() -> None:
    s = WaveSpawner()
    enemies = _tick(s, WAVE_START_DELAY + 0.1)
    assert len(enemies) >= 1


def test_wave_spawns_correct_count() -> None:
    s = WaveSpawner()
    # Skip initial delay + enough time for all 5 enemies
    total_time = WAVE_START_DELAY + ENEMIES_PER_WAVE * ENEMY_SPAWN_SPACING + 0.5
    enemies = _tick(s, total_time)
    assert len(enemies) == ENEMIES_PER_WAVE


def test_wave_pause_between_waves() -> None:
    s = WaveSpawner()
    # Tick until wave 1 is complete (all 5 enemies spawned)
    collected: list = []
    for _ in range(600):  # max 10 seconds
        result = s.update(DT)
        if result is not None:
            collected.append(result)
        if len(collected) == ENEMIES_PER_WAVE:
            break
    assert len(collected) == ENEMIES_PER_WAVE
    assert not s.wave_active

    # During the first second of the pause, no spawns should happen
    enemies_during_pause = _tick(s, 1.0)
    assert len(enemies_during_pause) == 0


def test_waves_loop_after_three() -> None:
    s = WaveSpawner()
    # Run through all 3 waves + pauses + start of wave 4
    single_wave_time = ENEMIES_PER_WAVE * ENEMY_SPAWN_SPACING + 0.1
    total_time = (
        WAVE_START_DELAY
        + single_wave_time
        + WAVE_PAUSE
        + single_wave_time
        + WAVE_PAUSE
        + single_wave_time
        + WAVE_PAUSE
        + 0.1
    )
    _tick(s, total_time)
    # After 3 waves, wave_index should be back to 0
    assert s.wave_index == 0


def test_wave_y_positions() -> None:
    s = WaveSpawner()
    # Wave 0: top
    _tick(s, WAVE_START_DELAY + 0.01)
    e0 = s._spawn_enemy()
    assert abs(e0.y - SCREEN_HEIGHT * WAVE_TOP_Y) < 1

    # Advance to wave 1
    s.wave_index = 1
    e1 = s._spawn_enemy()
    assert abs(e1.y - SCREEN_HEIGHT * WAVE_BOTTOM_Y) < 1

    # Wave 2
    s.wave_index = 2
    e2 = s._spawn_enemy()
    assert abs(e2.y - SCREEN_HEIGHT * WAVE_CENTER_Y) < 1


def test_wave_2_uses_sine_pattern() -> None:
    s = WaveSpawner()
    s.wave_index = 2
    e = s._spawn_enemy()
    assert e.pattern == "sine"


def test_reset() -> None:
    s = WaveSpawner()
    # Advance past initial state
    _tick(s, WAVE_START_DELAY + 1.0)
    s.reset()
    assert s.wave_index == 0
    assert s.timer == WAVE_START_DELAY
    assert s.spawned_in_wave == 0
    assert s.wave_active is False
