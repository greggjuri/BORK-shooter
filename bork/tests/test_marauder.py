"""Tests for the Zone 2 Marauder boss."""

from bork.boss import Sentinel
from bork.boss_fight import create_boss
from bork.constants import (
    MARAUDER_BATTLE_X,
    MARAUDER_HP,
    MARAUDER_PHASE2_HP,
    MARAUDER_PHASE3_HP,
    MARAUDER_SHOOT_INTERVAL_P1,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from bork.marauder import Marauder

DT = 1 / 60


def test_marauder_initial_state() -> None:
    m = Marauder(SCREEN_WIDTH + 200, SCREEN_HEIGHT / 2)
    assert m.core_hp == MARAUDER_HP
    assert m.max_hp == MARAUDER_HP
    assert m.state == "entering"
    assert m.phase == 1
    assert m.name == "MARAUDER"


def test_marauder_enters_from_right() -> None:
    m = Marauder(SCREEN_WIDTH + 200, SCREEN_HEIGHT / 2)
    old_x = m.x
    m.update(DT, 100, 270)
    assert m.x < old_x
    assert m.state == "entering"


def test_marauder_stops_at_battle_x() -> None:
    m = Marauder(MARAUDER_BATTLE_X + 5, SCREEN_HEIGHT / 2)
    # Tick enough to slide in
    for _ in range(60):
        m.update(DT, 100, 270)
    assert m.x == MARAUDER_BATTLE_X
    assert m.state == "fighting"


def test_marauder_patrols_vertically() -> None:
    m = Marauder(MARAUDER_BATTLE_X, SCREEN_HEIGHT / 2)
    m.state = "fighting"
    m.center_y = SCREEN_HEIGHT / 2
    initial_y = m.y
    # Tick enough for sinusoidal movement to be visible
    for _ in range(30):
        m.update(DT, 100, 270)
    assert m.y != initial_y


def test_marauder_phase_transitions() -> None:
    m = Marauder(MARAUDER_BATTLE_X, SCREEN_HEIGHT / 2)
    m.state = "fighting"
    assert m.phase == 1

    # Phase 2 at 50% HP
    m.core_hp = int(MARAUDER_HP * MARAUDER_PHASE2_HP)
    m._update_phase()
    assert m.phase == 2

    # Phase 3 at 25% HP
    m.core_hp = int(MARAUDER_HP * MARAUDER_PHASE3_HP)
    m._update_phase()
    assert m.phase == 3


def test_marauder_takes_damage() -> None:
    m = Marauder(MARAUDER_BATTLE_X, SCREEN_HEIGHT / 2)
    m.take_hit(10)
    assert m.core_hp == MARAUDER_HP - 10


def test_marauder_is_dead() -> None:
    m = Marauder(MARAUDER_BATTLE_X, SCREEN_HEIGHT / 2)
    assert not m.is_dead
    m.core_hp = 0
    assert m.is_dead


def test_marauder_fires_projectiles() -> None:
    m = Marauder(MARAUDER_BATTLE_X, SCREEN_HEIGHT / 2)
    m.state = "fighting"
    m.center_y = SCREEN_HEIGHT / 2
    # Tick past spread timer to trigger first volley
    all_projs = []
    frames = int(MARAUDER_SHOOT_INTERVAL_P1 * 60) + 10
    for _ in range(frames):
        projs = m.update(DT, 100, 270)
        all_projs.extend(projs)
    assert len(all_projs) > 0


def test_marauder_phase1_spread_count() -> None:
    """Phase 1 spread fires exactly 3 projectiles per volley."""
    m = Marauder(MARAUDER_BATTLE_X, SCREEN_HEIGHT / 2)
    m.state = "fighting"
    m.center_y = SCREEN_HEIGHT / 2
    m.spread_timer = 0.0  # Force immediate fire
    projs = m.update(DT, 100, 270)
    assert len(projs) == 3


def test_marauder_phase2_diagonal_count() -> None:
    """Phase 2 diagonal burst fires exactly 4 projectiles."""
    m = Marauder(MARAUDER_BATTLE_X, SCREEN_HEIGHT / 2)
    m.state = "fighting"
    m.center_y = SCREEN_HEIGHT / 2
    m.phase = 2
    m.core_hp = int(MARAUDER_HP * MARAUDER_PHASE2_HP)
    m.spread_timer = 999  # Prevent spread from firing
    m.diagonal_timer = 0.0  # Force immediate diagonal fire
    projs = m.update(DT, 100, 270)
    assert len(projs) == 4


def test_marauder_phase3_arc_count() -> None:
    """Phase 3 arc burst fires exactly 6 projectiles."""
    m = Marauder(MARAUDER_BATTLE_X, SCREEN_HEIGHT / 2)
    m.state = "fighting"
    m.center_y = SCREEN_HEIGHT / 2
    m.phase = 3
    m.core_hp = int(MARAUDER_HP * MARAUDER_PHASE3_HP)
    m.spread_timer = 999  # Prevent spread
    m.diagonal_timer = 999  # Prevent diagonal
    m.burst_timer = 0.0  # Force immediate arc fire
    projs = m.update(DT, 100, 270)
    assert len(projs) == 6


def test_marauder_interface_properties() -> None:
    """Marauder has all required boss interface properties."""
    m = Marauder(500, 270)
    assert hasattr(m, "x")
    assert hasattr(m, "y")
    assert hasattr(m, "core_hp")
    assert hasattr(m, "max_hp")
    assert hasattr(m, "name")
    assert hasattr(m, "state")
    assert hasattr(m, "phase")
    assert hasattr(m, "time_alive")
    assert hasattr(m, "death_timer")
    assert hasattr(m, "beam_visible_timer")
    assert hasattr(m, "beam_y")
    assert hasattr(m, "opening_width")
    assert hasattr(m, "opening_height")
    assert hasattr(m, "armor_width")
    assert hasattr(m, "armor_height")
    assert hasattr(m, "core_damage")
    assert hasattr(m, "body_damage")
    assert hasattr(m, "hp_fraction")
    assert hasattr(m, "is_dead")


def test_boss_factory_sentinel() -> None:
    boss = create_boss("sentinel", 800, 270)
    assert isinstance(boss, Sentinel)


def test_boss_factory_marauder() -> None:
    boss = create_boss("marauder", 800, 270)
    assert isinstance(boss, Marauder)


def test_boss_factory_unknown_defaults_to_sentinel() -> None:
    boss = create_boss("unknown", 800, 270)
    assert isinstance(boss, Sentinel)
