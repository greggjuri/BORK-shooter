"""Tests for the HUD state logic."""

from bork.constants import COMBO_MILESTONE_DURATION
from bork.hud import HUD

DT = 1 / 60


def test_hud_initial_state() -> None:
    hud = HUD()
    assert hud.milestone_timer == 0.0
    assert hud.milestone_text == ""
    assert hud.multi_pulse_timer == 0.0


def test_trigger_milestone_sets_text_and_timer() -> None:
    hud = HUD()
    hud.trigger_milestone("NICE!")
    assert hud.milestone_text == "NICE!"
    assert hud.milestone_timer == COMBO_MILESTONE_DURATION


def test_milestone_timer_decrements() -> None:
    hud = HUD()
    hud.trigger_milestone("NICE!")
    hud.update(0.1)
    assert hud.milestone_timer < COMBO_MILESTONE_DURATION


def test_milestone_timer_stops_at_zero() -> None:
    hud = HUD()
    hud.trigger_milestone("NICE!")
    # Tick well past duration
    hud.update(COMBO_MILESTONE_DURATION + 1.0)
    assert hud.milestone_timer == 0.0
