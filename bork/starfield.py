"""Parallax scrolling starfield background."""

import random

import arcade

from bork.constants import (
    COLOR_STAR,
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


class Starfield:
    """Multi-layer parallax scrolling starfield."""

    def __init__(self) -> None:
        self.stars: list[Star] = []
        for layer in range(len(STAR_COUNTS)):
            speed = STAR_SPEEDS[layer]
            size = STAR_SIZES[layer]
            alpha = STAR_COLORS_ALPHA[layer]
            for _ in range(STAR_COUNTS[layer]):
                x = random.uniform(0, SCREEN_WIDTH)
                y = random.uniform(0, SCREEN_HEIGHT)
                self.stars.append(Star(x, y, speed, size, alpha))

    def update(self, dt: float) -> None:
        """Move stars leftward; wrap at left edge."""
        for star in self.stars:
            star.x -= star.speed * dt
            if star.x < 0:
                star.x = SCREEN_WIDTH + random.uniform(0, 20)
                star.y = random.uniform(0, SCREEN_HEIGHT)

    def draw(self) -> None:
        """Draw each star as a filled circle."""
        for star in self.stars:
            color = (*COLOR_STAR, star.alpha)
            arcade.draw_circle_filled(star.x, star.y, star.size, color)
