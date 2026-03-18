# PRP-08d: Zone 2 Boss — The Marauder

**Created**: 2026-03-17
**Initial**: `initials/init-08d-zone2-boss.md`
**Status**: Draft

---

## Overview

### Problem Statement
Zone 2 currently uses the Sentinel as a placeholder boss. It needs its own boss that matches Zone 2's aggressive identity — faster, more erratic, with green-themed visuals matching the Dart enemies. The current boss_fight.py hardcodes Sentinel instantiation and collision dimensions.

### Proposed Solution
Create the Marauder boss entity with the same interface as the Sentinel (update/draw/take_hit, same state and phase properties). Make boss_fight.py boss-type-agnostic by using a factory function and reading collision dimensions from the boss instance. Update Zone 2 config to `boss_type: "marauder"`.

### Key Design Decision
The Marauder shares the same game states (`STATE_BOSS_WARNING`, `STATE_BOSS_FIGHT`, `STATE_BOSS_DYING`, `STATE_VICTORY`) and the same boss_fight.py handlers as the Sentinel. This means:
- No new game states needed
- game.py needs zero changes to state dispatch or drawing
- boss_fight.py needs a factory function and parameterized collision dimensions
- The Marauder class must expose the same properties/methods as Sentinel

### Success Criteria
- [ ] Marauder spawns in Zone 2 after waves complete (warning + 5s delay)
- [ ] Hull renders as forward-swept green-accented polygon (facing left) with core gap
- [ ] Boss patrols vertically in sinusoidal path
- [ ] Phase 1: 3-way spread fire every 1.8s
- [ ] Phase 2 (HP ≤ 50%): faster spread + diagonal cross burst every 4s
- [ ] Phase 3 (HP ≤ 25%): all above + 180° arc burst every 6s, faster patrol
- [ ] Core opening deals 2× damage, armor deals 1× damage
- [ ] Death sequence: staggered sub-explosions, hull vanishes at finale (ADR-012)
- [ ] Boss health bar shows "MARAUDER" label
- [ ] Zone 3 begins after Marauder victory
- [ ] Zone 1 still spawns Sentinel (no regression)
- [ ] `marauder.py` under 300 lines, `boss_fight.py` under 500 lines
- [ ] All constants in constants.py

---

## Context

### Related Documentation
- `docs/DECISIONS.md` — ADR-009 (2-zone damage), ADR-010 (polygon hulls), ADR-011 (layered exhaust), ADR-012 (multi-burst death)
- `prps/prp-08a-zone-infrastructure.md` — Zone system (complete)
- `prps/prp-08b-zone2-content.md` — Zone 2 content (complete)

### Dependencies
- **Required**: PRP-08a (zone infrastructure) ✓, PRP-08b (Zone 2 content) ✓
- **Required**: EnemyProjectile in `enemy_projectile.py` ✓
- **Required**: Boss attack factories in `boss_attacks.py` ✓

### Files to Modify/Create
```
bork/constants.py       # Add MARAUDER_* constants
bork/marauder.py        # NEW: Marauder boss entity
bork/boss_fight.py      # Boss factory function, parameterized collision dimensions
bork/game.py            # Update boss health bar to use boss properties (minimal)
bork/tests/test_marauder.py  # NEW: Marauder tests
```

---

## Technical Specification

### Boss Interface Contract

Both Sentinel and Marauder must expose:

```python
class Boss:
    x: float
    y: float
    core_hp: int
    max_hp: int           # NEW — needed for health bar (Sentinel uses global constant)
    state: str            # "entering", "fighting", "dying"
    phase: int            # 1, 2, 3
    time_alive: float
    death_timer: float
    beam_visible_timer: float  # 0.0 for bosses without beams
    beam_y: float              # unused for Marauder, but must exist for interface

    # Collision dimensions
    opening_width: float   # NEW — width of core opening hit zone
    opening_height: float  # NEW — height of core opening hit zone
    armor_width: float     # NEW — width of armor bounding box
    armor_height: float    # NEW — height of armor bounding box
    core_damage: int       # NEW — damage per core hit
    body_damage: int       # NEW — damage per armor hit
    name: str              # NEW — "SENTINEL" or "MARAUDER" for HUD

    @property
    def hp_fraction(self) -> float: ...
    @property
    def is_dead(self) -> bool: ...

    def update(self, dt, player_x, player_y) -> list[EnemyProjectile]: ...
    def take_hit(self, damage: int) -> None: ...
    def draw(self) -> None: ...
```

