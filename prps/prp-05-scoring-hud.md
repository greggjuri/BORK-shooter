# PRP-005: Scoring & HUD

**Created**: 2026-02-19
**Initial**: `initials/init-05-scoring-hud.md`
**Status**: Complete

---

## Overview

### Problem Statement
The game has no scoring, no lives system, and no heads-up display. Players destroy enemies and collect powerups with zero feedback on their performance. There's no score, no multiplier for skilled play, no combo reward, and death is instant game over with no lives. The game needs a scoring system to reward skill and a sci-fi HUD to communicate game state at a glance.

### Proposed Solution
Build three new modules: a `ScoringSystem` for score/multiplier/combo logic, a `HUD` for rendering the sci-fi display, and a `ScorePopup` manager for floating score text at kill locations. Wire these into the game loop alongside a lives system (player gets 3 lives, respawns on death, game over at 0). The HUD uses a cyan/white sci-fi aesthetic with geometric brackets and subtle pulse animations.

### Success Criteria
- [ ] Score increments when enemies are destroyed (100 points × multiplier)
- [ ] Score displays with comma formatting in a sci-fi bracket frame
- [ ] Multiplier increases by 0.1x per kill within 2s window, caps at 5x
- [ ] Multiplier decays to 1x after 3 seconds without kills
- [ ] Combo counter tracks consecutive kills within 2s window, displays at ≥3
- [ ] Milestone combos (5, 10, 20) trigger brief centered text flash
- [ ] Lives display shows current lives as chevron icons (▸), lost lives as dim outlines
- [ ] Lives decrement on player death; player respawns with brief invulnerability
- [ ] Game over triggers at 0 lives
- [ ] Score popup floats from kill location showing multiplied points
- [ ] Active powerup indicators shown in brackets on HUD
- [ ] All HUD/scoring constants in `constants.py`
- [ ] HUD drawn after screen shake reset (not affected by shake)

---

## Context

### Related Documentation
- `docs/DECISIONS.md` — ADR-005 (centralized constants), ADR-006 (entity update/draw pattern), ADR-003 (geometric shapes)
- `docs/PLANNING.md` — Phase 3: Progression (scoring, lives, HUD)
- `initials/init-05-scoring-hud.md` — Full feature specification
- `prps/prp-02-enemy-system.md` — Enemy kill detection this hooks into
- `prps/prp-03-powerup-system.md` — Powerup collection this displays
- `prps/prp-04-explosions.md` — Particle system and screen effects already integrated

### Dependencies
- **Required**: PRP-001 Core Engine (complete), PRP-002 Enemy System (complete), PRP-003 Powerup System (complete), PRP-004 Explosions (complete)

### Files to Create
```
bork/
├── scoring.py                  # NEW: ScoringSystem (score, multiplier, combo logic)
├── hud.py                      # NEW: HUD rendering (sci-fi display)
├── score_popup.py              # NEW: Floating score text at kill locations
└── tests/
    ├── test_scoring.py         # NEW: Scoring logic tests
    └── test_hud.py             # NEW: HUD state tests
```

### Files to Modify
```
bork/constants.py               # Add scoring, HUD, popup, lives constants
bork/game.py                    # Add ScoringSystem, HUD, ScorePopup, lives logic; rework death/respawn
bork/player.py                  # Add invulnerability timer and visual feedback
```

---

## Technical Specification

### Design Notes

**Lives & Respawn**: Currently, player death immediately triggers `STATE_GAME_OVER`. This PRP changes that: on death, a life is deducted, the player respawns at start position with brief invulnerability, and game over only occurs at 0 lives.

**Zone Indicator**: The init spec mentions `◄ ZONE 01 ►` on the HUD. Since there's no zone/level system yet, this will be rendered as a static "ZONE 01" label, future-proofed for later.

**Debug Speedometer**: The existing temporary speedometer in `on_draw()` will be removed as the HUD replaces it with proper game info.

### Constants to Add (`bork/constants.py`)

