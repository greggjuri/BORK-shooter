"""Wave spawner that manages timed enemy waves."""

from bork.constants import (
    ENEMIES_PER_WAVE,
    ENEMY_SIZE,
    ENEMY_SPAWN_SPACING,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WAVE_BOTTOM_Y,
    WAVE_CENTER_Y,
    WAVE_PAUSE,
    WAVE_START_DELAY,
    WAVE_TOP_Y,
)
from bork.enemy import Enemy

# Wave definitions: (y_fraction, pattern)
WAVE_DEFS: list[tuple[float, str]] = [
    (WAVE_TOP_Y, "straight"),
    (WAVE_BOTTOM_Y, "straight"),
    (WAVE_CENTER_Y, "sine"),
]


class WaveSpawner:
    """Manages wave timing and enemy spawning."""

    def __init__(self) -> None:
        self.wave_index = 0
        self.timer = WAVE_START_DELAY
        self.spawned_in_wave = 0
        self.wave_active = False

    def update(self, dt: float) -> Enemy | None:
        """Tick the spawner. Returns a new Enemy if one should spawn."""
        self.timer -= dt

        if not self.wave_active:
            # Waiting for next wave
            if self.timer <= 0:
                self.wave_active = True
                self.timer = 0  # spawn immediately on activation
            return None

        # Wave is active — check if it's time to spawn
        if self.timer <= 0:
            enemy = self._spawn_enemy()
            self.spawned_in_wave += 1

            if self.spawned_in_wave >= ENEMIES_PER_WAVE:
                # Wave complete — pause before next
                self.wave_active = False
                self.spawned_in_wave = 0
                self.wave_index = (self.wave_index + 1) % len(WAVE_DEFS)
                self.timer = WAVE_PAUSE
            else:
                self.timer = ENEMY_SPAWN_SPACING

            return enemy

        return None

    def _spawn_enemy(self) -> Enemy:
        """Create an enemy based on current wave definition."""
        y_frac, pattern = WAVE_DEFS[self.wave_index]
        y = SCREEN_HEIGHT * y_frac
        return Enemy(SCREEN_WIDTH + ENEMY_SIZE, y, pattern, y)

    def reset(self) -> None:
        """Reset to initial state for game restart."""
        self.wave_index = 0
        self.timer = WAVE_START_DELAY
        self.spawned_in_wave = 0
        self.wave_active = False
