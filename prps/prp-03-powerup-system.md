# PRP-003: Powerup System

**Created**: 2026-02-15
**Initial**: `initials/init-03-powerup-system.md`
**Status**: Draft

---

## Overview

### Problem Statement
B.O.R.K. has enemies to fight, but the player's ship never improves. Powerups reward survival and create risk/reward decisions — fly into danger for an upgrade or play it safe?

### Proposed Solution
Add a powerup system with a speed boost that spawns after every wave 3 (sine wave). Powerups are pulsing yellow circles with a black "S" that drift leftward. Collecting one increases the player's max speed by 20% until death. The system is designed to be extensible for future powerup types.

### Success Criteria
- [ ] Speed powerup spawns 1 second after wave 3 ends
- [ ] Powerup appears at right edge, 70% up screen
- [ ] Powerup drifts left at `POWERUP_SPEED`
- [ ] Powerup visual: yellow pulsing circle with black "S"
- [ ] Flying into powerup collects it (powerup disappears)
- [ ] Player max speed increases by 20% after collection
- [ ] Speed increase persists through subsequent waves
- [ ] Speed resets to normal on game over / restart
- [ ] Powerup despawns if it leaves left edge uncollected
- [ ] Powerup spawns again after each wave 3 (each loop)
- [ ] Collecting when already boosted has no additional effect

---

## Context

### Related Documentation
- `docs/DECISIONS.md` — ADR-005 (centralized constants), ADR-006 (entity update/draw pattern)
- `initials/init-03-powerup-system.md` — Full feature specification
- `prps/prp-02-enemy-system.md` — Enemy and wave system this builds on

### Dependencies
- **Required**: PRP-001 Core Engine (complete), PRP-002 Enemy System (complete)

### Files to Create
```
bork/
├── powerup.py                   # Powerup class with update/draw
└── tests/
    └── test_powerup.py
```

### Files to Modify
```
bork/constants.py                # Add powerup constants
bork/player.py                   # Add speed_multiplier
bork/wave_spawner.py             # Signal when wave 3 completes
bork/game.py                     # Integrate powerup spawning, collection, effects
```

---

## Technical Specification

### Constants to Add (`bork/constants.py`)
```python
# Powerups
POWERUP_SPEED = 100.0            # pixels/sec (slower than enemies)
POWERUP_SIZE = 18                # radius
POWERUP_COLOR = (255, 220, 0)    # yellow
POWERUP_TEXT_COLOR = (0, 0, 0)   # black letter

# Powerup spawn
POWERUP_SPAWN_DELAY = 1.0        # seconds after wave 3 completes
POWERUP_SPAWN_Y = 0.70           # 30% from top = 70% up

# Powerup effects
SPEED_BOOST_MULTIPLIER = 1.2     # 20% speed increase

# Powerup pulse animation
POWERUP_PULSE_SPEED = 4.0        # oscillations per second
POWERUP_PULSE_AMOUNT = 0.15      # scale varies ±15%

# Collect effect
POWERUP_COLLECT_FLASH_DURATION = 0.15
POWERUP_COLLECT_FLASH_COLOR = (255, 255, 150)
```

### Powerup (`bork/powerup.py`)
```python
class Powerup:
    """A collectible powerup that drifts leftward with a pulse animation."""

    def __init__(self, x: float, y: float, kind: str) -> None:
        self.x = x
        self.y = y
        self.kind = kind          # "speed" (extensible for future types)
        self.time_alive = 0.0     # for pulse animation

    def update(self, dt: float) -> None:
        """Move leftward and advance pulse timer."""
        self.x -= POWERUP_SPEED * dt
        self.time_alive += dt

    def is_off_screen(self) -> bool:
        """Return True if past the left edge."""
        return self.x < -POWERUP_SIZE

    def draw(self) -> None:
        """Draw as a pulsing yellow circle with black letter."""
        # Pulse: scale oscillates between 1-PULSE_AMOUNT and 1+PULSE_AMOUNT
        pulse = 1.0 + POWERUP_PULSE_AMOUNT * math.sin(
            self.time_alive * POWERUP_PULSE_SPEED * 2 * math.pi
        )
        r = POWERUP_SIZE * pulse
        arcade.draw_circle_filled(self.x, self.y, r, POWERUP_COLOR)
        arcade.draw_text(
            "S", self.x, self.y,
            POWERUP_TEXT_COLOR, font_size=14, bold=True,
            anchor_x="center", anchor_y="center",
        )
```

### Player Changes (`bork/player.py`)
```python
class Player:
    def __init__(self, x: float, y: float) -> None:
        ...
        self.speed_multiplier = 1.0    # NEW

    def update(self, dt: float, keys_pressed: set[int]) -> None:
        ...
        # Clamp to max speed (modified to use multiplier)
        max_speed = PLAYER_MAX_SPEED * self.speed_multiplier
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > max_speed:
            scale = max_speed / speed
            self.vx *= scale
            self.vy *= scale
```

Since `Player` is re-instantiated via `setup()` on restart, `speed_multiplier` resets to 1.0 automatically.

