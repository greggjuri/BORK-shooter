"""Floating score text that rises and fades from kill locations."""

import arcade

from bork.constants import (
    HUD_PRIMARY,
    SCORE_POPUP_DURATION,
    SCORE_POPUP_FONT_SIZE,
    SCORE_POPUP_RISE_SPEED,
)


class ScorePopup:
    """A single floating score text that rises and fades."""

    def __init__(self, x: float, y: float, points: int) -> None:
        self.x = x
        self.y = y
        self.points = points
        self.age = 0.0

    @property
    def is_done(self) -> bool:
        """Return True when popup has fully faded."""
        return self.age >= SCORE_POPUP_DURATION

    @property
    def alpha(self) -> int:
        """Current alpha value, fading from 255 to 0."""
        t = min(self.age / SCORE_POPUP_DURATION, 1.0)
        return int(255 * (1.0 - t))

    def update(self, dt: float) -> None:
        """Rise upward and age."""
        self.y += SCORE_POPUP_RISE_SPEED * dt
        self.age += dt

    def draw(self) -> None:
        """Draw the floating score text."""
        if self.is_done:
            return
        color = (*HUD_PRIMARY[:3], self.alpha)
        text = f"+{self.points:,}"
        arcade.draw_text(
            text,
            self.x,
            self.y,
            color,
            font_size=SCORE_POPUP_FONT_SIZE,
            anchor_x="center",
            anchor_y="center",
        )


class ScorePopupManager:
    """Manages multiple floating score popups."""

    def __init__(self) -> None:
        self.popups: list[ScorePopup] = []

    def spawn(self, x: float, y: float, points: int) -> None:
        """Create a new score popup at the given position."""
        self.popups.append(ScorePopup(x, y, points))

    def update(self, dt: float) -> None:
        """Update all popups and remove finished ones."""
        for p in self.popups:
            p.update(dt)
        self.popups = [p for p in self.popups if not p.is_done]

    def draw(self) -> None:
        """Draw all active popups."""
        for p in self.popups:
            p.draw()
