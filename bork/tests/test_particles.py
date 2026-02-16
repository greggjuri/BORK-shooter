"""Tests for the particle system."""

from bork.particles import Particle, ParticleSystem

DT = 1 / 60


def _make_particle(**kwargs) -> Particle:
    """Create a particle with sensible defaults, overridable via kwargs."""
    defaults = {
        "x": 100.0,
        "y": 200.0,
        "vx": 50.0,
        "vy": -30.0,
        "color_start": (255, 0, 0),
        "color_end": (255, 150, 0),
        "size_start": 6.0,
        "size_end": 1.0,
        "lifetime": 0.5,
        "shape": "square",
    }
    defaults.update(kwargs)
    return Particle(**defaults)


def test_particle_initial_values() -> None:
    p = _make_particle(x=10.0, y=20.0)
    assert p.x == 10.0
    assert p.y == 20.0
    assert p.age == 0.0
    assert p.is_dead is False


def test_particle_update_moves() -> None:
    p = _make_particle(vx=100.0, vy=-50.0)
    old_x, old_y = p.x, p.y
    p.update(DT)
    assert p.x > old_x
    assert p.y < old_y


def test_particle_dies_after_lifetime() -> None:
    p = _make_particle(lifetime=0.1)
    # Tick past lifetime
    for _ in range(10):
        p.update(DT)
    assert p.is_dead is True


def test_particle_not_dead_before_lifetime() -> None:
    p = _make_particle(lifetime=1.0)
    p.update(DT)
    assert p.is_dead is False


def test_particle_size_interpolates() -> None:
    p = _make_particle(size_start=10.0, size_end=2.0, lifetime=1.0)
    assert p.size == 10.0
    # Halfway through
    p.age = 0.5
    assert abs(p.size - 6.0) < 0.01
    # At end
    p.age = 1.0
    assert abs(p.size - 2.0) < 0.01


def test_particle_color_fades_alpha() -> None:
    p = _make_particle(lifetime=1.0)
    # At birth: alpha should be 255
    r, g, b, a = p.color
    assert a == 255
    # Near death: alpha should be near 0
    p.age = 0.99
    _, _, _, a = p.color
    assert a < 10


def test_particle_system_removes_dead() -> None:
    ps = ParticleSystem()
    p1 = _make_particle(lifetime=0.01)
    p2 = _make_particle(lifetime=10.0)
    ps.add([p1, p2])
    assert len(ps.particles) == 2
    # Tick enough to kill p1
    ps.update(0.1)
    assert len(ps.particles) == 1


def test_particle_system_respects_pool_limit() -> None:
    ps = ParticleSystem(max_particles=5)
    particles = [_make_particle() for _ in range(10)]
    ps.add(particles)
    assert len(ps.particles) == 5