### Wave Spawner Changes (`bork/wave_spawner.py`)

Add a `powerup_spawn_due` flag that signals to game.py when wave 3 (index 2) has just completed:

```python
class WaveSpawner:
    def __init__(self) -> None:
        ...
        self.powerup_spawn_due = False    # NEW

    def update(self, dt: float) -> Enemy | None:
        ...
        if self.spawned_in_wave >= ENEMIES_PER_WAVE:
            # Check if the wave that just finished was wave 3 (index 2)
            if self.wave_index == 2:
                self.powerup_spawn_due = True
            self.wave_index = (self.wave_index + 1) % len(WAVE_DEFS)
            ...

    def reset(self) -> None:
        ...
        self.powerup_spawn_due = False
```

### Game Loop Changes (`bork/game.py`)

New state:
- `self.powerups: list[Powerup]` — active powerups on screen
- `self.powerup_spawn_timer: float` — countdown after wave 3 ends

`on_update(dt)` additions:
1. Check `wave_spawner.powerup_spawn_due` → start `powerup_spawn_timer = POWERUP_SPAWN_DELAY`, clear flag
2. If `powerup_spawn_timer > 0`: decrement; when ≤ 0, spawn powerup at `(SCREEN_WIDTH + POWERUP_SIZE, SCREEN_HEIGHT * POWERUP_SPAWN_Y)`
3. Update powerups, remove off-screen
4. Check powerup→player collisions (circle-circle using `POWERUP_SIZE` and `PLAYER_SHIP_SIZE`):
   - On hit: remove powerup, apply effect, add collect flash
   - Speed powerup: set `player.speed_multiplier = SPEED_BOOST_MULTIPLIER` (only if currently 1.0)

`on_draw()` additions:
- Draw powerups after enemies, before player
- Draw collect flash effects (reuse `destroy_effects` pattern with powerup color)

`setup()` additions:
- Reset `powerups`, `powerup_spawn_timer`

---

## Implementation Steps

### Step 1: Add Powerup Constants
**Files**: `bork/constants.py`

Append all powerup constants as specified above.

**Validation**:
- [ ] `ruff check bork/` and `ruff format --check bork/` pass
- [ ] Existing tests still pass

---

### Step 2: Powerup Class
**Files**: `bork/powerup.py`, `bork/tests/test_powerup.py`

1. Create `Powerup` class with `update(dt)`, `draw()`, `is_off_screen()`
2. Constructor takes `x`, `y`, `kind` (str)
3. `update(dt)`: move left, advance `time_alive`
4. `is_off_screen()`: `x < -POWERUP_SIZE`
5. `draw()`: pulsing circle with centered text letter

Tests:
- `test_powerup_moves_left`: x decreases after update
- `test_powerup_off_screen_left`: True when past left edge
- `test_powerup_not_off_screen_when_visible`: False when on screen
- `test_powerup_pulse_changes_over_time`: time_alive advances
- `test_powerup_kind_stored`: kind attribute matches constructor arg

**Validation**:
- [ ] `pytest bork/tests/test_powerup.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 3: Player Speed Multiplier
**Files**: `bork/player.py`, `bork/tests/test_player.py`

1. Add `self.speed_multiplier = 1.0` in `Player.__init__`
2. In `update()`, change max speed clamp from `PLAYER_MAX_SPEED` to `PLAYER_MAX_SPEED * self.speed_multiplier`

New tests:
- `test_player_speed_multiplier_default`: `speed_multiplier` starts at 1.0
- `test_player_speed_multiplier_increases_max_speed`: with multiplier 1.2, player can exceed the base max speed

**Validation**:
- [ ] `pytest bork/tests/test_player.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 4: Wave Spawner Powerup Signal
**Files**: `bork/wave_spawner.py`, `bork/tests/test_wave_spawner.py`

1. Add `self.powerup_spawn_due = False` in `__init__` and `reset()`
2. In `update()`, when a wave completes and `wave_index == 2` (before incrementing), set `self.powerup_spawn_due = True`

New tests:
- `test_powerup_spawn_due_after_wave_3`: flag is True after wave 3 completes
- `test_powerup_spawn_due_not_after_wave_1`: flag stays False after wave 1
- `test_powerup_spawn_due_resets`: flag resets via `reset()`