```python
# Scoring
POINTS_BASIC_ENEMY = 100
MULTIPLIER_INCREMENT = 0.1
MULTIPLIER_MAX = 5.0
MULTIPLIER_DECAY_DELAY = 3.0      # seconds before decay starts
COMBO_WINDOW = 2.0                # seconds between kills to maintain combo

# Combo milestones
COMBO_MILESTONES = {
    5: "NICE!",
    10: "UNSTOPPABLE!",
    20: "GODLIKE!",
}
COMBO_MILESTONE_DURATION = 1.0    # seconds to display milestone text
COMBO_MILESTONE_FADE = 0.5        # seconds to fade out

# Lives
STARTING_LIVES = 3
RESPAWN_INVULNERABLE_TIME = 2.0   # seconds of invulnerability after respawn
INVULNERABLE_BLINK_RATE = 10.0    # blinks per second during invulnerability

# HUD colors
HUD_PRIMARY = (0, 255, 255)       # Cyan - main text and frames
HUD_SECONDARY = (100, 200, 255)   # Light blue - secondary elements
HUD_ACCENT = (255, 220, 100)      # Gold - multiplier/combo highlights
HUD_DIM = (60, 80, 90)            # Dim cyan - inactive/lost lives
HUD_BACKGROUND = (0, 10, 20, 180) # Dark blue, semi-transparent

# HUD layout
HUD_MARGIN = 20
HUD_SCORE_FONT_SIZE = 24
HUD_LABEL_FONT_SIZE = 12
HUD_MULTI_FONT_SIZE = 16
HUD_COMBO_FONT_SIZE = 14
HUD_LIVES_FONT_SIZE = 16
HUD_POWERUP_FONT_SIZE = 11
HUD_ZONE_FONT_SIZE = 12
HUD_MILESTONE_FONT_SIZE = 28

# HUD multiplier pulse
HUD_MULTI_PULSE_SPEED = 3.0       # pulses per second when active
HUD_MULTI_PULSE_AMOUNT = 0.3      # alpha varies ±30%

# Score popup
SCORE_POPUP_DURATION = 0.5        # seconds
SCORE_POPUP_RISE_SPEED = 60.0     # pixels per second upward
SCORE_POPUP_FONT_SIZE = 14
```

### ScoringSystem (`bork/scoring.py`)

```python
class ScoringSystem:
    """Tracks score, multiplier, and combo state."""

    def __init__(self) -> None:
        self.score: int = 0
        self.multiplier: float = 1.0
        self.combo: int = 0
        self.time_since_kill: float = 0.0
        self.has_killed: bool = False  # track if any kill has happened

    def register_kill(self, base_points: int) -> int:
        """Register a kill, update multiplier/combo, return points earned."""
        # Increase multiplier if within combo window
        if self.has_killed and self.time_since_kill <= COMBO_WINDOW:
            self.multiplier = min(self.multiplier + MULTIPLIER_INCREMENT, MULTIPLIER_MAX)
            self.combo += 1
        else:
            self.combo = 1
            self.multiplier = 1.0

        self.has_killed = True
        self.time_since_kill = 0.0
        points = int(base_points * self.multiplier)
        self.score += points
        return points

    def update(self, dt: float) -> None:
        """Decay multiplier if no kills recently."""
        if not self.has_killed:
            return
        self.time_since_kill += dt
        if self.time_since_kill > MULTIPLIER_DECAY_DELAY:
            self.multiplier = 1.0
            self.combo = 0

    def reset(self) -> None:
        """Reset all scoring state."""
        self.score = 0
        self.multiplier = 1.0
        self.combo = 0
        self.time_since_kill = 0.0
        self.has_killed = False
```

### ScorePopup (`bork/score_popup.py`)

```python
class ScorePopup:
    """A single floating score text that rises and fades."""

    def __init__(self, x: float, y: float, points: int) -> None:
        self.x = x
        self.y = y
        self.points = points
        self.age = 0.0

    @property
    def is_done(self) -> bool:
        return self.age >= SCORE_POPUP_DURATION

    @property
    def alpha(self) -> int:
        t = min(self.age / SCORE_POPUP_DURATION, 1.0)
        return int(255 * (1.0 - t))

    def update(self, dt: float) -> None:
        self.y += SCORE_POPUP_RISE_SPEED * dt
        self.age += dt

    def draw(self) -> None:
        if self.is_done:
            return
        color = (*HUD_PRIMARY[:3], self.alpha)
        text = f"+{self.points:,}"
        arcade.draw_text(
            text, self.x, self.y, color,
            font_size=SCORE_POPUP_FONT_SIZE,
            anchor_x="center", anchor_y="center",
        )


class ScorePopupManager:
    """Manages multiple floating score popups."""

    def __init__(self) -> None:
        self.popups: list[ScorePopup] = []

    def spawn(self, x: float, y: float, points: int) -> None:
        self.popups.append(ScorePopup(x, y, points))

    def update(self, dt: float) -> None:
        for p in self.popups:
            p.update(dt)
        self.popups = [p for p in self.popups if not p.is_done]

    def draw(self) -> None:
        for p in self.popups:
            p.draw()
```