Adding `max_hp`, `name`, collision dimensions, and damage values as instance properties lets boss_fight.py be fully boss-agnostic.

### Marauder Entity

```python
class Marauder:
    """Zone 2 boss — aggressive attack craft with sinusoidal patrol."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.core_hp = MARAUDER_HP
        self.max_hp = MARAUDER_HP
        self.state = "entering"
        self.phase = 1
        self.name = "MARAUDER"
        # Collision dimensions
        self.opening_width = MARAUDER_WIDTH
        self.opening_height = 16  # gap height
        self.armor_width = MARAUDER_WIDTH
        self.armor_height = MARAUDER_HEIGHT
        self.core_damage = 2
        self.body_damage = 1
        # Beam interface (unused, required for compatibility)
        self.beam_visible_timer = 0.0
        self.beam_y = 0.0
        # Movement & timers...
```

### Constants

All `MARAUDER_*` constants as specified in the init file, plus:

```python
MARAUDER_ENTER_SPEED = 150.0  # px/sec slide-in from right
MARAUDER_HULL_STROKE = (80, 200, 120)  # green hull outline
MARAUDER_PLATE_STROKE = (60, 160, 90)  # green plate outline
```

### Zone 2 Config Update

```python
2: {
    ...
    "boss_type": "marauder",  # was "sentinel"
}
```

---

## Implementation Steps

### Step 1: Add Marauder constants
**Files**: `bork/constants.py`

Add all `MARAUDER_*` constants (HP, dimensions, movement, phases, shooting intervals, colors, exhaust layers, hull stroke colors). Update Zone 2 config `boss_type` to `"marauder"`.

**Validation**:
- [ ] `ruff check bork/constants.py` passes
- [ ] Zone 1 config still has `boss_type: "sentinel"`

---

### Step 2: Add interface properties to Sentinel
**Files**: `bork/boss.py`

Add the new interface properties to Sentinel so boss_fight.py can read them generically:
- `self.max_hp = SENTINEL_CORE_HP`
- `self.name = "SENTINEL"`
- `self.opening_width = 100` (current hardcoded value in boss_fight.py)
- `self.opening_height = SENTINEL_OPENING_HEIGHT`
- `self.armor_width = 100`
- `self.armor_height = 80`
- `self.core_damage = SENTINEL_CORE_DAMAGE`
- `self.body_damage = SENTINEL_BODY_DAMAGE`

**Validation**:
- [ ] `ruff check bork/boss.py` passes
- [ ] Existing tests pass (no behavior change)

---

### Step 3: Create Marauder entity
**Files**: `bork/marauder.py` (NEW)

Implement the Marauder class following the boss interface:

**Movement**: Sinusoidal patrol on Y axis at fixed X. Enter from right edge, stop at `MARAUDER_X`. Patrol frequency increases with phase. Clamp patrol Y to `[MARAUDER_HEIGHT / 2 + margin, SCREEN_HEIGHT - MARAUDER_HEIGHT / 2 - margin]` to prevent hull clipping off-screen at high amplitude values.

**Phases**:
- Phase 1 (HP > 50%): 3-way spread every 1.8s
- Phase 2 (50% ≥ HP > 25%): faster spread (1.2s) + diagonal cross burst (4s)
- Phase 3 (HP ≤ 25%): fastest spread (0.8s) + diagonal (4s) + 180° arc burst (6s), doubled patrol frequency

**Drawing**: Mirrored polygon hull halves (top/bottom) with inner plate, green nose ellipse, weapon ports, panel lines. Engine exhaust from `MARAUDER_EXHAUST_LAYERS`.

Use `create_spread_shot` and `create_radial_burst` from `boss_attacks.py` for attacks.

**Validation**:
- [ ] `ruff check bork/marauder.py` passes
- [ ] Under 300 lines
- [ ] Import succeeds

---

### Step 4: Make boss_fight.py boss-agnostic
**Files**: `bork/boss_fight.py`

