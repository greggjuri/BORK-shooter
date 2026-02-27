"""Collision detection utilities."""


def circle_circle(
    x1: float, y1: float, r1: float, x2: float, y2: float, r2: float
) -> bool:
    """Return True if two circles overlap or touch."""
    dx = x1 - x2
    dy = y1 - y2
    combined_r = r1 + r2
    return (dx * dx + dy * dy) <= combined_r * combined_r


def point_in_circle(px: float, py: float, cx: float, cy: float, r: float) -> bool:
    """Return True if point is inside or on the circle."""
    dx = px - cx
    dy = py - cy
    return (dx * dx + dy * dy) <= r * r


def point_in_rect(
    px: float, py: float, rx: float, ry: float, width: float, height: float
) -> bool:
    """Return True if point is inside a rectangle centered at (rx, ry)."""
    half_w = width / 2
    half_h = height / 2
    return (rx - half_w) <= px <= (rx + half_w) and (ry - half_h) <= py <= (ry + half_h)