### HUD (`bork/hud.py`)

```python
class HUD:
    """Sci-fi heads-up display for score, multiplier, combo, lives, powerups."""

    def __init__(self) -> None:
        self.milestone_text: str = ""
        self.milestone_timer: float = 0.0
        self.multi_pulse_timer: float = 0.0

    def update(self, dt: float) -> None:
        """Update animations (milestone fade, multiplier pulse)."""
        if self.milestone_timer > 0:
            self.milestone_timer -= dt
        self.multi_pulse_timer += dt

    def trigger_milestone(self, text: str) -> None:
        """Show a combo milestone message."""
        self.milestone_text = text
        self.milestone_timer = COMBO_MILESTONE_DURATION

    def draw(
        self,
        score: int,
        multiplier: float,
        combo: int,
        lives: int,
        active_powerups: list[str],
    ) -> None:
        """Draw the full HUD overlay."""
        self._draw_score(score)
        self._draw_multiplier(multiplier)
        self._draw_combo(combo)
        self._draw_lives(lives)
        self._draw_powerups(active_powerups)
        self._draw_zone()
        self._draw_milestone()

    def _draw_score(self, score: int) -> None:
        """Draw score with sci-fi bracket framing."""
        # Label
        arcade.draw_text(
            "◄ SCORE ►", HUD_MARGIN, SCREEN_HEIGHT - HUD_MARGIN,
            HUD_DIM, font_size=HUD_LABEL_FONT_SIZE,
            anchor_x="left", anchor_y="top",
        )
        # Value
        arcade.draw_text(
            f"{score:,}", HUD_MARGIN, SCREEN_HEIGHT - HUD_MARGIN - 18,
            HUD_PRIMARY, font_size=HUD_SCORE_FONT_SIZE, bold=True,
            anchor_x="left", anchor_y="top",
        )

    def _draw_multiplier(self, multiplier: float) -> None:
        """Draw multiplier indicator with pulse when active."""
        if multiplier <= 1.0:
            return
        # Pulse alpha
        pulse = math.sin(self.multi_pulse_timer * HUD_MULTI_PULSE_SPEED * 2 * math.pi)
        alpha = int(255 * (0.7 + HUD_MULTI_PULSE_AMOUNT * pulse))
        alpha = max(0, min(255, alpha))
        color = (*HUD_ACCENT[:3], alpha)
        arcade.draw_text(
            f"x{multiplier:.1f} MULTI",
            HUD_MARGIN + 200, SCREEN_HEIGHT - HUD_MARGIN - 18,
            color, font_size=HUD_MULTI_FONT_SIZE,
            anchor_x="left", anchor_y="top",
        )

    def _draw_combo(self, combo: int) -> None:
        """Draw combo counter when ≥ 3."""
        if combo < 3:
            return
        # Color shifts toward gold at high combos
        t = min(combo / 20.0, 1.0)
        r = int(HUD_PRIMARY[0] + (HUD_ACCENT[0] - HUD_PRIMARY[0]) * t)
        g = int(HUD_PRIMARY[1] + (HUD_ACCENT[1] - HUD_PRIMARY[1]) * t)
        b = int(HUD_PRIMARY[2] + (HUD_ACCENT[2] - HUD_PRIMARY[2]) * t)
        arcade.draw_text(
            f"‹ {combo} COMBO ›",
            HUD_MARGIN, SCREEN_HEIGHT - HUD_MARGIN - 48,
            (r, g, b), font_size=HUD_COMBO_FONT_SIZE,
            anchor_x="left", anchor_y="top",
        )

    def _draw_lives(self, lives: int) -> None:
        """Draw lives as chevron icons, lost lives as dim outlines."""
        base_x = SCREEN_WIDTH - HUD_MARGIN - 140
        y = SCREEN_HEIGHT - HUD_MARGIN - 18
        # Label
        arcade.draw_text(
            "LIVES", base_x - 10, SCREEN_HEIGHT - HUD_MARGIN,
            HUD_DIM, font_size=HUD_LABEL_FONT_SIZE,
            anchor_x="left", anchor_y="top",
        )
        for i in range(STARTING_LIVES):
            color = HUD_PRIMARY if i < lives else HUD_DIM
            arcade.draw_text(
                "▸", base_x + i * 20, y,
                color, font_size=HUD_LIVES_FONT_SIZE,
                anchor_x="left", anchor_y="top",
            )

    def _draw_powerups(self, active_powerups: list[str]) -> None:
        """Draw active powerup indicators in brackets."""
        if not active_powerups:
            return
        x = SCREEN_WIDTH - HUD_MARGIN
        y = SCREEN_HEIGHT - HUD_MARGIN - 40
        for pu in active_powerups:
            label = {"speed": "SPEED+"}.get(pu, pu.upper())
            arcade.draw_text(
                f"[{label}]", x, y,
                POWERUP_COLOR, font_size=HUD_POWERUP_FONT_SIZE,
                anchor_x="right", anchor_y="top",
            )
            y -= 16

    def _draw_zone(self) -> None:
        """Draw zone indicator (static for now)."""
        arcade.draw_text(
            "◄ ZONE 01 ►",
            SCREEN_WIDTH - HUD_MARGIN, SCREEN_HEIGHT - HUD_MARGIN,
            HUD_DIM, font_size=HUD_ZONE_FONT_SIZE,
            anchor_x="right", anchor_y="top",
        )

    def _draw_milestone(self) -> None:
        """Draw combo milestone text centered on screen."""
        if self.milestone_timer <= 0:
            return
        # Fade out
        alpha = int(255 * min(self.milestone_timer / COMBO_MILESTONE_FADE, 1.0))
        color = (*HUD_ACCENT[:3], alpha)
        arcade.draw_text(
            self.milestone_text,
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60,
            color, font_size=HUD_MILESTONE_FONT_SIZE, bold=True,
            anchor_x="center", anchor_y="center",
        )
```

