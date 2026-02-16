"""Screen-level visual effects: flash overlay and camera shake."""

import random

import arcade

from bork.constants import SCREEN_HEIGHT, SCREEN_WIDTH


class ScreenFlash:
    """A full-screen color flash that fades out."""

    def __init__(
        self, color: tuple[int, int, int], duration: float, fade: float
    ) -> None:
        self.color = color
        self.duration = duration  # full-brightness phase
        self.fade = fade  # fade-out phase
        self.timer = 0.0

    @property
    def is_done(self) -> bool:
        """Return True when flash is fully faded."""
        return self.timer >= self.duration + self.fade

    def update(self, dt: float) -> None:
        """Advance the flash timer."""
        self.timer += dt

    def draw(self) -> None:
        """Draw the flash overlay."""
        if self.is_done:
            return
        if self.timer < self.duration:
            alpha = 180  # strong but not fully opaque
        else:
            fade_progress = (self.timer - self.duration) / self.fade
            alpha = int(180 * (1.0 - fade_progress))
        color = (*self.color, max(0, alpha))
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, color)


class ScreenShake:
    """Decaying random screen offset."""

    def __init__(self, intensity: float, duration: float) -> None:
        self.intensity = intensity
        self.duration = duration
        self.timer = 0.0

    @property
    def is_done(self) -> bool:
        """Return True when shake has fully decayed."""
        return self.timer >= self.duration

    def update(self, dt: float) -> None:
        """Advance the shake timer."""
        self.timer += dt

    def get_offset(self) -> tuple[float, float]:
        """Return current (x, y) shake offset."""
        if self.is_done:
            return (0.0, 0.0)
        decay = 1.0 - (self.timer / self.duration)
        current = self.intensity * decay
        ox = random.uniform(-current, current)
        oy = random.uniform(-current, current)
        return (ox, oy)
