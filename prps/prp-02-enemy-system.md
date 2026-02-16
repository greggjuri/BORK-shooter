# PRP-002: Enemy System

**Created**: 2026-02-15
**Initial**: `initials/init-02-enemy-system.md`
**Status**: Complete

---

## Overview

### Problem Statement
B.O.R.K. has a flying ship and shooting mechanics, but nothing to shoot at. Without enemies, there's no gameplay loop — no reason to move, dodge, or fire.

### Proposed Solution
Add an enemy system with three looping wave patterns, collision detection (projectile→enemy and enemy→player), a game-over state with restart, and a brief destruction flash effect. Enemies are drawn as diamond shapes (visually distinct from the player's triangle) and despawn off the left edge.

### Success Criteria
- [ ] First wave spawns 3 seconds after game start
- [ ] Wave 1: 5 enemies fly straight from right, 25% from top
- [ ] Wave 2: 5 enemies fly straight from right, 25% from bottom
- [ ] Wave 3: 5 enemies fly sine-wave pattern from center
- [ ] 2 second pause between waves
- [ ] Waves loop continuously after wave 3
- [ ] Player projectile destroys enemy (both removed)
- [ ] Player collision with enemy ends game
- [ ] Game over message displayed
- [ ] Press R to restart
- [ ] Enemies despawn off left edge of screen

---

## Context

### Related Documentation
- `docs/DECISIONS.md` — ADR-001 (Arcade), ADR-003 (geometric shapes), ADR-005 (centralized constants), ADR-006 (entity update/draw pattern)
- `initials/init-02-enemy-system.md` — Full feature specification
- `prps/prp-01-core-engine.md` — Foundation this builds on

### Dependencies
- **Required**: PRP-001 Core Engine (complete)
- **Optional**: None

### Files to Create
```
bork/
├── enemy.py                     # Enemy class with update/draw
├── wave_spawner.py              # Wave definitions and spawn timing
├── collision.py                 # Collision detection utilities
└── tests/
    ├── test_enemy.py
    ├── test_wave_spawner.py
    └── test_collision.py
```

### Files to Modify
```
bork/constants.py                # Add enemy/wave/collision constants
bork/game.py                     # Integrate enemies, waves, collisions, game state
```

---

## Technical Specification

### Constants to Add (`bork/constants.py`)
```python
# Enemies
ENEMY_SPEED = 150.0              # pixels/sec (horizontal, leftward)
ENEMY_SIZE = 15                  # half-width for collision and drawing
ENEMY_COLOR = (255, 60, 60)      # distinct red

# Waves
WAVE_START_DELAY = 3.0           # seconds before first wave
WAVE_PAUSE = 2.0                 # seconds between waves
ENEMIES_PER_WAVE = 5
ENEMY_SPAWN_SPACING = 0.3        # seconds between each enemy in a wave

# Sine wave pattern
SINE_AMPLITUDE = 80.0            # pixels
SINE_FREQUENCY = 2.0             # oscillations per second

# Spawn Y positions (fraction of screen height)
WAVE_TOP_Y = 0.75
WAVE_BOTTOM_Y = 0.25
WAVE_CENTER_Y = 0.5

# Destroy effect
DESTROY_FLASH_DURATION = 0.12    # seconds
DESTROY_FLASH_COLOR = (255, 255, 200)

# Game state
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
```

### Enemy (`bork/enemy.py`)
```python
class Enemy:
    """A single enemy entity."""

    def __init__(self, x: float, y: float, pattern: str, base_y: float) -> None:
        self.x = x
        self.y = y
        self.pattern = pattern      # "straight" or "sine"
        self.base_y = base_y        # center Y for sine oscillation
        self.time_alive = 0.0       # elapsed time for sine calculation

    def update(self, dt: float) -> None:
        """Move the enemy leftward. Apply sine pattern if applicable."""
        self.x -= ENEMY_SPEED * dt
        self.time_alive += dt
        if self.pattern == "sine":
            self.y = self.base_y + SINE_AMPLITUDE * math.sin(
                SINE_FREQUENCY * self.time_alive * 2 * math.pi
            )

    def is_off_screen(self) -> bool:
        """Return True if past the left edge."""
        return self.x < -ENEMY_SIZE

    def draw(self) -> None:
        """Draw the enemy as a diamond shape."""
        # Diamond: 4 points (left, top, right, bottom)
```

### Wave Spawner (`bork/wave_spawner.py`)
```python
class WaveSpawner:
    """Manages wave timing and enemy spawning."""

    def __init__(self) -> None:
        self.wave_index = 0           # 0, 1, 2 → loops
        self.timer = WAVE_START_DELAY # countdown to next spawn/wave
        self.spawned_in_wave = 0      # enemies spawned so far in current wave
        self.wave_active = False      # True while spawning enemies

    def update(self, dt: float) -> Enemy | None:
        """Tick the spawner. Returns a new Enemy if one should spawn, else None."""

    def _spawn_enemy(self) -> Enemy:
        """Create an enemy based on current wave_index."""

    def reset(self) -> None:
        """Reset to initial state for game restart."""
```

Wave definitions:
| Wave | Y Position | Pattern |
|------|-----------|---------|
| 0 | `SCREEN_HEIGHT * WAVE_TOP_Y` | straight |
| 1 | `SCREEN_HEIGHT * WAVE_BOTTOM_Y` | straight |
| 2 | `SCREEN_HEIGHT * WAVE_CENTER_Y` | sine |

Spawner state machine:
1. **Initial delay**: timer counts down from `WAVE_START_DELAY`
2. **Spawning**: emit one enemy every `ENEMY_SPAWN_SPACING` seconds, up to `ENEMIES_PER_WAVE`
3. **Between waves**: timer counts down from `WAVE_PAUSE`, then advance `wave_index` (mod 3)

### Collision Detection (`bork/collision.py`)
```python
def circle_circle(x1: float, y1: float, r1: float,
                  x2: float, y2: float, r2: float) -> bool:
    """Return True if two circles overlap."""
    dx = x1 - x2
    dy = y1 - y2
    return (dx * dx + dy * dy) <= (r1 + r2) ** 2

def point_in_circle(px: float, py: float,
                    cx: float, cy: float, r: float) -> bool:
    """Return True if point is inside circle."""
    dx = px - cx
    dy = py - cy
    return (dx * dx + dy * dy) <= r * r
```

Collision pairs:
- **Projectile → Enemy**: `point_in_circle(projectile.x, projectile.y, enemy.x, enemy.y, ENEMY_SIZE)` — projectile center vs enemy circle. Simple and sufficient since projectiles are small.
- **Enemy → Player**: `circle_circle(enemy.x, enemy.y, ENEMY_SIZE, player.x, player.y, PLAYER_SHIP_SIZE)` — both circles.

### Game State Changes (`bork/game.py`)

The game gains:
- `self.enemies: list[Enemy]` — active enemies
- `self.wave_spawner: WaveSpawner` — wave controller
- `self.state: str` — `STATE_PLAYING` or `STATE_GAME_OVER`
- `self.destroy_effects: list[tuple[float, float, float]]` — `(x, y, timer)` for flash effect

`on_update(dt)` changes:
- Early return if `state == STATE_GAME_OVER`
- Call `wave_spawner.update(dt)`, append returned enemies
- Update all enemies, remove off-screen ones
- Check projectile→enemy collisions (destroy both, add flash effect)
- Check enemy→player collisions (set state to game over)
- Update and expire destroy effects

`on_draw()` changes:
- Draw enemies after starfield, before player
- Draw destroy effects
- If game over: draw overlay text

`on_key_press()` changes:
- If `state == STATE_GAME_OVER` and key is R: call `setup()` to restart

`setup()` changes:
- Reset enemies, wave spawner, destroy effects, state

---

## Implementation Steps

### Step 1: Add Enemy Constants
**Files**: `bork/constants.py`

Append the enemy, wave, sine, spawn position, destroy effect, and game state constants as specified above.

**Validation**:
- [ ] `ruff check bork/` and `ruff format --check bork/` pass
- [ ] Existing tests still pass

---

### Step 2: Enemy Class
**Files**: `bork/enemy.py`, `bork/tests/test_enemy.py`

1. Create `Enemy` class following the entity pattern (`update(dt)`, `draw()`)
2. `__init__`: takes `x`, `y`, `pattern` ("straight" or "sine"), `base_y`
3. `update(dt)`: move left by `ENEMY_SPEED * dt`; if pattern is "sine", update `y` using `base_y + SINE_AMPLITUDE * sin(SINE_FREQUENCY * time_alive * 2π)`
4. `is_off_screen()`: `x < -ENEMY_SIZE`
5. `draw()`: draw a diamond using `arcade.draw_polygon_filled()` with 4 points (left, top, right, bottom) in `ENEMY_COLOR`

Tests:
- `test_enemy_moves_left`: x decreases after update
- `test_enemy_straight_pattern_constant_y`: y unchanged for "straight" pattern
- `test_enemy_sine_pattern_oscillates`: y differs from base_y after some time
- `test_enemy_off_screen_left`: is_off_screen True when past left edge
- `test_enemy_not_off_screen_when_visible`: is_off_screen False on screen

**Validation**:
- [ ] `pytest bork/tests/test_enemy.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 3: Collision Detection
**Files**: `bork/collision.py`, `bork/tests/test_collision.py`

1. `circle_circle(x1, y1, r1, x2, y2, r2) -> bool`: distance² ≤ (r1+r2)²
2. `point_in_circle(px, py, cx, cy, r) -> bool`: distance² ≤ r²

Tests:
- `test_circle_circle_overlap`: overlapping circles return True
- `test_circle_circle_no_overlap`: far-apart circles return False
- `test_circle_circle_touching`: exactly touching returns True
- `test_point_in_circle_inside`: point inside returns True
- `test_point_in_circle_outside`: point outside returns False
- `test_point_in_circle_on_edge`: point on edge returns True

**Validation**:
- [ ] `pytest bork/tests/test_collision.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 4: Wave Spawner
**Files**: `bork/wave_spawner.py`, `bork/tests/test_wave_spawner.py`

1. `WaveSpawner.__init__`: set `wave_index=0`, `timer=WAVE_START_DELAY`, `spawned_in_wave=0`, `wave_active=False`
2. `WaveSpawner.update(dt) -> Enemy | None`:
   - If not `wave_active`: decrement timer; when ≤ 0, set `wave_active=True`, reset spawn timer
   - If `wave_active`: decrement timer; when ≤ 0, spawn enemy, increment `spawned_in_wave`, reset timer to `ENEMY_SPAWN_SPACING`; when `spawned_in_wave >= ENEMIES_PER_WAVE`, end wave, advance `wave_index % 3`, set timer to `WAVE_PAUSE`, set `wave_active=False`, reset `spawned_in_wave`
3. `_spawn_enemy() -> Enemy`: create enemy at `(SCREEN_WIDTH + ENEMY_SIZE, wave_y)` based on `wave_index`
4. `WaveSpawner.reset()`: restore initial state

Tests:
- `test_no_spawn_during_initial_delay`: no enemy returned in first 2.9 seconds
- `test_first_spawn_after_delay`: enemy returned after 3+ seconds
- `test_wave_spawns_correct_count`: exactly 5 enemies per wave
- `test_wave_pause_between_waves`: no spawns during the pause
- `test_waves_loop_after_three`: wave_index wraps back to 0
- `test_wave_y_positions`: wave 0 spawns at top, wave 1 at bottom, wave 2 at center
- `test_wave_2_uses_sine_pattern`: wave 2 enemies have "sine" pattern
- `test_reset`: reset restores initial state

**Validation**:
- [ ] `pytest bork/tests/test_wave_spawner.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 5: Integrate into Game Loop
**Files**: `bork/game.py`

1. Add imports for `Enemy`, `WaveSpawner`, collision functions, and new constants
2. `__init__`: add `self.enemies`, `self.wave_spawner`, `self.state`, `self.destroy_effects`
3. `setup()`: initialize enemies=[], wave_spawner=WaveSpawner(), state=STATE_PLAYING, destroy_effects=[]
4. `on_update(dt)`:
   - Early return if `state != STATE_PLAYING` (starfield still updates for visual appeal)
   - Spawn enemies from wave_spawner
   - Update enemies, remove off-screen
   - Check projectile→enemy collisions:
     - For each projectile, check against each enemy
     - On hit: mark both for removal, add destroy effect at enemy position
     - Use `point_in_circle` for this check
   - Check enemy→player collisions:
     - For each enemy, check against player
     - On hit: set `state = STATE_GAME_OVER`
     - Use `circle_circle` for this check
   - Update destroy effects (decrement timer, remove expired)
5. `on_draw()`:
   - Draw enemies
   - Draw destroy effects as fading circles
   - If game over: draw "GAME OVER" and "Press R to restart" centered on screen using `arcade.draw_text()`
6. `on_key_press()`:
   - If game over and key is R: call `setup()`

**Validation**:
- [ ] `python3 bork/game.py` runs
- [ ] All existing tests still pass
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

**test_enemy.py**:
- `test_enemy_moves_left`: x decreases after update
- `test_enemy_straight_pattern_constant_y`: y unchanged for "straight"
- `test_enemy_sine_pattern_oscillates`: y differs from base_y after time
- `test_enemy_off_screen_left`: True when x < -ENEMY_SIZE
- `test_enemy_not_off_screen_when_visible`: False when on screen

**test_collision.py**:
- `test_circle_circle_overlap`: True when overlapping
- `test_circle_circle_no_overlap`: False when apart
- `test_circle_circle_touching`: True when exactly touching
- `test_point_in_circle_inside`: True
- `test_point_in_circle_outside`: False
- `test_point_in_circle_on_edge`: True

**test_wave_spawner.py**:
- `test_no_spawn_during_initial_delay`: None during delay
- `test_first_spawn_after_delay`: Enemy returned after delay
- `test_wave_spawns_correct_count`: 5 per wave
- `test_wave_pause_between_waves`: None during pause
- `test_waves_loop_after_three`: wave_index wraps to 0
- `test_wave_y_positions`: correct Y for each wave index
- `test_wave_2_uses_sine_pattern`: sine pattern on wave 2
- `test_reset`: restores initial state

### Integration Tests (Manual)
See Integration Test Plan below.

---

## Integration Test Plan

Manual tests after implementation:

### Prerequisites
- `pip install -r requirements.txt` completed
- Run `python3 bork/game.py`

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Launch game, wait 3 seconds | First wave of 5 enemies appears from right, ~75% up screen | ☐ |
| 2 | Don't shoot, watch wave 1 | Enemies fly straight left and disappear off left edge | ☐ |
| 3 | Wait 2 seconds after wave 1 clears | Wave 2: 5 enemies appear ~25% from bottom | ☐ |
| 4 | Wait 2 seconds after wave 2 | Wave 3: 5 enemies in sine-wave pattern from center | ☐ |
| 5 | Wait after wave 3 | Waves loop back to wave 1 | ☐ |
| 6 | Shoot at enemies | Projectile and enemy both destroyed on hit, brief flash | ☐ |
| 7 | Destroy all 5 in a wave | All removed, next wave still spawns on schedule | ☐ |
| 8 | Fly into an enemy | Game freezes, "GAME OVER" message appears | ☐ |
| 9 | Press R during game over | Game restarts fresh (player at start, no enemies) | ☐ |
| 10 | Observe enemy visuals | Enemies are diamonds, visually distinct from player triangle | ☐ |
| 11 | Observe destruction flash | Brief bright flash at destruction point | ☐ |

### Error Scenarios
| Scenario | How to Trigger | Expected Behavior | Pass? |
|----------|----------------|-------------------|-------|
| Projectile passes between enemies | Shoot between two close enemies | Only the hit enemy is destroyed | ☐ |
| Multiple enemies hit player simultaneously | Let a cluster reach player | Game over triggers once cleanly | ☐ |
| Restart mid-wave | Die during wave, press R | Fresh restart, wave timer starts from beginning | ☐ |

---

## Error Handling

### Edge Cases
- **Simultaneous collisions**: A single projectile can only destroy one enemy per frame (iterate and break on first hit)
- **Player dies same frame as enemy destroyed**: Check enemy→player collisions after projectile→enemy, so the player can destroy an enemy at point-blank without dying to it (projectile removes the enemy first)
- **Empty enemy list**: No collisions to check — loops are no-ops
- **Destroy effect after game over**: Effects still render during game over for visual polish
- **Many enemies on screen**: Off-screen cleanup prevents unbounded growth

---

## Cost Impact

N/A — standalone local game, no external services.

---

## Open Questions

None — all questions from the init spec are resolved:
- [x] Enemies per wave: 5
- [x] Time between waves: 2 seconds
- [x] First wave delay: 3 seconds
- [x] Collision ends game immediately (no lives)
- [x] Restart: R key

---

## Rollback Plan

If issues are discovered:
1. `git revert` the commits from this PRP
2. `bork/game.py` and `bork/constants.py` revert to pre-enemy state
3. New files (`enemy.py`, `wave_spawner.py`, `collision.py` + tests) can be deleted
4. Core engine (PRP-001) is unaffected

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 9 | Requirements are specific: exact wave counts, timings, patterns, and collision rules. Sine frequency may need tuning. |
| Feasibility | 10 | Builds cleanly on the entity pattern from PRP-001. Circle collision is trivial. No architectural risks. |
| Completeness | 9 | All P0 and P1 requirements covered. P2 items (sound hook, sine variation) deferred as they have no consumers. |
| Alignment | 10 | Follows all ADRs: entity pattern, geometric shapes, centralized constants, 500-line limit, Arcade library. |
| **Average** | **9.5** | High confidence. Well-scoped feature building on solid foundation. |

---

## Notes

- **Collision order matters**: Check projectile→enemy before enemy→player so the player can kill point-blank enemies without dying.
- **Sine frequency**: The init spec says "oscillations per screen width" but since enemies move at constant speed, I'm using oscillations per second (`SINE_FREQUENCY * time_alive * 2π`). This is simpler and produces the same visual effect. Tunable in constants.
- **Diamond shape**: Enemies drawn as rotated squares (diamond) to clearly distinguish from the player's triangle. Both use ENEMY_SIZE for consistent hitbox-to-visual mapping.
- **Destroy flash**: Minimal implementation — a white/yellow circle that shrinks over 0.12 seconds. Just enough feedback without a full particle system (deferred to init-04).
- **Game over state**: Updates freeze but starfield keeps scrolling for visual appeal. This is a deliberate choice.
