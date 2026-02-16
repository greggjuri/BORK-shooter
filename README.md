# B.O.R.K.

A horizontal scrolling shoot 'em up built with Python and Arcade.

## Inspiration

- **Delta** (C64) — Rob Hubbard soundtrack, smooth momentum
- **Sanxion** (C64) — Horizontal scrolling intensity
- **Xenon** (Bitmap Brothers) — Chunky, impactful feel
- **Galaga / Galaxian** — Learnable enemy patterns
- **Gyruss** — Rhythm and flow

## Features (Planned)

- 🚀 Momentum-based ship movement
- 🔫 Multiple weapon powerups (spread, laser, missiles)
- 💥 Satisfying explosions and particle effects
- 👾 Patterned enemy waves to memorize
- 🎯 Boss fights
- 🎵 Retro-style sound effects and music
- ⚡ Nasty surprises to keep you on your toes

## Requirements

- Python 3.8+
- Arcade library

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/bork.git
cd bork

# Install dependencies
pip install -r requirements.txt
```

## Running the Game

```bash
python bork/game.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move ship |
| Spacebar | Fire |
| ESC | Quit |

## Development

This project uses a structured workflow:

1. **Feature specs** in `initials/init-*.md`
2. **Implementation plans** in `prps/prp-*.md`
3. **Architecture decisions** in `docs/DECISIONS.md`

See `CLAUDE.md` for coding conventions.

### Running Tests

```bash
pytest bork/tests/ -v
```

## Project Status

**Phase 1: Core Engine** — In Progress

- [x] Project setup
- [ ] Player ship with momentum
- [ ] Basic shooting
- [ ] Parallax starfield

## License

MIT

---

*What does B.O.R.K. stand for? That's classified.*
