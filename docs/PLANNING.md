# B.O.R.K. - Architecture & Planning

## Overview

B.O.R.K. is a horizontal scrolling shoot 'em up built with Python and the Arcade library. Inspired by Delta, Sanxion (C64), Xenon, Galaga, and Gyruss.

**Core pillars:**
- Learnable enemy patterns for skill mastery
- Satisfying powerup progression
- Chunky explosions and impactful feedback
- Boss fights that test everything you've learned

**Design principles:**
- "Too much is not enough" — visual effects (especially explosions, boss deaths, screen shake) should feel excessive. If it seems like too much, it's probably about right.
- Polygon-based ship rendering — ships are built from mirrored polygon hulls with layered details (armor plates, panel lines, weapon ports, vents), not rectangles. This applies to both the player ship and the Sentinel boss.
- Layered gradient effects — engine exhaust uses 8-10 concentric ellipses graduating from bright inner core to dim outer glow. Both player and boss engines use this pattern.

## Tech Stack

- **Language**: Python 3.8+
- **Framework**: Arcade (2D game library)
- **Testing**: pytest
- **Linting**: ruff

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        BorkGame                              │
│                    (arcade.Window)                            │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │  Starfield  │  │   Player    │  │  ScoringSystem       │ │
│  │  (background)│  │   (ship)    │  │  (score, multi,      │ │
│  │             │  │             │  │   combo, popups)     │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ Projectiles │  │   Enemies   │  │      Powerups        │ │
│  │   (list)    │  │   (list)    │  │       (list)         │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ Particles   │  │  Sentinel   │  │  HUD + ScreenEffects │ │
│  │ (explosions)│  │  (boss)     │  │  (flash, shake)      │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ WaveSpawner │  │ BossFight   │  │    SoundManager      │ │
│  │ (9 waves →  │  │ (state      │  │    (SFX + music)     │ │
│  │  boss)      │  │  handlers)  │  │    (future)          │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Game Loop

```
┌──────────────────────────────────────────────────────────┐
│                      on_update(dt)                       │
├──────────────────────────────────────────────────────────┤
│ Always:                                                  │
│  1. Update starfield, particles, screen effects          │
│  2. Update scoring, HUD, score popups                    │
│                                                          │
│ State dispatch:                                          │
│  STATE_PLAYING:                                          │
│    - Player, projectiles, enemies, powerups              │
│    - Collisions (proj↔enemy, enemy↔player, powerups)    │
│    - Wave spawner → boss trigger at wave 9               │
│  STATE_BOSS_WARNING (5s):                                │
│    - Player, projectiles, enemies (scroll off naturally) │
│    - Enemy collisions still active                       │
│    - Spawn Sentinel when timer expires                   │
│  STATE_BOSS_FIGHT:                                       │
│    - Player, projectiles, boss, enemy projectiles        │
│    - Boss collisions (core opening=2x, armor=1x)        │
│    - Remaining enemies still interactive                 │
│  STATE_BOSS_DYING (2.5s staggered explosions, escalating  │
│    shake, boss hull visible) → final detonation → hull    │
│    disappears → STATE_VICTORY → restart                   │
└──────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│                       on_draw()                          │
├──────────────────────────────────────────────────────────┤
│ World space (with screen shake):                         │
│  1. Starfield → enemies → powerups → boss → player      │
│  2. Player projectiles → enemy projectiles               │
│  3. Particles → score popups                             │
│ HUD space (no shake):                                    │
│  4. Screen flash overlay                                 │
│  5. HUD (score, multiplier, combo, lives, powerups)      │
│  6. Boss health bar, warning text, victory overlay       │
│  7. Game over overlay                                    │
└──────────────────────────────────────────────────────────┘
```

## Entity Model

### Player
```python
Player:
    x, y: float              # Position
    vx, vy: float            # Velocity
    shoot_timer: float       # Cooldown tracker
    weapon_level: int        # Current powerup tier
    lives: int               # Remaining lives
    invulnerable: float      # Invulnerability timer after hit
    shield: bool             # Active shield powerup
```

### Enemy
```python
Enemy:
    x, y: float              # Position
    health: int              # Hits to destroy
    points: int              # Score value
    pattern: Pattern         # Movement pattern
    pattern_time: float      # Time in current pattern
    can_shoot: bool          # Whether this enemy fires
    shoot_timer: float       # Shooting cooldown
```

