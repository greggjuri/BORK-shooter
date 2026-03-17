# PRP-009: Tiered Powerup System

**Created**: 2026-03-17
**Initial**: `initials/init-09-powerup-tiers.md`
**Status**: Complete

---

## Overview

### Problem Statement
The current powerup system is binary — the player either has a speed boost (1.35x) or doesn't. There's no progression arc, no meaningful death penalty beyond losing a life, and no fire rate powerup at all. This makes powerup collection feel flat and death stakes feel low.

### Proposed Solution
Replace the single `speed_multiplier` float with a tiered level system. Both speed and fire rate have 3 levels (1 = base, 2 = boosted, 3 = max). Collecting a speed powerup raises the speed level by 1 (capped at 3). On death, both levels drop by 1 (floored at 1). The HUD shows current SPD and ROF levels. Fire rate powerup pickups aren't spawned yet, but the level system is fully wired so adding the pickup later is trivial.

### Success Criteria
- [ ] Player speed has 3 distinct tiers with noticeably different feel
- [ ] Fire rate has 3 distinct tiers with noticeably different feel
- [ ] Collecting speed powerup raises speed level by 1 (capped at 3)
- [ ] Collecting speed powerup at max level still triggers collection effect (particles) but no stat change
- [ ] On death, both speed_level and fire_rate_level decrement by 1 (min 1)
- [ ] Death penalty applies in both normal play and boss fight
- [ ] HUD shows SPD and ROF level indicators in sci-fi style
- [ ] Speed powerup visual has glassy button + white "S" letter
- [ ] All tier values are in constants.py (no magic numbers)
- [ ] All existing tests updated and passing
- [ ] New tests for tier logic

---

## Context

### Related Documentation
- `docs/PLANNING.md` — Phase 4 (Content), design principles
- `docs/DECISIONS.md` — ADR-005 (constants centralized), ADR-006 (entity pattern)
- `initials/init-09-powerup-tiers.md` — Feature specification

### Dependencies
- **Required**: init-03 (powerup system) ✓, init-05 (HUD) ✓
- **Optional**: Fire rate powerup pickup entity (future — this PRP only wires the level system)

### Files to Modify/Create
```
bork/constants.py       # Add SPEED_LEVELS, FIRE_RATE_LEVELS, HUD tier indicator constants
bork/player.py          # Replace speed_multiplier with speed_level/fire_rate_level, add downgrade_on_death()
bork/game.py            # Update powerup collection, death handling, _get_active_powerups, HUD call
bork/powerup.py         # Add white "S" letter to glassy button
bork/hud.py             # Add _draw_tier_indicators() method, update draw() signature
bork/boss_fight.py      # Add tier downgrade in _handle_player_hit()
bork/tests/test_player.py    # Update speed tests, add tier tests
bork/tests/test_powerup.py   # Existing tests still pass
```

---

## Technical Specification

### Data Models

**Player (modified)**:
```python
# Remove:
self.speed_multiplier = 1.0

# Add:
self.speed_level: int = 1   # 1-3, index into SPEED_LEVELS
self.fire_rate_level: int = 1  # 1-3, index into FIRE_RATE_LEVELS
```

**Constants (new)**:
```python
# Speed tiers: max speed values per level
SPEED_LEVELS = (350.0, 470.0, 590.0)  # base, +34%, +69%

# Fire rate tiers: shoot cooldown values per level (lower = faster)
FIRE_RATE_LEVELS = (0.36, 0.24, 0.14)  # base (current), medium, fast

# HUD tier indicator constants
HUD_TIER_Y = 30  # Y position for tier indicators
HUD_TIER_FONT_SIZE = 11
HUD_TIER_LABEL_COLOR = (0, 255, 255)  # cyan (matches HUD_PRIMARY)
HUD_TIER_ACTIVE_COLOR = (0, 255, 180)  # bright teal for filled pips
HUD_TIER_INACTIVE_COLOR = (40, 60, 70)  # dim for unfilled pips
```

### State Changes

**Player state**:
- `speed_multiplier` (float) → `speed_level` (int, 1-3)
- New: `fire_rate_level` (int, 1-3)
- New: `max_speed` property that returns `SPEED_LEVELS[self.speed_level - 1]`
- New: `shoot_cooldown` property that returns `FIRE_RATE_LEVELS[self.fire_rate_level - 1]`
- New: `downgrade_on_death()` method

