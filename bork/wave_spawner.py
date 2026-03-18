"""Wave spawner that manages timed enemy waves."""

import random

from bork.constants import (
    ENEMY_DART_SHOOTER_CHANCE,
    ENEMY_DART_SIZE,
    ENEMY_SIZE,
    ENEMY_SPAWN_SPACING,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WAVE_PAUSE,
    WAVE_START_DELAY,
)
from bork.dart import Dart
from bork.enemy import Enemy


class WaveSpawner:
    """Manages wave timing and enemy spawning from zone config."""

    def __init__(self, zone_config: dict) -> None:
        self._wave_defs = zone_config["wave_patterns"]
        self._boss_after = zone_config["waves_before_boss"]
        self._enemies_per_wave = zone_config["enemies_per_wave"]
        self._enemy_speed = zone_config["enemy_speed"]
        self._powerup_after_wave = zone_config["powerup_after_wave"]
        self._enemy_type = zone_config.get("enemy_type", "batwing")

        self.wave_index = 0
        self.timer = WAVE_START_DELAY
        self.spawned_in_wave = 0
        self.wave_active = False
        self.powerup_spawn_due = False
        self.total_waves_completed = 0
        self.boss_triggered = False

    def update(self, dt: float) -> Enemy | Dart | None:
        """Tick the spawner. Returns a new enemy if one should spawn."""
        self.timer -= dt

        if not self.wave_active:
            if self.timer <= 0:
                self.wave_active = True
                self.timer = 0
            return None

        if self.timer <= 0:
            enemy = self._spawn_enemy()
            self.spawned_in_wave += 1

            if self.spawned_in_wave >= self._enemies_per_wave:
                if self.wave_index == self._powerup_after_wave:
                    self.powerup_spawn_due = True
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

    def _spawn_enemy(self) -> Enemy | Dart:
        """Create an enemy based on current wave definition and zone enemy type."""
        y_frac, pattern = self._wave_defs[self.wave_index]
        size = ENEMY_DART_SIZE if self._enemy_type == "dart" else ENEMY_SIZE
        spawn_x = SCREEN_WIDTH + size

        vy = 0.0
        if pattern == "diagonal_cross":
            # Alternate top/bottom entry for crossing pattern
            from_top = self.spawned_in_wave % 2 == 0
            y = SCREEN_HEIGHT * (0.8 if from_top else 0.2)
            vy = -self._enemy_speed * 0.4 if from_top else self._enemy_speed * 0.4
        else:
            y = SCREEN_HEIGHT * y_frac

        if self._enemy_type == "dart":
            is_shooter = random.random() < ENEMY_DART_SHOOTER_CHANCE
            return Dart(spawn_x, y, pattern, y, self._enemy_speed, vy, is_shooter)
        return Enemy(spawn_x, y, pattern, y, self._enemy_speed, vy)

    def reset(self) -> None:
        """Reset to initial state for zone/game restart."""
        self.wave_index = 0
        self.timer = WAVE_START_DELAY
        self.spawned_in_wave = 0
        self.wave_active = False
        self.powerup_spawn_due = False
        self.total_waves_completed = 0
        self.boss_triggered = False