1. Add boss factory function:
   ```python
   def create_boss(boss_type: str, x: float, y: float):
       if boss_type == "marauder":
           from bork.marauder import Marauder
           return Marauder(x, y)
       from bork.boss import Sentinel
       return Sentinel(x, y)
   ```

2. In `update_boss_warning()`: Replace `Sentinel(...)` with `create_boss(config["boss_type"], ...)`. Get width from config or boss instance for spawn X offset.

3. In `check_projectile_boss_collisions()`: Replace hardcoded `100, SENTINEL_OPENING_HEIGHT` and `100, 80` with `boss.opening_width, boss.opening_height` and `boss.armor_width, boss.armor_height`. Replace `SENTINEL_CORE_DAMAGE` / `SENTINEL_BODY_DAMAGE` with `boss.core_damage` / `boss.body_damage`.

4. In `check_beam_player_collision()`: Add guard `if boss.beam_visible_timer <= 0: return` (already exists, works for Marauder since beam_visible_timer is always 0).

5. Remove Sentinel-specific imports that are now read from boss instance.

**Validation**:
- [ ] `ruff check bork/boss_fight.py` passes
- [ ] Under 500 lines
- [ ] Zone 1 Sentinel fight unchanged

---

### Step 5: Update game.py boss health bar
**Files**: `bork/game.py`

Replace hardcoded Sentinel references in boss health bar and victory text with boss instance properties:

```python
# Health bar — use boss.max_hp and boss.name instead of SENTINEL_CORE_HP, "SENTINEL"
if self.boss and self.state in (STATE_BOSS_FIGHT, STATE_BOSS_DYING):
    self.hud.draw_boss_health_bar(
        self.boss.core_hp,
        self.boss.max_hp,
        self.boss.name,
        self.boss.phase,
    )
```

Remove `SENTINEL_CORE_HP` import if no longer needed.

**Validation**:
- [ ] `ruff check bork/game.py` passes
- [ ] Health bar works for both boss types

---

### Step 6: Write tests
**Files**: `bork/tests/test_marauder.py` (NEW)

- `test_marauder_initial_state`: HP, state, phase, position
- `test_marauder_enters_from_right`: x decreases during "entering" state
- `test_marauder_stops_at_battle_x`: Stops at MARAUDER_X, transitions to "fighting"
- `test_marauder_patrols_vertically`: Y oscillates during fighting state
- `test_marauder_phase_transitions`: Phase changes at HP thresholds
- `test_marauder_takes_damage`: take_hit reduces core_hp
- `test_marauder_is_dead`: is_dead True at 0 HP
- `test_marauder_fires_projectiles`: Returns projectiles from update during fighting
- `test_marauder_phase1_spread_count`: Phase 1 fires 3 projectiles per volley
- `test_marauder_phase2_diagonal_count`: Phase 2 diagonal burst fires 4 projectiles
- `test_marauder_phase3_arc_count`: Phase 3 arc burst fires 6 projectiles
- `test_marauder_interface_properties`: Has all required interface properties (name, max_hp, collision dims)
- `test_boss_factory_sentinel`: create_boss("sentinel", ...) returns Sentinel
- `test_boss_factory_marauder`: create_boss("marauder", ...) returns Marauder

**Validation**:
- [ ] `pytest bork/tests/ -v` — all tests pass

---

### Step 7: Manual play-test and commit

**Validation**:
- [ ] Zone 1: Sentinel fight unchanged
- [ ] Zone 2: Marauder appears, green hull, patrols vertically
- [ ] Phase 1: 3-way spread works
- [ ] Phase 2: faster spread + diagonal burst
- [ ] Phase 3: all attacks + arc burst, faster patrol
- [ ] Core opening hit zone works (2× damage visible in HP bar)
- [ ] Death sequence: staggered explosions, hull vanishes
- [ ] Victory → Zone 3 transition
- [ ] Health bar shows "MARAUDER"

**Commit**: `feat: Zone 2 boss — Marauder with patrol movement and phased attacks`

---

## Testing Requirements

