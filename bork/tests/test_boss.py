"""Tests for boss system: Sentinel, EnemyProjectile, wave trigger, collisions."""

from bork.boss import Sentinel
from bork.boss_attacks import EnemyProjectile
from bork.collision import point_in_rect
from bork.constants import (
    BOSS_SPAWN_AFTER_WAVES,
    ENEMIES_PER_WAVE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SENTINEL_BODY_DAMAGE_MULT,
    SENTINEL_CORE_HP,
    SENTINEL_PHASE2_THRESHOLD,
    SENTINEL_PHASE3_THRESHOLD,
    SENTINEL_WING_HP,
)
from bork.wave_spawner import WaveSpawner


# --- Helper ---


def _run_waves(spawner: WaveSpawner, count: int) -> None:
    """Run the spawner through `count` complete waves."""
    for _ in range(count):
        # Skip the inter-wave pause/start delay
        spawner.timer = 0.0
        spawner.update(0.001)  # Activates the wave (wave_active = True)

        # Now spawn all ENEMIES_PER_WAVE enemies
        for _ in range(ENEMIES_PER_WAVE):
            spawner.timer = 0.0
            spawner.update(0.001)


# --- Wave trigger tests ---


def test_boss_triggers_after_nine_waves():
    """Boss trigger fires after 9 complete waves."""
    spawner = WaveSpawner()
    _run_waves(spawner, BOSS_SPAWN_AFTER_WAVES)
    assert spawner.boss_triggered is True
    assert spawner.total_waves_completed >= BOSS_SPAWN_AFTER_WAVES


def test_boss_does_not_trigger_before_nine_waves():
    """Boss trigger does not fire before 9 waves."""
    spawner = WaveSpawner()
    _run_waves(spawner, BOSS_SPAWN_AFTER_WAVES - 1)
    assert spawner.boss_triggered is False
    assert spawner.total_waves_completed == BOSS_SPAWN_AFTER_WAVES - 1


def test_wave_spawner_reset_clears_boss_trigger():
    """Reset clears total_waves_completed and boss_triggered."""
    spawner = WaveSpawner()
    _run_waves(spawner, BOSS_SPAWN_AFTER_WAVES)
    assert spawner.boss_triggered is True
    spawner.reset()
    assert spawner.total_waves_completed == 0
    assert spawner.boss_triggered is False


# --- Sentinel HP tests ---


def test_sentinel_initial_hp():
    """Sentinel starts with correct HP values."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    assert boss.core_hp == SENTINEL_CORE_HP
    assert boss.left_wing_hp == SENTINEL_WING_HP
    assert boss.right_wing_hp == SENTINEL_WING_HP
    assert boss.left_wing_alive is True
    assert boss.right_wing_alive is True


def test_sentinel_core_takes_full_damage():
    """Core hit reduces core HP by full damage amount."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    boss.take_hit("core", 1)
    assert boss.core_hp == SENTINEL_CORE_HP - 1


def test_sentinel_core_takes_multiple_damage():
    """Core takes multiple hits correctly."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    for _ in range(10):
        boss.take_hit("core", 1)
    assert boss.core_hp == SENTINEL_CORE_HP - 10


def test_sentinel_body_takes_reduced_damage():
    """Body hit applies damage multiplier (0.5x, floored to 0 for 1 damage)."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    boss.take_hit("body", 1)
    expected = SENTINEL_CORE_HP - int(1 * SENTINEL_BODY_DAMAGE_MULT)
    assert boss.core_hp == expected


def test_sentinel_body_higher_damage_applies_multiplier():
    """Body hit with higher damage shows multiplier effect."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    boss.take_hit("body", 4)
    expected = SENTINEL_CORE_HP - int(4 * SENTINEL_BODY_DAMAGE_MULT)
    assert boss.core_hp == expected


def test_sentinel_wing_takes_full_damage():
    """Wing hits reduce wing HP directly."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    boss.take_hit("left_wing", 1)
    assert boss.left_wing_hp == SENTINEL_WING_HP - 1
    assert boss.left_wing_alive is True


def test_sentinel_wing_destruction():
    """Wing is destroyed when HP reaches 0."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    for _ in range(SENTINEL_WING_HP):
        result = boss.take_hit("left_wing", 1)
    assert boss.left_wing_hp == 0
    assert boss.left_wing_alive is False
    assert result["destroyed"] is True
    assert result["part"] == "left_wing"


def test_sentinel_right_wing_destruction():
    """Right wing can be destroyed independently."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    for _ in range(SENTINEL_WING_HP):
        boss.take_hit("right_wing", 1)
    assert boss.right_wing_alive is False
    assert boss.left_wing_alive is True  # Left wing unaffected


def test_sentinel_core_hp_floors_at_zero():
    """Core HP never goes below 0."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    for _ in range(SENTINEL_CORE_HP + 10):
        boss.take_hit("core", 1)
    assert boss.core_hp == 0


# --- Phase tests ---


def test_sentinel_starts_phase_1():
    """Boss starts in phase 1 at full HP."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    boss._update_phase()
    assert boss.phase == 1


