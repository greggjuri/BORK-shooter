# B.O.R.K. - Claude Code Conventions

## What This Is

B.O.R.K. is a horizontal scrolling shoot 'em up inspired by Delta, Sanxion, and classic C64/arcade games. Built with Python and the Arcade library.

## Quick Commands

```bash
# Run the game
python bork/game.py

# Run tests
pytest bork/tests/ -v

# Run specific test file
pytest bork/tests/test_player.py -v

# Lint check
ruff check bork/

# Format code
ruff format bork/
```

## Project Structure

```
bork/
├── CLAUDE.md                 # This file
├── README.md                 # Project overview
├── requirements.txt          # Python dependencies
├── docs/
│   ├── PLANNING.md           # Architecture overview
│   ├── TASK.md               # Current sprint tasks
│   ├── DECISIONS.md          # Architecture Decision Records
│   └── TESTING.md            # Testing standards
├── initials/                 # Feature specifications
│   └── init-*.md
├── prps/                     # Implementation plans
│   └── prp-*.md
├── bork/                     # Game source code
│   ├── __init__.py
│   ├── constants.py          # All tunable values
│   ├── game.py               # Main game window and loop
│   ├── player.py             # Player ship
│   ├── projectile.py         # Laser projectiles
│   ├── starfield.py          # Parallax background
│   ├── enemies/              # Enemy types (future)
│   ├── powerups/             # Powerup system (future)
│   └── tests/
│       ├── __init__.py
│       └── test_*.py
└── assets/                   # Sprites, sounds (future)
    ├── sprites/
    └── sounds/
```

## Coding Conventions

### General
- **File limit**: 500 lines max per file — split when approaching
- **Type hints**: Use them for function signatures
- **Docstrings**: Brief docstring for each class and public method
- **Constants**: All magic numbers go in `constants.py`

### Naming
- Classes: `PascalCase` (e.g., `PlayerShip`, `LaserProjectile`)
- Functions/methods: `snake_case` (e.g., `update_position`, `can_shoot`)
- Constants: `SCREAMING_SNAKE_CASE` (e.g., `PLAYER_MAX_SPEED`)
- Files: `snake_case.py`

### Game Architecture
- **Entity pattern**: Each game object (player, enemy, projectile) is a class with `update(dt)` and `draw()` methods
- **Delta time**: All movement uses `dt` for frame-rate independence
- **Separation**: Update logic and draw logic stay separate
- **Lists for entities**: Projectiles, enemies, powerups stored in lists, cleaned up when off-screen or destroyed

### Arcade-Specific
- Use `arcade.draw_*` primitives for geometric shapes
- Use `arcade.Sprite` when we add pixel art assets
- Input via `on_key_press`/`on_key_release` with a `keys_pressed` set
- Game loop via `on_update(dt)` and `on_draw()`

## Commit Convention

Use conventional commits:
- `feat:` — New feature (e.g., `feat: add spread shot powerup`)
- `fix:` — Bug fix (e.g., `fix: player can no longer leave screen`)
- `refactor:` — Code improvement, no behavior change
- `docs:` — Documentation only
- `test:` — Adding/updating tests
- `chore:` — Maintenance (deps, config)

**Auto-commit and push**: After every feature, update, or bug fix, automatically commit the changes and push to the remote. Do not wait for the user to ask — commit and push as soon as the work is validated (tests pass, lint clean).

## Workflow

1. **Feature specs** live in `initials/init-*.md`
2. **Generate PRP**: `/generate-prp initials/init-{feature}.md`
3. **Execute PRP**: `/execute-prp prps/prp-{feature}.md`
4. **Commit after each working step** — atomic, tested commits

## Testing

- Unit tests for game logic (movement, collision, spawning)
- Manual play-testing for feel and balance
- All tests must pass before committing

## Current Phase

**Phase 2: Combat** — Powerups, explosions, particle effects (init-03, init-04)
