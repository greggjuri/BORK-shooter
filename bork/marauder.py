"""Zone 2 boss: MARAUDER — aggressive attack craft with sinusoidal patrol."""

import math

import arcade

from bork.boss_attacks import create_radial_burst, create_spread_shot
from bork.constants import (
    MARAUDER_BATTLE_X,
    MARAUDER_BURST_INTERVAL,
    MARAUDER_DIAGONAL_INTERVAL,
    MARAUDER_ENTER_SPEED,
    MARAUDER_EXHAUST_LAYERS,
    MARAUDER_HEIGHT,
    MARAUDER_HP,
    MARAUDER_HULL_COLOR,
    MARAUDER_HULL_STROKE,
    MARAUDER_NOSE_COLOR,
    MARAUDER_PATROL_AMP,
    MARAUDER_PATROL_FREQ,
    MARAUDER_PHASE2_HP,
    MARAUDER_PHASE3_HP,
    MARAUDER_PLATE_COLOR,
    MARAUDER_PLATE_STROKE,
    MARAUDER_PROJ_COLOR,
    MARAUDER_PROJ_SPEED,
    MARAUDER_SHOOT_INTERVAL_P1,
    MARAUDER_SHOOT_INTERVAL_P2,
    MARAUDER_SHOOT_INTERVAL_P3,
    MARAUDER_WIDTH,
    SCREEN_HEIGHT,
)
from bork.enemy_projectile import EnemyProjectile

# Hull vertex offsets (top half, nose left). Mirrored for bottom.
_TOP_HULL = (
    (-70, 0), (-40, 18), (20, 30), (70, 22), (70, 10), (20, 14), (-30, 8),
)
_TOP_PLATE = (
    (-55, 4), (-30, 14), (15, 24), (60, 19), (60, 12), (15, 16), (-25, 10),
)
_BOTTOM_HULL = tuple((ox, -oy) for ox, oy in _TOP_HULL)
_BOTTOM_PLATE = tuple((ox, -oy) for ox, oy in _TOP_PLATE)


