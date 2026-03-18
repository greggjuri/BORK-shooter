# PRP-08b: Zone 2 Content — Dart Enemy, Diagonal Cross, Nebula Background

**Created**: 2026-03-17
**Initial**: `initials/init-08b-zone2-content.md`
**Status**: Complete

---

## Overview

### Problem Statement
Zone 2 currently plays identically to Zone 1 — same bat wing enemies, same 3 wave patterns, same plain starfield. There's no visual or gameplay distinction when transitioning zones. Players need a reason to feel like they've progressed into new territory.

### Proposed Solution
Give Zone 2 its own identity with three new elements:
1. **Dart enemy** — a fast, small, green arrow-shaped ship. Some darts shoot aimed projectiles at the player (first time regular enemies shoot back).
2. **Diagonal cross pattern** — enemies enter from upper-right and lower-right simultaneously, crossing paths at screen center.
3. **Nebula background** — purple/pink semi-transparent cloud shapes drifting in the deepest parallax layer, with slightly tinted stars.

### Success Criteria
- [ ] Dart enemy renders as distinct green arrow shape, clearly different from bat wing
- [ ] Dart size is ~60-70% of bat wing
- [ ] ~35% of darts shoot aimed projectiles at the player on a cooldown
- [ ] Enemy projectiles damage player during normal gameplay (not just boss fights)
- [ ] Diagonal cross pattern spawns enemies from top-right and bottom-right simultaneously
- [ ] Zone 2 rotates through 4 patterns (straight, straight, sine, diagonal_cross)
- [ ] Nebula background has 3-5 slow-drifting colored clouds behind stars
- [ ] Zone 1 background is unchanged (no clouds)
- [ ] Zone 2 config uses `"dart"` enemy type, Zone 1 still uses `"batwing"`
- [ ] All existing tests pass, new tests for Dart and diagonal cross
- [ ] File sizes under 500 lines

---

## Context

### Related Documentation
- `docs/PLANNING.md` — Phase 4 (Content)
- `docs/DECISIONS.md` — ADR-003 (geometric shapes), ADR-006 (entity pattern)
- `prps/prp-08a-zone-infrastructure.md` — Zone infrastructure (complete)

### Dependencies
- **Required**: PRP-08a (zone infrastructure) ✓
- **Required**: EnemyProjectile in `enemy_projectile.py` ✓

### Files to Modify/Create
```
bork/constants.py         # Dart constants, nebula constants, update Zone 2 config
bork/dart.py              # NEW: Dart enemy class (subclass-style, own draw/update)
bork/wave_spawner.py      # Add diagonal_cross spawn logic, enemy type dispatch
bork/starfield.py         # Add nebula cloud layer, style parameter
bork/game.py              # Enemy projectile collision during normal play, pass style to starfield
bork/tests/test_dart.py   # NEW: Dart enemy tests
bork/tests/test_enemy.py  # Possibly update for shared interface
```

---

## Technical Specification

### Data Models

**Dart enemy (new class in `bork/dart.py`)**:
```python
class Dart:
    """Zone 2 fast enemy — small green arrow that may shoot."""

    def __init__(
        self, x: float, y: float, pattern: str, base_y: float,
        speed: float, is_shooter: bool = False
    ) -> None:
        self.x, self.y = x, y
        self.pattern = pattern
        self.base_y = base_y
        self.speed = speed
        self.is_shooter = is_shooter
        self.shoot_timer = ENEMY_DART_SHOOT_COOLDOWN
        self.time_alive = 0.0

    def update(self, dt: float) -> EnemyProjectile | None:
        """Move and optionally return a projectile if shooter."""
        ...

    def draw(self) -> None:
        """Draw as a small green arrow."""
        ...
```

**Key difference from Enemy**: Dart's `update()` returns an optional `EnemyProjectile` when a shooter fires. This avoids needing the game loop to reach into internal state.

**Nebula cloud (added to Starfield)**:
```python
class Cloud:
    """A semi-transparent nebula cloud."""
    x: float
    y: float
    speed: float
    width: float
    height: float
    color: tuple[int, int, int, int]  # RGBA with low alpha
```

