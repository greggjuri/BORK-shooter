"""Tests for the zone progression manager."""

from bork.constants import ZONE_CONFIGS, ZONE_COUNT
from bork.wave_spawner import WaveSpawner
from bork.zone_manager import ZoneManager


def test_starts_at_zone_1() -> None:
    zm = ZoneManager()
    assert zm.current_zone == 1


def test_config_returns_zone_data() -> None:
    zm = ZoneManager()
    config = zm.config
    assert config["name"] == "DEEP SPACE"
    assert "waves_before_boss" in config
    assert "wave_patterns" in config
    assert "enemies_per_wave" in config
    assert "enemy_speed" in config
    assert "boss_type" in config
    assert "boss_points" in config
    assert "boss_nodamage_bonus" in config
    assert "powerup_after_wave" in config


def test_advance_increments_zone() -> None:
    zm = ZoneManager()
    result = zm.advance()
    assert result is True
    assert zm.current_zone == 2


def test_advance_to_zone_3() -> None:
    zm = ZoneManager()
    zm.advance()
    zm.advance()
    assert zm.current_zone == 3


def test_advance_returns_false_at_final() -> None:
    zm = ZoneManager()
    zm.current_zone = ZONE_COUNT
    result = zm.advance()
    assert result is False
    assert zm.current_zone == ZONE_COUNT


def test_is_final_zone() -> None:
    zm = ZoneManager()
    assert zm.is_final_zone is False
    zm.current_zone = 2
    assert zm.is_final_zone is False
    zm.current_zone = 3
    assert zm.is_final_zone is True


def test_reset_returns_to_zone_1() -> None:
    zm = ZoneManager()
    zm.advance()
    zm.advance()
    assert zm.current_zone == 3
    zm.reset()
    assert zm.current_zone == 1


def test_all_zone_configs_exist() -> None:
    for z in range(1, ZONE_COUNT + 1):
        assert z in ZONE_CONFIGS


def test_spawner_uses_zone_enemy_speed() -> None:
    config = ZONE_CONFIGS[2]
    spawner = WaveSpawner(config)
    assert spawner._enemy_speed == config["enemy_speed"]


def test_spawner_uses_zone_wave_count() -> None:
    config = ZONE_CONFIGS[2]
    spawner = WaveSpawner(config)
    assert spawner._boss_after == config["waves_before_boss"]
