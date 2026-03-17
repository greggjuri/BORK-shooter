# PRP-08a: Zone Infrastructure — Manager, Transitions, Parameterized Spawner

**Created**: 2026-03-17
**Initial**: `initials/init-08-levels-progression.md`
**Status**: Complete

---

## Overview

### Problem Statement
The game currently has a single zone with hardcoded wave patterns, enemy type, boss, and background. There's no progression beyond beating the Sentinel — the game just shows "VICTORY" and restarts. The wave spawner, boss spawning, and HUD zone display are all hardcoded to Zone 1 values.

### Proposed Solution
Build the zone infrastructure layer: a `ZoneConfig` data structure, a `ZoneManager` to track progression, parameterized `WaveSpawner`, and zone transition logic in game.py. This PRP does NOT add new enemies, bosses, or backgrounds — it wires the system so Zone 1 plays exactly as before but is now driven by zone config data. Future PRPs (08b-08e) layer content on top.

### Success Criteria
- [ ] `ZONE_CONFIGS` dictionary in constants.py defines Zone 1 (and placeholder Zone 2/3 configs)
- [ ] `ZoneManager` tracks current zone, returns config, advances zones
- [ ] `WaveSpawner` accepts zone config (wave count, patterns, enemy count, enemy speed)
- [ ] Beating the Zone 1 boss transitions to Zone 2 (using Zone 1 config as placeholder)
- [ ] Beating Zone 3's boss shows "GAME COMPLETE" instead of zone transition
- [ ] Player keeps powerup tier levels across zone transitions
- [ ] Game over resets to Zone 1
- [ ] HUD shows current zone number dynamically
- [ ] Wave spawner resets between zones, uses new zone's config
- [ ] All existing tests pass (Zone 1 behavior unchanged)
- [ ] New tests for ZoneManager and parameterized WaveSpawner

---

## Context

### Related Documentation
- `docs/PLANNING.md` — Phase 4 (Content), development phases
- `docs/DECISIONS.md` — ADR-005 (centralized constants), ADR-006 (entity pattern), ADR-008 (boss state extraction)
- `initials/init-08-levels-progression.md` — Full feature specification

### Dependencies
- **Required**: All Phase 1-4 features ✓, init-09 (tiered powerups) ✓
- **Blocks**: PRP-08b (Zone 2 enemies), PRP-08c (Zone 3 enemies), PRP-08d (Zone 2 boss), PRP-08e (Zone 3 boss)

### Files to Modify/Create
```
bork/constants.py       # Add ZONE_CONFIGS, STATE_ZONE_TRANSITION, zone-related constants
bork/zone_manager.py    # NEW: ZoneManager class and ZoneConfig type
bork/wave_spawner.py    # Parameterize from zone config (patterns, counts, speed)
bork/game.py            # Zone transition logic, ZoneManager integration, setup changes
bork/boss_fight.py      # Victory → zone advance or game complete
bork/hud.py             # Dynamic zone number display + zone transition overlay
bork/tests/test_zone_manager.py   # NEW: ZoneManager tests
bork/tests/test_wave_spawner.py   # Update for parameterized spawner
```

---

## Technical Specification

### Data Models

**ZoneConfig (new TypedDict or dataclass)**:
```python
class ZoneConfig(TypedDict):
    name: str                    # "DEEP SPACE", "NEBULA", "ASTEROID BELT"
    waves_before_boss: int       # 9, 12, 15
    wave_patterns: tuple[tuple[float, str], ...]  # ((0.75, "straight"), ...)
    enemies_per_wave: int        # 5, 6, 7
    enemy_speed: float           # 150.0, 180.0, 210.0
    boss_type: str               # "sentinel" (future: "zone2_boss", "zone3_boss")
    boss_points: int             # 5000
    boss_nodamage_bonus: int     # 2500
    powerup_after_wave: int      # wave index that triggers powerup spawn (0-based)
```

