# PRP-007b: Sentinel Redesign — Remove Wings, Simplify to Armor + Core Opening

**Created**: 2026-02-26
**Initial**: `initials/init-07-boss-fix.md`
**Status**: Complete

---

## Overview

### Problem Statement

The current Sentinel boss has wings as separate destructible components, adding complexity that doesn't match the intended design. The redesign simplifies the boss to a solid armored body with a horizontal core opening — shots through the opening deal 2x damage, shots hitting armor deal 1x. No wings, no wing attacks, no wing scoring.

Additionally, the init notes two behavior bugs to fix:
1. Existing enemies should continue scrolling during the warning sequence, not vanish
2. Core hitbox must be checked before armor in collision priority

### Proposed Solution

1. Remove all wing-related code, fields, constants, and HUD elements
2. Replace the wing visual with upper armor / lower armor / core opening layout
3. Change damage model: core opening = 2x damage, armor = 1x damage (both reduce core HP)
4. Remove wing points from scoring and victory display
5. Fix enemy clearing behavior during boss warning
6. Simplify the HUD health bar (no wing pips)

### Success Criteria

- [ ] Boss visual is a solid rectangle with a horizontal core opening in the center
- [ ] Shots hitting the core opening deal 2 damage to core HP
- [ ] Shots hitting upper/lower armor deal 1 damage to core HP
- [ ] No wing-related fields, constants, attacks, or scoring exist
- [ ] HUD health bar has no wing pips
- [ ] Victory screen shows core points and no-damage bonus only (no wing line)
- [ ] Enemies continue scrolling during boss warning, not instantly cleared
- [ ] All existing tests updated and passing
- [ ] Lint clean

---

## Context

### Related Documentation

- `initials/init-07-boss-fix.md` — Redesign specification
- `prps/prp-07-boss.md` — Original boss implementation PRP
- `docs/DECISIONS.md` — ADR-003 (geometric shapes), ADR-006 (entity pattern)

### Dependencies

- **Required**: init-07 boss implementation (already complete)

### Files to Modify

```
bork/boss.py              # MODIFY: Remove wings, new armor+opening layout and draw
bork/boss_fight.py         # MODIFY: Remove wing collision, simplify to core opening vs armor
bork/constants.py          # MODIFY: Remove SENTINEL_WING_*, add SENTINEL_CORE_DAMAGE/BODY_DAMAGE
bork/game.py               # MODIFY: Remove wing HP from HUD call, remove victory_wing_pts
bork/hud.py                # MODIFY: Remove wing pips from health bar, remove wing line from victory
bork/tests/test_boss.py    # MODIFY: Remove wing tests, add armor/opening damage tests
```

---

## Technical Specification

### Damage Model (replacing wing + body multiplier)

```python
# Replace old constants
# REMOVE: SENTINEL_WING_HP, SENTINEL_WING_WIDTH, SENTINEL_WING_HEIGHT,
#         SENTINEL_WING_COLOR, SENTINEL_WING_POINTS, SENTINEL_WING_INTERVAL,
#         SENTINEL_BODY_DAMAGE_MULT
# ADD:
SENTINEL_CORE_DAMAGE = 2    # shots through opening
SENTINEL_BODY_DAMAGE = 1    # shots hitting armor
```

### Collision Zones (simplified, 2 zones)

Priority order for player projectile hits:

1. **Core opening** — horizontal rect centered vertically on boss, narrow height (~20px), full body width. Uses `point_in_rect`. Deals `SENTINEL_CORE_DAMAGE` to core HP.
2. **Armor** — full body rect (`_BODY_WIDTH x _BODY_HEIGHT`). Deals `SENTINEL_BODY_DAMAGE` to core HP.

### Visual Layout

```
┌─────────────────────────┐
│      UPPER ARMOR        │  ← dark gray (80, 85, 95)
│                         │
├─────────────────────────┤
│   ═══════●═══════       │  ← recessed opening (20, 25, 35) with core glow
├─────────────────────────┤
│                         │
│      LOWER ARMOR        │  ← dark gray (80, 85, 95)
└─────────────────────────┘
```

### Constants Changes

```python
# REMOVE these constants entirely:
SENTINEL_WING_HP = 15
SENTINEL_WING_WIDTH = 30
SENTINEL_WING_HEIGHT = 80
SENTINEL_WING_COLOR = (80, 85, 95)
SENTINEL_WING_POINTS = 1000
SENTINEL_WING_INTERVAL = 1.5
SENTINEL_BODY_DAMAGE_MULT = 0.5

# ADD these constants:
SENTINEL_CORE_DAMAGE = 2      # damage per hit through opening
SENTINEL_BODY_DAMAGE = 1      # damage per hit on armor
SENTINEL_OPENING_HEIGHT = 20  # height of the core opening slot
SENTINEL_OPENING_COLOR = (20, 25, 35)  # dark recessed slot color
```

