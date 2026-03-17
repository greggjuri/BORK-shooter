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
│  STATE_BOSS_DYING → STATE_VICTORY → restart              │
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
- [ ] Multiple enemy types
- [ ] Multiple levels/zones
- [ ] Difficulty progression

### Phase 5: Polish
- [ ] Sound effects
- [ ] Music
- [ ] Pixel art sprites
- [x] Screen shake (implemented in Phase 2)
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
| constants.py | ~240 | All tunable values |
| game.py | ~455 | Main window and loop |
| player.py | ~80 | Player ship |
| projectile.py | ~30 | Player projectiles |
| starfield.py | ~60 | Parallax background |
| enemy.py | ~60 | Enemy entity |
| wave_spawner.py | ~90 | Wave spawning, boss trigger |
| powerup.py | ~50 | Powerup entity |
| collision.py | ~30 | Collision helpers |
| explosions.py | ~180 | Particle factory functions |
| particles.py | ~100 | ParticleSystem + Particle |
| scoring.py | ~70 | ScoringSystem (multiplier, combo) |
| score_popup.py | ~60 | Floating score text |
| screen_effects.py | ~60 | ScreenFlash, ScreenShake |
| hud.py | ~335 | HUD, boss health bar, warning, victory |
| boss.py | ~380 | Sentinel boss entity |
| boss_attacks.py | ~125 | EnemyProjectile + attack factories |
| boss_fight.py | ~225 | Boss state handlers + collision |
