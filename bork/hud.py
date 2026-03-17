"""Sci-fi heads-up display for score, multiplier, combo, lives, and powerups."""

import math

import arcade

from bork.constants import (
    BOSS_HP_BAR_HEIGHT,
    BOSS_HP_BAR_WIDTH,
    BOSS_HP_BAR_Y,
    COMBO_MILESTONE_DURATION,
    COMBO_MILESTONE_FADE,
    HUD_ACCENT,
    HUD_COMBO_FONT_SIZE,
    HUD_DIM,
    HUD_LABEL_FONT_SIZE,
    HUD_LIVES_FONT_SIZE,
    HUD_MARGIN,
    HUD_MILESTONE_FONT_SIZE,
    HUD_MULTI_FONT_SIZE,
    HUD_MULTI_PULSE_AMOUNT,
    HUD_MULTI_PULSE_SPEED,
    HUD_PRIMARY,
    HUD_SCORE_FONT_SIZE,
    HUD_TIER_ACTIVE_COLOR,
    HUD_TIER_FONT_SIZE,
    HUD_TIER_INACTIVE_COLOR,
    HUD_TIER_PIP_SIZE,
    HUD_TIER_Y,
    HUD_ZONE_FONT_SIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STARTING_LIVES,
    WARNING_TEXT_COLOR,
)