**Game state**:
- `_get_active_powerups()` → returns dict `{"speed_level": int, "fire_rate_level": int}` instead of `list[str]`
- Powerup collection calls `player.speed_level = min(3, player.speed_level + 1)` instead of setting multiplier

**HUD**:
- `draw()` receives tier levels instead of active powerup list
- New `_draw_tier_indicators()` renders SPD/ROF pips at bottom of screen

---

## Implementation Steps

### Step 1: Add tier constants
**Files**: `bork/constants.py`

Add after existing powerup constants:

```python
# Powerup tier levels
SPEED_LEVELS = (350.0, 470.0, 590.0)  # max speed per tier
FIRE_RATE_LEVELS = (0.36, 0.24, 0.14)  # shoot cooldown per tier (lower = faster)
POWERUP_LABEL_COLOR = (255, 255, 255, 220)  # white letter on glassy button

# HUD tier indicators
HUD_TIER_Y = 30
HUD_TIER_FONT_SIZE = 11
HUD_TIER_ACTIVE_COLOR = (0, 255, 180)
HUD_TIER_INACTIVE_COLOR = (40, 60, 70)
```

Remove `SPEED_BOOST_MULTIPLIER` (no longer used). Keep `PLAYER_MAX_SPEED` as it's referenced in tests and serves as the level 1 base (should equal `SPEED_LEVELS[0]`).

**Validation**:
- [ ] `ruff check bork/constants.py` passes
- [ ] `SPEED_LEVELS[0]` equals `PLAYER_MAX_SPEED`
- [ ] `FIRE_RATE_LEVELS[0]` equals `SHOOT_COOLDOWN`

---

### Step 2: Replace player speed_multiplier with tier levels
**Files**: `bork/player.py`

1. Replace `self.speed_multiplier = 1.0` with:
   ```python
   self.speed_level: int = 1
   self.fire_rate_level: int = 1
   ```

2. Add imports for `SPEED_LEVELS` and `FIRE_RATE_LEVELS`.

3. In `update()`, replace speed_multiplier usage:
   ```python
   # Replace: self.vx += ax * self.speed_multiplier * dt
   # With:
   self.vx += ax * dt
   self.vy += ay * dt

   # Replace: max_speed = PLAYER_MAX_SPEED * self.speed_multiplier
   # With:
   max_speed = SPEED_LEVELS[self.speed_level - 1]
   ```

   Note: acceleration no longer scales with speed level — only max speed does. This keeps input responsiveness consistent; higher tiers just have a higher ceiling.

4. In `reset_shoot_timer()`, replace:
   ```python
   # Replace: self.shoot_timer = SHOOT_COOLDOWN
   # With:
   self.shoot_timer = FIRE_RATE_LEVELS[self.fire_rate_level - 1]
   ```

5. Add death penalty method:
   ```python
   def downgrade_on_death(self) -> None:
       """Drop both tier levels by 1 on death (min 1)."""
       self.speed_level = max(1, self.speed_level - 1)
       self.fire_rate_level = max(1, self.fire_rate_level - 1)
   ```

**Validation**:
- [ ] `ruff check bork/player.py` passes
- [ ] `python -c "from bork.player import PlayerShip"` succeeds
- [ ] Player update tests updated and passing

---

### Step 3: Update game.py powerup collection and death handling
**Files**: `bork/game.py`

1. **Powerup collection** — Replace `_check_powerup_player_collisions()`:
   ```python
   # Replace:
   if self.player.speed_multiplier <= 1.0:
       self.player.speed_multiplier = SPEED_BOOST_MULTIPLIER
   # With:
   if p.kind == "speed":
       self.player.speed_level = min(3, self.player.speed_level + 1)
   ```
   Remove `SPEED_BOOST_MULTIPLIER` import. The collection always triggers particles regardless of current level.

2. **Death handling** — In `_check_enemy_player_collisions()`, after respawn position reset, add:
   ```python
   self.player.downgrade_on_death()
   ```

3. **Active powerups for HUD** — Replace `_get_active_powerups()`:
   ```python
   def _get_tier_levels(self) -> tuple[int, int]:
       """Return (speed_level, fire_rate_level) for HUD display."""
       return (self.player.speed_level, self.player.fire_rate_level)
   ```

4. **HUD call** — Update the `hud.draw()` call to pass tier levels instead of active powerup list.

5. **Game reset** — In `_reset_game()` or equivalent, ensure player levels reset to 1 (handled by Player.__init__).

