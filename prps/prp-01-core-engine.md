# PRP-001: Core Engine

**Created**: 2026-02-15
**Initial**: `initials/init-01-core-engine.md`
**Status**: Complete

---

## Overview

### Problem Statement
B.O.R.K. needs a playable foundation before enemies, powerups, scoring, or sound can be layered on. The core game loop, player ship, scrolling starfield, and basic shooting mechanics must be solid and performant first.

### Proposed Solution
Build the core engine using the Python Arcade library: a game window at 960x540 with a clean update/draw loop, a player ship with momentum-based 8-directional movement, spacebar-triggered laser projectiles with cooldown, and a continuously scrolling 2-layer parallax starfield. All rendering uses geometric shapes (no external assets).

### Success Criteria
- [ ] Game window opens at 960x540 and maintains 60 FPS
- [ ] Player ship responds to arrow keys and WASD for 8-directional movement
- [ ] Player ship has acceleration/deceleration (not instant stop)
- [ ] Player ship is constrained to screen bounds
- [ ] Spacebar fires laser projectiles with a cooldown
- [ ] Projectiles travel rightward and despawn when leaving the screen
- [ ] 2-layer parallax starfield scrolls continuously leftward
- [ ] Game loop cleanly separates update logic from draw logic

---

## Context

### Related Documentation
- `docs/PLANNING.md` - Architecture overview (templates only — this is the first feature)
- `docs/DECISIONS.md` - No existing ADRs yet
- `initials/init-01-core-engine.md` - Full feature specification
- Python Arcade docs: https://api.arcade.academy/

### Dependencies
- **Required**: Python 3.8+, `arcade` library
- **Optional**: None (this is the foundation; everything else depends on it)

### Files to Create
```
requirements.txt             # Python dependencies (project root)
bork/
├── __init__.py              # Package marker
├── game.py                  # Main game window, game loop, entry point
├── player.py                # Player ship class (movement, drawing, bounds)
├── projectile.py            # Laser projectile class
├── starfield.py             # Parallax starfield system
├── constants.py             # Shared constants (screen size, speeds, colors)
└── tests/
    ├── __init__.py
    ├── test_player.py
    ├── test_projectile.py
    └── test_starfield.py
```

---

## Technical Specification

### Constants (`bork/constants.py`)
```python
# Window
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
SCREEN_TITLE = "B.O.R.K."
TARGET_FPS = 60

# Player
PLAYER_ACCELERATION = 600.0      # pixels/sec^2
PLAYER_FRICTION = 0.88           # velocity multiplier per frame (at 60fps)
PLAYER_MAX_SPEED = 350.0         # pixels/sec
PLAYER_SHIP_SIZE = 20            # half-width of the ship triangle
PLAYER_START_X = 100
PLAYER_START_Y = SCREEN_HEIGHT // 2

# Projectiles
PROJECTILE_SPEED = 700.0         # pixels/sec
PROJECTILE_LENGTH = 16
PROJECTILE_WIDTH = 3
SHOOT_COOLDOWN = 0.18            # seconds between shots

# Starfield
STAR_LAYER_COUNT = 2
STAR_COUNTS = [60, 30]           # back layer (dim/slow), front layer (bright/fast)
STAR_SPEEDS = [40.0, 100.0]      # pixels/sec per layer
STAR_SIZES = [1.5, 2.5]          # radius per layer
STAR_COLORS_ALPHA = [100, 200]   # alpha per layer (0-255)

# Colors
COLOR_BACKGROUND = (5, 5, 15)
COLOR_PLAYER = (0, 200, 255)
COLOR_LASER = (255, 80, 80)
COLOR_STAR = (255, 255, 255)
```

### Player Ship (`bork/player.py`)
```python
class Player:
    """Player ship with momentum-based 8-directional movement."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.shoot_timer = 0.0    # cooldown tracker

    def update(self, dt: float, keys_pressed: set[int]) -> None:
        """Update position based on input, friction, and bounds."""
        # Apply acceleration from input
        # Apply friction to velocity
        # Clamp to max speed
        # Update position
        # Clamp to screen bounds

    def draw(self) -> None:
        """Draw the ship as a right-pointing triangle."""

    def can_shoot(self) -> bool:
        """Return True if shoot cooldown has elapsed."""
        return self.shoot_timer <= 0.0

    def reset_shoot_timer(self) -> None:
        """Reset the shoot cooldown timer."""
        self.shoot_timer = SHOOT_COOLDOWN
```

