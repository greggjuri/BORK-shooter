"""Parallax scrolling starfield background with optional nebula clouds."""

import random

import arcade

from bork.constants import (
    COLOR_STAR,
    NEBULA_CLOUD_COLORS,
    NEBULA_CLOUD_COUNT,
    NEBULA_CLOUD_SIZE_RANGE,
    NEBULA_CLOUD_SPEED,
    NEBULA_STAR_TINT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STAR_COLORS_ALPHA,
    STAR_COUNTS,
    STAR_SIZES,
    STAR_SPEEDS,
)


class Star:
    """A single star in the parallax field."""

    def __init__(
        self, x: float, y: float, speed: float, size: float, alpha: int
    ) -> None:
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.alpha = alpha


class Cloud:
    """A semi-transparent nebula cloud in the deepest parallax layer."""

    def __init__(
        self, x: float, y: float, width: float, height: float,
        color: tuple[int, int, int, int],
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color


class Starfield:
    """Multi-layer parallax scrolling starfield with optional nebula clouds."""

    def __init__(self, style: str = "deep_space") -> None:
        self.style = style
        self.star_tint = NEBULA_STAR_TINT if style == "nebula" else COLOR_STAR

        # Stars
        self.stars: list[Star] = []
        for layer in range(len(STAR_COUNTS)):
            speed = STAR_SPEEDS[layer]
            size = STAR_SIZES[layer]
            alpha = STAR_COLORS_ALPHA[layer]
            for _ in range(STAR_COUNTS[layer]):
                x = random.uniform(0, SCREEN_WIDTH)
                y = random.uniform(0, SCREEN_HEIGHT)
                self.stars.append(Star(x, y, speed, size, alpha))

        # Nebula clouds (only for nebula style)
        self.clouds: list[Cloud] = []
        if style == "nebula":
            for i in range(NEBULA_CLOUD_COUNT):
                x = random.uniform(0, SCREEN_WIDTH)
                y = random.uniform(0, SCREEN_HEIGHT)
                r = random.uniform(*NEBULA_CLOUD_SIZE_RANGE)
                color = NEBULA_CLOUD_COLORS[i % len(NEBULA_CLOUD_COLORS)]
                self.clouds.append(Cloud(x, y, r * 2, r * 1.2, color))

    def update(self, dt: float) -> None:
        """Move stars and clouds leftward; wrap at left edge."""
        for star in self.stars:
            star.x -= star.speed * dt
            if star.x < 0:
                star.x = SCREEN_WIDTH + random.uniform(0, 20)
                star.y = random.uniform(0, SCREEN_HEIGHT)

        for cloud in self.clouds:
            cloud.x -= NEBULA_CLOUD_SPEED * dt
            if cloud.x < -cloud.width:
                cloud.x = SCREEN_WIDTH + cloud.width + random.uniform(0, 100)
                cloud.y = random.uniform(0, SCREEN_HEIGHT)

    def draw(self) -> None:
        """Draw clouds (deepest layer), then stars."""
        # Nebula clouds behind everything
        for cloud in self.clouds:
            arcade.draw_ellipse_filled(
                cloud.x, cloud.y, cloud.width, cloud.height, cloud.color
            )

        # Stars
        for star in self.stars:
            color = (*self.star_tint, star.alpha)
            arcade.draw_circle_filled(star.x, star.y, star.size, color)