def test_sentinel_phase_2_at_66_percent():
    """Phase transitions to 2 at or below 66% HP."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    # Set to exactly 66% threshold
    boss.core_hp = int(SENTINEL_CORE_HP * SENTINEL_PHASE2_THRESHOLD)
    boss._update_phase()
    assert boss.phase == 2


def test_sentinel_phase_3_at_33_percent():
    """Phase transitions to 3 at or below 33% HP."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    boss.core_hp = int(SENTINEL_CORE_HP * SENTINEL_PHASE3_THRESHOLD)
    boss._update_phase()
    assert boss.phase == 3


def test_sentinel_phase_3_at_low_hp():
    """Phase 3 is active at very low HP."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    boss.core_hp = 1
    boss._update_phase()
    assert boss.phase == 3


# --- Boss death tests ---


def test_sentinel_dead_at_zero_hp():
    """Boss is dead when core HP reaches 0."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    boss.core_hp = 0
    assert boss.is_dead is True


def test_sentinel_alive_above_zero_hp():
    """Boss is alive when core HP is above 0."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    assert boss.is_dead is False


def test_sentinel_hp_fraction():
    """HP fraction correctly reports proportion of max HP."""
    boss = Sentinel(SCREEN_WIDTH, SCREEN_HEIGHT / 2)
    assert boss.hp_fraction == 1.0
    boss.core_hp = SENTINEL_CORE_HP // 2
    assert boss.hp_fraction == 0.5


# --- Boss entering state ---


def test_sentinel_entering_state():
    """Boss starts in entering state."""
    boss = Sentinel(SCREEN_WIDTH + 100, SCREEN_HEIGHT / 2)
    assert boss.state == "entering"


def test_sentinel_enters_and_transitions():
    """Boss moves left during entering and transitions to fighting."""
    boss = Sentinel(SCREEN_WIDTH + 100, SCREEN_HEIGHT / 2)
    # Update many times to reach battle position
    for _ in range(200):
        boss.update(1 / 60, 100, SCREEN_HEIGHT / 2)
    assert boss.state == "fighting"


# --- EnemyProjectile tests ---


def test_enemy_projectile_moves_correctly():
    """EnemyProjectile moves by velocity * dt."""
    proj = EnemyProjectile(100, 100, -200, 50, (255, 0, 0))
    proj.update(1 / 60)
    assert proj.x < 100  # moved left
    assert proj.y > 100  # moved up


def test_enemy_projectile_moves_exact():
    """EnemyProjectile position matches velocity * dt exactly."""
    proj = EnemyProjectile(100, 200, -300, 100, (255, 0, 0))
    dt = 0.5
    proj.update(dt)
    assert proj.x == 100 + (-300) * dt
    assert proj.y == 200 + 100 * dt


def test_enemy_projectile_off_screen_left():
    """EnemyProjectile is off-screen when past left edge."""
    proj = EnemyProjectile(-10, 100, -200, 0, (255, 0, 0), size=5.0)
    assert proj.is_off_screen() is True


def test_enemy_projectile_off_screen_bottom():
    """EnemyProjectile is off-screen when past bottom edge."""
    proj = EnemyProjectile(100, -10, 0, -200, (255, 0, 0), size=5.0)
    assert proj.is_off_screen() is True


def test_enemy_projectile_on_screen():
    """EnemyProjectile on screen reports not off-screen."""
    proj = EnemyProjectile(100, 100, -200, 0, (255, 0, 0))
    assert proj.is_off_screen() is False


# --- Collision helper tests ---


def test_point_in_rect_inside():
    """Point inside rectangle returns True."""
    assert point_in_rect(50, 50, 50, 50, 20, 20) is True


def test_point_in_rect_outside():
    """Point outside rectangle returns False."""
    assert point_in_rect(100, 100, 50, 50, 20, 20) is False


def test_point_in_rect_on_edge():
    """Point on edge of rectangle returns True."""
    assert point_in_rect(60, 50, 50, 50, 20, 20) is True


def test_point_in_rect_just_outside():
    """Point just outside rectangle returns False."""
    assert point_in_rect(61, 50, 50, 50, 20, 20) is False


# --- Boss attack generation ---


def test_sentinel_fighting_returns_projectiles():
    """Boss in fighting state returns projectiles over time."""
    boss = Sentinel(SCREEN_WIDTH + 100, SCREEN_HEIGHT / 2)
    # Fast-forward entering
    for _ in range(200):
        boss.update(1 / 60, 100, SCREEN_HEIGHT / 2)
    assert boss.state == "fighting"

    # Accumulate projectiles over several seconds
    all_projs = []
    for _ in range(180):  # 3 seconds at 60fps
        projs = boss.update(1 / 60, 100, SCREEN_HEIGHT / 2)
        all_projs.extend(projs)
    assert len(all_projs) > 0  # Boss should have fired something
