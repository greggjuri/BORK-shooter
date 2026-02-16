# Init Template - Feature Specification

## init-01: Core Engine

**Created**: 2025-02-15  
**Priority**: High  
**Depends On**: None

---

## Problem Statement

B.O.R.K. needs a solid foundation before we can add enemies, powerups, and explosions. We need the core game loop, player ship, scrolling starfield, and basic shooting mechanics working first.

## Goal

A playable prototype where the player can fly a ship horizontally across the screen, shoot lasers, and see a scrolling parallax starfield. The foundation that everything else builds on.

## Requirements

### Must Have (P0)
1. Game window (960x540 or similar 16:9) with consistent 60 FPS
2. Player ship with smooth 8-directional movement (arrow keys or WASD)
3. Player can shoot basic laser projectiles (spacebar)
4. Horizontal scrolling parallax starfield (at least 2 layers)
5. Player ship constrained to screen bounds
6. Clean game loop with update/draw separation

### Should Have (P1)
1. Ship has slight acceleration/deceleration (not instant stop)
2. Shooting has cooldown (can't hold spacebar for laser stream)
3. Basic ship sprite (can be simple geometric shape initially)
4. Projectiles despawn when leaving screen

### Nice to Have (P2)
1. Screen shake foundation (for later explosions)
2. Delta time handling for consistent speed across frame rates

## User Stories

**As a** player  
**I want to** move my ship smoothly in all directions  
**So that** I can dodge enemies and position for shots

**As a** player  
**I want to** shoot lasers  
**So that** I can destroy enemies (when they exist)

## Technical Considerations

### Data Changes
- Player entity with position, velocity, sprite
- Projectile entity with position, velocity, damage
- Star entity with position, speed, layer (for parallax)

### API Changes
- N/A (standalone game)

### UI Changes
- Game window with starfield background
- Player ship sprite
- Laser projectile sprites

### Integration Points
- Python Arcade library for rendering and input
- Future: Sound system hooks

## Constraints

- Python Arcade library (not Pygame)
- Single file initially, split when approaching 500 lines
- Must run at stable 60 FPS on modest hardware
- No external assets required for this phase (geometric shapes OK)

## Success Criteria

- [ ] Game window opens at target resolution
- [ ] Player ship responds to arrow keys / WASD
- [ ] Player ship cannot leave screen bounds
- [ ] Spacebar fires laser projectiles
- [ ] Projectiles travel right and despawn off-screen
- [ ] Parallax starfield scrolls continuously left
- [ ] Maintains 60 FPS

## Out of Scope

- Enemies (init-02)
- Collisions with enemies (init-02)
- Powerups (init-03)
- Sound effects (init-06)
- Scoring / HUD (init-05)
- Title screen / menus

## Open Questions

- [x] Screen resolution: 960x540 (16:9, scales well)
- [x] Framework: Python Arcade
- [x] Ship sprite style: Geometric shapes initially, pixel art polish later

## Notes

Inspiration: Delta, Sanxion (C64) - horizontal scrollers with momentum and smooth parallax. The feel should be responsive but not twitchy.