### Boss Fields to Remove

```python
# Remove from Sentinel.__init__:
self.left_wing_hp
self.right_wing_hp
self.left_wing_alive
self.right_wing_alive
self.wing_timer
self.wing_alternate
```

### Boss Methods to Remove

```python
_left_wing_pos()
_right_wing_pos()
_draw_wing()
_tick_wing_sweep()      # Phase 1 wing attack
_tick_wing_barrage()    # Phase 2 wing attack
```

### Boss take_hit Simplification

```python
def take_hit(self, part: str, damage: int) -> None:
    """Apply damage to core HP."""
    self.core_hp = max(0, self.core_hp - damage)
```

No return dict needed — no wing destruction events to report.

---

## Implementation Steps

### Step 1: Update Constants

**Files**: `bork/constants.py`

- Remove: `SENTINEL_WING_HP`, `SENTINEL_WING_WIDTH`, `SENTINEL_WING_HEIGHT`, `SENTINEL_WING_COLOR`, `SENTINEL_WING_POINTS`, `SENTINEL_WING_INTERVAL`, `SENTINEL_BODY_DAMAGE_MULT`
- Add: `SENTINEL_CORE_DAMAGE = 2`, `SENTINEL_BODY_DAMAGE = 1`, `SENTINEL_OPENING_HEIGHT = 20`, `SENTINEL_OPENING_COLOR = (20, 25, 35)`

**Validation**:
- [ ] Lint passes
- [ ] No remaining references to removed constants (grep check)

---

### Step 2: Simplify Sentinel Boss Class

**Files**: `bork/boss.py`

Remove all wing fields, wing position methods, wing drawing, and wing attack methods.

**`__init__`**: Remove `left_wing_hp`, `right_wing_hp`, `left_wing_alive`, `right_wing_alive`, `wing_timer`, `wing_alternate`. Remove import of wing constants.

**`take_hit`**: Simplify to just reduce core HP by the given damage amount. No part parameter needed — the caller passes the appropriate damage value. Change signature to `take_hit(self, damage: int) -> None`.

**`_update_attacks`**:
- Phase 1: spread shot only (remove `_tick_wing_sweep` call)
- Phase 2: spread shot + aimed shot only (remove `_tick_wing_barrage` call)
- Phase 3: unchanged (radial burst + beam)

**`draw`**: Replace wing drawing with new armor + opening layout:
- Draw full body rect in armor color `(80, 85, 95)`
- Draw horizontal opening slot (dark rect) at vertical center
- Draw core glow inside the opening slot
- Draw cyan accent lines on armor edges
- Remove `_draw_wing` method entirely

**Validation**:
- [ ] Lint passes
- [ ] Under 500 lines
- [ ] No references to wings remain

---

### Step 3: Simplify Boss Fight Collision Logic

**Files**: `bork/boss_fight.py`

**`check_projectile_boss_collisions`**: Replace 4-zone collision (core → left wing → right wing → body) with 2-zone collision:
1. Core opening: `point_in_rect(proj.x, proj.y, boss.x, boss.y, _BODY_WIDTH, SENTINEL_OPENING_HEIGHT)` → `boss.take_hit(SENTINEL_CORE_DAMAGE)`
2. Armor: `point_in_rect(proj.x, proj.y, boss.x, boss.y, _BODY_WIDTH, _BODY_HEIGHT)` → `boss.take_hit(SENTINEL_BODY_DAMAGE)`

Remove all wing collision code, wing destruction scoring, and wing explosion spawning.

Remove imports: `SENTINEL_WING_HEIGHT`, `SENTINEL_WING_POINTS`, `SENTINEL_WING_WIDTH`.
Add imports: `SENTINEL_CORE_DAMAGE`, `SENTINEL_BODY_DAMAGE`, `SENTINEL_OPENING_HEIGHT`.

**`_award_boss_victory_points`**: Remove wing points tracking. Set `game.victory_wing_pts = 0` always (or remove field entirely).

**Fix enemy clearing during warning**: In `update_boss_warning`, when `boss_warning_timer <= 0`, do NOT set `game.enemies = []`. Let enemies continue until they scroll off-screen naturally during the boss fight state.

**Validation**:
- [ ] Lint passes
- [ ] Core opening hits deal 2 damage
- [ ] Armor hits deal 1 damage

---

### Step 4: Simplify Game Integration

**Files**: `bork/game.py`

- Remove `self.victory_wing_pts` field from `__init__` and `setup` (or keep as 0, never set)
- Update `draw_boss_health_bar` call: remove `left_wing_hp` and `right_wing_hp` arguments
- Update `draw_victory_text` call: pass `wing_pts=0` or remove the parameter

**Validation**:
- [ ] Lint passes
- [ ] Game compiles

---

### Step 5: Simplify HUD