### Player Changes (`bork/player.py`)

Add invulnerability support:

```python
# New fields in __init__:
self.invulnerable_timer: float = 0.0

# New property:
@property
def is_invulnerable(self) -> bool:
    return self.invulnerable_timer > 0.0

# In update(): tick invulnerable timer
if self.invulnerable_timer > 0:
    self.invulnerable_timer -= dt

# In draw(): blink during invulnerability
if self.is_invulnerable:
    # Blink: skip drawing every other frame based on timer
    if int(self.invulnerable_timer * INVULNERABLE_BLINK_RATE * 2) % 2 == 0:
        return
```

### Game Loop Changes (`bork/game.py`)

**New state fields:**
- `self.scoring: ScoringSystem`
- `self.hud: HUD`
- `self.score_popups: ScorePopupManager`
- `self.lives: int = STARTING_LIVES`

**`setup()` changes:**
- Init `ScoringSystem`, `HUD`, `ScorePopupManager`
- Set `self.lives = STARTING_LIVES`
- Reset player invulnerability

**`on_update(dt)` changes:**
- Call `self.scoring.update(dt)` to decay multiplier
- Call `self.hud.update(dt)` for animations
- Call `self.score_popups.update(dt)` to age popups
- Skip enemy-player collision when `player.is_invulnerable`

**`_check_projectile_enemy_collisions()` changes:**
- On enemy kill: call `scoring.register_kill(POINTS_BASIC_ENEMY)` to get points earned
- Spawn `ScorePopup` at enemy position with earned points
- Check for combo milestones, trigger `hud.trigger_milestone()` if applicable

**`_check_enemy_player_collisions()` changes:**
- Skip collision if `player.is_invulnerable`
- On hit: decrement `self.lives`
- If `self.lives > 0`: respawn player (reset position, set invulnerable timer), don't set game over
- If `self.lives <= 0`: set `STATE_GAME_OVER` (as before)
- Spawn explosion, screen flash, screen shake on any hit

**`on_draw()` changes:**
- Draw HUD after resetting screen shake projection (HUD is not affected by shake)
- Draw score popups (in world space, affected by shake — they float from kill location)
- Remove debug speedometer
- Pass game state to `hud.draw()`: score, multiplier, combo, lives, active powerups
- Update game over text to include final score