### Projectile (`bork/projectile.py`)
```python
class Projectile:
    """A single laser projectile moving rightward."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def update(self, dt: float) -> None:
        """Move the projectile rightward."""
        self.x += PROJECTILE_SPEED * dt

    def is_off_screen(self) -> bool:
        """Return True if past the right edge of the screen."""
        return self.x > SCREEN_WIDTH + PROJECTILE_LENGTH

    def draw(self) -> None:
        """Draw the laser bolt as a small filled rectangle."""
```

### Starfield (`bork/starfield.py`)
```python
class Star:
    """A single star in the parallax field."""

    def __init__(self, x: float, y: float, speed: float, size: float, alpha: int) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.alpha = alpha

class Starfield:
    """Multi-layer parallax scrolling starfield."""

    def __init__(self) -> None:
        self.stars: list[Star] = []
        # Initialize stars for each layer, randomly distributed

    def update(self, dt: float) -> None:
        """Move stars leftward; wrap at left edge."""

    def draw(self) -> None:
        """Draw each star as a filled circle."""
```

### Game Window (`bork/game.py`)
```python
import arcade

class BorkGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(COLOR_BACKGROUND)
        self.player = None
        self.projectiles = []
        self.starfield = None
        self.keys_pressed = set()

    def setup(self):
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.projectiles = []
        self.starfield = Starfield()

    def on_update(self, dt):
        self.starfield.update(dt)
        self.player.update(dt, self.keys_pressed)
        self.player.shoot_timer -= dt
        # Update projectiles, remove off-screen ones
        # Continuous shooting: fire while Space is held and cooldown allows
        if arcade.key.SPACE in self.keys_pressed:
            self._try_shoot()

    def on_draw(self):
        self.clear()
        self.starfield.draw()
        self.player.draw()
        for p in self.projectiles:
            p.draw()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)

    def _try_shoot(self):
        if self.player.can_shoot():
            self.projectiles.append(Projectile(self.player.x, self.player.y))
            self.player.reset_shoot_timer()

def main():
    game = BorkGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
```

### Input Mapping
| Key | Action |
|-----|--------|
| Arrow Up / W | Accelerate up |
| Arrow Down / S | Accelerate down |
| Arrow Left / A | Accelerate left |
| Arrow Right / D | Accelerate right |
| Space | Fire laser (with cooldown) |

### Movement Model
- **Acceleration**: When a direction key is held, velocity increases in that direction at `PLAYER_ACCELERATION` pixels/sec².
- **Friction**: Each frame, velocity is multiplied by `PLAYER_FRICTION` (scaled by delta time). This gives a smooth deceleration when keys are released.
- **Speed cap**: Velocity magnitude is clamped to `PLAYER_MAX_SPEED`.
- **Bounds clamping**: Position is clamped so the ship triangle stays fully within the 960x540 window.

---

## Implementation Steps

### Step 1: Project Setup and Constants
**Files**: `requirements.txt`, `bork/__init__.py`, `bork/constants.py`

1. Create `requirements.txt` at project root with `arcade>=2.7` and `ruff>=0.4` (dev linting)
2. Create `bork/__init__.py` (empty package marker)
3. Create `bork/constants.py` with all game constants as specified above (with type hints on any module-level helpers)
4. Install dependencies: `pip install -r requirements.txt`

**Validation**:
- [ ] `pip install -r requirements.txt` succeeds
- [ ] `python -c "import arcade; print(arcade.version)"` works
- [ ] `ruff check bork/` passes
- [ ] `ruff format --check bork/` passes

---

### Step 2: Starfield System
**Files**: `bork/starfield.py`, `bork/tests/__init__.py`, `bork/tests/test_starfield.py`

1. Create the `Star` dataclass and `Starfield` class
2. `Starfield.__init__`: populate stars randomly across the screen for each layer using `random.uniform`
3. `Starfield.update(dt)`: move each star left by `star.speed * dt`; if `star.x < 0`, wrap to `SCREEN_WIDTH + random offset` with a new random y
4. `Starfield.draw()`: draw each star as `arcade.draw_circle_filled(star.x, star.y, star.size, (R, G, B, star.alpha))`
5. Write unit tests:
   - Stars initialize within screen bounds
   - `update()` moves stars leftward
   - Stars that pass x=0 wrap to the right edge

**Validation**:
- [ ] `pytest bork/tests/test_starfield.py` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 3: Player Ship
**Files**: `bork/player.py`, `bork/tests/test_player.py`

