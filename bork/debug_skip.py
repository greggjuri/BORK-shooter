"""
DEBUG ONLY — delete this file and its import in game.py before release.
Keyboard shortcuts to jump to any zone or boss phase for testing.

Key bindings:
    F1  = Jump to Zone 1
    F2  = Jump to Zone 2
    F3  = Jump to Zone 3
    F9  = Spawn boss now (current zone)
    F10 = Force boss to Phase 2
    F11 = Force boss to Phase 3
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from bork.constants import DEBUG_SKIP_ENABLED

if TYPE_CHECKING:
    from bork.game import BorkGame


def handle_debug_key(key: int, game: BorkGame) -> None:
    """Handle debug skip keys. No-op if DEBUG_SKIP_ENABLED is False."""
    if not DEBUG_SKIP_ENABLED:
        return
    import arcade

    if key == arcade.key.F1:
        _jump_to_zone(game, 1)
    elif key == arcade.key.F2:
        _jump_to_zone(game, 2)
    elif key == arcade.key.F3:
        _jump_to_zone(game, 3)
    elif key == arcade.key.F9:
        _spawn_boss_now(game)
    elif key == arcade.key.F10:
        _set_boss_phase(game, 2)
    elif key == arcade.key.F11:
        _set_boss_phase(game, 3)


def _jump_to_zone(game: BorkGame, zone_number: int) -> None:
    """Reset to start of given zone, keeping player state."""
    game.zone_manager.current_zone = zone_number
    game._start_zone()
    print(f"[DEBUG] Jumped to Zone {zone_number}")


def _spawn_boss_now(game: BorkGame) -> None:
    """Skip remaining waves and trigger boss warning immediately."""
    game.enemies.clear()
    game.enemy_projectiles.clear()
    game.powerups.clear()
    game.wave_spawner.boss_triggered = True
    print("[DEBUG] Boss triggered")


def _set_boss_phase(game: BorkGame, phase: int) -> None:
    """Force boss into given phase (only works during boss fight)."""
    from bork.constants import STATE_BOSS_FIGHT

    if game.state != STATE_BOSS_FIGHT or game.boss is None:
        print("[DEBUG] No active boss fight — F9 to spawn boss first")
        return
    if phase == 2:
        game.boss.core_hp = int(game.boss.max_hp * 0.49)
    elif phase == 3:
        game.boss.core_hp = int(game.boss.max_hp * 0.24)
    game.boss._update_phase()
    print(f"[DEBUG] Boss forced to phase {phase}")