---

## Implementation Steps

### Step 1: Add Constants
**Files**: `bork/constants.py`

Append all scoring, HUD, lives, popup, and combo milestone constants as specified above. Group them clearly with section comments.

**Validation**:
- [ ] `ruff check bork/` and `ruff format --check bork/` pass
- [ ] Existing tests still pass

---

### Step 2: ScoringSystem
**Files**: `bork/scoring.py`, `bork/tests/test_scoring.py`

1. Create `ScoringSystem` class with `register_kill(base_points)`, `update(dt)`, `reset()`
2. Implement multiplier increment on rapid kills (within `COMBO_WINDOW`)
3. Implement multiplier decay after `MULTIPLIER_DECAY_DELAY`
4. Implement combo counter that resets when window expires

Tests:
- `test_initial_state`: score=0, multiplier=1.0, combo=0
- `test_register_kill_adds_score`: score increases by base_points when multiplier is 1x
- `test_register_kill_returns_points`: return value matches points added
- `test_multiplier_increases_on_rapid_kills`: multiplier goes up with kills within window
- `test_multiplier_caps_at_max`: multiplier cannot exceed MULTIPLIER_MAX
- `test_multiplier_decays_after_delay`: multiplier returns to 1.0 after MULTIPLIER_DECAY_DELAY
- `test_combo_increments_within_window`: combo count increases on rapid kills
- `test_combo_resets_after_window`: combo resets to 1 when gap exceeds COMBO_WINDOW
- `test_score_uses_multiplier`: score adds `int(base_points * multiplier)`
- `test_reset_clears_state`: all fields back to initial values

**Validation**:
- [ ] `pytest bork/tests/test_scoring.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 3: ScorePopup System
**Files**: `bork/score_popup.py`

1. Create `ScorePopup` class with `update(dt)`, `draw()`, `is_done` property
2. Create `ScorePopupManager` with `spawn(x, y, points)`, `update(dt)`, `draw()`
3. Popups rise at `SCORE_POPUP_RISE_SPEED` and fade over `SCORE_POPUP_DURATION`

No dedicated test file — popups are simple visual entities. Logic is trivial (rise + fade). Tested through integration.

**Validation**:
- [ ] `ruff check bork/` and `ruff format --check bork/` pass
- [ ] Module imports without error

---

### Step 4: HUD
**Files**: `bork/hud.py`, `bork/tests/test_hud.py`

1. Create `HUD` class with `update(dt)`, `draw(score, multiplier, combo, lives, active_powerups)`
2. Implement `_draw_score`, `_draw_multiplier` (with pulse), `_draw_combo` (with color shift), `_draw_lives` (chevrons), `_draw_powerups` (brackets), `_draw_zone` (static), `_draw_milestone` (centered text fade)
3. `trigger_milestone(text)` sets milestone text and timer

Tests:
- `test_hud_initial_state`: milestone_timer starts at 0
- `test_trigger_milestone_sets_text_and_timer`: text and timer set correctly
- `test_milestone_timer_decrements`: timer decreases on update
- `test_milestone_timer_stops_at_zero`: doesn't go negative

**Validation**:
- [ ] `pytest bork/tests/test_hud.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 5: Player Invulnerability
**Files**: `bork/player.py`, `bork/tests/test_player.py`

1. Add `invulnerable_timer` field (default 0.0)
2. Add `is_invulnerable` property
3. Tick down `invulnerable_timer` in `update()`
4. Blink effect in `draw()`: skip drawing on alternating intervals during invulnerability

Tests (add to existing test_player.py):
- `test_player_not_invulnerable_initially`: `is_invulnerable` is False
- `test_player_invulnerable_when_timer_set`: setting timer makes `is_invulnerable` True
- `test_invulnerable_timer_decrements`: timer ticks down during update
- `test_invulnerable_ends_at_zero`: `is_invulnerable` becomes False when timer expires

**Validation**:
- [ ] `pytest bork/tests/test_player.py -v` passes
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 6: Integrate into Game Loop
**Files**: `bork/game.py`