### Projectile
```python
Projectile:
    x, y: float              # Position
    vx, vy: float            # Velocity (allows angled shots)
    damage: int              # Damage dealt
    owner: str               # "player" or "enemy"
    projectile_type: str     # "laser", "spread", "missile", etc.
```

### Powerup
```python
Powerup:
    x, y: float              # Position
    powerup_type: str        # "speed", "spread", "shield", "bomb", "multiplier"
    drift_speed: float       # Leftward drift
```

## Boss Behaviour Reference

### Sentinel (Zone 1)
- **Movement**: Tracks player Y with `SENTINEL_TRACK_SPEED` (per phase). Fixed X at `SENTINEL_BATTLE_X`. Phase 2 adds lunges. Phase 3 adds erratic sinusoidal jitter (`SENTINEL_ERRATIC_FREQ`, `SENTINEL_ERRATIC_AMP`).
- **Hull**: Mirrored polygon halves (ADR-010), nose left, engines right. Gap between halves = core opening.
- **Phases**: 3 phases at 66%/33% HP thresholds. Phase 1: spread shots. Phase 2: spread + aimed shots + lunges. Phase 3: radial burst + beam attack + erratic movement.
- **Damage zones**: Core opening (2×), armor (1×) — single HP pool (ADR-009).
- **Death**: ADR-012 staggered multi-burst sequence, hull vanishes at detonation.
- **Exhaust**: 10-layer blue gradient (`SENTINEL_EXHAUST_LAYERS`), ADR-011 pattern.
- **Constants prefix**: `SENTINEL_*`

### Marauder (Zone 2)
- **Movement**: Sinusoidal vertical patrol, wider amplitude and faster frequency than Sentinel. Fixed X on right side of screen. Patrol frequency increases with phase.
- **Patrol**: `MARAUDER_PATROL_FREQ`, `MARAUDER_PATROL_AMP` (see constants.py)
- **Hull**: Mirrored polygon, nose left, engines right. Leaner and more angular than Sentinel. Green accent inner plate. Gap between halves = core opening with throbbing layered energy effect (3 concentric ellipses, pulsing on sine wave).
- **Phases**: 3 phases (HP thresholds). Phase 1: 3-way spread. Phase 2: faster spread + diagonal cross burst. Phase 3: all above + 180° arc burst.
- **Damage zones**: Core opening (2×), armor (1×) — single HP pool (ADR-009)
- **Death**: ADR-012 staggered multi-burst sequence, hull vanishes at detonation
- **No beam attack** — `beam_visible_timer` and `beam_y` exist at 0.0 for interface compatibility only
- **Exhaust**: 10-layer green gradient (`MARAUDER_EXHAUST_LAYERS`), ADR-011 pattern.
- **Constants prefix**: `MARAUDER_*`

### Boss Interface Contract
All bosses expose: `x`, `y`, `core_hp`, `max_hp`, `state`, `phase`, `name`, `is_dead`, collision dimensions (`opening_width/height`, `armor_width/height`, `core_damage`, `body_damage`), `beam_visible_timer`/`beam_y` (0 if no beam). Methods: `update(dt, player_x, player_y) -> list[EnemyProjectile]`, `take_hit(damage)`, `draw()`.

## Powerup System (Planned)

| Powerup | Effect | Duration |
|---------|--------|----------|
| Speed Boost | Increase player max speed | Permanent until death |
| Spread Shot | Fire 3-way or 5-way | Permanent until death |
| Piercing Laser | Shots pass through enemies | Permanent until death |
| Shield | Absorb one hit | Until hit |
| Bomb | Clear screen of enemies | Instant |
| Score Multiplier | 2x points | 15 seconds |
| Drone | Wingman that fires with you | Permanent until death |

## Enemy Patterns (Planned)

- **Linear**: Straight line movement
- **Sine Wave**: Oscillating vertical movement
- **Dive Bomb**: Swoop toward player then retreat
- **Formation**: Group movement in sync
- **Orbiter**: Circle around a point
- **Tracker**: Follow player position
- **Splitter**: Split into smaller enemies when killed

## Development Phases

### Phase 1: Core Engine ✓
- [x] Game window and loop
- [x] Player movement with momentum
- [x] Basic shooting
- [x] Parallax starfield

