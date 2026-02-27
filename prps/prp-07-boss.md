# PRP-007: Boss Fights — Zone 1 Sentinel

**Created**: 2026-02-26
**Initial**: `initials/init-07-boss.md`
**Status**: Complete

---

## Overview

### Problem Statement

B.O.R.K. currently loops wave patterns indefinitely with no climactic goal. Players need a skill-check encounter that tests everything they've learned — a boss fight. The Zone 1 boss "SENTINEL" provides a multi-phase, learnable battle with telegraphed attacks, destructible sub-parts, and a dramatic death sequence.

### Proposed Solution

Implement a boss encounter system with:
- A wave-count trigger that spawns the boss after 9 waves (3 complete cycles)
- A warning sequence that builds tension before the fight
- The Sentinel boss — a geometric fortress with core, body, and two destructible wings
- Three escalating attack phases (Probing → Aggressive → Desperate)
- A boss health bar in the HUD
- Enemy projectiles (new mechanic — enemies currently don't shoot)
- A beam attack (Phase 3) with telegraphed charge-up
- Dramatic multi-explosion death sequence and victory state
- No-damage bonus for skilled play

### Success Criteria

- [ ] Boss spawns after 9 enemy waves with a warning sequence
- [ ] Boss has 3 distinct phases with escalating attacks
- [ ] Boss health bar displays at top of screen with color shift (green → yellow → red)
- [ ] Wings are independently destructible for bonus points
- [ ] Phase 3 beam attack is telegraphed with 1-second charge-up glow
- [ ] Boss death triggers multi-explosion sequence with screen shake
- [ ] Victory state shows "SENTINEL DESTROYED" + bonus points
- [ ] No-damage bonus (2,500 pts) awarded if player wasn't hit during fight
- [ ] Normal enemy spawning pauses during boss fight
- [ ] All boss constants in `constants.py`
- [ ] Unit tests pass for boss HP, phases, wing destruction, and spawn trigger

---

## Context

### Related Documentation

- `docs/PLANNING.md` — Architecture overview (boss is Phase 4: Content)
- `docs/DECISIONS.md` — ADR-003 (geometric shapes), ADR-005 (centralized constants), ADR-006 (entity pattern with update/draw)
- `initials/init-07-boss.md` — Full feature specification

### Dependencies

- **Required**: init-02 (enemy system) ✓, init-04 (explosions/particles) ✓, init-05 (scoring/HUD) ✓
- **Optional**: init-06 (sound system) — boss SFX can be added later

### Files to Modify/Create

```
bork/boss.py              # NEW: Sentinel boss class (core, body, wings, phases)
bork/boss_attacks.py      # NEW: Attack patterns + EnemyProjectile class
bork/tests/test_boss.py   # NEW: Unit tests for boss logic
bork/constants.py         # ADD: Boss constants section (~35 new constants)
bork/game.py              # MODIFY: Boss states, spawn trigger, fight loop, victory
bork/wave_spawner.py      # MODIFY: Add total_waves_completed counter
bork/collision.py         # MODIFY: Add point_in_rect helper
bork/hud.py               # MODIFY: Add boss health bar rendering
bork/explosions.py        # MODIFY: Add create_boss_explosion factory
```

---

## Technical Specification

### New Game States

```python
# Add to constants.py
STATE_BOSS_WARNING = "boss_warning"
STATE_BOSS_FIGHT = "boss_fight"
STATE_BOSS_DYING = "boss_dying"
STATE_VICTORY = "victory"
```

### Enemy Projectile (New Entity)

```python
class EnemyProjectile:
    """A projectile fired by enemies/bosses toward the player."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: tuple, size: float = 5.0, shape: str = "diamond"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.shape = shape  # "diamond", "circle"

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    def is_off_screen(self) -> bool:
        return (self.x < -self.size or self.x > SCREEN_WIDTH + self.size
                or self.y < -self.size or self.y > SCREEN_HEIGHT + self.size)

    def draw(self) -> None: ...
```

### Sentinel Boss (Core Entity)

```python
class Sentinel:
    """Zone 1 boss — geometric fortress with core, body, and wings."""

    def __init__(self, x: float, y: float):
        # Position
        self.x = x      # starts off-screen right, moves to SENTINEL_BATTLE_X
        self.y = y
        # Health pools
        self.core_hp: int = SENTINEL_CORE_HP
        self.left_wing_hp: int = SENTINEL_WING_HP
        self.right_wing_hp: int = SENTINEL_WING_HP
        self.left_wing_alive: bool = True
        self.right_wing_alive: bool = True
        # State
        self.state: str = "entering"  # entering, fighting, dying
        self.phase: int = 1           # 1, 2, or 3
        # Attack timers
        self.spread_timer: float = SENTINEL_SPREAD_INTERVAL_P1
        self.wing_timer: float = 1.5
        self.aimed_timer: float = SENTINEL_AIMED_INTERVAL
        self.beam_charge_timer: float = 0.0
        self.beam_cooldown_timer: float = SENTINEL_BEAM_COOLDOWN
        self.beam_active: bool = False
        self.beam_charging: bool = False
        self.beam_y: float = 0.0
        self.beam_visible_timer: float = 0.0
        # Death
        self.death_timer: float = 0.0
        self.death_explosions_spawned: int = 0

    @property
    def hp_fraction(self) -> float:
        return self.core_hp / SENTINEL_CORE_HP

    def update(self, dt: float, player_x: float, player_y: float) -> list[EnemyProjectile]:
        """Update boss state. Returns new projectiles to add to game."""

    def take_hit(self, part: str, damage: float) -> dict:
        """Hit a boss part. Returns {'destroyed': bool, 'part': str, 'points': int}."""

    def _update_phase(self) -> None:
        """Check HP thresholds, transition phase."""

    def _update_entering(self, dt: float) -> None:
        """Move from right edge to battle position."""

    def _update_movement(self, dt: float, player_y: float) -> None:
        """Vertical tracking of player."""

    def _attack_spread(self, player_x: float, player_y: float) -> list[EnemyProjectile]:
        """Fire spread shot toward player."""

    def _attack_wing_shot(self) -> list[EnemyProjectile]:
        """Alternating straight-left shots from wings."""

    def _attack_aimed(self, player_x: float, player_y: float) -> list[EnemyProjectile]:
        """Single fast bullet aimed at player's current position."""

    def _attack_beam(self, player_y: float) -> None:
        """Initiate beam charge sequence."""

    @property
    def is_dead(self) -> bool:
        return self.core_hp <= 0

    def draw(self) -> None: ...
```

### Hit Detection Zones

Boss collision uses multiple zones checked in priority order:

1. **Core** (circle): center of boss, radius `SENTINEL_CORE_SIZE/2` — full damage
2. **Left Wing** (rectangle): offset left of body — full damage, destroyable
3. **Right Wing** (rectangle): offset right of body — full damage, destroyable
4. **Body** (rectangle): main mass — half damage to core

Player projectiles are checked against zones in order: core → wings → body. First hit consumes the projectile.

### Beam Attack

The beam is NOT a projectile. It's an instant-hit mechanic:

1. `beam_charging = True` for 1 second (core glows bright white)
2. When charge completes: check if `abs(player.y - beam_y) < BEAM_HIT_HEIGHT / 2`
3. If hit: damage player
4. `beam_visible_timer = 0.1` — draw a full-width horizontal line at `beam_y`
5. Screen shake on fire
6. `beam_cooldown_timer` starts (4 seconds)

### Constants to Add

```python
# === Boss System ===

# Boss spawn
BOSS_SPAWN_AFTER_WAVES = 9
WARNING_DURATION = 1.5

# Game states
STATE_BOSS_WARNING = "boss_warning"
STATE_BOSS_FIGHT = "boss_fight"
STATE_BOSS_DYING = "boss_dying"
STATE_VICTORY = "victory"

# Sentinel stats
SENTINEL_CORE_HP = 50
SENTINEL_WING_HP = 15
SENTINEL_BODY_DAMAGE_MULT = 0.5

# Sentinel size
SENTINEL_WIDTH = 200
SENTINEL_HEIGHT = 150
SENTINEL_CORE_SIZE = 40
SENTINEL_WING_WIDTH = 30
SENTINEL_WING_HEIGHT = 80

# Sentinel colors
SENTINEL_BODY_COLOR = (60, 65, 75)
SENTINEL_BODY_ACCENT = (0, 200, 220)
SENTINEL_CORE_COLOR = (255, 80, 40)
SENTINEL_CORE_GLOW_COLOR = (255, 200, 100)
SENTINEL_WING_COLOR = (80, 85, 95)

# Sentinel movement
SENTINEL_BATTLE_X = SCREEN_WIDTH - 150
SENTINEL_ENTER_SPEED = 120.0
SENTINEL_TRACK_SPEED = 60
SENTINEL_TRACK_SPEED_P2 = 100
SENTINEL_TRACK_SPEED_P3 = 140
SENTINEL_LUNGE_SPEED = 200
SENTINEL_LUNGE_DURATION = 0.5

# Sentinel points
SENTINEL_CORE_POINTS = 5000
SENTINEL_WING_POINTS = 1000
SENTINEL_NODAMAGE_BONUS = 2500

# Phase thresholds (fraction of max HP)
SENTINEL_PHASE2_THRESHOLD = 0.66
SENTINEL_PHASE3_THRESHOLD = 0.33

# Attack timing (seconds)
SENTINEL_SPREAD_INTERVAL_P1 = 2.0
SENTINEL_SPREAD_INTERVAL_P2 = 1.5
SENTINEL_AIMED_INTERVAL = 1.0
SENTINEL_WING_INTERVAL = 1.5
SENTINEL_BEAM_CHARGE_TIME = 1.0
SENTINEL_BEAM_COOLDOWN = 4.0
SENTINEL_BEAM_HIT_HEIGHT = 20

# Bullet speeds
BOSS_BULLET_SPEED_MEDIUM = 200
BOSS_BULLET_SPEED_FAST = 350

# Boss bullet colors
BOSS_BULLET_COLOR_CYAN = (0, 220, 255)
BOSS_BULLET_COLOR_WHITE = (255, 255, 255)
BOSS_BULLET_COLOR_RED = (255, 60, 60)
BOSS_BEAM_COLOR = (255, 255, 200)

# Boss health bar
BOSS_HP_BAR_WIDTH = 400
BOSS_HP_BAR_HEIGHT = 12
BOSS_HP_BAR_Y = SCREEN_HEIGHT - 55

# Boss death
BOSS_DEATH_DURATION = 2.0
BOSS_DEATH_SMALL_EXPLOSION_INTERVAL = 0.15
BOSS_DEATH_FINAL_SHAKE_INTENSITY = 20.0
BOSS_DEATH_FINAL_SHAKE_DURATION = 1.0

# Boss explosion
BOSS_EXPLOSION_PARTICLE_COUNT_MIN = 50
BOSS_EXPLOSION_PARTICLE_COUNT_MAX = 80
BOSS_EXPLOSION_SPEED_MIN = 200
BOSS_EXPLOSION_SPEED_MAX = 600
BOSS_EXPLOSION_LIFETIME_MIN = 0.6
BOSS_EXPLOSION_LIFETIME_MAX = 1.2
BOSS_EXPLOSION_SIZE_MIN = 8
BOSS_EXPLOSION_SIZE_MAX = 16

# Warning
WARNING_FLASH_COLOR = (255, 40, 20, 60)
WARNING_TEXT_COLOR = (255, 60, 40)

# Victory
VICTORY_DISPLAY_DURATION = 3.0
```

---

## Implementation Steps

### Step 1: Add Boss Constants

**Files**: `bork/constants.py`

Add all boss-related constants listed above in a new `# === Boss System ===` section at the end of the file (before any existing trailing content). Include states, stats, sizes, colors, timing, points, and visual constants.

**Validation**:
- [ ] `ruff check bork/constants.py` passes
- [ ] All constants from init-07 spec are present
- [ ] No duplicate constant names

---

### Step 2: Add Collision Helper

**Files**: `bork/collision.py`

Add `point_in_rect(px, py, rx, ry, width, height) -> bool` function. The rect is centered at `(rx, ry)` with given width/height. Returns True if the point is inside.

**Validation**:
- [ ] Lint passes
- [ ] Quick manual test in test file

---

### Step 3: Add Wave Completion Counter to WaveSpawner

**Files**: `bork/wave_spawner.py`

Add `self.total_waves_completed: int = 0` and `self.boss_triggered: bool = False` to `__init__`. Increment `total_waves_completed` each time a wave finishes all its enemies. Set `boss_triggered = True` when `total_waves_completed >= BOSS_SPAWN_AFTER_WAVES`. Also reset these in `reset()`.

**Validation**:
- [ ] Lint passes
- [ ] Existing tests still pass
- [ ] Add test: `test_wave_spawner_counts_total_waves`
- [ ] Add test: `test_wave_spawner_boss_trigger_at_nine_waves`

---

### Step 4: Create EnemyProjectile Class

**Files**: `bork/boss_attacks.py`

Create `EnemyProjectile` class with `__init__(x, y, vx, vy, color, size, shape)`, `update(dt)`, `is_off_screen()`, and `draw()`. The draw method supports "diamond" and "circle" shapes using arcade primitives.

Also create attack factory functions:
- `create_spread_shot(x, y, target_x, target_y, count, speed, color) -> list[EnemyProjectile]` — fan of bullets toward target
- `create_aimed_shot(x, y, target_x, target_y, speed, color, size) -> list[EnemyProjectile]` — single bullet aimed at target
- `create_wing_shot(x, y, speed, color) -> list[EnemyProjectile]` — straight-left bullet

**Validation**:
- [ ] Lint passes
- [ ] `EnemyProjectile` follows entity pattern (update/draw/is_off_screen)
- [ ] Add tests: projectile moves correctly, goes off-screen correctly

---

### Step 5: Create Sentinel Boss Class

**Files**: `bork/boss.py`

Implement the `Sentinel` class with:

**State machine**: `entering` → `fighting` → `dying`

**Entering state**: Move left from off-screen to `SENTINEL_BATTLE_X` at `SENTINEL_ENTER_SPEED`. Transition to `fighting` when arrived.

**Fighting state**:
- Vertical player tracking (speed varies by phase)
- Phase calculation from `hp_fraction`
- Attack dispatch based on current phase and timer cooldowns
- Phase 1: spread shot (3 bullets, 2s) + wing sweep (alternating, 1.5s)
- Phase 2: spread shot (5 bullets, 1.5s) + aimed shot (1s) + wing barrage (if alive, 1.5s) + occasional horizontal lunge
- Phase 3: radial burst (7 bullets, 1.5s) + beam attack (1s charge, 4s cooldown)

**Hit handling**: `take_hit(part, damage)` reduces HP on the appropriate pool. Body hits apply `SENTINEL_BODY_DAMAGE_MULT`. Returns info dict about what happened (wing destroyed, etc.).

**Phase transitions**: Recalculated each frame from `hp_fraction` vs thresholds.

**Drawing**: Geometric shapes using arcade primitives — rectangles for body/wings with accent lines, circle for core with pulsing glow, beam charge-up glow effect.

**Validation**:
- [ ] Lint passes
- [ ] Under 500 lines
- [ ] Boss follows entity pattern
- [ ] Phase transitions at correct HP thresholds

---

### Step 6: Add Boss Explosion Factory

**Files**: `bork/explosions.py`

Add `create_boss_explosion(x, y) -> list[Particle]` — uses larger particle counts (50-80), bigger sizes (8-16), faster speeds (200-600), longer lifetimes (0.6-1.2s). Colors: mix of cyan, orange, yellow, white for dramatic effect.

Also add `create_boss_small_explosion(x, y) -> list[Particle]` — smaller pops used during the dying sequence (reuse enemy explosion params with slight color variation).

**Validation**:
- [ ] Lint passes

---

### Step 7: Add Boss Health Bar to HUD

**Files**: `bork/hud.py`

Add `draw_boss_health_bar(core_hp, core_max, left_wing_hp, right_wing_hp, boss_name, phase)` method:
- Centered at top of play area (`BOSS_HP_BAR_Y`)
- Boss name "SENTINEL" above bar in warning color
- Main bar: depletes left-to-right, color interpolates green → yellow → red based on HP fraction
- Optional: small wing health pips on either side of the main bar
- Phase indicator (subtle text or visual cue for current phase)
- Outline/border in `HUD_DIM` color

Also add `draw_warning_text(timer)` — pulses "WARNING" text at screen center.

Also add `draw_victory_text(boss_name, bonus_points)` — "SENTINEL DESTROYED" + point breakdown.

**Validation**:
- [ ] Lint passes
- [ ] HUD stays under 500 lines (currently 199, budget ~300 for additions)

---

### Step 8: Integrate Boss into Game Loop

**Files**: `bork/game.py`

This is the largest integration step. Changes:

**New fields in `__init__`/`setup()`:**
```python
self.boss: Sentinel | None = None
self.enemy_projectiles: list[EnemyProjectile] = []
self.boss_warning_timer: float = 0.0
self.player_hit_during_boss: bool = False
self.victory_timer: float = 0.0
```

**`on_update(dt)` additions:**

1. After wave spawner update: check `wave_spawner.boss_triggered` → transition to `STATE_BOSS_WARNING`
2. New `STATE_BOSS_WARNING` handler:
   - Tick `boss_warning_timer`, show warning text/edge flashes
   - When timer expires: create `Sentinel` off-screen right, transition to `STATE_BOSS_FIGHT`
3. New `STATE_BOSS_FIGHT` handler:
   - Skip `wave_spawner.update()` (no regular enemies)
   - `new_projectiles = boss.update(dt, player.x, player.y)` → extend `enemy_projectiles`
   - Update all `enemy_projectiles`, remove off-screen
   - `_check_projectile_boss_collisions()` — player shots vs boss parts
   - `_check_enemy_projectile_player_collisions()` — boss shots vs player
   - Check beam hit (if `boss.beam_active`)
   - On player hit: set `player_hit_during_boss = True`
   - On boss death (`boss.is_dead`): transition to `STATE_BOSS_DYING`
4. New `STATE_BOSS_DYING` handler:
   - Boss runs death animation timer
   - Spawn small explosions at random positions on boss body
   - After `BOSS_DEATH_DURATION`: final large explosion, screen shake, transition to `STATE_VICTORY`
5. New `STATE_VICTORY` handler:
   - Award points: core, wings (if destroyed), no-damage bonus
   - Display victory text
   - After `VICTORY_DISPLAY_DURATION`: freeze (for now; later transitions to next zone)

**New collision methods:**

`_check_projectile_boss_collisions()`:
- For each player projectile, check boss hit zones in priority: core → left wing → right wing → body
- On hit: remove projectile, `boss.take_hit(part, damage)`, spawn small particle burst
- On wing destroyed: `scoring.register_kill(SENTINEL_WING_POINTS)`, explosion at wing position

`_check_enemy_projectile_player_collisions()`:
- For each enemy projectile, `point_in_circle(proj, player, PLAYER_SHIP_SIZE)`
- On hit: remove projectile, apply damage (same as enemy collision — lives, invulnerability, etc.)
- Set `player_hit_during_boss = True`

**`on_draw()` additions:**
- Draw boss (after enemies, before player) in fighting/dying states
- Draw enemy projectiles
- Draw beam effect when visible
- Draw boss health bar (HUD layer, no shake)
- Draw warning overlay in `STATE_BOSS_WARNING`
- Draw victory overlay in `STATE_VICTORY`

**Validation**:
- [ ] Lint passes
- [ ] `game.py` stays under 500 lines — if approaching limit, extract boss-specific collision methods to a helper
- [ ] Existing tests still pass
- [ ] Game compiles and runs

---

### Step 9: Write Unit Tests

**Files**: `bork/tests/test_boss.py`

Tests:

**Wave trigger:**
- `test_boss_triggers_after_nine_waves` — run wave spawner through 9 waves, assert `boss_triggered`
- `test_boss_does_not_trigger_before_nine_waves` — 8 waves, assert not triggered

**Boss HP:**
- `test_sentinel_initial_hp` — core=50, wings=15 each
- `test_sentinel_core_takes_full_damage` — hit core, HP decreases by 1
- `test_sentinel_body_takes_reduced_damage` — hit body, core HP decreases by 0 (floor of 0.5)
- `test_sentinel_wing_takes_full_damage` — hit wing, wing HP decreases
- `test_sentinel_wing_destruction` — reduce wing to 0, assert `left_wing_alive == False`

**Phases:**
- `test_sentinel_starts_phase_1` — full HP, phase == 1
- `test_sentinel_phase_2_at_66_percent` — set core HP to 33, assert phase == 2
- `test_sentinel_phase_3_at_33_percent` — set core HP to 16, assert phase == 3

**Boss death:**
- `test_sentinel_dead_at_zero_hp` — set core HP to 0, assert `is_dead`

**Enemy projectile:**
- `test_enemy_projectile_moves_correctly` — update with dt, check position
- `test_enemy_projectile_off_screen` — move past edges, assert `is_off_screen()`

**Collision helper:**
- `test_point_in_rect_inside` — point inside rect returns True
- `test_point_in_rect_outside` — point outside returns False

**Validation**:
- [ ] All tests pass: `pytest bork/tests/test_boss.py -v`
- [ ] Lint passes on test file

---

### Step 10: Integration Test (Manual Play-test)

**Commands**:
```bash
python bork/game.py
```

**Validation**:
- [ ] Full integration test plan passes (see below)
- [ ] All automated tests pass: `pytest bork/tests/ -v`
- [ ] Lint clean: `ruff check bork/`

---

## Testing Requirements

### Unit Tests

- `test_boss_triggers_after_nine_waves`: WaveSpawner triggers boss at wave 9
- `test_boss_does_not_trigger_early`: No trigger at wave 8
- `test_sentinel_initial_hp`: Correct starting HP values
- `test_sentinel_core_full_damage`: Core takes 1 damage per hit
- `test_sentinel_body_reduced_damage`: Body hits apply 0.5x multiplier
- `test_sentinel_wing_damage_and_destruction`: Wings take damage and can be destroyed
- `test_sentinel_phase_transitions`: Phase changes at correct HP thresholds
- `test_sentinel_dead_at_zero_core_hp`: Boss death condition
- `test_enemy_projectile_movement`: Projectile moves by velocity * dt
- `test_enemy_projectile_offscreen`: Projectile reports off-screen correctly
- `test_point_in_rect`: Collision helper works for inside and outside

---

## Integration Test Plan

### Prerequisites

- Game running: `python bork/game.py`
- Player can survive 9 waves (or temporarily lower `BOSS_SPAWN_AFTER_WAVES` to 3 for testing)

### Test Steps

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Survive 9 waves of enemies | "WARNING" text pulses at screen center, edges flash red | ☐ |
| 2 | Wait through warning (1.5s) | Boss enters from right side, sliding to battle position | ☐ |
| 3 | Observe boss appearance | Geometric fortress with visible core (red glow), body, and two wings | ☐ |
| 4 | Check HUD | Boss health bar appears at top of screen, "SENTINEL" label visible | ☐ |
| 5 | Observe no regular enemies | No wave enemies spawn during boss fight | ☐ |
| 6 | Shoot boss body | Small impact, health decreases slowly (reduced damage) | ☐ |
| 7 | Shoot boss core | Health bar depletes faster (full damage) | ☐ |
| 8 | Observe Phase 1 attacks | 3-bullet spread shots + alternating wing shots | ☐ |
| 9 | Destroy one wing | Wing explodes, bonus points popup, wing attacks stop from that side | ☐ |
| 10 | Reduce HP to ~66% | Phase 2 begins — attacks become more aggressive, 5-bullet spread | ☐ |
| 11 | Observe Phase 2 aimed shots | Red bullets fire directly at player position | ☐ |
| 12 | Reduce HP to ~33% | Phase 3 begins — radial burst pattern, beam charge-up visible | ☐ |
| 13 | Observe beam telegraph | Core glows bright for 1 second before beam fires | ☐ |
| 14 | Dodge beam vertically | Horizontal beam crosses screen at player's previous Y position | ☐ |
| 15 | Get hit by beam (intentionally) | Player takes damage, invulnerability triggers | ☐ |
| 16 | Destroy boss core (0 HP) | Boss stops attacking, small explosions pop across body | ☐ |
| 17 | Wait through death sequence | Large final explosion, screen shake, "SENTINEL DESTROYED" text | ☐ |
| 18 | Check score awards | Core points (5,000) + wing points (1,000 each if destroyed) shown | ☐ |
| 19 | Replay and beat without taking damage | No-damage bonus (2,500) awarded | ☐ |
| 20 | Die during boss fight | Normal death/respawn, boss fight continues | ☐ |
| 21 | Lose all lives during boss | Game over screen, R to restart works | ☐ |

### Error Scenarios

| Scenario | How to Trigger | Expected Behavior | Pass? |
|----------|----------------|-------------------|-------|
| Player dies during warning | Get hit by lingering enemy projectile | Respawn, warning continues | ☐ |
| All lives lost during boss | Don't dodge boss attacks | Normal game over state, R restarts from beginning | ☐ |
| Both wings destroyed | Focus fire on wings | Wing attacks fully removed, boss still fights with core attacks | ☐ |
| Boss at edge of screen | Boss tracks player to top/bottom | Boss Y position clamped to screen bounds | ☐ |

---

## Error Handling

### Expected Errors

| Error | Cause | Handling |
|-------|-------|----------|
| Boss spawns off-screen | Entry animation start position wrong | Boss enters from `SCREEN_WIDTH + SENTINEL_WIDTH` |
| Beam hits through invulnerability | Player just respawned | Check `player.is_invulnerable` before beam damage |
| Projectile hits dead wing | Wing destroyed but hitbox still active | Skip collision check if `wing_alive == False` |
| Game over during boss fight | Player loses all lives | Transition to `STATE_GAME_OVER` normally, boss is discarded |

### Edge Cases

- **Boss HP exactly at threshold**: Phase transitions use `<=` (e.g., `hp_fraction <= 0.66` → Phase 2)
- **Multiple projectiles hit same frame**: Each projectile processed independently; boss can die mid-collision-loop, remaining projectiles skip
- **Player at screen edge during beam**: Beam fires at player.y at charge start, not fire time — player can dodge
- **Body damage rounding**: `int(damage * SENTINEL_BODY_DAMAGE_MULT)` — at 1 damage × 0.5 = 0.5, floored to 0. Body hits deal 0 damage per single shot. This is intentional (forces players to aim for core/wings). If this feels too punishing, bump to `max(1, int(...))` during tuning.
- **Victory during invulnerability blink**: Player may be blinking when victory triggers — stop blink and show player normally

---

## Cost Impact

N/A — local game, no API or infrastructure costs.

---

## Open Questions

None — the init-07 spec is comprehensive and all design decisions are resolved.

---

## Rollback Plan

If issues are discovered:
1. Revert the commit(s) from this PRP
2. The boss system is self-contained — removing `boss.py`, `boss_attacks.py`, and reverting changes to `game.py`, `constants.py`, `wave_spawner.py`, `collision.py`, `hud.py`, and `explosions.py` fully removes the feature
3. Verify: `pytest bork/tests/ -v` passes, game runs normally without boss

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 9 | Init spec is very detailed with exact values, attack patterns, timing |
| Feasibility | 9 | Architecture supports this — entity pattern, particle system, HUD all ready. Only new mechanic is enemy projectiles. |
| Completeness | 9 | Covers all aspects: spawn trigger, 3 phases, health, attacks, beam, death sequence, victory, scoring, testing |
| Alignment | 10 | Boss fights are explicitly Phase 4 in PLANNING.md, follows all ADRs |
| **Average** | **9.25** | |

---

## Notes

- `game.py` is currently 367 lines. Boss integration will add significant logic. If it approaches 500 lines, extract boss-specific collision and state handling into a `boss_fight.py` helper module.
- The body taking 0 damage from single hits (due to `int(1 * 0.5) = 0`) is a deliberate design choice that rewards precision aiming at the core. If play-testing reveals this is confusing, change to `max(1, ...)`.
- The beam attack's Y position is locked at charge start (when `beam_charging` begins), not when it fires. This gives the player the full 1-second charge window to dodge.
- Enemy projectiles (`self.enemy_projectiles`) are a new list in game.py. Future enemy types that shoot can also add to this list.
- Victory state currently freezes the game. init-08 (levels/progression) will replace this with a zone transition.