**Validation**:
- [ ] `ruff check bork/game.py` passes
- [ ] No references to `speed_multiplier` or `SPEED_BOOST_MULTIPLIER` remain
- [ ] Collecting powerup at level 3 still triggers particle burst

---

### Step 4: Update boss_fight.py death handling
**Files**: `bork/boss_fight.py`

In `_handle_player_hit()`, after the respawn block (setting position, velocity, invulnerability), add:
```python
game.player.downgrade_on_death()
```

**Validation**:
- [ ] `ruff check bork/boss_fight.py` passes
- [ ] Death during boss fight downgrades tiers

---

### Step 5: Add "S" letter to powerup visual
**Files**: `bork/powerup.py`

Add a white "S" letter centered in the glassy button, drawn after the inner circle but before the highlight:

```python
arcade.draw_text(
    "S", cx, cy, POWERUP_LABEL_COLOR,
    font_size=int(r * 0.8), bold=True,
    anchor_x="center", anchor_y="center",
)
```

Import `POWERUP_LABEL_COLOR` from constants.

**Validation**:
- [ ] `ruff check bork/powerup.py` passes
- [ ] Visual: white "S" visible on glassy teal button

---

### Step 6: Add HUD tier indicators
**Files**: `bork/hud.py`

1. Update `draw()` signature to accept `speed_level: int` and `fire_rate_level: int` instead of `active_powerups: list[str]`.

2. Replace `_draw_powerups()` with `_draw_tier_indicators()`:
   - Position at bottom of screen (`HUD_TIER_Y`)
   - Draw "SPD" label + 3 pips (filled/unfilled based on level)
   - Draw "ROF" label + 3 pips
   - Use `HUD_TIER_ACTIVE_COLOR` for filled, `HUD_TIER_INACTIVE_COLOR` for unfilled
   - Small rectangles or circles for pips, spaced evenly
   - Match existing sci-fi HUD style (cyan, geometric)

Example layout:
```
SPD ■ ■ □     ROF ■ □ □
```

**Validation**:
- [ ] `ruff check bork/hud.py` passes
- [ ] HUD renders at bottom without overlapping other elements
- [ ] Pips update when speed level changes

---

### Step 7: Update tests
**Files**: `bork/tests/test_player.py`, `bork/tests/test_powerup.py`

1. **test_player.py** — Update existing speed_multiplier tests:
   - Replace `speed_multiplier` assertions with `speed_level` assertions
   - Add: `test_speed_level_default_is_1`
   - Add: `test_fire_rate_level_default_is_1`
   - Add: `test_max_speed_scales_with_speed_level` (set level 1/2/3, verify max speed matches SPEED_LEVELS)
   - Add: `test_shoot_cooldown_scales_with_fire_rate_level`
   - Add: `test_downgrade_on_death_decrements_levels`
   - Add: `test_downgrade_on_death_floors_at_1`

2. **test_powerup.py** — Existing tests should pass (no API changes to Powerup entity).

3. **New test file** `bork/tests/test_tiers.py` (optional, could go in test_player.py):
   - Test that SPEED_LEVELS[0] == PLAYER_MAX_SPEED
   - Test that FIRE_RATE_LEVELS[0] == SHOOT_COOLDOWN

**Validation**:
- [ ] `pytest bork/tests/ -v` — all tests pass
- [ ] No test references `speed_multiplier`

---

### Step 8: Manual play-test and commit
**Commands**:
```bash
python bork/game.py
```

**Validation**:
- [ ] Speed feels different at each tier (play through wave 3+ to collect powerup)
- [ ] Dying drops speed noticeably
- [ ] HUD tier indicators display correctly
- [ ] "S" visible on powerup
- [ ] No visual regressions

**Commit**: `feat: tiered powerup system with speed and fire rate levels`

---

## Testing Requirements

### Unit Tests
- `test_speed_level_default_is_1`: Player starts at speed level 1
- `test_fire_rate_level_default_is_1`: Player starts at fire rate level 1
- `test_max_speed_at_each_tier`: Max speed equals SPEED_LEVELS[level-1] for each level
- `test_shoot_cooldown_at_each_tier`: Cooldown equals FIRE_RATE_LEVELS[level-1] for each level
- `test_downgrade_on_death`: Both levels decrement by 1
- `test_downgrade_floors_at_1`: Level 1 doesn't go to 0
- `test_speed_level_caps_at_3`: Setting level above 3 is handled (capped in game.py)
- `test_constants_consistency`: SPEED_LEVELS[0] == PLAYER_MAX_SPEED, FIRE_RATE_LEVELS[0] == SHOOT_COOLDOWN