**Constants (new)**:
```python
ZONE_COUNT = 3

ZONE_CONFIGS: dict[int, ZoneConfig] = {
    1: {
        "name": "DEEP SPACE",
        "waves_before_boss": 9,
        "wave_patterns": (
            (WAVE_TOP_Y, "straight"),
            (WAVE_BOTTOM_Y, "straight"),
            (WAVE_CENTER_Y, "sine"),
        ),
        "enemies_per_wave": 5,
        "enemy_speed": 150.0,
        "boss_type": "sentinel",
        "boss_points": 5000,
        "boss_nodamage_bonus": 2500,
        "powerup_after_wave": 2,  # after wave 3 (0-indexed)
    },
    2: {
        "name": "NEBULA",
        "waves_before_boss": 12,
        "wave_patterns": (
            (WAVE_TOP_Y, "straight"),
            (WAVE_BOTTOM_Y, "straight"),
            (WAVE_CENTER_Y, "sine"),
        ),  # placeholder — PRP-08b adds diagonal cross
        "enemies_per_wave": 6,
        "enemy_speed": 180.0,
        "boss_type": "sentinel",   # placeholder — PRP-08d adds Zone 2 boss
        "boss_points": 7500,
        "boss_nodamage_bonus": 3500,
        "powerup_after_wave": 3,
    },
    3: {
        "name": "ASTEROID BELT",
        "waves_before_boss": 15,
        "wave_patterns": (
            (WAVE_TOP_Y, "straight"),
            (WAVE_BOTTOM_Y, "straight"),
            (WAVE_CENTER_Y, "sine"),
        ),  # placeholder — PRP-08c adds pincer/tracker
        "enemies_per_wave": 7,
        "enemy_speed": 210.0,
        "boss_type": "sentinel",   # placeholder — PRP-08e adds Zone 3 boss
        "boss_points": 10000,
        "boss_nodamage_bonus": 5000,
        "powerup_after_wave": 4,
    },
}

STATE_ZONE_TRANSITION = "zone_transition"
ZONE_TRANSITION_DURATION = 3.0  # seconds to show "ZONE X COMPLETE"
```

**ZoneManager (new class)**:
```python
class ZoneManager:
    """Tracks current zone and provides zone config."""

    def __init__(self) -> None:
        self.current_zone: int = 1

    @property
    def config(self) -> ZoneConfig:
        """Return config for current zone."""
        return ZONE_CONFIGS[self.current_zone]

    @property
    def is_final_zone(self) -> bool:
        """Return True if current zone is the last one."""
        return self.current_zone >= ZONE_COUNT

    def advance(self) -> bool:
        """Advance to next zone. Returns True if advanced, False if already final."""
        if self.is_final_zone:
            return False
        self.current_zone += 1
        return True

    def reset(self) -> None:
        """Reset to Zone 1."""
        self.current_zone = 1
```

### State Changes

**Game state machine** — new state added:
```
STATE_VICTORY → STATE_ZONE_TRANSITION (if not final zone)
                                      → load next zone config
                                      → STATE_PLAYING
STATE_VICTORY → "GAME COMPLETE" screen (if final zone)
                                      → R to restart from Zone 1
```

**WaveSpawner** — constructor accepts zone config:
```python
class WaveSpawner:
    def __init__(self, config: ZoneConfig) -> None:
        self._wave_defs = config["wave_patterns"]
        self._boss_after = config["waves_before_boss"]
        self._enemies_per_wave = config["enemies_per_wave"]
        self._enemy_speed = config["enemy_speed"]
        self._powerup_after_wave = config["powerup_after_wave"]
```

**game.py** — new instance variables:
```python
self.zone_manager = ZoneManager()
```

---

## Implementation Steps

### Step 1: Add zone config constants
**Files**: `bork/constants.py`

Add `ZONE_COUNT`, `ZONE_CONFIGS` dictionary with all 3 zones (Zone 2/3 use placeholder patterns and boss_type="sentinel"), `STATE_ZONE_TRANSITION`, `ZONE_TRANSITION_DURATION`.