**Constants (new)**:
```python
# Dart enemy
ENEMY_DART_SIZE = 10
ENEMY_DART_BODY_COLOR = (30, 180, 80)
ENEMY_DART_ACCENT_COLOR = (80, 255, 130)
ENEMY_DART_SCANNER_COLOR = (50, 255, 120)
ENEMY_DART_SHOOTER_CHANCE = 0.35
ENEMY_DART_SHOOT_COOLDOWN = 2.0
ENEMY_DART_PROJECTILE_SPEED = 250.0
ENEMY_DART_PROJECTILE_COLOR = (100, 255, 120)

# Nebula clouds
NEBULA_CLOUD_COUNT = 5
NEBULA_CLOUD_SPEED = 25.0
NEBULA_CLOUD_SIZE_RANGE = (60, 140)
NEBULA_CLOUD_COLORS = (
    (180, 80, 200, 25),
    (220, 80, 180, 30),
    (100, 120, 220, 25),
    (160, 60, 180, 20),
    (120, 100, 240, 28),
)
NEBULA_STAR_TINT = (200, 180, 255)  # slight purple tint for nebula stars
```

### State Changes

**Zone 2 config update**:
```python
2: {
    ...
    "enemy_type": "dart",
    "background_style": "nebula",
    "wave_patterns": (
        (WAVE_TOP_Y, "straight"),
        (WAVE_BOTTOM_Y, "straight"),
        (WAVE_CENTER_Y, "sine"),
        (WAVE_CENTER_Y, "diagonal_cross"),
    ),
}
```

**Zone 1 config additions** (to keep schema consistent):
```python
1: {
    ...
    "enemy_type": "batwing",
    "background_style": "deep_space",
}
```

**Zone 3 config additions**:
```python
3: {
    ...
    "enemy_type": "batwing",  # placeholder until PRP-08c
    "background_style": "deep_space",  # placeholder until PRP-08c
}
```

**WaveSpawner changes**:
- Constructor reads `enemy_type` from zone config
- `_spawn_enemy()` instantiates `Dart` or `Enemy` based on type
- Diagonal cross pattern alternates top/bottom spawns

**game.py changes**:
- Collect projectiles returned by Dart `update()` calls into `enemy_projectiles` list
- Run enemy projectile collision check during `STATE_PLAYING` (reuse `point_in_circle` logic)
- Pass `background_style` to Starfield on zone transition

**Starfield changes**:
- Constructor accepts optional `style` parameter
- `"nebula"` style: adds cloud layer, optionally tints stars
- `"deep_space"` or default: current behavior

---

## Implementation Steps

### Step 1: Add Dart and nebula constants
**Files**: `bork/constants.py`

Add `ENEMY_DART_*` constants, `NEBULA_*` constants. Update all three `ZONE_CONFIGS` entries to include `"enemy_type"` and `"background_style"` fields. Add `"diagonal_cross"` pattern to Zone 2's `wave_patterns`.

**Validation**:
- [ ] `ruff check bork/constants.py` passes
- [ ] Zone 1 config unchanged functionally

---

### Step 2: Create Dart enemy class
**Files**: `bork/dart.py` (NEW)

Create `Dart` class following entity pattern (`update(dt)`, `draw()`, `is_off_screen()`). Implements:
- Green arrow geometry (small pointed triangle with minimal fins)
- Green scanner eye glow
- Movement: same pattern dispatch as Enemy (straight, sine, diagonal_cross)
- Diagonal cross support: accepts `vy` parameter for diagonal movement
- Optional shooting: `is_shooter` flag, `shoot_timer` cooldown, returns `EnemyProjectile` from `update()`
- `update()` signature: `update(self, dt: float, player_x: float = 0, player_y: float = 0) -> EnemyProjectile | None`

Import `EnemyProjectile` from `bork.enemy_projectile`.

**Validation**:
- [ ] `ruff check bork/dart.py` passes
- [ ] Import succeeds

---

### Step 3: Add diagonal_cross movement to Enemy base class
**Files**: `bork/enemy.py`

Add optional `vy` parameter to `Enemy.__init__()` for diagonal movement. In `update()`, apply `self.vy * dt` to `self.y` when `vy != 0`. This lets the wave spawner set a vertical velocity for diagonal cross patterns on bat wing enemies too (future zones could use it).

