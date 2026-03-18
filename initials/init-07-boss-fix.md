# Boss Modification: Sentinel Redesign - Simple

## Design: Armored Body with Core Opening

Simple geometric fortress. Solid armored body with a small opening in the front. The glowing core is visible through that opening.

### Visual Layout

```
        ┌─────────────────────────────┐
        │                             │
        │        UPPER ARMOR          │
        │                             │
        ├─────────────────────────────┤
        │                             │
        │      ═══════●═══════        │  ← opening with core visible
        │                             │
        ├─────────────────────────────┤
        │                             │
        │        LOWER ARMOR          │
        │                             │
        └─────────────────────────────┘
        
        ←←←←  Player shoots from left
```

### Components (only 3)

1. **Upper Armor** — top half of body
2. **Lower Armor** — bottom half of body
3. **Core Opening** — horizontal slot in center with glowing core inside

That's it. No wings.

### Collision

1. **Core opening** (center slot) → 2x damage to core HP
2. **Upper Armor** → 1x damage to core HP
3. **Lower Armor** → 1x damage to core HP

### Damage

```python
SENTINEL_CORE_DAMAGE = 2    # shots through opening
SENTINEL_BODY_DAMAGE = 1    # shots hitting armor
```

### Visual

- **Armor**: Dark gray `(80, 85, 95)` with cyan accent lines
- **Opening**: Dark recessed slot `(20, 25, 35)`
- **Core**: Glowing red-orange `(255, 80, 40)`, pulses

### Bug Fixes

1. Boss spawns after 9 COMPLETE waves, not 9 spawns
2. Existing enemies continue during warning, don't vanish
3. Check core hitbox FIRST, then armor

### Points

- Core destroyed: 5,000 points
- No-damage bonus: 2,500 points

## Files to Modify

- `bork/boss.py` — Remove wings entirely, new draw/collision
- `bork/constants.py` — Remove wing constants, simplify
- `bork/wave_spawner.py` — Fix wave count
- `bork/game.py` — Remove wing logic, fix enemy clearing
