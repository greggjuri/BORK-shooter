"""Scoring system with multiplier and combo tracking."""

from bork.constants import (
    COMBO_WINDOW,
    MULTIPLIER_DECAY_DELAY,
    MULTIPLIER_INCREMENT,
    MULTIPLIER_MAX,
)


class ScoringSystem:
    """Tracks score, multiplier, and combo state."""

    def __init__(self) -> None:
        self.score: int = 0
        self.multiplier: float = 1.0
        self.combo: int = 0
        self.time_since_kill: float = 0.0
        self.has_killed: bool = False

    def register_kill(self, base_points: int) -> int:
        """Register a kill, update multiplier/combo, return points earned."""
        if self.has_killed and self.time_since_kill <= COMBO_WINDOW:
            self.multiplier = min(
                self.multiplier + MULTIPLIER_INCREMENT, MULTIPLIER_MAX
            )
            self.combo += 1
        else:
            self.combo = 1
            self.multiplier = 1.0

        self.has_killed = True
        self.time_since_kill = 0.0
        points = int(base_points * self.multiplier)
        self.score += points
        return points

    def update(self, dt: float) -> None:
        """Decay multiplier if no kills recently."""
        if not self.has_killed:
            return
        self.time_since_kill += dt
        if self.time_since_kill > MULTIPLIER_DECAY_DELAY:
            self.multiplier = 1.0
            self.combo = 0

    def reset(self) -> None:
        """Reset all scoring state."""
        self.score = 0
        self.multiplier = 1.0
        self.combo = 0
        self.time_since_kill = 0.0
        self.has_killed = False
