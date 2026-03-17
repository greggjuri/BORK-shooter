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

## ADR-004: Instant Movement at Tier Speed

**Date**: 2025-02-15 (revised 2026-03-17)
**Status**: Accepted (supersedes original momentum-based design)

### Context
Player ship movement was originally momentum-based (acceleration + friction). After adding tiered speed powerups with instant movement, the acceleration ramp-up masked the difference between tiers — collecting a powerup didn't feel noticeably different until the ship had time to accelerate to the new max.

### Decision
**Instant movement** — when a direction key is held, the ship moves at `SPEED_LEVELS[speed_level - 1]` immediately. When released, the ship stops instantly. No acceleration or friction.

### Rationale
- Tier speed changes are felt immediately on powerup collection
- Simpler movement model — easier to predict and control
- Removes PLAYER_ACCELERATION, PLAYER_FRICTION, TARGET_FPS from player.py
- Diagonal movement still normalized to prevent faster diagonal speed
- Speed values tuned lower (200/300/420) to compensate for no ramp-up

### Consequences
- No "sliding on ice" feel — movement is direct and responsive
- Diagonal normalization still required
- Speed tuning is simpler (one value per tier instead of acceleration + friction + max speed)

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

## ADR-010: Polygon-Based Ship Hulls

**Date**: 2026-03-16
**Status**: Accepted

### Context
The Sentinel boss was rendering as a flat rectangle — `draw_lrbt_rectangle_filled` for the body with a rectangle "opening" painted on top. This looked wrong; the concept called for a swept, ship-like silhouette with a real gap for the core opening.

### Decision
Replace rectangle-based boss rendering with mirrored polygon hulls (top half and bottom half) using `draw_polygon_filled`. Each hull half has an outer shell and an inset inner armor plate. The gap between the two halves IS the core opening — no separate opening rectangle needed.

### Rationale
- Polygons create a proper ship silhouette (tapered nose, widening body toward rear engines)
- Real gap between hull halves makes the core opening visually obvious
- Layered polygons (outer hull + inner plate) add depth without sprites
- Detail elements (panel lines, weapon ports, vents, nose ellipse) add visual interest cheaply
- Pattern matches the player ship's polygon-based rendering

### Consequences
- Hull vertex coordinates are defined as module-level tuples, scaled from a 160px reference to SENTINEL_WIDTH
- Collision detection still uses simple rectangles (point_in_rect) — visual and collision shapes are decoupled
- Adding new boss types should follow the same mirrored-polygon pattern
- `SENTINEL_ARMOR_COLOR` and `SENTINEL_OPENING_COLOR` constants are no longer used by boss.py draw code (retained for potential future use)

---

## ADR-011: Layered Gradient Engine Exhaust

**Date**: 2026-03-16
**Status**: Accepted

### Context
Engine exhaust effects on both the player ship and boss used simple shapes. The player had a proven layered ellipse approach defined in `EXHAUST_LAYERS` — a tuple of (offset, width, height, r, g, b, alpha) values sorted outermost-first.

### Decision
Apply the same layered gradient pattern to the Sentinel's engine exhaust. Define `SENTINEL_EXHAUST_LAYERS` as a 10-layer tuple graduating from light blue (140, 140, 255) at low opacity to dark blue (30, 30, 180) at higher opacity. Draw exhaust for both top and bottom engine positions.

### Rationale
- Consistent visual language between player and boss
- Loop-over-tuples pattern is simple and fast
- Constants-driven: easy to tune colors and sizes without touching draw code

### Consequences
- Each engine draws 10 ellipses per frame (20 total for two engines) — negligible performance impact
- Exhaust positions are hardcoded relative to hull vertex coordinates

---

## ADR-012: Massive Multi-Burst Boss Death Sequence

**Date**: 2026-03-16
**Status**: Accepted

### Context
The original boss death was a single explosion burst (50-80 particles) with a screen shake. For a boss fight that takes significant effort to win, the payoff felt underwhelming.

### Decision
Overhaul the boss death to be deliberately excessive ("too much is not enough"):
- 2.5-second death sequence with sub-explosions every 0.08s (25-40 particles each)
- Escalating screen shake throughout the sequence
- Final detonation: 5 overlapping full explosions (180-250 particles each, ~1000 total)
- Boss hull disappears at final detonation, leaving only particles
- Particle pool bumped from 500 to 1500

### Rationale
- Boss death should feel like an event — the reward for sustained combat
- Staggered explosions across the hull create a "breaking apart" effect
- Escalating shake builds tension before the finale
- Hull vanishing at the climax makes the explosion feel like it actually destroyed something

### Consequences
- Particle pool increased 3x (1500) — may need monitoring on lower-end hardware
- Boss death duration increased from 2.0s to 2.5s
- Victory state begins only after particles clear (3.0s victory display)

---

## ADR-013: Circular Particles with Glow Layers

**Date**: 2026-03-16
**Status**: Accepted

### Context
Explosion particles used mixed shapes (squares, triangles, circles) which looked jagged and inconsistent. Particles disappeared abruptly at end of life.

### Decision
All explosion particles now render as circles (`draw_circle_filled`). Particles larger than 4px radius get a glow layer — a second circle at 1.6x size with 1/4 opacity drawn behind. Size distribution uses a tiered system: 60% tiny (1-3px), 30% medium (3-8px), 10% large (6-14px).

### Rationale
- Circles look smoother and more natural for explosions/fire
- Glow layers on large particles create a soft halo effect without shaders
- Tiered sizes create depth — many tiny sparks with a few big glowing embers
- Alpha fadeout was already implemented (`alpha = 255 * (1 - progress)`)

### Consequences
- `shape` parameter retained on Particle class but effectively unused for non-circle values
- Slightly higher draw cost per large particle (2 draw calls instead of 1)
- Factory functions no longer import `*_SIZE` constants (sizes are inline in `_pick_size` calls)

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
