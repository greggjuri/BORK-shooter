# B.O.R.K. - Testing Standards

## Test Commands

```bash
# Run all tests
pytest bork/tests/ -v

# Run specific test file
pytest bork/tests/test_player.py -v

# Run with coverage
pytest bork/tests/ --cov=bork --cov-report=term-missing

# Run tests matching a pattern
pytest bork/tests/ -k "player"
```

## Test Structure

```
bork/tests/
├── __init__.py
├── test_player.py        # Player movement, shooting cooldown (159 lines)
├── test_projectile.py    # Projectile movement, despawning (29 lines)
├── test_starfield.py     # Star spawning, parallax scrolling (35 lines)
├── test_enemy.py         # Enemy entity, patterns (38 lines)
├── test_collision.py     # Collision helpers (28 lines)
├── test_powerup.py       # Powerup entity (35 lines)
├── test_scoring.py       # Scoring system, multiplier, combo (100 lines)
├── test_explosions.py    # Explosion factories, particle shapes (59 lines)
├── test_particles.py     # Particle system, lifecycle (93 lines)
├── test_screen_effects.py # ScreenFlash, ScreenShake (44 lines)
├── test_wave_spawner.py  # Wave spawning, boss trigger (155 lines)
├── test_hud.py           # HUD rendering (35 lines)
└── test_boss.py          # Sentinel boss entity, phases (273 lines)
```

**116 tests passing** as of 2026-03-16.

## What to Test

### Unit Tests (Automated)

**Player:**
- Initial position is correct
- Acceleration applies when keys pressed
- Friction decelerates when no input
- Max speed is clamped
- Position clamps to screen bounds
- Diagonal speed doesn't exceed max (normalization)
- Shoot cooldown prevents rapid fire
- Shoot cooldown resets after firing

**Projectile:**
- Spawns at correct position
- Moves rightward at correct speed
- `is_off_screen()` returns True past screen edge
- `is_off_screen()` returns False when visible

**Starfield:**
- Correct number of stars spawn
- Stars are within screen bounds initially
- Stars move leftward on update
- Stars wrap from left edge to right edge

**Enemies:**
- Pattern movement is correct (straight, sine, diagonal)
- Enemies spawn at correct positions
- Enemies despawn when off-screen
- Bat wing wobble and bob animation

**Powerups:**
- Powerups drift leftward
- Powerups despawn off-screen
- Pulse animation

**Collision:**
- Point-in-circle detection
- Point-in-rect detection

**Scoring:**
- Score increments on kill
- Multiplier builds and decays
- Combo counter and milestones

**Explosions:**
- All factories produce correct particle counts
- All particles use circle shape
- Correct start positions

**Particles:**
- Lifecycle (age, death)
- Color interpolation and alpha fade
- Size interpolation

**Boss (Sentinel):**
- Phase transitions at HP thresholds
- State machine (entering, fighting, dying)
- Attack timing (spread, aimed, radial burst, beam)
- Damage handling (core vs armor zones)
- Movement tracking and clamping

**Wave Spawner:**
- Initial delay before first wave
- Correct enemy count per wave
- Wave pause timing
- Pattern cycling (3 patterns)
- Boss trigger after wave 9
- Powerup spawn signaling

### Integration Tests (Manual)

Play the game and verify:

| Test | What to Check |
|------|---------------|
| Movement feel | Ship accelerates and decelerates smoothly, not twitchy or too floaty |
| Screen bounds | Ship cannot leave screen on any edge |
| Shooting | Spacebar fires at cooldown rate, not too fast, not too slow |
| Projectiles | Lasers travel right and disappear off-screen |
| Starfield | Two layers visible, back layer slower/dimmer |
| Frame rate | No stuttering or hitching during gameplay (especially boss death with 1000+ particles) |
| Input | All controls responsive, no stuck keys |
| Boss entry | Warning phase → Sentinel slides in from right |
| Boss phases | Attack patterns escalate as HP drops (spread → aimed → radial + beam) |
| Boss death | Staggered sub-explosions across hull, escalating shake, massive finale, hull vanishes |
| Powerups | Cleared when boss warning starts, no stale powerups during boss fight |
| Particle glow | Large particles have visible soft glow halo behind them |

## Testing Tips

### Delta Time Testing

When testing movement, pass explicit `dt` values:

```python
def test_player_moves_with_dt():
    player = Player(100, 100)
    player.update(dt=1/60, keys_pressed={arcade.key.RIGHT})
    assert player.vx > 0
```

### Avoiding Arcade Dependency in Tests

For unit tests, avoid needing a full Arcade window. Test logic separately:

```python
# Good: Test logic directly
def test_projectile_moves_right():
    proj = Projectile(100, 100)
    proj.update(dt=1/60)
    assert proj.x > 100

# Avoid: Needing window context
def test_draw():  # Hard to test, skip or mock
    pass
```

### Testing Edge Cases

- Zero delta time (first frame)
- Very large delta time (lag spike)
- Diagonal movement (both axes)
- Rapid key press/release
- Shooting while moving
- Multiple projectiles on screen

## Debugging Tips

### Show FPS

Add to `on_draw()`:

```python
arcade.draw_text(f"FPS: {1/self.delta_time:.0f}", 10, 10, arcade.color.WHITE)
```

### Show Hitboxes

Draw entity bounds during development:

```python
arcade.draw_rectangle_outline(self.x, self.y, self.width, self.height, arcade.color.GREEN)
```

### Print State

Log entity state each frame (remove before commit):

```python
print(f"Player: pos=({self.x:.1f}, {self.y:.1f}) vel=({self.vx:.1f}, {self.vy:.1f})")
```

## When to Test

- **Before commit**: All unit tests pass
- **After major changes**: Manual play-test
- **Before PRP completion**: Full integration test checklist
- **After tuning constants**: Play-test for feel

## Known Test Gaps

Document areas that need more testing:

- [ ] Frame rate independence under varying dt
- [ ] Behavior when many entities on screen (especially boss death particle load)
- [ ] Edge cases with simultaneous collisions
- [ ] Boss beam collision accuracy at screen edges
- [ ] Particle pool trimming behavior under heavy load (1500 pool limit)
- [ ] Player respawn during boss fight (invulnerability + position reset)