### Integration Tests (Manual)
- Collect speed powerup → verify speed increase is noticeable
- Collect 2 speed powerups → verify level 3 feels noticeably faster than level 2
- Collect speed powerup at level 3 → particles still trigger, speed unchanged
- Die at level 3 → respawn at level 2, speed noticeably slower
- Die at level 1 → still level 1, no crash
- Check HUD: SPD pips match current level
- Check HUD: ROF pips start at 1 (no fire rate powerup spawning yet)

---

## Integration Test Plan

### Prerequisites
- Game running: `python bork/game.py`

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Start game, check HUD bottom | SPD ■□□ and ROF ■□□ visible | ☐ |
| 2 | Survive to wave 3+, collect speed powerup | SPD becomes ■■□, ship moves faster | ☐ |
| 3 | Collect another speed powerup | SPD becomes ■■■, ship at max speed | ☐ |
| 4 | Collect speed powerup at level 3 | Particle burst plays, SPD stays ■■■ | ☐ |
| 5 | Intentionally die | SPD drops to ■■□, ROF stays ■□□ | ☐ |
| 6 | Die again | SPD drops to ■□□ | ☐ |
| 7 | Die at level 1 | SPD stays ■□□, no crash | ☐ |
| 8 | Reach boss, verify powerup cleared on warning | No powerups on screen | ☐ |

### Error Scenarios
| Scenario | How to Trigger | Expected Behavior | Pass? |
|----------|----------------|-------------------|-------|
| Max level overflow | Collect 4+ speed powerups | Level stays at 3, particles still fire | ☐ |
| Death at minimum | Die at both levels 1 | Levels stay at 1, no crash | ☐ |
| Game restart | Game over → restart | Both levels reset to 1 | ☐ |

---

## Error Handling

### Expected Errors
| Error | Cause | Handling |
|-------|-------|----------|
| Level out of bounds | Code sets level > 3 or < 1 | Clamped in collection (min/max) and downgrade (max) |

### Edge Cases
- **Rapid powerup collection**: Two powerups collected same frame — each increments separately, second may cap at 3
- **Death during invulnerability**: Can't happen (invulnerability prevents hits)
- **Boss fight death**: Same tier downgrade as normal death (handled in boss_fight.py)
- **Game restart**: Player.__init__ resets levels to 1

---

## Cost Impact

N/A — local game, no infrastructure.

---

## Open Questions

All resolved:
- ~~Fire rate powerup pickup spawning?~~ → Not in this PRP. Only wire the level system.
- ~~Acceleration scaling with tier?~~ → No. Only max speed scales. Keeps controls responsive.
- ~~Speed values for each tier?~~ → 350/470/590 (base/+34%/+69%, matching original SPEED_BOOST_MULTIPLIER ratio for level 2)

---

## Rollback Plan

1. Revert commits for this feature (`git revert`)
2. Restore `speed_multiplier` in player.py
3. Restore `SPEED_BOOST_MULTIPLIER` usage in game.py
4. Restore `_draw_powerups()` in hud.py
5. Verify: `pytest bork/tests/ -v` passes, game plays normally

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 9 | Init spec is detailed; only ambiguity was acceleration scaling (resolved: no) |
| Feasibility | 10 | Straightforward refactor of existing systems, no new architecture needed |
| Completeness | 9 | All files, tests, edge cases covered. Fire rate pickup deferred by spec. |
| Alignment | 10 | Follows ADR-005 (constants), ADR-006 (entity pattern), 500-line budget |
| **Average** | **9.5** | |

---

## Notes

- `PLAYER_MAX_SPEED` is kept as a constant for backwards compatibility (tests reference it) but should equal `SPEED_LEVELS[0]`.
- `SHOOT_COOLDOWN` is kept similarly but should equal `FIRE_RATE_LEVELS[0]`.
- The fire rate pickup entity can be added in a future PRP — this PRP ensures the level infrastructure is in place.
- Speed tier values (350/470/590) are tunable. The ratio between levels should feel meaningful during play-testing.
- The "S" letter on the powerup uses a font-size scaled to the pulsing radius so it scales with the pulse animation.
