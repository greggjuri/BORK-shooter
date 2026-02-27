# init-07: Boss Fights

## Goal

Create a boss encounter system with a multi-phase Zone 1 boss. The boss should feel like a proper skill check — intimidating, learnable, and satisfying to defeat.

## Design Philosophy

Classic shmup boss principles:
- **Telegraphed attacks** — fair, learnable patterns
- **Multi-phase** — escalating threat as health decreases
- **Visual presence** — big, imposing, fills part of the screen
- **Dramatic entrance and death** — memorable moments
- **Rewards skill** — patient players who learn patterns win

## Features

### 1. Boss Spawn Trigger

**When boss appears:**
- After 3 complete wave cycles (9 total waves)
- Brief warning sequence before boss enters
- Normal enemy spawning pauses during boss fight
- Boss defeated → victory state (for now, later leads to next zone)

**Warning sequence:**
- Screen edges flash red/orange
- "WARNING" text pulses center screen
- Brief pause (1.5 seconds) to build tension
- Boss enters from right side of screen

### 2. Zone 1 Boss: "SENTINEL"

A geometric fortress — fits the placeholder art style while being imposing.

**Visual design (geometric shapes):**
```
        ┌───────────┐
    ┌───┤  CORE     ├───┐
    │   │  (eye)    │   │
┌───┤   └─────┬─────┘   ├───┐
│ W │         │         │ W │
│ I │    ┌────┴────┐    │ I │
│ N │    │  BODY   │    │ N │
│ G │    │         │    │ G │
└───┤    └─────────┘    ├───┘
    └───────────────────┘
```

**Components:**
- **Core** (center) — glowing eye/reactor, the weak point
- **Body** — main geometric mass, takes reduced damage
- **Wings** (×2) — side panels, destructible for bonus points

**Size:** Approximately 200×150 pixels (large but not overwhelming)

**Colors:**
- Body: Dark steel gray with cyan accent lines
- Core: Pulsing red/orange (danger!)
- Wings: Slightly lighter gray, cyan trim

### 3. Boss Health System

**Health pools:**
- Core: 50 HP (main health bar)
- Left Wing: 15 HP (optional destroy)
- Right Wing: 15 HP (optional destroy)

**Damage rules:**
- Core takes full damage (1 HP per hit)
- Body takes reduced damage (0.5 HP per hit, rounded down)
- Wings take full damage, destroyed independently
- Destroying wings = bonus points + removes some attacks

**Health bar display:**
- Large health bar at top of screen (below HUD)
- Boss name "SENTINEL" above bar
- Bar depletes left-to-right, color shifts green → yellow → red
- Optional: small indicators for wing health

### 4. Attack Patterns (3 Phases)

#### Phase 1: "Probing" (100% - 66% HP)

**Attack A — Spread Shot:**
- Core fires 3-bullet spread toward player
- 2 second interval
- Bullets: medium speed, cyan color

**Attack B — Wing Sweep:**
- Each wing fires a single bullet straight left
- Alternating wings, 1.5 second interval
- Bullets: fast, small, white

**Movement:**
- Slow vertical drift (follows player Y loosely)
- Stays on right third of screen

#### Phase 2: "Aggressive" (66% - 33% HP)

**Attack A — Rapid Spread:**
- Spread shot increases to 5 bullets
- 1.5 second interval (faster)

**Attack B — Aimed Shot:**
- Core fires single fast bullet directly at player position
- 1 second interval
- Bullet: fast, red, slightly larger

**Attack C — Wing Barrage (if wings alive):**
- Both wings fire simultaneously
- 3-bullet burst each
- 1.5 second interval

**Movement:**
- More aggressive vertical tracking
- Occasional horizontal lunge toward player (retreat after 0.5s)

#### Phase 3: "Desperate" (33% - 0% HP)

**Attack A — Bullet Hell Lite:**
- Core fires 7-bullet radial burst
- 1.5 second interval
- Bullets spread in arc, not full circle

**Attack B — Beam Charge (telegraphed):**
- Core glows bright for 1 second (warning!)
- Fires horizontal beam across screen at player's Y position
- Beam is instant-hit, must dodge vertically
- 4 second cooldown

**Movement:**
- Erratic vertical movement
- Screen shake on beam fire

### 5. Boss Entrance Animation

