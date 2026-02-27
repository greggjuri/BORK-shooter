# B.O.R.K. - Architecture Decision Records

## ADR-001: Use Python Arcade Library

**Date**: 2025-02-15  
**Status**: Accepted

### Context
Need to choose a 2D game framework for Python. Main options:
- Pygame (most common, lots of tutorials)
- Arcade (modern, cleaner API)
- Pyxel (built-in retro aesthetic, 16 colors)
- Godot with Python bindings

### Decision
Use the **Arcade** library.

### Rationale
- Cleaner, more modern API than Pygame
- Good documentation
- Built-in support for delta time in game loop
- Easy to draw primitives (good for geometric shape prototyping)
- Sprite support for when we add pixel art
- Active development

### Consequences
- Must install arcade (`pip install arcade`)
- Need to learn Arcade's patterns (Window subclass, on_update/on_draw)
- Locked into Arcade's coordinate system (origin at bottom-left)

---

## ADR-002: Horizontal Scroller Format

**Date**: 2025-02-15  
**Status**: Accepted

### Context
Choosing the game format. Options:
- Vertical scroller (Xenon, 1942)
- Horizontal scroller (Delta, R-Type, Gradius)
- Fixed screen (Galaga, Space Invaders)

### Decision
**Horizontal scroller** (Delta/Sanxion style).

### Rationale
- Matches the primary inspiration (Delta, Sanxion on C64)
- Widescreen displays (16:9) suit horizontal scrolling naturally
- Allows for longer enemy approach patterns
- Classic "flying into danger" feel

### Consequences
- Player on left side of screen
- Enemies approach from right
- Parallax scrolls left
- May need to handle different aspect ratios in the future

---

## ADR-003: Geometric Shapes Before Pixel Art

**Date**: 2025-02-15  
**Status**: Accepted

### Context
Need to decide when to introduce visual assets (sprites). Options:
- Pixel art from day one
- Geometric shapes (triangles, rectangles) during development, pixel art later

### Decision
Start with **geometric shapes**, add pixel art in a polish pass.

### Rationale
- Faster iteration during core gameplay development
- Don't want art to block progress
- Easier to change sizes/hitboxes when everything is parameterized
- Polish is explicitly deferred to Phase 5
- Can still nail the "feel" with shapes

### Consequences
- Early builds will look programmer-arty
- Need to design with eventual sprite swap in mind
- Asset pipeline (sprite loading) added later

---

## ADR-004: Momentum-Based Movement

**Date**: 2025-02-15  
**Status**: Accepted

### Context
Player ship movement style. Options:
- Instant movement (press right = immediately at max speed)
- Momentum-based (acceleration/deceleration)

### Decision
**Momentum-based** movement with acceleration and friction.

### Rationale
- Matches Delta/Sanxion feel ("sliding on ice")
- More satisfying and skill-based
- Allows for subtle control — tap for small adjustments, hold for speed
- Makes dodging feel more tense

### Consequences
- Need to tune acceleration, friction, and max speed carefully
- Diagonal movement needs normalization to prevent faster diagonal speed
- May feel floaty to players used to instant response — values are tunable

---

## ADR-005: Constants Centralized in One File

**Date**: 2025-02-15  
**Status**: Accepted

### Context
Where to put magic numbers (speeds, sizes, colors, timings).

### Decision
All constants in a single `constants.py` file.

### Rationale
- Easy to find and tweak values
- No hunting through code for magic numbers
- Enables quick balance adjustments
- Single source of truth

### Consequences
- `constants.py` will grow as features are added
- May need to organize into sections (PLAYER, ENEMY, POWERUP, etc.)
- All modules import from constants

---

## ADR-006: Entity Pattern (update/draw methods)

**Date**: 2025-02-15  
**Status**: Accepted

### Context
How to structure game objects (player, enemies, projectiles).

### Decision
Each entity is a class with `update(dt)` and `draw()` methods.

### Rationale
- Simple, predictable pattern
- Easy to iterate over lists of entities
- Clear separation of logic and rendering
- Scales well as entity types grow

### Consequences
- All game objects follow same interface
- Game loop calls update on all entities, then draw on all entities
- Inheritance or composition for shared behavior (e.g., base Enemy class)

---

## ADR-007: File Size Limit (500 lines)

**Date**: 2025-02-15  
**Status**: Accepted

### Context
Preventing monolithic files that are hard to navigate and maintain.

### Decision
**500 lines max** per file. Split when approaching this limit.

### Rationale
- Forces modularity
- Easier to understand individual files
- Better for version control (smaller diffs)
- Encourages separation of concerns

### Consequences
- May need more files than a "simple" project would have
- Must plan file structure ahead of time
- Enemy types may each get their own file if complex

---

## ADR-008: Boss State Extraction Pattern

**Date**: 2026-02-26
**Status**: Accepted

### Context
The Sentinel boss fight added 6 game states (warning, fight, dying, victory) with collision handlers, state transitions, and scoring logic. Putting all of this in `game.py` pushed it over the 500-line limit (679 lines).

### Decision
Extract boss state handlers and boss-specific collision methods into a separate `boss_fight.py` module. The module imports `BorkGame` via `TYPE_CHECKING` and takes the game instance as a parameter.

### Rationale
- Keeps `game.py` under 500 lines (ADR-007)
- Boss logic is cohesive and self-contained
- `TYPE_CHECKING` import avoids circular dependencies
- Pattern can be reused for future boss types or game modes

### Consequences
- Boss state handlers live in `boss_fight.py`, not on the `BorkGame` class
- Normal enemy collision methods remain on `BorkGame` and are called by boss handlers when enemies are present during boss states
- Adding new bosses follows the same extraction pattern

---

## ADR-009: Simplified Boss Damage Model (Armor + Core Opening)

**Date**: 2026-02-26
**Status**: Accepted (supersedes original wing-based design)

### Context
The original Sentinel design had destructible wings as separate HP pools with their own attacks, scoring, and collision zones. This added complexity without matching the intended design of a solid armored fortress.

### Decision
Replace wing system with a 2-zone damage model: core opening (2x damage) and armor (1x damage). Both reduce the single core HP pool. No separate destructible components.

### Rationale
- Simpler collision logic (2 zones vs 4)
- Clearer player feedback (aim for the opening = more damage)
- Fewer edge cases (wing destruction events, partial boss states)
- Easier to tune difficulty

### Consequences
- Boss has only one HP pool (core HP)
- Phase 1 and Phase 2 have fewer attack patterns (no wing attacks)
- Victory scoring is simpler (core points + no-damage bonus only)
- May need to compensate for reduced difficulty via tighter attack timing

---

## Template for New ADRs

```markdown
## ADR-XXX: Title

**Date**: YYYY-MM-DD  
**Status**: Proposed / Accepted / Deprecated / Superseded

### Context
What is the issue or decision we're facing?

### Decision
What did we decide?

### Rationale
Why did we choose this option?

### Consequences
What are the implications (good and bad)?
```
