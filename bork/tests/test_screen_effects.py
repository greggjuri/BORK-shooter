"""Tests for screen effects."""

from bork.screen_effects import ScreenFlash, ScreenShake


def test_screen_flash_not_done_initially() -> None:
    f = ScreenFlash((255, 255, 255), duration=0.1, fade=0.2)
    assert f.is_done is False


def test_screen_flash_done_after_duration_plus_fade() -> None:
    f = ScreenFlash((255, 255, 255), duration=0.1, fade=0.2)
    # Advance past total time (0.1 + 0.2 = 0.3)
    f.update(0.35)
    assert f.is_done is True


def test_screen_shake_not_done_initially() -> None:
    s = ScreenShake(intensity=6.0, duration=0.3)
    assert s.is_done is False


def test_screen_shake_done_after_duration() -> None:
    s = ScreenShake(intensity=6.0, duration=0.3)
    s.update(0.35)
    assert s.is_done is True


def test_screen_shake_offset_zero_when_done() -> None:
    s = ScreenShake(intensity=6.0, duration=0.3)
    s.update(0.5)
    ox, oy = s.get_offset()
    assert ox == 0.0
    assert oy == 0.0


def test_screen_shake_offset_within_intensity() -> None:
    s = ScreenShake(intensity=10.0, duration=1.0)
    # Sample many offsets to check bounds
    for _ in range(100):
        s.timer = 0.0  # reset to keep active
        ox, oy = s.get_offset()
        assert -10.0 <= ox <= 10.0
        assert -10.0 <= oy <= 10.0
