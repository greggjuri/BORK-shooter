# init-09: Tiered Powerup System

## Overview

Replace the single-level speed boost with a tiered powerup progression system. Speed and fire rate each have 3 levels. Powerups raise levels, death drops them. HUD shows current levels.

## Requirements

### Tiered Levels

- **Speed**: 3 levels (1 = base, 2 = boosted, 3 = max)
- **Fire rate**: 3 levels (1 = base/slow, 2 = medium, 3 = fast)
- Both start at level 1 on game start
- Each level maps to a concrete value in `constants.py`:
  - `SPEED_LEVELS = [base_speed, level2_speed, level3_speed]`
  - `FIRE_RATE_LEVELS = [base_cooldown, level2_cooldown, level3_cooldown]`
- Values should feel meaningfully different between tiers

### Powerup Behavior

- **Speed powerup (existing)**: Collecting raises speed level by 1
- At max level (3), collecting additional powerups has no stat effect (still collect for score if applicable)
- **Fire rate powerup**: Not spawning yet — wire up the level system so it's ready when we add the pickup later
- Fire rate was recently halved — level 1 should reflect this slower base rate

### Death Penalty

- On player death, both speed level and fire rate level drop by 1
- Minimum level is 1 (can't go below base)

### Speed Powerup Visual

- Keep the glassy button aesthetic (layered semi-transparent circles, highlight, glow)
- **Must have letter "S" inside** — white/bright, centered
- Outer glow to make it feel collectible and worth chasing

### HUD Indicators

- Display at bottom of screen
- **SPD** label with current level (1/2/3)
- **ROF** label with current level (1/2/3)
- Match existing sci-fi HUD style (cyan, geometric framing)
- Compact and unobtrusive — don't compete with main HUD elements

## Constants

All new values in `constants.py`:
- `SPEED_LEVELS` — list of 3 speed values per tier
- `FIRE_RATE_LEVELS` — list of 3 cooldown values per tier
- Powerup visual colors (glassy button palette)
- HUD indicator positions and styling

## Files Affected

- `constants.py` — new tier values, visual constants
- `player.py` — speed_level and fire_rate_level properties, death penalty logic
- `powerup.py` — glassy button visual with "S" label
- `hud.py` — SPD/ROF indicators at bottom of screen
- `game.py` — powerup collection logic (apply level-up instead of flat boost)

## Constraints

- No magic numbers — all values in constants.py
- File budget: 500 lines max per file
- Geometric/sci-fi visual style (cyan/white, sharp, no rounded elements)
- Entity pattern: update(dt) and draw() methods