### Unit Tests
- `test_marauder_initial_state`: Correct HP, state, phase defaults
- `test_marauder_enters_from_right`: X decreases during entering
- `test_marauder_stops_at_battle_x`: Transitions to fighting at correct X
- `test_marauder_patrols_vertically`: Y changes during fighting
- `test_marauder_phase_transitions`: Phase 1→2→3 at HP thresholds
- `test_marauder_takes_damage`: HP decreases on hit
- `test_marauder_is_dead`: True when HP = 0
- `test_marauder_fires_projectiles`: Returns projectiles during fighting
- `test_marauder_phase1_spread_count`: Phase 1 volley returns exactly 3 projectiles
- `test_marauder_phase2_diagonal_count`: Phase 2 diagonal burst returns exactly 4 projectiles
- `test_marauder_phase3_arc_count`: Phase 3 arc burst returns exactly 6 projectiles
- `test_marauder_interface_properties`: All required properties exist
- `test_boss_factory`: Returns correct type for each boss_type string

### Integration Tests (Manual)
- Zone 1 → Sentinel (unchanged)
- Zone 2 → Marauder spawns with warning
- Marauder patrols, shoots, takes damage
- Phase transitions with screen flash
- Death sequence matches ADR-012
- Zone 3 loads after victory

---

## Integration Test Plan

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Play through Zone 1, beat Sentinel | Zone 2 loads | ☐ |
| 2 | Play Zone 2 waves, observe warning | "WARNING" text, Marauder slides in from right | ☐ |
| 3 | Observe Marauder visuals | Green-accented hull, forward-swept, gap visible | ☐ |
| 4 | Observe movement | Vertical sinusoidal patrol | ☐ |
| 5 | Phase 1 attacks | 3-way green spread from nose | ☐ |
| 6 | Damage to 50% HP | Phase 2: faster spread + diagonal bursts | ☐ |
| 7 | Damage to 25% HP | Phase 3: arc burst added, faster patrol | ☐ |
| 8 | Shoot through core gap | Health drops faster (2× damage) | ☐ |
| 9 | Kill Marauder | Staggered explosions → hull vanishes → victory | ☐ |
| 10 | Victory screen | Points displayed, Zone 3 loads | ☐ |
| 11 | Health bar | Shows "MARAUDER", phases indicated | ☐ |

---

## Error Handling

### Edge Cases
- **Marauder beam interface**: `beam_visible_timer` always 0.0, so beam collision check is a no-op
- **Boss factory unknown type**: Default to Sentinel (safe fallback)
- **Phase transition during entering**: Can't happen (HP only decreases during fighting)
- **Patrol off-screen**: Clamp Y to screen bounds with margin

---

## Cost Impact

N/A — local game.

---

## Open Questions

All resolved:
- ~~Patrol vs. charge?~~ → Sinusoidal patrol only for first pass (per init recommendation)
- ~~Cross burst aimed or fixed?~~ → Fixed 45° angles (per init recommendation)
- ~~Zone 2 wave count?~~ → constants.py has `waves_before_boss: 12` for Zone 2 (set by PRP-08a). The init spec assumed 9 but 12 is the live value. Play-testing should validate whether 12 waves feels right before the Marauder appears.

---

## Rollback Plan

1. Revert commits
2. Remove `marauder.py` and `test_marauder.py`
3. Restore Zone 2 config `boss_type: "sentinel"`
4. Revert boss_fight.py collision hardcoding
5. Revert Sentinel interface additions
6. Verify: `pytest bork/tests/ -v` passes

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 9 | Init spec is very detailed with exact vertices, constants, and phases |
| Feasibility | 9 | Same interface as Sentinel, boss_fight.py parameterization is straightforward |
| Completeness | 9 | All files, tests, edge cases covered |
| Alignment | 10 | Follows ADR-009 (damage model), ADR-010 (polygon hulls), ADR-011 (exhaust), ADR-012 (death) |
| **Average** | **9.25** | |

---

## Notes

- The Marauder has no beam attack (unlike Sentinel Phase 3). The `beam_visible_timer` and `beam_y` properties exist but remain at 0.0 to satisfy the interface.
- The boss factory function uses lazy imports to avoid circular dependencies and keep the module lightweight.
- game.py changes are minimal — just replacing `SENTINEL_CORE_HP` and `"SENTINEL"` with `self.boss.max_hp` and `self.boss.name`. No new state dispatch needed.
- `marauder.py` target is under 300 lines. The Sentinel (boss.py) is 410 lines, but the Marauder has no beam attack and simpler drawing, so 250-280 is realistic.