1. Add imports for `ScoringSystem`, `HUD`, `ScorePopupManager`, new constants
2. Add `self.scoring`, `self.hud`, `self.score_popups`, `self.lives` fields
3. `setup()`: init all new systems, set `self.lives = STARTING_LIVES`
4. `on_update(dt)`:
   - Call `self.scoring.update(dt)`, `self.hud.update(dt)`, `self.score_popups.update(dt)`
   - Update these even during game over (so popups/milestones finish playing)
5. `_check_projectile_enemy_collisions()`:
   - On enemy kill: `points = self.scoring.register_kill(POINTS_BASIC_ENEMY)`
   - `self.score_popups.spawn(enemy.x, enemy.y, points)`
   - Check combo milestones: `if self.scoring.combo in COMBO_MILESTONES: self.hud.trigger_milestone(...)`
6. `_check_enemy_player_collisions()`:
   - Early return if `self.player.is_invulnerable`
   - On collision: spawn explosion, flash, shake (as before)
   - Decrement `self.lives`
   - If lives > 0: respawn player (reset position, velocity, invulnerability timer)
   - If lives <= 0: set `STATE_GAME_OVER`
7. `on_draw()`:
   - Draw `self.score_popups.draw()` in world space (before shake reset)
   - After shake projection reset: draw HUD and milestone
   - Remove debug speedometer
   - Update game over text to show final score
8. Build `active_powerups` list from player state for HUD

**Validation**:
- [ ] `python bork/game.py` runs
- [ ] All existing tests pass
- [ ] `ruff check bork/` and `ruff format --check bork/` pass

---

### Step 7: Run All Tests and Lint
**Commands**:
```bash
pytest bork/tests/ -v --tb=short
ruff check bork/
ruff format --check bork/
```

**Validation**:
- [ ] All tests pass
- [ ] No lint errors
- [ ] No format errors

---

## Testing Requirements

### Unit Tests

**test_scoring.py**:
- `test_initial_state`: score=0, multiplier=1.0, combo=0
- `test_register_kill_adds_score`: base points added to score
- `test_register_kill_returns_points`: return value correct
- `test_multiplier_increases_on_rapid_kills`: +0.1x per rapid kill
- `test_multiplier_caps_at_max`: cannot exceed 5.0x
- `test_multiplier_decays_after_delay`: back to 1.0 after 3s idle
- `test_combo_increments_within_window`: combo increases on rapid kills
- `test_combo_resets_after_window`: combo resets after 2s gap
- `test_score_uses_multiplier`: multiplied points added to score
- `test_reset_clears_state`: all fields reset

**test_hud.py**:
- `test_hud_initial_state`: milestone_timer at 0
- `test_trigger_milestone_sets_text_and_timer`: correct values
- `test_milestone_timer_decrements`: timer counts down
- `test_milestone_timer_stops_at_zero`: no negative values

**test_player.py** (additions):
- `test_player_not_invulnerable_initially`
- `test_player_invulnerable_when_timer_set`
- `test_invulnerable_timer_decrements`
- `test_invulnerable_ends_at_zero`

---

## Integration Test Plan

### Prerequisites
- `pip install -r requirements.txt`
- Run `python bork/game.py`

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Shoot and destroy an enemy | Score increments by 100, "+100" popup floats up from kill location, HUD score updates with comma formatting | ☐ |
| 2 | Kill enemies rapidly (within 2s) | Multiplier increases (x1.1, x1.2...), popup shows multiplied value ("+110", "+120"), multiplier display appears with pulse | ☐ |
| 3 | Stop killing for 3+ seconds | Multiplier fades back to 1x, multiplier display disappears | ☐ |
| 4 | Get a 3-kill combo | Combo counter appears: "‹ 3 COMBO ›" | ☐ |
| 5 | Get a 5-kill combo | Centered "NICE!" text flashes and fades | ☐ |
| 6 | Let an enemy hit the player | Explosion, flash, shake play; life icon goes dim; player respawns at left-center with blinking invulnerability | ☐ |
| 7 | During invulnerability, touch an enemy | No damage taken, player blinks, enemies pass through | ☐ |
| 8 | After invulnerability ends, get hit again | Second life lost, one chevron remaining | ☐ |
| 9 | Lose final life | Game over screen shows "GAME OVER" and final score | ☐ |
| 10 | Press R to restart after game over | Score resets to 0, lives back to 3, all HUD elements reset | ☐ |
| 11 | Collect speed powerup | "[SPEED+]" indicator appears on HUD | ☐ |
| 12 | Check HUD readability | Score, lives, zone all readable at a glance; cyan/sci-fi aesthetic cohesive; HUD doesn't obscure gameplay | ☐ |

