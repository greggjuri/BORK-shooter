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
├── test_player.py        # Player movement, shooting cooldown
├── test_projectile.py    # Projectile movement, despawning
├── test_starfield.py     # Star spawning, parallax scrolling
├── test_enemies.py       # Enemy patterns, collision (future)
├── test_powerups.py      # Powerup effects (future)
└── test_collision.py     # Collision detection (future)
```

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

**Enemies (future):**
- Pattern movement is correct
- Enemies spawn at correct positions
- Health decreases on hit
- Enemies despawn when destroyed or off-screen

**Powerups (future):**
- Powerups drift leftward
- Powerups despawn off-screen
- Correct effect applied when collected

**Collision (future):**
- Player projectile hits enemy
- Enemy projectile hits player
- Player collects powerup
- Player collision with enemy

### Integration Tests (Manual)

Play the game and verify:

| Test | What to Check |
|------|---------------|
| Movement feel | Ship accelerates and decelerates smoothly, not twitchy or too floaty |
| Screen bounds | Ship cannot leave screen on any edge |
| Shooting | Spacebar fires at cooldown rate, not too fast, not too slow |
| Projectiles | Lasers travel right and disappear off-screen |
| Starfield | Two layers visible, back layer slower/dimmer |
| Frame rate | No stuttering or hitching during gameplay |
| Input | All controls responsive, no stuck keys |

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
- [ ] Behavior when many entities on screen
- [ ] Edge cases with simultaneous collisions