### Phase 2: Combat ✓
- [x] Enemy spawning system (3 wave patterns, WaveSpawner)
- [x] Enemy movement patterns (straight, sine, diagonal)
- [x] Player-enemy collision
- [x] Projectile-enemy collision
- [x] Explosions and particles (ParticleSystem, ScreenFlash, ScreenShake)
- [x] Powerup system (speed boost, pulse animation)

### Phase 3: Progression ✓
- [x] Scoring system (multiplier, combo, milestones)
- [x] Lives system (3 lives, invulnerability on respawn)
- [x] HUD (sci-fi style: score, multiplier, combo, lives, powerups, zone)
- [x] Score popups (floating text on kills)

### Phase 4: Content (Current)
- [x] Boss fights (Sentinel: 3 phases, armor + core opening, beam attack)
- [x] Sentinel visual redesign — polygon hull with real core gap, layered exhaust
- [x] Massive multi-burst boss death explosion (staggered sub-explosions, 1000+ particles)
- [x] Smooth circular particles with glow layers and opacity fade
- [x] Boss disappears on final detonation
- [x] Powerups cleared on boss transition
- [x] Tiered powerups — speed/fire rate 3-level system with death penalty
- [x] Instant ship movement model (no acceleration ramp)
- [x] Zone infrastructure — ZoneManager, parameterized WaveSpawner, 3-zone progression
- [x] Zone 2: Dart enemy (green arrow, shooters), diagonal cross pattern, nebula background
- [ ] Zone 3: Heavy enemy + pincer/tracker patterns + asteroid background (PRP-08c)
- [x] Zone 2 boss — Marauder (PRP-08d)
- [ ] Zone 3 boss (PRP-08e)
- [ ] Difficulty progression

### Phase 5: Polish
- [ ] Sound effects
- [ ] Music
- [ ] Pixel art sprites
- [x] Screen shake (implemented in Phase 2, enhanced for boss death)
- [x] Particle system overhaul — all circles, tiered sizes, glow layers
- [ ] Title screen / menus
- [ ] High score persistence

## Screen Layout

```
┌─────────────────────────────────────────────────────────────┐
│ SCORE: 00000000    ♦♦♦ LIVES    [SPREAD] [SHIELD]   ZONE 1 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│     ★        ·                    ·                    ★    │
│          ·            ★                   ·                 │
│   ·               ·           ★       ·            ·        │
│        ★     ▶                    ★           ★             │
│     ·        PLAYER    ·                  ·                 │
│          ·         ★          ·       ★        ·            │
│   ★           ·          ·                          ★       │
│        ·           ★              ·           ·             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## File Budget

Target: Each file under 500 lines

| File | Lines | Purpose |
|------|-------|---------|
| constants.py | ~460 | All tunable values + zone configs |
| game.py | ~500 | Main window and loop |
| player.py | ~141 | Player ship (polygon hull, exhaust) |
| projectile.py | ~38 | Player projectiles |
| starfield.py | ~103 | Parallax background + nebula clouds |
| enemy.py | ~129 | Bat wing enemy entity |
| dart.py | ~108 | Zone 2 Dart enemy (shooter) |
| enemy_projectile.py | ~56 | Shared enemy/boss projectile entity |
| wave_spawner.py | ~100 | Wave spawning from zone config |
| zone_manager.py | ~31 | Zone progression (1-3) |
| powerup.py | ~71 | Powerup entity (glassy button) |
| collision.py | ~27 | Collision helpers |
| explosions.py | ~181 | Particle factory functions |
| particles.py | ~105 | ParticleSystem + Particle (circles + glow) |
| scoring.py | ~53 | ScoringSystem (multiplier, combo) |
| score_popup.py | ~74 | Floating score text |
| screen_effects.py | ~68 | ScreenFlash, ScreenShake |
| hud.py | ~411 | HUD, boss health bar, warning, victory, zone transitions |
| boss.py | ~424 | Sentinel boss entity (polygon hull) |
| marauder.py | ~299 | Marauder boss entity (Zone 2) |
| boss_attacks.py | ~72 | Boss attack pattern factories |
| boss_fight.py | ~275 | Boss state handlers, zone transitions, collision |
| debug_skip.py | ~74 | DEBUG ONLY — zone/boss skip keys (remove before release) |