**Validation**:
- [ ] `pytest bork/tests/test_wave_spawner.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 5: Integrate into Game Loop
**Files**: `bork/game.py`

1. Add imports for `Powerup` and new constants
2. `__init__`: add `self.powerups`, `self.powerup_spawn_timer`
3. `setup()`: reset `powerups=[]`, `powerup_spawn_timer=0`
4. `on_update(dt)`:
   - After wave spawner update: if `wave_spawner.powerup_spawn_due`, set `powerup_spawn_timer = POWERUP_SPAWN_DELAY`, clear flag
   - Tick `powerup_spawn_timer`; when it fires, create `Powerup` at spawn position
   - Update powerups, remove off-screen
   - Check powerup→player collisions after enemy collisions:
     - On hit: remove powerup, set `player.speed_multiplier = SPEED_BOOST_MULTIPLIER` (if not already boosted), add collect flash to `destroy_effects`
5. `on_draw()`: draw powerups after enemies, before player

**Validation**:
- [ ] `python3 bork/game.py` runs
- [ ] All existing tests pass
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 6: Run All Tests
**Commands**:
```bash
pytest bork/tests/ -v --tb=short
ruff check bork/
ruff format --check bork/
```

**Validation**:
- [ ] All tests pass
- [ ] No lint errors

---

## Testing Requirements

### Unit Tests

**test_powerup.py**:
- `test_powerup_moves_left`: x decreases after update
- `test_powerup_off_screen_left`: True past left edge
- `test_powerup_not_off_screen_when_visible`: False on screen
- `test_powerup_pulse_changes_over_time`: time_alive advances
- `test_powerup_kind_stored`: kind matches constructor

**test_player.py** (new tests):
- `test_player_speed_multiplier_default`: starts at 1.0
- `test_player_speed_multiplier_increases_max_speed`: higher cap with multiplier

**test_wave_spawner.py** (new tests):
- `test_powerup_spawn_due_after_wave_3`: flag True after wave 3
- `test_powerup_spawn_due_not_after_wave_1`: flag False after wave 1
- `test_powerup_spawn_due_resets`: flag resets

---

## Integration Test Plan

### Prerequisites
- `pip install -r requirements.txt`
- Run `python3 bork/game.py`

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Wait through waves 1-3 + 1 second | Yellow pulsing "S" powerup appears from right, ~70% up | ☐ |
| 2 | Watch powerup drift | Moves left, slower than enemies, pulsing animation visible | ☐ |
| 3 | Don't collect it | Powerup drifts off left edge and disappears | ☐ |
| 4 | Wait for next wave 3, collect the powerup | Powerup disappears with flash, ship feels faster | ☐ |
| 5 | Move ship at max speed before and after | Noticeably faster after collection (20% increase) | ☐ |
| 6 | Survive through more waves | Speed boost persists | ☐ |
| 7 | Collect a second powerup (next loop) | No additional speed increase (no stacking) | ☐ |
| 8 | Die (fly into enemy), press R | Ship speed back to normal after restart | ☐ |
| 9 | After restart, wait for wave 3 + 1s | Powerup spawns again | ☐ |

### Error Scenarios
| Scenario | How to Trigger | Expected Behavior | Pass? |
|----------|----------------|-------------------|-------|
| Die while powerup on screen | Let enemy hit you with powerup visible | Game over; powerup stays visible but frozen | ☐ |
| Powerup and enemy overlap | Let both be near player | Enemy collision takes priority (game over) | ☐ |

---

## Error Handling

### Edge Cases
- **No stacking**: If `player.speed_multiplier` is already > 1.0, collecting again does nothing
- **Powerup despawn**: Off-screen cleanup prevents orphaned powerups
- **Game over with powerup on screen**: Powerup stops updating (early return in on_update) but still renders
- **Multiple powerups**: Only one spawns per loop, but the list supports multiples for future extensibility
- **Restart clears all**: `setup()` creates a fresh Player (speed_multiplier=1.0) and empty powerup list

---

## Cost Impact

N/A — standalone local game.

---

## Open Questions

None — all resolved:
- [x] Powerup speed: 100 px/sec
- [x] Spawn timing: 1 second after wave 3
- [x] Spawn position: 30% from top
- [x] Effect duration: Until death
- [x] Stacking: No

---

## Rollback Plan

1. `git revert` the commits from this PRP
2. Remove `bork/powerup.py` and `bork/tests/test_powerup.py`
3. Revert modifications to `player.py`, `wave_spawner.py`, `game.py`, `constants.py`
4. Enemy system (PRP-002) is unaffected

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 10 | Very specific requirements. Spawn timing, position, multiplier value, visual design all defined. |
| Feasibility | 10 | Reuses existing patterns (entity update/draw, circle_circle collision, destroy_effects). Minimal new code. |
| Completeness | 9 | All P0 and P1 covered. P2 items (sound hook, HUD indicator) deferred to their own inits. |
| Alignment | 10 | Follows all ADRs, stays under 500 lines, uses geometric shapes, centralized constants. |
| **Average** | **9.75** | High confidence. Straightforward extension of existing systems. |

---

## Notes

- **Extensibility**: The `kind` field on `Powerup` and the collection logic in `game.py` are designed so adding new powerup types (spread shot, shield) only requires: a new constant, a new `kind` string, and a new branch in the collection handler.
- **Pulse animation**: Uses `sin(time * speed * 2π)` for smooth oscillation. The scale varies ±15% around 1.0, making it noticeable without being distracting.
- **Collect flash**: Reuses the existing `destroy_effects` list with a different color (`POWERUP_COLLECT_FLASH_COLOR`). No new data structure needed.
- **Wave spawner signal**: The `powerup_spawn_due` flag is a clean interface — game.py reads it and clears it. The spawner doesn't need to know about powerups.