Remove `BOSS_SPAWN_AFTER_WAVES` (moved into zone config). Keep `SENTINEL_CORE_POINTS` and `SENTINEL_NODAMAGE_BONUS` as standalone constants (still referenced by boss_fight.py for the Sentinel specifically) but also include their values in zone configs for the generic victory path.

**Validation**:
- [ ] `ruff check bork/constants.py` passes
- [ ] Zone 1 config values match current hardcoded values exactly

---

### Step 2: Create ZoneManager
**Files**: `bork/zone_manager.py` (NEW)

Simple class: `current_zone`, `config` property, `advance()`, `reset()`, `is_final_zone`. Imports `ZONE_CONFIGS` and `ZONE_COUNT` from constants.

**Validation**:
- [ ] `ruff check bork/zone_manager.py` passes
- [ ] Import succeeds

---

### Step 3: Parameterize WaveSpawner
**Files**: `bork/wave_spawner.py`

Change `__init__` to accept a `ZoneConfig` dict. Replace hardcoded `WAVE_DEFS`, `BOSS_SPAWN_AFTER_WAVES`, `ENEMIES_PER_WAVE`, `ENEMY_SPEED`, and the powerup trigger wave index with values from the config.

The `_spawn_enemy()` method creates an `Enemy` with the zone's `enemy_speed` instead of the global `ENEMY_SPEED` constant. This means `Enemy.__init__` needs a `speed` parameter (or we pass it to `update`).

**Enemy speed parameterization**: Add `speed` parameter to `Enemy.__init__` so wave spawner can set it from zone config. Update `enemy.py` to use `self.speed` instead of the global `ENEMY_SPEED` constant.

**Validation**:
- [ ] `ruff check bork/wave_spawner.py bork/enemy.py` passes
- [ ] `WaveSpawner(ZONE_CONFIGS[1])` produces identical behavior to current spawner

---

### Step 4: Integrate ZoneManager into game.py
**Files**: `bork/game.py`

1. Add `self.zone_manager = ZoneManager()` in `__init__`.
2. In `setup()`, create `WaveSpawner(self.zone_manager.config)` instead of `WaveSpawner()`.
3. Add new method `_start_zone()` that:
   - Creates new `WaveSpawner` from current zone config
   - Resets enemies, projectiles, powerups lists
   - Sets `state = STATE_PLAYING`
   - Does NOT reset player position or powerup levels
4. In `setup()` (full restart): call `self.zone_manager.reset()` then `_start_zone()` plus player/score reset.
5. Pass `self.zone_manager.current_zone` to HUD for zone display.
6. Add `STATE_ZONE_TRANSITION` handling in update dispatch.

**Validation**:
- [ ] `ruff check bork/game.py` passes
- [ ] Game plays Zone 1 identically to before

---

### Step 5: Update boss_fight.py for zone advancement
**Files**: `bork/boss_fight.py`

1. In `update_victory()`: when `game.victory_timer <= 0`:
   - If `game.zone_manager.is_final_zone` → stay in `STATE_VICTORY` (game complete)
   - Else → set `game.state = STATE_ZONE_TRANSITION`, start transition timer

2. Add `update_zone_transition(game, dt)`:
   - Decrement `game.zone_transition_timer`
   - When timer expires: `game.zone_manager.advance()`, call `game._start_zone()`

3. Update `_award_boss_victory_points()` to use zone config values for points:
   ```python
   config = game.zone_manager.config
   game.scoring.register_kill(config["boss_points"])
   ```

**Validation**:
- [ ] `ruff check bork/boss_fight.py` passes
- [ ] Beating Zone 1 boss triggers zone transition
- [ ] Beating Zone 3 boss shows game complete

---

### Step 6: Update HUD for dynamic zone display
**Files**: `bork/hud.py`

