"""Tests for the starfield system."""

from bork.constants import SCREEN_HEIGHT, SCREEN_WIDTH, STAR_COUNTS
from bork.starfield import Star, Starfield


def test_starfield_initializes_correct_star_count() -> None:
    field = Starfield()
    assert len(field.stars) == sum(STAR_COUNTS)


def test_stars_within_screen_bounds() -> None:
    field = Starfield()
    for star in field.stars:
        assert 0 <= star.x <= SCREEN_WIDTH
        assert 0 <= star.y <= SCREEN_HEIGHT


def test_starfield_update_moves_stars_left() -> None:
    field = Starfield()
    # Place all stars well within screen so none wrap
    for star in field.stars:
        star.x = SCREEN_WIDTH / 2
    old_xs = [star.x for star in field.stars]
    field.update(1 / 60)
    for old_x, star in zip(old_xs, field.stars):
        assert star.x < old_x


def test_star_wraps_when_off_screen_left() -> None:
    star = Star(x=-1, y=100, speed=50.0, size=2.0, alpha=200)
    field = Starfield()
    field.stars = [star]
    field.update(1 / 60)
    assert star.x > SCREEN_WIDTH