1. "WARNING" text appears, pulses 3 times (1.5 sec total)
2. Screen edges tint red briefly
3. Boss enters from right, moving left to battle position
4. Boss "activates" — core lights up, wings extend
5. Health bar appears
6. Fight begins

### 6. Boss Death Sequence

1. Boss stops attacking, drifts
2. Small explosions pop across body (0.5 sec)
3. Core overloads — bright flash
4. Massive explosion (use player death explosion ×3 scale)
5. Screen shake (large intensity)
6. Boss fragments scatter (particles)
7. Victory text: "SENTINEL DESTROYED" + bonus points
8. Brief pause, then victory state

**Points:**
- Core destroyed: 5,000 points
- Each wing destroyed: 1,000 points
- No-damage bonus: 2,500 points (if player never got hit during fight)

### 7. Boss Projectiles

**Standard bullet:**
- Small square or diamond shape
- Cyan or white color
- Medium speed (~200 px/sec)

**Aimed bullet:**
- Slightly larger, red
- Fast (~350 px/sec)
- Travels toward player's position at fire time

**Beam:**
- Full-width horizontal line
- Bright white/yellow with glow effect
- Instant (no travel time)
- Brief duration (0.1 sec visible)
- Preceded by 1-second charge-up (core glows)

### 8. Technical Approach

#### New Files

- `bork/boss.py` — Boss base class and Sentinel implementation
- `bork/boss_attacks.py` — Attack pattern definitions
- `bork/tests/test_boss.py`

#### Modified Files

- `bork/constants.py` — Boss constants (health, timing, speeds)
- `bork/game.py` — Boss spawn logic, warning sequence, victory state

#### Constants (add to constants.py)

```python
# Boss spawn
BOSS_SPAWN_AFTER_WAVES = 9  # 3 complete cycles
WARNING_DURATION = 1.5

# Sentinel stats
SENTINEL_CORE_HP = 50
SENTINEL_WING_HP = 15
SENTINEL_BODY_DAMAGE_MULT = 0.5

# Sentinel size
SENTINEL_WIDTH = 200
SENTINEL_HEIGHT = 150
SENTINEL_CORE_SIZE = 40

# Sentinel movement
SENTINEL_BATTLE_X = SCREEN_WIDTH - 150  # right side
SENTINEL_TRACK_SPEED = 60  # vertical tracking px/sec

# Sentinel points
SENTINEL_CORE_POINTS = 5000
SENTINEL_WING_POINTS = 1000
SENTINEL_NODAMAGE_BONUS = 2500

# Phase thresholds (percentage of max HP)
SENTINEL_PHASE2_THRESHOLD = 0.66
SENTINEL_PHASE3_THRESHOLD = 0.33

# Attack timing (seconds)
SENTINEL_SPREAD_INTERVAL_P1 = 2.0
SENTINEL_SPREAD_INTERVAL_P2 = 1.5
SENTINEL_AIMED_INTERVAL = 1.0
SENTINEL_BEAM_CHARGE_TIME = 1.0
SENTINEL_BEAM_COOLDOWN = 4.0

# Bullet speeds
BOSS_BULLET_SPEED_MEDIUM = 200
BOSS_BULLET_SPEED_FAST = 350
```

## Acceptance Criteria

- [ ] Boss spawns after 9 enemy waves
- [ ] Warning sequence plays before boss enters
- [ ] Boss has 3 distinct phases based on HP percentage
- [ ] Boss health bar displays at top of screen
- [ ] Destroying wings removes some attacks + bonus points
- [ ] Phase 3 beam attack is telegraphed with charge-up glow
- [ ] Boss death triggers dramatic multi-explosion sequence
- [ ] Victory state triggers after boss destroyed
- [ ] No-damage bonus awarded if player wasn't hit during fight
- [ ] Normal enemies don't spawn during boss fight
- [ ] All boss constants in constants.py

## Testing

### Automated
- Boss spawns at correct wave count
- Boss HP decreases on hit
- Phase transitions at correct HP thresholds
- Wings can be destroyed independently
- Boss death triggers at 0 HP

### Manual Play-test
- Warning sequence builds tension
- Boss feels threatening but fair
- Attacks are readable/dodgeable
- Phase transitions are noticeable
- Death sequence is satisfying
- Overall fight takes 60-90 seconds for skilled player

## Future Enhancements (Not This PR)

- Additional bosses for later zones
- Boss attack variations based on difficulty
- Mid-bosses (mini-boss encounters)
- Boss rush mode