1. Update `draw()` signature to accept `zone: int` parameter.
2. Update `_draw_zone()` to show `f"ZONE {zone:02d}"` instead of hardcoded "ZONE 01".
3. Add `draw_zone_transition_text(zone_name: str)` method for the transition overlay (shows "ZONE X COMPLETE" centered on screen).
4. Add `draw_game_complete_text()` for the final victory screen.

**Validation**:
- [ ] `ruff check bork/hud.py` passes
- [ ] Zone display shows correct number

---

### Step 7: Update game.py draw methods
**Files**: `bork/game.py`

1. Update `hud.draw()` call to pass `self.zone_manager.current_zone`.
2. Add draw logic for `STATE_ZONE_TRANSITION` (call `hud.draw_zone_transition_text`).
3. Update `STATE_VICTORY` draw to distinguish between zone victory and game complete.
4. Allow R key restart from both `STATE_VICTORY` (game complete) and `STATE_GAME_OVER`.

**Validation**:
- [ ] `ruff check bork/game.py` passes
- [ ] Zone transition overlay displays correctly

---

### Step 8: Write tests
**Files**: `bork/tests/test_zone_manager.py` (NEW), `bork/tests/test_wave_spawner.py`

**ZoneManager tests**:
- `test_starts_at_zone_1`: Initial zone is 1
- `test_config_returns_zone_data`: Config has expected keys
- `test_advance_increments_zone`: Zone 1 → 2
- `test_advance_returns_false_at_final`: Can't advance past Zone 3
- `test_is_final_zone`: True at zone 3, False at 1 and 2
- `test_reset_returns_to_zone_1`: After advancing, reset goes back to 1

**WaveSpawner tests** — update existing:
- Update `WaveSpawner()` calls to `WaveSpawner(ZONE_CONFIGS[1])`
- Add: `test_spawner_uses_zone_enemy_speed`: Verify spawned enemy has zone's speed
- Add: `test_spawner_uses_zone_wave_count`: Boss triggers at zone's wave count

**Validation**:
- [ ] `pytest bork/tests/ -v` — all tests pass
- [ ] New tests cover ZoneManager lifecycle

---

### Step 9: Commit and verify
**Commands**:
```bash
ruff check bork/
pytest bork/tests/ -v
python bork/game.py  # Manual play-test
```

**Validation**:
- [ ] Zone 1 plays identically to before
- [ ] Beating boss shows zone transition, then loads Zone 2 (same enemies/boss as Zone 1 — placeholders)
- [ ] Beating Zone 3 boss shows game complete
- [ ] Game over resets to Zone 1
- [ ] Powerup levels persist across zones
- [ ] HUD zone number updates correctly

**Commit**: `feat: zone infrastructure with manager, parameterized spawner, and transitions`

---

## Testing Requirements

### Unit Tests
- `test_zone_manager_starts_at_1`: ZoneManager starts at zone 1
- `test_zone_manager_config_has_keys`: Config dict has all expected keys
- `test_zone_manager_advance`: Advances 1→2→3
- `test_zone_manager_advance_at_final`: Returns False, stays at 3
- `test_zone_manager_is_final_zone`: True only at zone 3
- `test_zone_manager_reset`: Returns to zone 1
- `test_wave_spawner_zone_config`: Spawner uses zone config values
- `test_enemy_custom_speed`: Enemy uses speed passed at construction

### Integration Tests (Manual)
- Play through Zone 1 normally — behavior identical to before
- Beat boss → zone transition screen → Zone 2 loads
- Beat Zone 2 boss → Zone 3 loads
- Beat Zone 3 boss → "GAME COMPLETE" screen
- Die in Zone 2 → game over → restart at Zone 1
- Powerup levels persist from Zone 1 to Zone 2

---

## Integration Test Plan

