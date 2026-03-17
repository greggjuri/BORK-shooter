"""Zone 1 boss: SENTINEL — a geometric fortress with armored body and core opening."""

import math

import arcade

from bork.boss_attacks import (
    EnemyProjectile,
    create_aimed_shot,
    create_radial_burst,
    create_spread_shot,
)
from bork.constants import (
    BOSS_BULLET_COLOR_CYAN,
    BOSS_BULLET_COLOR_RED,
    BOSS_BULLET_SPEED_FAST,
    BOSS_BULLET_SPEED_MEDIUM,
    SCREEN_HEIGHT,
    SENTINEL_AIMED_INTERVAL,
    SENTINEL_ARMOR_COLOR,
    SENTINEL_BATTLE_X,
    SENTINEL_BEAM_CHARGE_TIME,
    SENTINEL_BEAM_COOLDOWN,
    SENTINEL_BODY_ACCENT,
    SENTINEL_CORE_COLOR,
    SENTINEL_CORE_GLOW_COLOR,
    SENTINEL_CORE_HP,
    SENTINEL_CORE_SIZE,
    SENTINEL_ENTER_SPEED,
    SENTINEL_EXHAUST_LAYERS,
    SENTINEL_HEIGHT,
    SENTINEL_LUNGE_DURATION,
    SENTINEL_LUNGE_SPEED,
    SENTINEL_OPENING_COLOR,
    SENTINEL_OPENING_HEIGHT,
    SENTINEL_PHASE2_THRESHOLD,
    SENTINEL_PHASE3_THRESHOLD,
    SENTINEL_SPREAD_INTERVAL_P1,
    SENTINEL_SPREAD_INTERVAL_P2,
    SENTINEL_TRACK_SPEED,
    SENTINEL_TRACK_SPEED_P2,
    SENTINEL_TRACK_SPEED_P3,
)

# Boss sub-part dimensions for layout
_BODY_WIDTH = 100
_BODY_HEIGHT = 80