**Validation**:
- [ ] `ruff check bork/enemy.py` passes
- [ ] Existing enemy tests pass (vy defaults to 0)

---

### Step 4: Update WaveSpawner for enemy types and diagonal cross
**Files**: `bork/wave_spawner.py`

1. Read `enemy_type` from zone config in constructor
2. Import `Dart` class
3. In `_spawn_enemy()`: instantiate `Dart` or `Enemy` based on `self._enemy_type`
4. For `"diagonal_cross"` pattern: alternate spawning from top-right (vy < 0) and bottom-right (vy > 0). Use `spawned_in_wave % 2` to alternate. Set entry Y to top or bottom quarter.
5. For Dart shooters: use `random.random() < ENEMY_DART_SHOOTER_CHANCE` to flag shooters

**Validation**:
- [ ] `ruff check bork/wave_spawner.py` passes
- [ ] Zone 1 spawns bat wings as before
- [ ] Zone 2 spawns darts

---

### Step 5: Add nebula style to Starfield
**Files**: `bork/starfield.py`

1. Add `Cloud` class (x, y, speed, width, height, color)
2. Add `style` parameter to `Starfield.__init__()` (default `"deep_space"`)
3. If style is `"nebula"`: initialize cloud entities using `NEBULA_*` constants, optionally tint star colors
4. `update()`: move clouds leftward, wrap at left edge
5. `draw()`: draw clouds before stars (deeper layer)

**Validation**:
- [ ] `ruff check bork/starfield.py` passes
- [ ] Default style looks identical to current

---

### Step 6: Wire enemy projectiles during normal gameplay
**Files**: `bork/game.py`

1. In `on_update()` during `STATE_PLAYING`, after updating enemies:
   - For each enemy, if it returns a projectile from `update()`, add to `self.enemy_projectiles`
   - Note: Only Dart returns projectiles; Enemy returns None (update() currently returns None)
2. Update and cull `enemy_projectiles` during `STATE_PLAYING` (same as boss fight does)
3. Add enemy projectile → player collision check during `STATE_PLAYING`
4. Pass `background_style` from zone config to `Starfield` in `_start_zone()` and `setup()`
5. Update Enemy `update()` calls to pass player position for Dart shooting

**Implementation note**: Enemy.update() currently returns None (void). To avoid changing its signature, we can check `isinstance(e, Dart)` or check if the enemy has an `update` that returns projectiles. Simpler: call `e.update(dt)` for bat wings, and `e.update(dt, player_x, player_y)` for darts — but that means game.py needs to know the type. Alternative: store returned projectiles in a list attribute on the enemy. Simplest: make all enemy `update()` return `EnemyProjectile | None`, with Enemy always returning None.

**Validation**:
- [ ] `ruff check bork/game.py` passes
- [ ] Enemy projectiles visible and damaging during normal gameplay

---

### Step 7: Update `_start_zone()` for background switching
**Files**: `bork/game.py`

In `_start_zone()`, create `Starfield(style=config.get("background_style", "deep_space"))`. In `setup()`, same.

**Validation**:
- [ ] Zone 1 has plain starfield
- [ ] Zone 2 has nebula clouds

---

### Step 8: Write tests
**Files**: `bork/tests/test_dart.py` (NEW)

- `test_dart_initial_position`: Dart at correct position
- `test_dart_moves_leftward`: x decreases on update
- `test_dart_off_screen`: Off-screen detection works
- `test_dart_shooter_fires`: Shooter dart returns projectile after cooldown
- `test_dart_non_shooter_no_fire`: Non-shooter dart returns None
- `test_dart_diagonal_cross_movement`: Dart with vy moves diagonally

Update `bork/tests/test_wave_spawner.py`:
- `test_zone2_spawns_darts`: Zone 2 config spawns Dart instances

**Validation**:
- [ ] `pytest bork/tests/ -v` — all tests pass

---

### Step 9: Manual play-test and commit

**Validation**:
- [ ] Zone 1: bat wings, plain starfield, no enemy shooting — unchanged
- [ ] Zone 2: green dart enemies, smaller and faster
- [ ] Some darts fire green projectiles at player
- [ ] Diagonal cross pattern: enemies cross from top-right and bottom-right
- [ ] Nebula clouds visible behind stars in Zone 2
- [ ] Getting hit by dart projectile damages player

