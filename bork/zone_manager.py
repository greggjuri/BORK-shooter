"""Zone progression manager for multi-zone gameplay."""

from bork.constants import ZONE_CONFIGS, ZONE_COUNT


class ZoneManager:
    """Tracks current zone and provides zone config."""

    def __init__(self) -> None:
        self.current_zone: int = 1

    @property
    def config(self) -> dict:
        """Return config for current zone."""
        return ZONE_CONFIGS[self.current_zone]

    @property
    def is_final_zone(self) -> bool:
        """Return True if current zone is the last one."""
        return self.current_zone >= ZONE_COUNT

    def advance(self) -> bool:
        """Advance to next zone. Returns True if advanced, False if already final."""
        if self.is_final_zone:
            return False
        self.current_zone += 1
        return True

    def reset(self) -> None:
        """Reset to Zone 1."""
        self.current_zone = 1
