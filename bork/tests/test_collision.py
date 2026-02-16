"""Tests for collision detection."""

from bork.collision import circle_circle, point_in_circle


def test_circle_circle_overlap() -> None:
    assert circle_circle(0, 0, 10, 5, 0, 10)


def test_circle_circle_no_overlap() -> None:
    assert not circle_circle(0, 0, 5, 100, 100, 5)


def test_circle_circle_touching() -> None:
    # Exactly touching: distance = r1 + r2
    assert circle_circle(0, 0, 5, 10, 0, 5)


def test_point_in_circle_inside() -> None:
    assert point_in_circle(1, 1, 0, 0, 10)


def test_point_in_circle_outside() -> None:
    assert not point_in_circle(100, 100, 0, 0, 10)


def test_point_in_circle_on_edge() -> None:
    assert point_in_circle(10, 0, 0, 0, 10)