class Sentinel:
    """Zone 1 boss — geometric fortress with armored body and core opening."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        # Health
        self.core_hp: int = SENTINEL_CORE_HP
        # State
        self.state: str = "entering"  # entering, fighting, dying
        self.phase: int = 1
        self.time_alive: float = 0.0
        # Attack timers
        self.spread_timer: float = SENTINEL_SPREAD_INTERVAL_P1
        self.aimed_timer: float = SENTINEL_AIMED_INTERVAL
        self.beam_charge_timer: float = 0.0
        self.beam_cooldown_timer: float = SENTINEL_BEAM_COOLDOWN
        self.beam_charging: bool = False
        self.beam_y: float = 0.0
        self.beam_visible_timer: float = 0.0
        # Movement
        self.lunge_timer: float = 0.0
        self.lunge_cooldown: float = 3.0
        self.lunging: bool = False
        self.lunge_return_x: float = 0.0
        # Death sequence
        self.death_timer: float = 0.0

    @property
    def hp_fraction(self) -> float:
        """Current HP as fraction of max."""
        return self.core_hp / SENTINEL_CORE_HP

    @property
    def is_dead(self) -> bool:
        """Return True if boss core HP is depleted."""
        return self.core_hp <= 0

    def _update_phase(self) -> None:
        """Recalculate phase from HP fraction."""
        frac = self.hp_fraction
        if frac <= SENTINEL_PHASE3_THRESHOLD:
            self.phase = 3
        elif frac <= SENTINEL_PHASE2_THRESHOLD:
            self.phase = 2
        else:
            self.phase = 1

    # --- Hit zones (world positions) ---

    @property
    def core_pos(self) -> tuple[float, float]:
        """Core center position."""
        return (self.x, self.y + 20)

    # --- Main update ---

    def update(
        self, dt: float, player_x: float, player_y: float
    ) -> list[EnemyProjectile]:
        """Update boss. Returns new projectiles to add to game."""
        self.time_alive += dt
        projectiles: list[EnemyProjectile] = []

        # Beam visible timer always ticks
        if self.beam_visible_timer > 0:
            self.beam_visible_timer -= dt

        if self.state == "entering":
            self._update_entering(dt)
        elif self.state == "fighting":
            self._update_phase()
            self._update_movement(dt, player_y)
            projectiles = self._update_attacks(dt, player_x, player_y)

        return projectiles

    def _update_entering(self, dt: float) -> None:
        """Slide from right edge to battle position."""
        self.x -= SENTINEL_ENTER_SPEED * dt
        if self.x <= SENTINEL_BATTLE_X:
            self.x = SENTINEL_BATTLE_X
            self.state = "fighting"

    def _update_movement(self, dt: float, player_y: float) -> None:
        """Track player Y and handle lunges."""
        # Select tracking speed by phase
        track_speed = SENTINEL_TRACK_SPEED
        if self.phase == 2:
            track_speed = SENTINEL_TRACK_SPEED_P2
        elif self.phase == 3:
            track_speed = SENTINEL_TRACK_SPEED_P3

        # Lunge logic (phase 2 only)
        if self.lunging:
            self.lunge_timer -= dt
            if self.lunge_timer <= 0:
                self.lunging = False
                self.lunge_cooldown = 3.0
            else:
                self.x -= SENTINEL_LUNGE_SPEED * dt
        elif self.phase == 2 and not self.lunging:
            self.lunge_cooldown -= dt
            if self.lunge_cooldown <= 0:
                self.lunging = True
                self.lunge_timer = SENTINEL_LUNGE_DURATION
                self.lunge_return_x = self.x

        # Return to battle X if not lunging
        if not self.lunging and self.x < SENTINEL_BATTLE_X:
            self.x += SENTINEL_LUNGE_SPEED * dt
            if self.x > SENTINEL_BATTLE_X:
                self.x = SENTINEL_BATTLE_X

        # Vertical tracking
        diff = player_y - self.y
        if abs(diff) > 2.0:
            direction = 1.0 if diff > 0 else -1.0
            self.y += direction * track_speed * dt

        # Clamp to screen (with margin for boss height)
        margin = SENTINEL_HEIGHT / 2
        self.y = max(margin, min(SCREEN_HEIGHT - margin, self.y))

        # Erratic movement in phase 3
        if self.phase == 3:
            self.y += math.sin(self.time_alive * 5) * 30 * dt

    def _update_attacks(
        self, dt: float, player_x: float, player_y: float
    ) -> list[EnemyProjectile]:
        """Run attack patterns for current phase. Returns new projectiles."""
        projectiles: list[EnemyProjectile] = []
        cx, cy = self.core_pos

        if self.phase == 1:
            projectiles.extend(
                self._tick_spread(dt, cx, cy, player_x, player_y, count=3)
            )
        elif self.phase == 2:
            projectiles.extend(
                self._tick_spread(dt, cx, cy, player_x, player_y, count=5)
            )
            projectiles.extend(self._tick_aimed(dt, cx, cy, player_x, player_y))
        elif self.phase == 3:
            projectiles.extend(self._tick_radial_burst(dt, cx, cy))
            self._tick_beam(dt, player_y)

        return projectiles

    # --- Attack tickers ---

    def _tick_spread(
        self,
        dt: float,
        cx: float,
        cy: float,
        px: float,
        py: float,
        count: int,
    ) -> list[EnemyProjectile]:
        """Tick spread shot timer, fire when ready."""
        interval = (
            SENTINEL_SPREAD_INTERVAL_P1
            if self.phase == 1
            else SENTINEL_SPREAD_INTERVAL_P2
        )
        self.spread_timer -= dt
        if self.spread_timer <= 0:
            self.spread_timer = interval
            return create_spread_shot(
                cx, cy, px, py, count, BOSS_BULLET_SPEED_MEDIUM, BOSS_BULLET_COLOR_CYAN
            )
        return []

    def _tick_aimed(
        self, dt: float, cx: float, cy: float, px: float, py: float
    ) -> list[EnemyProjectile]:
        """Phase 2: aimed shot at player."""
        self.aimed_timer -= dt
        if self.aimed_timer <= 0:
            self.aimed_timer = SENTINEL_AIMED_INTERVAL
            return create_aimed_shot(
                cx, cy, px, py, BOSS_BULLET_SPEED_FAST, BOSS_BULLET_COLOR_RED
            )
        return []

    def _tick_radial_burst(
        self, dt: float, cx: float, cy: float
    ) -> list[EnemyProjectile]:
        """Phase 3: radial burst of 7 bullets in a leftward arc."""
        self.spread_timer -= dt
        if self.spread_timer <= 0:
            self.spread_timer = SENTINEL_SPREAD_INTERVAL_P2
            return create_radial_burst(
                cx,
                cy,
                7,
                BOSS_BULLET_SPEED_MEDIUM,
                BOSS_BULLET_COLOR_CYAN,
                arc_degrees=150.0,
            )
        return []

    def _tick_beam(self, dt: float, player_y: float) -> None:
        """Phase 3: beam charge and fire cycle. Beam hit is checked by game.py."""
        if self.beam_charging:
            self.beam_charge_timer -= dt
            if self.beam_charge_timer <= 0:
                # Fire beam
                self.beam_charging = False
                self.beam_visible_timer = 0.1
                self.beam_cooldown_timer = SENTINEL_BEAM_COOLDOWN
        else:
            self.beam_cooldown_timer -= dt
            if self.beam_cooldown_timer <= 0:
                # Start charging
                self.beam_charging = True
                self.beam_charge_timer = SENTINEL_BEAM_CHARGE_TIME
                self.beam_y = player_y  # Lock Y at charge start

    # --- Hit handling ---

    def take_hit(self, damage: int) -> None:
        """Apply damage to core HP."""
        self.core_hp = max(0, self.core_hp - damage)

    # --- Drawing ---

    def draw(self) -> None:
        """Draw the Sentinel boss using geometric shapes."""
        self._draw_engine_exhaust()
        self._draw_body()
        self._draw_opening()
        self._draw_core()
        if self.beam_visible_timer > 0:
            self._draw_beam()
        if self.beam_charging:
            self._draw_beam_charge()

    def _draw_engine_exhaust(self) -> None:
        """Draw layered gradient exhaust glow for top and bottom engine blocks."""
        # Engine blocks sit at top and bottom of the body, exhaust extends rightward
        top_engine_y = self.y + _BODY_HEIGHT / 2 - 10
        bottom_engine_y = self.y - _BODY_HEIGHT / 2 + 10
        engine_x = self.x + _BODY_WIDTH / 2

        for ey in (top_engine_y, bottom_engine_y):
            for ox, w, h, r, g, b, a in SENTINEL_EXHAUST_LAYERS:
                arcade.draw_ellipse_filled(engine_x + ox, ey, w, h, (r, g, b, a))

    def _draw_body(self) -> None:
        """Draw the armored body with upper and lower armor panels."""
        # Full body background in armor color
        arcade.draw_lrbt_rectangle_filled(
            self.x - _BODY_WIDTH / 2,
            self.x + _BODY_WIDTH / 2,
            self.y - _BODY_HEIGHT / 2,
            self.y + _BODY_HEIGHT / 2,
            SENTINEL_ARMOR_COLOR,
        )
        # Accent outline
        arcade.draw_lrbt_rectangle_outline(
            self.x - _BODY_WIDTH / 2,
            self.x + _BODY_WIDTH / 2,
            self.y - _BODY_HEIGHT / 2,
            self.y + _BODY_HEIGHT / 2,
            SENTINEL_BODY_ACCENT,
            border_width=2,
        )
        # Horizontal accent lines at armor panel edges
        arcade.draw_line(
            self.x - _BODY_WIDTH / 2,
            self.y - _BODY_HEIGHT / 2 + 4,
            self.x + _BODY_WIDTH / 2,
            self.y - _BODY_HEIGHT / 2 + 4,
            (*SENTINEL_BODY_ACCENT[:3], 80),
            1,
        )
        arcade.draw_line(
            self.x - _BODY_WIDTH / 2,
            self.y + _BODY_HEIGHT / 2 - 4,
            self.x + _BODY_WIDTH / 2,
            self.y + _BODY_HEIGHT / 2 - 4,
            (*SENTINEL_BODY_ACCENT[:3], 80),
            1,
        )

    def _draw_opening(self) -> None:
        """Draw the recessed core opening slot at vertical center."""
        half_h = SENTINEL_OPENING_HEIGHT / 2
        arcade.draw_lrbt_rectangle_filled(
            self.x - _BODY_WIDTH / 2,
            self.x + _BODY_WIDTH / 2,
            self.y - half_h,
            self.y + half_h,
            SENTINEL_OPENING_COLOR,
        )

    def _draw_core(self) -> None:
        """Draw the glowing core visible through the opening."""
        cx, cy = self.core_pos
        # Shift core to body center Y for the opening
        cy = self.y
        r = SENTINEL_CORE_SIZE / 2

        # Glow pulse
        pulse = 0.7 + 0.3 * math.sin(self.time_alive * 4)
        glow_r = r * (1.2 + 0.2 * pulse)
        glow_alpha = int(60 * pulse)
        arcade.draw_circle_filled(
            cx, cy, glow_r, (*SENTINEL_CORE_COLOR[:3], glow_alpha)
        )

        # Core circle
        arcade.draw_circle_filled(cx, cy, r, SENTINEL_CORE_COLOR)
        # Inner bright spot
        arcade.draw_circle_filled(cx, cy, r * 0.4, SENTINEL_CORE_GLOW_COLOR)

    def _draw_beam_charge(self) -> None:
        """Draw charge-up glow on the core before beam fires."""
        cx = self.x
        cy = self.y
        progress = 1.0 - (self.beam_charge_timer / SENTINEL_BEAM_CHARGE_TIME)
        glow_r = SENTINEL_CORE_SIZE * (0.5 + progress * 0.8)
        alpha = int(120 * progress)
        arcade.draw_circle_filled(cx, cy, glow_r, (255, 255, 255, alpha))

    def _draw_beam(self) -> None:
        """Draw the beam effect across the screen."""
        # Main beam line
        arcade.draw_lrbt_rectangle_filled(
            0,
            self.x,
            self.beam_y - 4,
            self.beam_y + 4,
            (255, 255, 200, 220),
        )
        # Outer glow
        arcade.draw_lrbt_rectangle_filled(
            0,
            self.x,
            self.beam_y - 10,
            self.beam_y + 10,
            (255, 255, 200, 60),
        )
