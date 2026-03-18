# init-08b: Zone 2 Content — Dart Enemy, Diagonal Cross, Nebula Background

## Overview

Fill in Zone 2 ("Nebula") with its own identity: a new fast enemy type, a new wave pattern, and a distinct background. This builds on the zone infrastructure from PRP-08a.

## Zone 2 Enemy: Dart

A small, fast, aggressive ship that comes in tight clusters. Contrasts the bat wing's wider, wobblier style.

### Visual Design
- **Shape**: Small pointed triangle/arrow facing left — sharp, minimal, fast-looking
- **Color scheme**: Green/lime to contrast Zone 1's red enemies
- **Scanner eye**: Small green glow at center
- **Size**: ~60-70% of the bat wing — should feel like a swarm of smaller ships
- **Detail**: Minimal — these are fast and disposable, not armored. Maybe a single hull line or two small fins
- **No wobble** — these fly straight and direct, their speed IS the threat

### Behavior
- **HP**: 1 (one hit kill, same as bat wing)
- **Speed**: Uses zone config `enemy_speed` (180.0 for Zone 2, faster than Zone 1's 150.0)
- **Shooting**: Can fire single aimed shots at the player's position (simple leading shot)
  - Not every dart shoots — maybe 30-40% chance per wave of a dart being a "shooter"
  - Shoot cooldown: ~2 seconds
  - Projectile speed: moderate, dodgeable but forces movement

### Constants
- Prefix: `ENEMY_DART_`
- Colors, size, shoot chance, shoot cooldown, projectile speed all in `constants.py`

## New Wave Pattern: Diagonal Cross

Enemies enter from top-right and bottom-right simultaneously, crossing paths in the middle of the screen.

### Pattern Details
- **Top group**: Enters from upper-right, travels diagonally down-left, exits lower-left
- **Bottom group**: Enters from lower-right, travels diagonally up-left, exits upper-left
- The two streams cross near screen center — creates a dangerous X-shaped kill zone
- Each group is half the wave's enemy count (e.g. 3 from top, 3 from bottom for 6 total)
- Stagger the entries slightly so they don't perfectly overlap

### Integration
- Added as 4th pattern in Zone 2's `wave_patterns` config
- Pattern string: `"diagonal_cross"`
- Zone 2 rotates through: straight top → straight bottom → sine center → diagonal cross

## Nebula Background

Zone 2's starfield should feel different from Deep Space — more colorful, more atmosphere.

### Visual Design
- **Base starfield**: Keep the parallax star layers but tint stars slightly purple/blue
- **Nebula clouds**: 3-5 large, slow-drifting semi-transparent colored shapes in the background layer
  - Colors: Purple, pink, deep blue — low opacity (0.05-0.15)
  - Move slower than the slowest star layer (deep parallax)
  - Soft shapes — large ellipses or clusters of overlapping ellipses
  - These are backdrop atmosphere, not gameplay elements
- **Optional**: A few brighter star clusters (small groups of slightly larger/brighter stars)

### Implementation
- Starfield gets a `set_style(style_name)` method or accepts a style config
- Zone manager passes background style on zone transition
- Nebula clouds are simple parallax entities in the starfield system

## Files Affected

- `constants.py` — Dart enemy constants, diagonal cross pattern constants, nebula colors
- `enemy.py` — New Dart enemy type (subclass or parameterized variant with distinct draw method)
- `wave_spawner.py` — Add diagonal cross pattern spawning logic
- `starfield.py` — Add nebula background style with colored clouds
- `zone_manager.py` — Possibly minor updates to pass background style
- `game.py` — Wire background style switching on zone transition
- Update Zone 2 config in `ZONE_CONFIGS` to use `"dart"` enemy type and include `"diagonal_cross"` pattern

## Enemy Shooting System

This is the first time regular enemies shoot back. Needs a lightweight system:
- Reuse `EnemyProjectile` from `boss_attacks.py` (or extract to shared module if needed)
- Dart enemies that are flagged as shooters fire aimed shots on a cooldown
- Enemy projectiles follow the same collision path as boss projectiles (damage player)
- Keep it simple — no fancy bullet patterns, just single aimed shots

## Constraints

- No magic numbers — all values in constants.py
- File budget: 500 lines max per file
- Geometric shapes only (ADR-003)
- Entity pattern: update(dt) and draw() methods
- Enemy type selection driven by zone config `enemy_type` field
- Dart enemy should be clearly visually distinct from bat wing at game speed