class Marauder:
    """Zone 2 boss — aggressive attack craft with sinusoidal patrol."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.center_y = y
        # Health
        self.core_hp: int = MARAUDER_HP
        self.max_hp: int = MARAUDER_HP
        self.name: str = "MARAUDER"
        # Collision dimensions (boss interface contract)
        self.opening_width: float = MARAUDER_WIDTH
        self.opening_height: float = 16
        self.armor_width: float = MARAUDER_WIDTH
        self.armor_height: float = MARAUDER_HEIGHT
        self.core_damage: int = 2
        self.body_damage: int = 1
        # State
        self.state: str = "entering"
        self.phase: int = 1
        self.time_alive: float = 0.0
        # Beam interface (unused, required for boss contract)
        self.beam_visible_timer: float = 0.0
        self.beam_y: float = 0.0
        # Attack timers
        self.spread_timer: float = MARAUDER_SHOOT_INTERVAL_P1
        self.diagonal_timer: float = MARAUDER_DIAGONAL_INTERVAL
        self.burst_timer: float = MARAUDER_BURST_INTERVAL
        # Death
        self.death_timer: float = 0.0

    @property
    def hp_fraction(self) -> float:
        """Current HP as fraction of max."""
        return self.core_hp / MARAUDER_HP

    @property
    def is_dead(self) -> bool:
        """Return True if HP is depleted."""
        return self.core_hp <= 0

    def _update_phase(self) -> None:
        """Recalculate phase from HP fraction."""
        frac = self.hp_fraction
        if frac <= MARAUDER_PHASE3_HP:
            self.phase = 3
        elif frac <= MARAUDER_PHASE2_HP:
            self.phase = 2
        else:
            self.phase = 1

    def update(
        self, dt: float, player_x: float, player_y: float
    ) -> list[EnemyProjectile]:
        """Update boss. Returns new projectiles."""
        self.time_alive += dt
        projectiles: list[EnemyProjectile] = []

        if self.state == "entering":
            self._update_entering(dt)
        elif self.state == "fighting":
            self._update_phase()
            self._update_patrol(dt)
            projectiles = self._update_attacks(dt, player_x, player_y)

        return projectiles

    def _update_entering(self, dt: float) -> None:
        """Slide from right edge to battle position."""
        self.x -= MARAUDER_ENTER_SPEED * dt
        if self.x <= MARAUDER_BATTLE_X:
            self.x = MARAUDER_BATTLE_X
            self.center_y = self.y
            self.state = "fighting"

    def _update_patrol(self, dt: float) -> None:
        """Sinusoidal vertical patrol. Frequency increases with phase."""
        freq = MARAUDER_PATROL_FREQ
        if self.phase == 2:
            freq *= 1.5
        elif self.phase == 3:
            freq *= 2.0

        self.y = self.center_y + math.sin(
            self.time_alive * freq * 2 * math.pi
        ) * MARAUDER_PATROL_AMP

        # Clamp to screen bounds
        margin = MARAUDER_HEIGHT / 2 + 10
        self.y = max(margin, min(SCREEN_HEIGHT - margin, self.y))

    def _update_attacks(
        self, dt: float, player_x: float, player_y: float
    ) -> list[EnemyProjectile]:
        """Run attack patterns for current phase."""
        projectiles: list[EnemyProjectile] = []
        nose_x = self.x - 70  # nose tip

        # Spread volley (all phases, speed increases with phase)
        interval = {
            1: MARAUDER_SHOOT_INTERVAL_P1,
            2: MARAUDER_SHOOT_INTERVAL_P2,
            3: MARAUDER_SHOOT_INTERVAL_P3,
        }[self.phase]
        self.spread_timer -= dt
        if self.spread_timer <= 0:
            self.spread_timer = interval
            projectiles.extend(
                create_spread_shot(
                    nose_x, self.y, player_x, player_y, 3,
                    MARAUDER_PROJ_SPEED, MARAUDER_PROJ_COLOR,
                )
            )

        # Diagonal cross burst (phase 2+)
        if self.phase >= 2:
            self.diagonal_timer -= dt
            if self.diagonal_timer <= 0:
                self.diagonal_timer = MARAUDER_DIAGONAL_INTERVAL
                projectiles.extend(self._fire_diagonal_cross())

        # 180° arc burst (phase 3)
        if self.phase == 3:
            self.burst_timer -= dt
            if self.burst_timer <= 0:
                self.burst_timer = MARAUDER_BURST_INTERVAL
                projectiles.extend(
                    create_radial_burst(
                        nose_x, self.y, 6, MARAUDER_PROJ_SPEED,
                        MARAUDER_PROJ_COLOR, arc_degrees=180.0,
                    )
                )

        return projectiles

    def _fire_diagonal_cross(self) -> list[EnemyProjectile]:
        """Fire 4 projectiles at fixed 45° angles."""
        projectiles: list[EnemyProjectile] = []
        cx, cy = self.x, self.y
        for angle_deg in (135, 225, 45, 315):
            angle = math.radians(angle_deg)
            vx = math.cos(angle) * MARAUDER_PROJ_SPEED
            vy = math.sin(angle) * MARAUDER_PROJ_SPEED
            projectiles.append(
                EnemyProjectile(cx, cy, vx, vy, MARAUDER_PROJ_COLOR, size=5.0)
            )
        return projectiles

    def take_hit(self, damage: int) -> None:
        """Apply damage to HP."""
        self.core_hp = max(0, self.core_hp - damage)

    # --- Drawing ---

    def draw(self) -> None:
        """Draw the Marauder boss."""
        self._draw_exhaust()
        self._draw_hull()

    def _draw_exhaust(self) -> None:
        """Draw green gradient exhaust from both engine ports."""
        top_ey = self.y + 16
        bot_ey = self.y - 16
        engine_x = self.x + 70

        for ey in (top_ey, bot_ey):
            for ox, w, h, r, g, b, a in MARAUDER_EXHAUST_LAYERS:
                arcade.draw_ellipse_filled(engine_x + ox, ey, w, h, (r, g, b, a))

    def _draw_hull(self) -> None:
        """Draw polygon hull halves with plates and details."""
        x, y = self.x, self.y
        stroke_dim = (*MARAUDER_HULL_STROKE[:3], 60)
        plate_dim = (*MARAUDER_PLATE_STROKE[:3], 50)

        # Top hull
        top_pts = [(x + ox, y + oy) for ox, oy in _TOP_HULL]
        arcade.draw_polygon_filled(top_pts, MARAUDER_HULL_COLOR)
        arcade.draw_polygon_outline(top_pts, MARAUDER_HULL_STROKE, 2)

        # Top plate
        top_plate = [(x + ox, y + oy) for ox, oy in _TOP_PLATE]
        arcade.draw_polygon_filled(top_plate, MARAUDER_PLATE_COLOR)
        arcade.draw_polygon_outline(top_plate, MARAUDER_PLATE_STROKE, 1)

        # Bottom hull
        bot_pts = [(x + ox, y + oy) for ox, oy in _BOTTOM_HULL]
        arcade.draw_polygon_filled(bot_pts, MARAUDER_HULL_COLOR)
        arcade.draw_polygon_outline(bot_pts, MARAUDER_HULL_STROKE, 2)

        # Bottom plate
        bot_plate = [(x + ox, y + oy) for ox, oy in _BOTTOM_PLATE]
        arcade.draw_polygon_filled(bot_plate, MARAUDER_PLATE_COLOR)
        arcade.draw_polygon_outline(bot_plate, MARAUDER_PLATE_STROKE, 1)

        # Nose ellipse
        arcade.draw_ellipse_filled(x - 70, y, 10, 6, MARAUDER_NOSE_COLOR)

        # Weapon port ellipses
        arcade.draw_ellipse_filled(x - 40, y + 12, 6, 3, MARAUDER_HULL_STROKE)
        arcade.draw_ellipse_filled(x - 40, y - 12, 6, 3, MARAUDER_HULL_STROKE)

        # Panel lines
        arcade.draw_line(x - 10, y + 20, x + 50, y + 18, stroke_dim, 1)
        arcade.draw_line(x + 10, y + 14, x + 55, y + 13, plate_dim, 1)
        arcade.draw_line(x - 10, y - 20, x + 50, y - 18, stroke_dim, 1)
        arcade.draw_line(x + 10, y - 14, x + 55, y - 13, plate_dim, 1)