### Prerequisites
- Game running: `python bork/game.py`

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Start game, check HUD | Zone shows "ZONE 01" | ☐ |
| 2 | Play through 9 waves + boss | Boss fight plays normally | ☐ |
| 3 | Beat boss | "ZONE 1 COMPLETE" transition screen | ☐ |
| 4 | Wait 3 seconds | Zone 2 loads, HUD shows "ZONE 02" | ☐ |
| 5 | Verify powerup levels | Tier levels preserved from Zone 1 | ☐ |
| 6 | Play Zone 2 through boss | 12 waves + boss fight | ☐ |
| 7 | Beat Zone 2 boss | Zone 3 loads | ☐ |
| 8 | Beat Zone 3 boss | "GAME COMPLETE" screen | ☐ |
| 9 | Press R | Restart at Zone 1 with fresh state | ☐ |
| 10 | Die in any zone | Game over → R restarts at Zone 1 | ☐ |

---

## Error Handling

### Expected Errors
| Error | Cause | Handling |
|-------|-------|----------|
| Invalid zone number | Bug in advance logic | Clamp to ZONE_COUNT |
| Missing zone config | Zone number not in ZONE_CONFIGS | KeyError — would be a code bug, caught by tests |

### Edge Cases
- **Die during zone transition**: Not possible — player doesn't move during transition
- **Multiple rapid boss kills**: Not possible — only one boss per zone
- **Zone config missing key**: Caught by TypedDict type hints and tests
- **Restart during zone transition**: R key should work — reset to Zone 1

---

## Cost Impact

N/A — local game, no infrastructure.

---

## Open Questions

All resolved:
- ~~Should Zone 2/3 use placeholder enemies?~~ → Yes, use bat wings with zone speed until PRP-08b/08c
- ~~Should Zone 2/3 use placeholder bosses?~~ → Yes, use Sentinel until PRP-08d/08e
- ~~Score/lives reset between zones?~~ → No. Score persists, lives persist, powerup levels persist. Only wave spawner resets.
- ~~What happens to the victory timer?~~ → Used to show "ZONE X COMPLETE" for 3 seconds, then transition

---

## Rollback Plan

1. Revert commits for this feature
2. Restore `WaveSpawner()` with no arguments
3. Restore hardcoded zone display in HUD
4. Restore `BOSS_SPAWN_AFTER_WAVES` in constants
5. Remove `zone_manager.py`
6. Verify: `pytest bork/tests/ -v` passes

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 9 | Init spec is detailed and recommends this exact split |
| Feasibility | 9 | Clean architecture, minimal coupling. Only concern is game.py at 453 lines — zone transition logic needs to be lean or extracted. |
| Completeness | 9 | All files, tests, edge cases covered. Placeholder configs for Zone 2/3 are explicit. |
| Alignment | 10 | Follows ADR-005 (constants), ADR-006 (entity), ADR-008 (extraction), 500-line budget |
| **Average** | **9.25** | |

---

## Notes

- This PRP intentionally keeps Zone 2 and 3 as clones of Zone 1 (same enemies, same boss, same background). The only differences are wave count, enemy speed, and enemies per wave. Content differentiation comes from PRPs 08b-08e.
- The `Enemy` class needs a `speed` parameter added to its constructor. This is a small change but touches `enemy.py` and `wave_spawner.py`.
- `game.py` is at 453 lines. Zone transition logic should be extracted to `boss_fight.py` (or a new `zone_transition.py`) if it pushes past 500.
- The `boss_type` field in zone config is a string for now. When PRP-08d/08e add new bosses, a factory function will map strings to boss classes.
- Powerup spawn timing is moved into zone config (`powerup_after_wave`), allowing different zones to spawn powerups at different wave milestones.

## Relationship to Other PRPs

```
PRP-08a (this) ← infrastructure layer
  ├── PRP-08b: Zone 2 enemies + diagonal cross pattern + nebula background
  ├── PRP-08c: Zone 3 enemies + pincer/tracker patterns + asteroid background
  ├── PRP-08d: Zone 2 boss (replaces Sentinel placeholder)
  └── PRP-08e: Zone 3 boss (replaces Sentinel placeholder)
```
