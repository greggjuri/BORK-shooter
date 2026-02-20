"""Sci-fi heads-up display for score, multiplier, combo, lives, and powerups."""

import math

import arcade

from bork.constants import (
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
    HUD_POWERUP_FONT_SIZE,
    HUD_PRIMARY,
    HUD_SCORE_FONT_SIZE,
    HUD_ZONE_FONT_SIZE,
    POWERUP_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STARTING_LIVES,
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
        active_powerups: list[str],
    ) -> None:
        """Draw the full HUD overlay."""
        self._draw_score(score)
        self._draw_multiplier(multiplier)
        self._draw_combo(combo)
        self._draw_lives(lives)
        self._draw_powerups(active_powerups)
        self._draw_zone()
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

    def _draw_powerups(self, active_powerups: list[str]) -> None:
        """Draw active powerup indicators in brackets."""
        if not active_powerups:
            return
        x = SCREEN_WIDTH - HUD_MARGIN
        y = SCREEN_HEIGHT - HUD_MARGIN - 40
        for pu in active_powerups:
            label = {"speed": "SPEED+"}.get(pu, pu.upper())
            arcade.draw_text(
                f"[{label}]",
                x,
                y,
                POWERUP_COLOR,
                font_size=HUD_POWERUP_FONT_SIZE,
                anchor_x="right",
                anchor_y="top",
            )
            y -= 16

    def _draw_zone(self) -> None:
        """Draw zone indicator (static for now)."""
        arcade.draw_text(
            "\u25c4 ZONE 01 \u25ba",
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
