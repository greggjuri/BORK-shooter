# B.O.R.K. - Task Tracking

## Current Sprint: Content & Polish

**Goal**: Boss polish, visual overhaul, new content

### In Progress
_(none)_

### Ready
- [ ] Multiple enemy types
- [ ] Multiple levels/zones
- [ ] Difficulty progression
- [ ] Sound system (init-06)

### Done
- [x] Set up project structure (CE-templates)
- [x] init-01: Core Engine — player ship, shooting, parallax starfield (PRP-001 complete)
- [x] init-02: Enemy System — 3 wave patterns, collisions, game over, restart (PRP-002 complete)
- [x] init-03: Powerup System — speed boost, pulse animation, wave 3 trigger (PRP-003 complete)
- [x] init-04: Explosions — particle system, screen flash, screen shake (PRP-004 complete)
- [x] init-05: Scoring & HUD — score, multiplier, combo, lives, sci-fi HUD, popups (PRP-005 complete)
- [x] init-07: Boss fights — Sentinel boss with 3 phases, enemy projectiles, beam attack (PRP-007 complete)
- [x] init-07-fix: Sentinel redesign — remove wings, simplify to armor + core opening (PRP-007b complete)
- [x] fix: Enemy collisions active during boss warning/fight, 5s warning delay
- [x] feat: Sentinel engine exhaust with layered gradient glow (10-layer blue ellipses)
- [x] fix: Clear powerups when boss appears (prevents stale powerups during boss fight)
- [x] fix: Rebuild Sentinel as polygon-based ship hull with real core gap (replaced rectangles)
- [x] feat: Massive multi-burst boss death explosion (staggered sub-explosions, 5 final bursts, 1000+ particles)
- [x] fix: Smoother circular explosion particles with opacity fade, tiered sizes, and glow layers
- [x] fix: Boss hull disappears on final detonation (no lingering sprite)
- [x] docs: Added "too much is not enough" design principle

---

## Backlog

### Phase 2: Combat ✓
- [x] init-02: Enemy system (spawning, patterns, collision)
- [x] init-03: Powerup system
- [x] init-04: Explosions & particle effects

### Phase 3: Progression ✓
- [x] init-05: Scoring & UI (HUD, lives, multipliers)
- [ ] init-06: Sound system (SFX, music)

### Phase 4: Content (Current)
- [x] init-07: Boss fights (PRP-007 + PRP-007b complete)
- [x] Sentinel visual overhaul (polygon hull, exhaust, death explosion, particle rework)
- [ ] init-08: Levels & progression
- [ ] Multiple enemy types

### Phase 5: Polish
- [ ] Pixel art sprites
- [x] Screen shake (implemented in init-04, enhanced for boss death)
- [x] Particle system overhaul (circles, glow, tiered sizes, opacity fade)
- [ ] Title screen / menus
- [ ] High score persistence

---

## Nasty Surprises Wishlist

Ideas for unexpected twists to keep players on their toes:

- [ ] Enemies that split when killed
- [ ] Sudden speed changes (slowdown zones, speed boost zones)
- [ ] "Fake" powerups that debuff you
- [ ] Screen-flip moments (gravity reversal?)
- [ ] Bullet-reflecting enemies
- [ ] Enemies that appear from behind
- [ ] Environmental hazards (asteroids, laser gates)
- [ ] Decoy bosses

---

## Known Issues

_(none)_

---

## Notes

- Sound system (init-06) can be done in parallel with other features
- Particle pool size bumped to 1500 to accommodate boss death (was 500)
- All explosion particles are now circles — shape parameter retained in Particle class but unused for squares/triangles
- Boss hull hides at STATE_VICTORY transition; sub-explosions play over visible hull during STATE_BOSS_DYING
- Powerups are cleared and spawn timer reset when transitioning to STATE_BOSS_WARNING