1. Create `Player` class with position, velocity, and shoot timer
2. `Player.update(dt, keys_pressed)`:
   - Read arrow keys and WASD from `keys_pressed` set
   - Apply acceleration: e.g., if `arcade.key.RIGHT` or `arcade.key.D` in `keys_pressed`, `vx += PLAYER_ACCELERATION * dt`
   - Apply friction: `vx *= PLAYER_FRICTION ** (dt * TARGET_FPS)` (frame-rate independent friction)
   - Clamp speed: if magnitude exceeds `PLAYER_MAX_SPEED`, normalize and scale
   - Update position: `x += vx * dt`, `y += vy * dt`
   - Clamp position to screen bounds (accounting for ship size)
3. `Player.draw()`: draw a triangle pointing right using `arcade.draw_triangle_filled()` with `COLOR_PLAYER`
4. `Player.can_shoot()` and `Player.reset_shoot_timer()` for cooldown
5. Write unit tests:
   - Initial position is correct
   - Acceleration applies when key is in `keys_pressed`
   - Friction decelerates when no keys pressed
   - Position clamps to screen bounds
   - Shoot cooldown prevents rapid fire, resets correctly

**Validation**:
- [ ] `pytest bork/tests/test_player.py` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 4: Projectile System
**Files**: `bork/projectile.py`, `bork/tests/test_projectile.py`

1. Create `Projectile` class with position
2. `Projectile.update(dt)`: move right by `PROJECTILE_SPEED * dt`
3. `Projectile.is_off_screen()`: return `True` if `x > SCREEN_WIDTH + PROJECTILE_LENGTH`
4. `Projectile.draw()`: draw a small filled rectangle using `arcade.draw_lrtb_rectangle_filled()` with `COLOR_LASER`
5. Write unit tests:
   - Projectile moves rightward each update
   - `is_off_screen()` returns `True` only when past screen edge
   - Projectile initializes at given position

**Validation**:
- [ ] `pytest bork/tests/test_projectile.py` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 5: Game Window and Main Loop
**Files**: `bork/game.py`

1. Create `BorkGame(arcade.Window)` subclass
2. `__init__`: set up window size, title, background color, declare instance vars
3. `setup()`: initialize Player, empty projectile list, Starfield
4. `on_update(dt)`:
   - Update starfield
   - Update player (passing `keys_pressed`)
   - Decrement `player.shoot_timer` by `dt`
   - Update all projectiles
   - Remove projectiles where `is_off_screen()` is `True`
   - Handle continuous shooting: if Space is held and `can_shoot()`, fire
