# init-08: Levels & Progression

## Overview

Add a 3-zone progression system. Each zone has its own enemy types, wave patterns, background style, and difficulty curve. Beating the boss at the end of a zone transitions to the next zone. Beating Zone 3's boss wins the game.

## Zone Structure

### Zone 1: Deep Space (current)
- **Background**: Current dark starfield (already done)
- **Enemy type**: Bat wing (existing `ENEMY_BATWING`)
- **Wave patterns**: Current 3 patterns (top straight, bottom straight, center sine)
- **Boss**: Sentinel (existing)
- **Difficulty**: Base — current enemy speed, count, and aggression
- **Waves before boss**: 9 (current)

### Zone 2: Nebula
- **Background**: Starfield with colored nebula clouds drifting through — purple/pink hues, maybe some particle wisps
- **Enemy type**: NEW — a faster, smaller enemy (suggest: "Dart" or "Stinger" — small triangular ship, quick, comes in tighter formations)
- **Wave patterns**: 4 patterns — existing 3 plus a new diagonal cross pattern (enemies enter top-right, exit bottom-left and vice versa simultaneously)
- **Boss**: NEW — different from Sentinel, design TBD (could be a fast-moving boss vs the Sentinel's fortress style)
- **Difficulty**: +20% enemy speed, +1 enemy per wave, enemies start shooting back (simple aimed shots)
- **Waves before boss**: 12

### Zone 3: Asteroid Belt
- **Background**: Starfield with drifting asteroid shapes (brown/gray geometric rocks in parallax layers)
- **Enemy type**: NEW — a tanky enemy (suggest: "Heavy" or "Crusher" — larger, takes 2-3 hits, slower, fires back)
- **Wave patterns**: 5 patterns — all previous plus a pincer pattern (enemies from top AND bottom simultaneously) and a tracker pattern (enemies that drift toward player Y position)
- **Boss**: NEW — design TBD (could combine Sentinel's fortress with Zone 2 boss's mobility)
- **Difficulty**: +40% enemy speed over base, +2 enemies per wave, all enemies shoot, boss has more HP
- **Waves before boss**: 15

## Zone Transition

1. Player defeats boss → `STATE_VICTORY` displays "ZONE X COMPLETE" for 3 seconds
2. Brief fade-to-black or flash transition
3. Zone counter increments, new zone loads (background, enemy type, wave config)
4. Wave counter resets, player keeps current powerup levels
5. After Zone 3 boss: "GAME COMPLETE" victory screen → R to restart from Zone 1

## Architecture

### ZoneManager (new module: `zone_manager.py`)
- Holds current zone number (1-3)
- Returns zone config: enemy type, wave patterns, wave count before boss, difficulty multipliers, background style, boss type
- Zone configs defined as data in `constants.py`

### Changes to Existing Systems
- **WaveSpawner**: Receives zone config instead of hardcoded values. Pattern list, enemy count, enemy speed come from zone config.
- **Starfield**: Add ability to switch background style (color palette, optional cloud/asteroid layers)
- **Enemy**: Base enemy class stays. New enemy types as subclasses or parameterized variants.
- **Boss**: Boss base class or factory pattern for different boss types per zone.
- **HUD**: Show current zone number (already has zone display slot)
- **game.py**: On victory, check if more zones remain → transition or final victory

## New Enemy Designs

### Zone 2: Dart/Stinger
- Small, fast, triangular
- Minimal HP (1 hit kill)
- Comes in tight clusters
- Can fire single aimed shots at player
- Color scheme: green/yellow to contrast Zone 1 red

### Zone 3: Heavy/Crusher
- Larger, slower
- Takes 2-3 hits
- Fires spread shots
- Color scheme: orange/white
- Maybe a slight shield shimmer effect

## Constants

All per-zone values in `constants.py`:
```python
ZONE_CONFIGS = {
    1: {
        "name": "DEEP SPACE",
        "waves_before_boss": 9,
        "enemy_type": "batwing",
        "wave_patterns": ["top_straight", "bottom_straight", "center_sine"],
        "enemy_speed_mult": 1.0,
        "enemy_count_bonus": 0,
        "enemies_shoot": False,
        "boss_type": "sentinel",
        "bg_style": "deep_space",
    },
    2: { ... },
    3: { ... },
}
```

## Files Affected

- `constants.py` — zone configs, new enemy constants, new background colors
- `zone_manager.py` — NEW: zone state and config lookup
- `wave_spawner.py` — parameterize from zone config
- `enemy.py` — refactor to support multiple enemy types (subclass or parameterized)
- `starfield.py` — add background style switching (nebula clouds, asteroids)
- `boss.py` — refactor for multiple boss types (or new boss modules)
- `boss_fight.py` — handle different boss types
- `hud.py` — zone display updates
- `game.py` — zone transition logic on victory

## Constraints

- No magic numbers — all values in constants.py
- File budget: 500 lines max per file
- New enemy types follow entity pattern (update/draw)
- Geometric shapes only (ADR-003)
- Boss extraction pattern (ADR-008) for new bosses
- Player keeps powerup levels across zone transitions
- Game over resets to Zone 1

## Scope Notes

This is a BIG init. Consider splitting into sub-PRPs:
- **PRP-08a**: Zone manager + zone transition + parameterized wave spawner
- **PRP-08b**: Zone 2 enemy type + wave pattern + background
- **PRP-08c**: Zone 3 enemy type + wave patterns + background  
- **PRP-08d**: Zone 2 boss
- **PRP-08e**: Zone 3 boss

Start with 08a to get the infrastructure in place, then layer content on top.
