"""Wave spawner that manages timed enemy waves."""

from bork.constants import (
    ENEMY_SIZE,
    ENEMY_SPAWN_SPACING,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WAVE_PAUSE,
    WAVE_START_DELAY,
)
from bork.enemy import Enemy


class WaveSpawner:
    """Manages wave timing and enemy spawning from zone config."""

    def __init__(self, zone_config: dict) -> None:
        self._wave_defs = zone_config["wave_patterns"]
        self._boss_after = zone_config["waves_before_boss"]
        self._enemies_per_wave = zone_config["enemies_per_wave"]
        self._enemy_speed = zone_config["enemy_speed"]
        self._powerup_after_wave = zone_config["powerup_after_wave"]

        self.wave_index = 0
        self.timer = WAVE_START_DELAY
        self.spawned_in_wave = 0
        self.wave_active = False
        self.powerup_spawn_due = False
        self.total_waves_completed = 0
        self.boss_triggered = False

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

            if self.spawned_in_wave >= self._enemies_per_wave:
                # Signal powerup spawn after the configured wave
                if self.wave_index == self._powerup_after_wave:
                    self.powerup_spawn_due = True
                # Wave complete — pause before next
                self.wave_active = False
                self.spawned_in_wave = 0
                self.wave_index = (self.wave_index + 1) % len(self._wave_defs)
                self.timer = WAVE_PAUSE
                self.total_waves_completed += 1
                if (
                    self.total_waves_completed >= self._boss_after
                    and not self.boss_triggered
                ):
                    self.boss_triggered = True
            else:
                self.timer = ENEMY_SPAWN_SPACING

            return enemy

        return None

    def _spawn_enemy(self) -> Enemy:
        """Create an enemy based on current wave definition."""
        y_frac, pattern = self._wave_defs[self.wave_index]
        y = SCREEN_HEIGHT * y_frac
        return Enemy(SCREEN_WIDTH + ENEMY_SIZE, y, pattern, y, self._enemy_speed)

    def reset(self) -> None:
        """Reset to initial state for zone/game restart."""
        self.wave_index = 0
        self.timer = WAVE_START_DELAY
        self.spawned_in_wave = 0
        self.wave_active = False
        self.powerup_spawn_due = False
        self.total_waves_completed = 0
        self.boss_triggered = False