5. `on_draw()`:
   - `self.clear()`
   - Draw starfield, then player, then projectiles (painter's order)
6. `on_key_press(key, modifiers)`: add to `keys_pressed` (no shooting here — that's driven by `on_update`)
7. `on_key_release(key, modifiers)`: discard from `keys_pressed`
8. `_try_shoot()`: create `Projectile` at player nose position if cooldown allows (called from `on_update` when Space is held)
9. `main()` entry point

**Validation**:
- [ ] `python bork/game.py` opens a window
- [ ] Ship moves with arrow keys and WASD
- [ ] Ship decelerates smoothly when keys released
- [ ] Ship cannot leave screen bounds
- [ ] Spacebar fires lasers with cooldown
- [ ] Lasers travel right and disappear off-screen
- [ ] Starfield scrolls left with parallax effect
- [ ] Stable 60 FPS (no visible hitching)

---

### Step 6: Run All Tests
**Commands**:
```bash
pytest bork/tests/ -v --tb=short
```

**Validation**:
- [ ] All tests pass
- [ ] No warnings or errors

---

## Testing Requirements

### Unit Tests

**test_starfield.py**:
- `test_starfield_initializes_correct_star_count`: Total stars equals sum of `STAR_COUNTS`
- `test_stars_within_screen_bounds`: All initial star positions within (0, SCREEN_WIDTH) x (0, SCREEN_HEIGHT)
- `test_starfield_update_moves_stars_left`: After update with positive dt, all star x positions decrease
- `test_star_wraps_when_off_screen_left`: A star at x=-1 wraps to x > SCREEN_WIDTH after update

**test_player.py**:
- `test_player_initial_position`: Starts at PLAYER_START_X, PLAYER_START_Y
- `test_player_accelerates_right`: With RIGHT key pressed, vx increases after update
- `test_player_decelerates_without_input`: With no keys, velocity decreases toward zero
- `test_player_clamped_to_screen_bounds`: Position cannot exceed screen edges
- `test_player_max_speed_clamped`: Velocity magnitude never exceeds PLAYER_MAX_SPEED
- `test_player_shoot_cooldown`: `can_shoot()` returns False immediately after shooting, True after cooldown
- `test_player_diagonal_movement`: Both x and y axes respond simultaneously

**test_projectile.py**:
- `test_projectile_moves_right`: x increases after update
- `test_projectile_off_screen_detection`: Returns True past SCREEN_WIDTH + PROJECTILE_LENGTH
- `test_projectile_not_off_screen_when_visible`: Returns False when within screen

### Integration Tests (Manual)
See Integration Test Plan below.

---

## Integration Test Plan

Manual tests to perform after implementation:

### Prerequisites
- `pip install -r requirements.txt` completed
- Run `python bork/game.py`

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Launch game | 960x540 window opens with dark background and scrolling starfield | ☐ |
| 2 | Observe starfield | Two distinct star layers scroll left at different speeds; back layer is dimmer and slower | ☐ |
| 3 | Press Right arrow | Ship accelerates rightward smoothly | ☐ |
| 4 | Release Right arrow | Ship decelerates and glides to a stop | ☐ |
| 5 | Press W + D simultaneously | Ship moves diagonally up-right | ☐ |
| 6 | Move ship to right edge | Ship stops at screen boundary, cannot leave | ☐ |
| 7 | Move ship to all 4 edges | Ship constrained on all sides | ☐ |
| 8 | Tap Spacebar | Single laser fires from ship nose, travels right | ☐ |
| 9 | Hold Spacebar | Lasers fire at cooldown rate, not continuous stream | ☐ |
| 10 | Watch lasers reach right edge | Lasers disappear cleanly past the screen edge | ☐ |
| 11 | Observe FPS | No visible stuttering or frame drops (check with arcade's built-in FPS if available) | ☐ |

### Error Scenarios
| Scenario | How to Trigger | Expected Behavior | Pass? |
|----------|----------------|-------------------|-------|
| Multiple keys held then released | Mash arrow keys rapidly | No stuck movement, ship responds correctly | ☐ |
| Shoot while moving | Move and press space simultaneously | Both movement and shooting work independently | ☐ |
| Alt-tab away and back | Switch focus away, return | Game continues normally, no crash | ☐ |

---

## Error Handling

### Expected Errors
| Error | Cause | Handling |
|-------|-------|----------|
| `ModuleNotFoundError: arcade` | arcade not installed | Clear error message; `requirements.txt` documents dependency |
| Low FPS on weak hardware | Too many stars or draw calls | Reduce `STAR_COUNTS` in constants; all values are tunable |

### Edge Cases
- **Diagonal speed**: Diagonal movement should not exceed `PLAYER_MAX_SPEED` (normalize velocity vector before clamping)
- **Accumulated projectiles**: If many projectiles exist, off-screen ones are removed each frame preventing unbounded list growth
- **Zero dt**: If `dt` is 0 (first frame edge case), all update logic safely produces no change
- **Very large dt**: If frame hitches, friction clamping and position clamping prevent teleporting through walls

---

## Cost Impact

N/A — This is a standalone local game with no API calls, cloud services, or external dependencies beyond the `arcade` library (free, open source).

---

## Open Questions

None — all questions from the initial spec are resolved:
- [x] Screen resolution: 960x540
- [x] Framework: Python Arcade
- [x] Ship style: Geometric shapes initially

---

## Rollback Plan

If issues are discovered:
1. `git revert` the commit(s) from this PRP
2. Delete `bork/` directory if starting over
3. Verify clean state: `git status` shows no game files

Since this is the first feature with no dependents, rollback is trivial.

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 9 | Requirements are specific and all open questions resolved. Ship "feel" (acceleration/friction values) may need tuning but that's expected. |
| Feasibility | 10 | Python Arcade is well-suited for this. No technical risks — standard 2D game patterns. |
| Completeness | 9 | All P0 and P1 requirements covered. P2 items (screen shake foundation, delta time) are addressed: delta time is built in, screen shake deferred to a later PRP as it has no consumer yet. |
| Alignment | 9 | Follows 500-line file limit (split into 5 files), uses Python Arcade as specified, no external assets needed. |
| **Average** | **9.25** | High confidence. This is a straightforward, well-scoped foundation. |

---

## Notes

- **Inspiration**: Delta, Sanxion (C64) — horizontal scrollers with momentum. The friction model gives that "sliding on ice" feel without being twitchy.
- **Tuning**: The acceleration, friction, and max speed constants will likely need play-testing adjustment. All values are centralized in `constants.py` for easy tweaking.
- **File budget**: With 5 source files, each should stay well under 500 lines. `game.py` will be the largest at ~80-100 lines.
- **Screen shake (P2)**: Deferred — no consumers exist yet. Will add as a utility when explosions are implemented (init-02 or init-03).
- **Delta time (P2)**: Arcade's `on_update(delta_time)` provides this natively. All movement calculations use `dt` for frame-rate independence.