**Files**: `bork/hud.py`

**`draw_boss_health_bar`**: Remove `left_wing_hp` and `right_wing_hp` parameters. Remove wing pip rendering (the two small circles flanking the health bar).

**`draw_victory_text`**: Remove the `wing_pts` parameter and the conditional "Wings:" line.

**Validation**:
- [ ] Lint passes
- [ ] No wing-related rendering remains

---

### Step 6: Update Tests

**Files**: `bork/tests/test_boss.py`

**Remove tests**:
- `test_sentinel_wing_takes_full_damage`
- `test_sentinel_wing_destruction`
- `test_sentinel_right_wing_destruction`

**Modify tests**:
- `test_sentinel_initial_hp`: Remove wing HP assertions
- `test_sentinel_body_takes_reduced_damage` → rename to `test_sentinel_armor_takes_1_damage`: hit with `SENTINEL_BODY_DAMAGE`, assert core HP decreases by 1
- `test_sentinel_body_higher_damage_applies_multiplier` → rename to `test_sentinel_core_opening_takes_2_damage`: hit with `SENTINEL_CORE_DAMAGE`, assert core HP decreases by 2

**Add tests**:
- `test_sentinel_has_no_wing_fields`: assert `Sentinel` has no `left_wing_hp` attribute
- `test_sentinel_take_hit_reduces_core_hp`: verify `take_hit(2)` reduces core HP by 2
- `test_sentinel_take_hit_floors_at_zero`: verify core HP doesn't go below 0

**Validation**:
- [ ] All tests pass
- [ ] Lint passes

---

### Step 7: Final Validation and Commit

**Commands**:
```bash
pytest bork/tests/ -v
ruff check bork/
python bork/game.py  # manual play-test
```

**Validation**:
- [ ] All tests pass
- [ ] Lint clean
- [ ] Boss plays correctly with new visual and damage model

---

## Testing Requirements

### Unit Tests

- `test_sentinel_initial_hp`: Core HP = 50, no wing fields
- `test_sentinel_core_opening_takes_2_damage`: Hit with `SENTINEL_CORE_DAMAGE`, core HP decreases by 2
- `test_sentinel_armor_takes_1_damage`: Hit with `SENTINEL_BODY_DAMAGE`, core HP decreases by 1
- `test_sentinel_take_hit_floors_at_zero`: Core HP never goes below 0
- `test_sentinel_has_no_wing_fields`: No `left_wing_hp` attribute exists
- `test_sentinel_phase_transitions`: Still work at correct HP thresholds
- `test_sentinel_dead_at_zero_hp`: Boss death condition unchanged

---

## Integration Test Plan

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Survive 9 waves | WARNING text appears, existing enemies continue scrolling | ☐ |
| 2 | Observe boss | Solid body with horizontal slot, no protruding wings | ☐ |
| 3 | Shoot center slot | Health bar depletes faster (2x damage) | ☐ |
| 4 | Shoot armor (top/bottom) | Health bar depletes slower (1x damage) | ☐ |
| 5 | Check HUD | Health bar has no wing pips on sides | ☐ |
| 6 | Destroy boss | Victory shows core points + no-damage bonus only, no "Wings:" line | ☐ |

---

## Error Handling

### Edge Cases

- **Boss HP exactly at threshold with 2-damage hit**: Phase transition uses `<=`, so a 2-damage hit crossing a threshold still works
- **Core opening overlaps with armor rect**: Core opening check runs first, so a projectile hitting the opening area only deals opening damage, not both

---

## Cost Impact

N/A — local game.

---

## Open Questions

None — the init spec is clear and self-contained.

---

## Rollback Plan

1. Revert the commit
2. Original boss code (with wings) is restored
3. Verify: tests pass, game runs

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 10 | Init spec is very specific — remove wings, 2-zone damage, exact colors |
| Feasibility | 10 | Pure simplification — removing code, not adding complexity |
| Completeness | 9 | Covers all files, all wing references, all tests |
| Alignment | 10 | Follows all ADRs, simplifies existing design |
| **Average** | **9.75** | |

---

## Notes

- The wave count "bug" from the init spec is NOT actually a bug — `total_waves_completed` increments after each wave's full enemy batch spawns. The count correctly represents 9 complete spawn rounds. No fix needed.
- The enemy clearing behavior during warning IS a real issue — `update_boss_warning` sets `game.enemies = []` when transitioning to boss fight. The fix removes that line so enemies scroll off naturally.
- The `take_hit` method signature changes from `(self, part: str, damage: float) -> dict` to `(self, damage: int) -> None`. All callers in `boss_fight.py` must be updated.
- Wing attack removal means Phase 1 has only spread shots and Phase 2 has only spread + aimed shots. This may make the boss slightly easier — can be tuned later by adjusting intervals or adding new non-wing attacks.