### Error Scenarios
| Scenario | How to Trigger | Expected Behavior | Pass? |
|----------|----------------|-------------------|-------|
| Multiple popups at once | Kill 3+ enemies rapidly | All popups visible and independent, no overlap issues | ☐ |
| Death during combo | Get hit while at high combo | Combo/multiplier reset, lives decrease normally | ☐ |
| Restart during milestone | Press R while "NICE!" is showing | Milestone cleared, clean restart | ☐ |
| Max multiplier sustained | Kill 40+ enemies rapidly | Multiplier stays at 5.0, doesn't exceed | ☐ |

---

## Error Handling

### Edge Cases
- **Zero lives display**: When lives reach 0, all chevrons show dim — game over triggers immediately so this is only briefly visible
- **Multiplier at exactly 1.0**: Multiplier display hidden (only shows when > 1.0)
- **Combo at 0-2**: Combo display hidden (only shows at ≥ 3)
- **Score overflow**: Python integers have no overflow — no concern
- **Respawn during active particles**: ParticleSystem continues independently, no conflict
- **Multiple deaths in rapid succession**: Invulnerability prevents this; timer must expire before next hit
- **Powerup collected while invulnerable**: Powerup collection is independent of invulnerability — works normally
- **No active powerups**: Powerup section of HUD simply not drawn

---

## Cost Impact

N/A — standalone local game.

---

## Open Questions

None — all resolved:
- [x] HUD layout: top-left for score/combo, top-right for lives/powerups/zone
- [x] Respawn behavior: reset position + velocity, 2s invulnerability with blink
- [x] Multiplier decay: instant snap to 1.0 after delay (not gradual)
- [x] Score popup style: cyan text, rises and fades, shows multiplied value
- [x] Combo milestones: 5, 10, 20 with text flash
- [x] Zone indicator: static "ZONE 01" for now
- [x] Debug speedometer: removed, replaced by HUD

---

## Rollback Plan

1. `git revert` the commits from this PRP
2. Remove `bork/scoring.py`, `bork/hud.py`, `bork/score_popup.py` and test files
3. Revert `bork/game.py` to restore instant-death behavior (no lives)
4. Revert `bork/player.py` to remove invulnerability
5. Revert `bork/constants.py` to remove scoring/HUD constants
6. Previous systems (enemies, powerups, explosions) are unaffected

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | 9 | Very detailed init spec with exact values, colors, layout, and acceptance criteria. Only minor ambiguity is precise HUD pixel positioning (tunable). |
| Feasibility | 10 | Straightforward extension of existing architecture. All Arcade text drawing primitives are well-established. Lives/respawn is a simple state change. |
| Completeness | 9 | Covers scoring, multiplier, combo, lives, HUD, popups, milestones, and invulnerability. High score persistence explicitly deferred. |
| Alignment | 10 | Follows all ADRs (centralized constants, entity pattern, geometric shapes, 500-line limit). Fits Phase 3 progression roadmap. |
| **Average** | **9.5** | High confidence. Builds naturally on existing collision and effect systems. |

---

## Notes

- **File sizes**: `scoring.py` ~50 lines, `hud.py` ~160 lines, `score_popup.py` ~60 lines — all well within the 500-line limit.
- **Debug speedometer removal**: The existing temporary speedometer (`SPD: X / Y`) in `on_draw()` is removed. The HUD replaces ad-hoc debug text with proper game information.
- **Multiplier decay is instant**: After `MULTIPLIER_DECAY_DELAY` seconds without a kill, the multiplier snaps to 1.0 (not gradual decay). This matches the init spec and gives a clear "lost your streak" feeling.
- **Combo resets on death**: When the player is hit, the combo/multiplier naturally reset because `time_since_kill` exceeds `COMBO_WINDOW` during respawn. No explicit reset needed on death, but the window gap handles it.
- **HUD not affected by screen shake**: The HUD is drawn after the projection is reset to default, so it stays stable during shake — this is the correct UX for a heads-up display.
- **Score popups in world space**: Popups float from where the enemy died, so they ARE affected by screen shake. This feels natural — they're "in the world", not on the HUD.
