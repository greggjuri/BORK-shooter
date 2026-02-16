"""Particle and ParticleSystem for visual effects."""

import arcade

from bork.constants import PARTICLE_POOL_SIZE


class Particle:
    """A single visual particle with velocity, color fade, size shrink, and shape."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color_start: tuple[int, int, int],
        color_end: tuple[int, int, int],
        size_start: float,
        size_end: float,
        lifetime: float,
        shape: str,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color_start = color_start
        self.color_end = color_end
        self.size_start = size_start
        self.size_end = size_end
        self.lifetime = lifetime
        self.shape = shape  # "square", "triangle", "circle"
        self.age = 0.0

    @property
    def progress(self) -> float:
        """0.0 at birth, 1.0 at death."""
        return min(self.age / self.lifetime, 1.0)

    @property
    def is_dead(self) -> bool:
        """Return True if particle has exceeded its lifetime."""
        return self.age >= self.lifetime

    @property
    def size(self) -> float:
        """Current size, interpolated from start to end."""
        t = self.progress
        return self.size_start + (self.size_end - self.size_start) * t

    @property
    def color(self) -> tuple[int, int, int, int]:
        """Current RGBA color with alpha fade-out."""
        t = self.progress
        r = int(self.color_start[0] + (self.color_end[0] - self.color_start[0]) * t)
        g = int(self.color_start[1] + (self.color_end[1] - self.color_start[1]) * t)
        b = int(self.color_start[2] + (self.color_end[2] - self.color_start[2]) * t)
        alpha = int(255 * (1.0 - t))
        return (r, g, b, alpha)

    def update(self, dt: float) -> None:
        """Move and age the particle."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt

    def draw(self) -> None:
        """Draw the particle as its configured shape."""
        s = self.size
        if s <= 0:
            return
        c = self.color
        if self.shape == "circle":
            arcade.draw_circle_filled(self.x, self.y, s, c)
        elif self.shape == "square":
            arcade.draw_lrbt_rectangle_filled(
                self.x - s, self.x + s, self.y - s, self.y + s, c
            )
        elif self.shape == "triangle":
            arcade.draw_triangle_filled(
                self.x,
                self.y + s,
                self.x - s,
                self.y - s,
                self.x + s,
                self.y - s,
                c,
            )


class ParticleSystem:
    """Manages a pool of particles with automatic cleanup."""

    def __init__(self, max_particles: int = PARTICLE_POOL_SIZE) -> None:
        self.particles: list[Particle] = []
        self.max_particles = max_particles

    def add(self, particles: list[Particle]) -> None:
        """Add particles to the system, trimming oldest if over limit."""
        self.particles.extend(particles)
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles :]

    def update(self, dt: float) -> None:
        """Update all particles and remove dead ones."""
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead]

    def draw(self) -> None:
        """Draw all active particles."""
        for p in self.particles:
            p.draw()