**Commit**: `feat: Zone 2 content — Dart enemy, diagonal cross pattern, nebula background`

---

## Testing Requirements

### Unit Tests
- `test_dart_initial_position`: Dart spawns at given coordinates
- `test_dart_moves_leftward`: x decreases after update
- `test_dart_off_screen`: Returns True past left edge
- `test_dart_shooter_fires`: Returns EnemyProjectile after cooldown elapses
- `test_dart_non_shooter_no_fire`: Always returns None
- `test_dart_sine_pattern`: Sine pattern oscillates y
- `test_dart_diagonal_movement`: vy applies to y position
- `test_zone2_spawns_darts`: WaveSpawner with Zone 2 config creates Dart instances

### Integration Tests (Manual)
- Play through Zone 1 → behavior identical to before
- Transition to Zone 2 → darts appear, green, smaller
- Dart projectiles fire at player → dodgeable, damaging
- Diagonal cross pattern → enemies cross from corners
- Nebula background → purple/pink clouds drift slowly
- Die from dart projectile → respawn with invulnerability

---

## Integration Test Plan

### Prerequisites
- Game running: `python bork/game.py`

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Play Zone 1 | Bat wings, plain starfield, 3 patterns | ☐ |
| 2 | Beat Zone 1 boss, enter Zone 2 | Darts appear (green arrows), nebula background | ☐ |
| 3 | Observe dart visuals | Small green arrows, clearly distinct from bat wings | ☐ |
| 4 | Wait for dart shooting | Some darts fire green projectiles at player | ☐ |
| 5 | Get hit by dart projectile | Player takes damage, respawns | ☐ |
| 6 | Observe diagonal cross pattern | Enemies enter from top-right and bottom-right, cross | ☐ |
| 7 | Observe nebula background | Purple/pink clouds drift behind stars | ☐ |
| 8 | Return to Zone 1 (die + restart) | Plain starfield, bat wings restored | ☐ |

---

## Error Handling

### Edge Cases
- **Dart shoots off-screen**: Projectile culled by `is_off_screen()` — handled
- **All darts are non-shooters**: Random chance (35%) means some waves may have none — acceptable
- **Diagonal cross with odd enemy count**: Extra enemy goes to one group — acceptable
- **Zone transition preserves enemy projectiles**: Clear `enemy_projectiles` in `_start_zone()` — already done

---

## Cost Impact

N/A — local game, no infrastructure.

---

## Open Questions

All resolved:
- ~~Dart as subclass or parameterized?~~ → Separate class in `dart.py` (cleaner, distinct visuals)
- ~~How does Dart return projectiles?~~ → `update()` returns `EnemyProjectile | None`
- ~~Enemy.update() signature change?~~ → No change to Enemy. Dart has its own signature accepting player position.
- ~~Where does EnemyProjectile come from?~~ → `bork.enemy_projectile` (shared module, already extracted)

---

## Rollback Plan

1. Revert commits
2. Remove `dart.py` and `test_dart.py`
3. Restore Zone 2 config to placeholder values
4. Restore `Starfield()` without style parameter
5. Verify: `pytest bork/tests/ -v` passes

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 9 | Init spec is detailed, enemy design clear |
| Feasibility | 8 | Dart shooting requires threading projectiles back through game loop — slightly complex but well-understood pattern |
| Completeness | 9 | All files, tests, edge cases covered |
| Alignment | 10 | Follows entity pattern (ADR-006), geometric shapes (ADR-003), 500-line budget |
| **Average** | **9.0** | |

---

## Notes

- `dart.py` is a separate file (not in `enemy.py`) to keep both under 500 lines and maintain clear separation.
- The Dart `update()` method accepts `player_x, player_y` for aimed shooting. Game.py passes these when updating dart enemies.
- Diagonal cross movement uses a `vy` parameter — this could be reused by future enemy patterns.
- Nebula clouds are purely cosmetic. They don't affect gameplay.
- Zone 3 keeps `"batwing"` and `"deep_space"` as placeholders until PRP-08c.