class HUD:
    """Sci-fi heads-up display for score, multiplier, combo, lives, powerups."""

    def __init__(self) -> None:
        self.milestone_text: str = ""
        self.milestone_timer: float = 0.0
        self.multi_pulse_timer: float = 0.0

    def update(self, dt: float) -> None:
        """Update animations (milestone fade, multiplier pulse)."""
        if self.milestone_timer > 0:
            self.milestone_timer -= dt
            if self.milestone_timer < 0:
                self.milestone_timer = 0.0
        self.multi_pulse_timer += dt

    def trigger_milestone(self, text: str) -> None:
        """Show a combo milestone message."""
        self.milestone_text = text
        self.milestone_timer = COMBO_MILESTONE_DURATION

    def draw(
        self,
        score: int,
        multiplier: float,
        combo: int,
        lives: int,
        speed_level: int,
        fire_rate_level: int,
        zone: int = 1,
    ) -> None:
        """Draw the full HUD overlay."""
        self._draw_score(score)
        self._draw_multiplier(multiplier)
        self._draw_combo(combo)
        self._draw_lives(lives)
        self._draw_tier_indicators(speed_level, fire_rate_level)
        self._draw_zone(zone)
        self._draw_milestone()

    def _draw_score(self, score: int) -> None:
        """Draw score with sci-fi bracket framing."""
        arcade.draw_text(
            "\u25c4 SCORE \u25ba",
            HUD_MARGIN,
            SCREEN_HEIGHT - HUD_MARGIN,
            HUD_DIM,
            font_size=HUD_LABEL_FONT_SIZE,
            anchor_x="left",
            anchor_y="top",
        )
        arcade.draw_text(
            f"{score:,}",
            HUD_MARGIN,
            SCREEN_HEIGHT - HUD_MARGIN - 18,
            HUD_PRIMARY,
            font_size=HUD_SCORE_FONT_SIZE,
            bold=True,
            anchor_x="left",
            anchor_y="top",
        )

    def _draw_multiplier(self, multiplier: float) -> None:
        """Draw multiplier indicator with pulse when active."""
        if multiplier <= 1.0:
            return
        pulse = math.sin(self.multi_pulse_timer * HUD_MULTI_PULSE_SPEED * 2 * math.pi)
        alpha = int(255 * (0.7 + HUD_MULTI_PULSE_AMOUNT * pulse))
        alpha = max(0, min(255, alpha))
        color = (*HUD_ACCENT[:3], alpha)
        arcade.draw_text(
            f"x{multiplier:.1f} MULTI",
            HUD_MARGIN + 200,
            SCREEN_HEIGHT - HUD_MARGIN - 18,
            color,
            font_size=HUD_MULTI_FONT_SIZE,
            anchor_x="left",
            anchor_y="top",
        )

    def _draw_combo(self, combo: int) -> None:
        """Draw combo counter when >= 3."""
        if combo < 3:
            return
        t = min(combo / 20.0, 1.0)
        r = int(HUD_PRIMARY[0] + (HUD_ACCENT[0] - HUD_PRIMARY[0]) * t)
        g = int(HUD_PRIMARY[1] + (HUD_ACCENT[1] - HUD_PRIMARY[1]) * t)
        b = int(HUD_PRIMARY[2] + (HUD_ACCENT[2] - HUD_PRIMARY[2]) * t)
        arcade.draw_text(
            f"\u2039 {combo} COMBO \u203a",
            HUD_MARGIN,
            SCREEN_HEIGHT - HUD_MARGIN - 48,
            (r, g, b),
            font_size=HUD_COMBO_FONT_SIZE,
            anchor_x="left",
            anchor_y="top",
        )

    def _draw_lives(self, lives: int) -> None:
        """Draw lives as chevron icons, lost lives as dim outlines."""
        base_x = SCREEN_WIDTH - HUD_MARGIN - 140
        y = SCREEN_HEIGHT - HUD_MARGIN - 18
        arcade.draw_text(
            "LIVES",
            base_x - 10,
            SCREEN_HEIGHT - HUD_MARGIN,
            HUD_DIM,
            font_size=HUD_LABEL_FONT_SIZE,
            anchor_x="left",
            anchor_y="top",
        )
        for i in range(STARTING_LIVES):
            color = HUD_PRIMARY if i < lives else HUD_DIM
            arcade.draw_text(
                "\u25b8",
                base_x + i * 20,
                y,
                color,
                font_size=HUD_LIVES_FONT_SIZE,
                anchor_x="left",
                anchor_y="top",
            )

    def _draw_tier_indicators(
        self, speed_level: int, fire_rate_level: int
    ) -> None:
        """Draw SPD and ROF tier pip indicators at bottom of screen."""
        s = HUD_TIER_PIP_SIZE
        y = HUD_TIER_Y

        # SPD indicator — left side
        x = HUD_MARGIN
        arcade.draw_text(
            "SPD", x, y, HUD_PRIMARY,
            font_size=HUD_TIER_FONT_SIZE, anchor_x="left", anchor_y="center",
        )
        pip_x = x + 55
        for i in range(3):
            color = HUD_TIER_ACTIVE_COLOR if i < speed_level else HUD_TIER_INACTIVE_COLOR
            arcade.draw_lrbt_rectangle_filled(
                pip_x - s, pip_x + s, y - s, y + s, color,
            )
            pip_x += s * 3

        # ROF indicator — offset right of SPD
        x = HUD_MARGIN + 130
        arcade.draw_text(
            "ROF", x, y, HUD_PRIMARY,
            font_size=HUD_TIER_FONT_SIZE, anchor_x="left", anchor_y="center",
        )
        pip_x = x + 55
        for i in range(3):
            color = HUD_TIER_ACTIVE_COLOR if i < fire_rate_level else HUD_TIER_INACTIVE_COLOR
            arcade.draw_lrbt_rectangle_filled(
                pip_x - s, pip_x + s, y - s, y + s, color,
            )
            pip_x += s * 3

    def _draw_zone(self, zone: int) -> None:
        """Draw zone indicator."""
        arcade.draw_text(
            f"\u25c4 ZONE {zone:02d} \u25ba",
            SCREEN_WIDTH - HUD_MARGIN,
            SCREEN_HEIGHT - HUD_MARGIN,
            HUD_DIM,
            font_size=HUD_ZONE_FONT_SIZE,
            anchor_x="right",
            anchor_y="top",
        )

    def _draw_milestone(self) -> None:
        """Draw combo milestone text centered on screen."""
        if self.milestone_timer <= 0:
            return
        alpha = int(255 * min(self.milestone_timer / COMBO_MILESTONE_FADE, 1.0))
        color = (*HUD_ACCENT[:3], alpha)
        arcade.draw_text(
            self.milestone_text,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 60,
            color,
            font_size=HUD_MILESTONE_FONT_SIZE,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )

    # --- Boss HUD elements ---

    def draw_boss_health_bar(
        self,
        core_hp: int,
        core_max: int,
        boss_name: str,
        phase: int,
    ) -> None:
        """Draw the boss health bar at top of screen."""
        cx = SCREEN_WIDTH / 2
        bar_y = BOSS_HP_BAR_Y

        # Boss name
        arcade.draw_text(
            boss_name,
            cx,
            bar_y + BOSS_HP_BAR_HEIGHT + 8,
            WARNING_TEXT_COLOR,
            font_size=12,
            bold=True,
            anchor_x="center",
            anchor_y="bottom",
        )

        # Background bar
        bar_left = cx - BOSS_HP_BAR_WIDTH / 2
        arcade.draw_lrbt_rectangle_filled(
            bar_left,
            bar_left + BOSS_HP_BAR_WIDTH,
            bar_y,
            bar_y + BOSS_HP_BAR_HEIGHT,
            (20, 20, 30),
        )

        # Fill bar (color shifts green → yellow → red)
        frac = core_hp / core_max if core_max > 0 else 0
        fill_w = BOSS_HP_BAR_WIDTH * frac
        if frac > 0.5:
            t = (frac - 0.5) * 2  # 1 at full, 0 at half
            r = int(255 * (1 - t))
            g = 255
        else:
            t = frac * 2  # 1 at half, 0 at empty
            r = 255
            g = int(255 * t)
        bar_color = (r, g, 0)

        if fill_w > 0:
            arcade.draw_lrbt_rectangle_filled(
                bar_left,
                bar_left + fill_w,
                bar_y,
                bar_y + BOSS_HP_BAR_HEIGHT,
                bar_color,
            )

        # Outline
        arcade.draw_lrbt_rectangle_outline(
            bar_left,
            bar_left + BOSS_HP_BAR_WIDTH,
            bar_y,
            bar_y + BOSS_HP_BAR_HEIGHT,
            HUD_DIM,
            border_width=1,
        )

        # Phase indicator
        arcade.draw_text(
            f"PHASE {phase}",
            cx,
            bar_y - 4,
            HUD_DIM,
            font_size=9,
            anchor_x="center",
            anchor_y="top",
        )

    def draw_warning_text(self, timer: float) -> None:
        """Draw pulsing WARNING text at screen center."""
        # Pulse 3 times over the warning duration
        pulse = math.sin(timer * 6 * math.pi)
        alpha = int(180 + 75 * pulse)
        alpha = max(0, min(255, alpha))
        color = (*WARNING_TEXT_COLOR[:3], alpha)
        arcade.draw_text(
            "WARNING",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            color,
            font_size=48,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )

    def draw_victory_text(
        self, boss_name: str, core_pts: int, bonus_pts: int
    ) -> None:
        """Draw victory overlay with point breakdown."""
        cy = SCREEN_HEIGHT / 2 + 40
        arcade.draw_text(
            f"{boss_name} DESTROYED",
            SCREEN_WIDTH / 2,
            cy,
            HUD_ACCENT,
            font_size=32,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Core: +{core_pts:,}",
            SCREEN_WIDTH / 2,
            cy - 40,
            HUD_PRIMARY,
            font_size=16,
            anchor_x="center",
            anchor_y="center",
        )
        if bonus_pts > 0:
            arcade.draw_text(
                f"No-Damage Bonus: +{bonus_pts:,}",
                SCREEN_WIDTH / 2,
                cy - 62,
                HUD_ACCENT,
                font_size=16,
                bold=True,
                anchor_x="center",
                anchor_y="center",
            )

    def draw_zone_transition_text(self, zone_name: str) -> None:
        """Draw zone complete overlay during transition."""
        arcade.draw_text(
            f"{zone_name} COMPLETE",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 20,
            HUD_ACCENT,
            font_size=32,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "Entering next zone...",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 20,
            HUD_PRIMARY,
            font_size=16,
            anchor_x="center",
            anchor_y="center",
        )

    def draw_game_complete_text(self, score: int) -> None:
        """Draw final game complete overlay."""
        arcade.draw_text(
            "GAME COMPLETE",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 40,
            HUD_ACCENT,
            font_size=36,
            bold=True,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            f"Final Score: {score:,}",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2,
            HUD_PRIMARY,
            font_size=20,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "Press R to restart",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 - 35,
            HUD_DIM,
            font_size=16,
            anchor_x="center",
            anchor_y="center",
        )
