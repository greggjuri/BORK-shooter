# B.O.R.K. - Architecture & Planning

## Overview

B.O.R.K. is a horizontal scrolling shoot 'em up built with Python and the Arcade library. Inspired by Delta, Sanxion (C64), Xenon, Galaga, and Gyruss.

**Core pillars:**
- Learnable enemy patterns for skill mastery
- Satisfying powerup progression
- Chunky explosions and impactful feedback
- Boss fights that test everything you've learned

## Tech Stack

- **Language**: Python 3.8+
- **Framework**: Arcade (2D game library)
- **Testing**: pytest
- **Linting**: ruff

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        BorkGame                             │
│                    (arcade.Window)                          │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Starfield  │  │   Player    │  │     GameState       │ │
│  │  (background)│  │   (ship)    │  │  (score, lives,     │ │
│  │             │  │             │  │   level, phase)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Projectiles │  │   Enemies   │  │      Powerups       │ │
│  │   (list)    │  │   (list)    │  │       (list)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Explosions  │  │    Boss     │  │     SoundManager    │ │
│  │ (particles) │  │  (special)  │  │    (SFX + music)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Game Loop

```
┌──────────────────────────────────────────────────────────┐
│                      on_update(dt)                       │
├──────────────────────────────────────────────────────────┤
│ 1. Update starfield (scroll)                            │
│ 2. Update player (movement, shoot cooldown)             │
│ 3. Update projectiles (move, despawn off-screen)        │
│ 4. Update enemies (patterns, shooting)                  │
│ 5. Update powerups (drift, despawn)                     │
│ 6. Check collisions:                                    │
│    - Player projectiles vs enemies                      │
│    - Enemy projectiles vs player                        │
│    - Player vs powerups                                 │
│    - Player vs enemies (collision damage)               │
│ 7. Spawn explosions for destroyed entities              │
│ 8. Update explosions (animate, despawn)                 │
│ 9. Check win/lose conditions                            │
│ 10. Update UI (score, lives, powerup indicators)        │
└──────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│                       on_draw()                          │
├──────────────────────────────────────────────────────────┤
│ 1. Clear screen                                         │
│ 2. Draw starfield (back layer)                          │
│ 3. Draw enemies                                         │
│ 4. Draw powerups                                        │
│ 5. Draw player                                          │
│ 6. Draw projectiles (player + enemy)                    │
│ 7. Draw explosions                                      │
│ 8. Draw starfield (front layer, optional)               │
│ 9. Draw HUD (score, lives, powerups)                    │
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

### Phase 1: Core Engine ✓ (Current)
- [x] Game window and loop
- [x] Player movement with momentum
- [x] Basic shooting
- [x] Parallax starfield

### Phase 2: Combat
- [ ] Enemy spawning system
- [ ] Enemy movement patterns
- [ ] Player-enemy collision
- [ ] Projectile-enemy collision
- [ ] Explosions and particles

### Phase 3: Progression
- [ ] Powerup drops
- [ ] Powerup effects
- [ ] Scoring system
- [ ] Lives system
- [ ] HUD

### Phase 4: Content
- [ ] Multiple enemy types
- [ ] Boss fights
- [ ] Multiple levels/zones
- [ ] Difficulty progression

### Phase 5: Polish
- [ ] Sound effects
- [ ] Music
- [ ] Pixel art sprites
- [ ] Screen shake
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

| File | Estimated Lines | Purpose |
|------|-----------------|---------|
| constants.py | ~50 | All tunable values |
| game.py | ~150 | Main window and loop |
| player.py | ~80 | Player ship |
| projectile.py | ~50 | Projectiles |
| starfield.py | ~60 | Background |
| enemies/base.py | ~100 | Enemy base class |
| enemies/patterns.py | ~150 | Movement patterns |
| powerups.py | ~100 | Powerup system |
| explosions.py | ~80 | Particle effects |
| hud.py | ~60 | Score/lives display |
| sound.py | ~50 | Sound management |
