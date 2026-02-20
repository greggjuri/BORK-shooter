"""Tests for the scoring system."""

from bork.constants import (
    COMBO_WINDOW,
    MULTIPLIER_DECAY_DELAY,
    MULTIPLIER_INCREMENT,
    MULTIPLIER_MAX,
    POINTS_BASIC_ENEMY,
)
from bork.scoring import ScoringSystem


def test_initial_state() -> None:
    s = ScoringSystem()
    assert s.score == 0
    assert s.multiplier == 1.0
    assert s.combo == 0


def test_register_kill_adds_score() -> None:
    s = ScoringSystem()
    s.register_kill(POINTS_BASIC_ENEMY)
    assert s.score == POINTS_BASIC_ENEMY


def test_register_kill_returns_points() -> None:
    s = ScoringSystem()
    points = s.register_kill(POINTS_BASIC_ENEMY)
    assert points == POINTS_BASIC_ENEMY


def test_multiplier_increases_on_rapid_kills() -> None:
    s = ScoringSystem()
    s.register_kill(POINTS_BASIC_ENEMY)
    # Small time gap within combo window
    s.update(0.5)
    s.register_kill(POINTS_BASIC_ENEMY)
    assert abs(s.multiplier - (1.0 + MULTIPLIER_INCREMENT)) < 0.001


def test_multiplier_caps_at_max() -> None:
    s = ScoringSystem()
    # Kill many times rapidly to push multiplier past max
    for _ in range(100):
        s.register_kill(POINTS_BASIC_ENEMY)
    assert s.multiplier <= MULTIPLIER_MAX
    assert abs(s.multiplier - MULTIPLIER_MAX) < 0.001


def test_multiplier_decays_after_delay() -> None:
    s = ScoringSystem()
    s.register_kill(POINTS_BASIC_ENEMY)
    s.register_kill(POINTS_BASIC_ENEMY)
    assert s.multiplier > 1.0
    # Wait past decay delay
    s.update(MULTIPLIER_DECAY_DELAY + 0.1)
    assert s.multiplier == 1.0


def test_combo_increments_within_window() -> None:
    s = ScoringSystem()
    s.register_kill(POINTS_BASIC_ENEMY)
    s.update(0.5)
    s.register_kill(POINTS_BASIC_ENEMY)
    s.update(0.5)
    s.register_kill(POINTS_BASIC_ENEMY)
    assert s.combo == 3


def test_combo_resets_after_window() -> None:
    s = ScoringSystem()
    s.register_kill(POINTS_BASIC_ENEMY)
    s.update(0.5)
    s.register_kill(POINTS_BASIC_ENEMY)
    assert s.combo == 2
    # Wait past combo window
    s.update(COMBO_WINDOW + 0.1)
    s.register_kill(POINTS_BASIC_ENEMY)
    assert s.combo == 1


def test_score_uses_multiplier() -> None:
    s = ScoringSystem()
    s.register_kill(POINTS_BASIC_ENEMY)  # 100 at 1.0x
    s.register_kill(POINTS_BASIC_ENEMY)  # 100 at 1.1x = 110
    expected = POINTS_BASIC_ENEMY + int(
        POINTS_BASIC_ENEMY * (1.0 + MULTIPLIER_INCREMENT)
    )
    assert s.score == expected


def test_reset_clears_state() -> None:
    s = ScoringSystem()
    s.register_kill(POINTS_BASIC_ENEMY)
    s.register_kill(POINTS_BASIC_ENEMY)
    s.reset()
    assert s.score == 0
    assert s.multiplier == 1.0
    assert s.combo == 0
    assert s.has_killed is False
