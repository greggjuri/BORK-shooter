"""Boss fight state handlers and collision methods extracted from game.py."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import arcade

from bork.boss import Sentinel
from bork.collision import point_in_circle, point_in_rect
from bork.constants import (
    BOSS_DEATH_DURATION,
    BOSS_DEATH_FINAL_SHAKE_DURATION,
    BOSS_DEATH_FINAL_SHAKE_INTENSITY,
    BOSS_DEATH_SMALL_EXPLOSION_INTERVAL,
    PLAYER_SHIP_SIZE,
    PLAYER_START_X,
    PLAYER_START_Y,
    RESPAWN_INVULNERABLE_TIME,
    SCREEN_FLASH_COLOR,
    SCREEN_FLASH_DURATION,
    SCREEN_FLASH_FADE,
    SCREEN_HEIGHT,
    SCREEN_SHAKE_DURATION,
    SCREEN_SHAKE_INTENSITY,
    SCREEN_WIDTH,
    SENTINEL_BEAM_HIT_HEIGHT,
    SENTINEL_BODY_DAMAGE,
    SENTINEL_CORE_DAMAGE,
    SENTINEL_OPENING_HEIGHT,
    SENTINEL_WIDTH,
    STATE_BOSS_DYING,
    STATE_BOSS_FIGHT,
    STATE_GAME_OVER,
    STATE_VICTORY,
    STATE_ZONE_TRANSITION,
    VICTORY_DISPLAY_DURATION,
    ZONE_TRANSITION_DURATION,
)
from bork.explosions import (
    create_boss_explosion,
    create_boss_small_explosion,
    create_enemy_explosion,
    create_player_explosion,
)
from bork.screen_effects import ScreenFlash, ScreenShake

if TYPE_CHECKING:
    from bork.game import BorkGame


def update_boss_warning(game: BorkGame, dt: float) -> None:
    """Handle WARNING state before boss appears."""
    game.boss_warning_timer -= dt
    # Player still moves during warning
    game.player.update(dt, game.keys_pressed)
    game.player.shoot_timer -= dt
    if arcade.key.SPACE in game.keys_pressed:
        game._try_shoot()
    # Update remaining projectiles
    for proj in game.projectiles:
        proj.update(dt)
    game.projectiles = [p for p in game.projectiles if not p.is_off_screen()]
    # Let existing enemies continue scrolling (they'll leave screen naturally)
    for e in game.enemies:
        e.update(dt)
    game.enemies = [e for e in game.enemies if not e.is_off_screen()]

    # Enemies still interact normally during warning
    game._check_projectile_enemy_collisions()
    game._check_enemy_player_collisions()

    if game.boss_warning_timer <= 0:
        game.boss = Sentinel(SCREEN_WIDTH + SENTINEL_WIDTH, SCREEN_HEIGHT / 2)
        game.enemy_projectiles = []
        game.player_hit_during_boss = False
        game.state = STATE_BOSS_FIGHT


def update_boss_fight(game: BorkGame, dt: float) -> None:
    """Handle active boss fight."""
    game.player.update(dt, game.keys_pressed)
    game.player.shoot_timer -= dt

    for proj in game.projectiles:
        proj.update(dt)
    game.projectiles = [p for p in game.projectiles if not p.is_off_screen()]

    if arcade.key.SPACE in game.keys_pressed:
        game._try_shoot()

    new_projs = game.boss.update(dt, game.player.x, game.player.y)
    game.enemy_projectiles.extend(new_projs)

    for ep in game.enemy_projectiles:
        ep.update(dt)
    game.enemy_projectiles = [
        ep for ep in game.enemy_projectiles if not ep.is_off_screen()
    ]

    # Let remaining enemies from warning phase continue scrolling off
    for e in game.enemies:
        e.update(dt)
    game.enemies = [e for e in game.enemies if not e.is_off_screen()]

    # Enemies still interact normally until they scroll off
    game._check_projectile_enemy_collisions()
    game._check_enemy_player_collisions()

    check_projectile_boss_collisions(game)
    check_enemy_projectile_player_collisions(game)
    check_beam_player_collision(game)

    if game.boss.is_dead:
        game.boss.state = "dying"
        game.state = STATE_BOSS_DYING
        game.boss.death_timer = BOSS_DEATH_DURATION
        game.boss_death_explosion_timer = 0.0
        game.enemy_projectiles = []


def update_boss_dying(game: BorkGame, dt: float) -> None:
    """Handle boss death animation — staggered multi-burst destruction."""
    game.boss.death_timer -= dt
    game.boss_death_explosion_timer -= dt

    # Escalating shake throughout the death sequence
    elapsed = BOSS_DEATH_DURATION - game.boss.death_timer
    shake_ramp = min(1.0, elapsed / BOSS_DEATH_DURATION)
    game.screen_shake = ScreenShake(
        BOSS_DEATH_FINAL_SHAKE_INTENSITY * 0.3 * (1.0 + shake_ramp), 0.15
    )

    if game.boss_death_explosion_timer <= 0:
        game.boss_death_explosion_timer = BOSS_DEATH_SMALL_EXPLOSION_INTERVAL
        # Spawn sub-explosions across the full hull area
        rx = game.boss.x + random.uniform(-90, 90)
        ry = game.boss.y + random.uniform(-70, 70)
        game.particle_system.add(create_boss_small_explosion(rx, ry))

    if game.boss.death_timer <= 0:
        # Final detonation: multiple offset bursts for a wall of fire
        bx, by = game.boss.x, game.boss.y
        game.particle_system.add(create_boss_explosion(bx, by))
        for _ in range(4):
            ox = random.uniform(-60, 60)
            oy = random.uniform(-50, 50)
            game.particle_system.add(create_boss_explosion(bx + ox, by + oy))
        game.screen_shake = ScreenShake(
            BOSS_DEATH_FINAL_SHAKE_INTENSITY, BOSS_DEATH_FINAL_SHAKE_DURATION
        )
        game.screen_flash = ScreenFlash((255, 255, 255), 0.25, 0.6)
        game.state = STATE_VICTORY
        game.victory_timer = VICTORY_DISPLAY_DURATION
        _award_boss_victory_points(game)


def update_victory(game: BorkGame, dt: float) -> None:
    """Handle victory display countdown, then trigger zone transition or game complete."""
    game.victory_timer -= dt
    if game.victory_timer <= 0:
        if game.zone_manager.is_final_zone:
            # Stay in victory state — game complete, wait for R to restart
            pass
        else:
            game.state = STATE_ZONE_TRANSITION
            game.zone_transition_timer = ZONE_TRANSITION_DURATION


def update_zone_transition(game: BorkGame, dt: float) -> None:
    """Handle zone transition countdown, then advance to next zone."""
    game.zone_transition_timer -= dt
    if game.zone_transition_timer <= 0:
        game.zone_manager.advance()
        game._start_zone()


def _award_boss_victory_points(game: BorkGame) -> None:
    """Award points for boss defeat using zone config values."""
    config = game.zone_manager.config
    boss_points = config["boss_points"]
    nodamage_bonus = config["boss_nodamage_bonus"]

    game.scoring.register_kill(boss_points)
    game.score_popups.spawn(game.boss.x, game.boss.y, boss_points)

    game.victory_bonus_pts = 0
    if not game.player_hit_during_boss:
        game.victory_bonus_pts = nodamage_bonus
        game.scoring.score += nodamage_bonus
    game.victory_points_awarded = True


def check_projectile_boss_collisions(game: BorkGame) -> None:
    """Check player projectiles against boss hit zones (core opening then armor)."""
    if game.boss is None or game.boss.state != "fighting":
        return

    hit_projectiles: set[int] = set()
    for pi, proj in enumerate(game.projectiles):
        if pi in hit_projectiles:
            continue

        # Zone 1: Core opening (narrow horizontal slot, checked first for priority)
        if point_in_rect(
            proj.x, proj.y, game.boss.x, game.boss.y, 100, SENTINEL_OPENING_HEIGHT
        ):
            hit_projectiles.add(pi)
            game.boss.take_hit(SENTINEL_CORE_DAMAGE)
            game.particle_system.add(create_enemy_explosion(proj.x, proj.y))
            continue

        # Zone 2: Armor (full body rect)
        if point_in_rect(proj.x, proj.y, game.boss.x, game.boss.y, 100, 80):
            hit_projectiles.add(pi)
            game.boss.take_hit(SENTINEL_BODY_DAMAGE)

    game.projectiles = [
        p for i, p in enumerate(game.projectiles) if i not in hit_projectiles
    ]


def check_enemy_projectile_player_collisions(game: BorkGame) -> None:
    """Check boss projectiles against the player."""
    if game.player.is_invulnerable:
        return

    for ep in game.enemy_projectiles:
        if point_in_circle(ep.x, ep.y, game.player.x, game.player.y, PLAYER_SHIP_SIZE):
            _handle_player_hit(game)
            return


def check_beam_player_collision(game: BorkGame) -> None:
    """Check if the boss beam hits the player."""
    if game.boss is None or game.boss.beam_visible_timer <= 0:
        return
    if game.player.is_invulnerable:
        return
    if abs(game.player.y - game.boss.beam_y) < SENTINEL_BEAM_HIT_HEIGHT / 2:
        _handle_player_hit(game)


def _handle_player_hit(game: BorkGame) -> None:
    """Apply damage to the player from boss attacks."""
    game.player_hit_during_boss = True
    game.particle_system.add(create_player_explosion(game.player.x, game.player.y))
    game.screen_flash = ScreenFlash(
        SCREEN_FLASH_COLOR, SCREEN_FLASH_DURATION, SCREEN_FLASH_FADE
    )
    game.screen_shake = ScreenShake(SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_DURATION)
    game.lives -= 1
    if game.lives <= 0:
        game.state = STATE_GAME_OVER
    else:
        game.player.x = PLAYER_START_X
        game.player.y = PLAYER_START_Y
        game.player.vx = 0.0
        game.player.vy = 0.0
        game.player.invulnerable_timer = RESPAWN_INVULNERABLE_TIME
        game.player.downgrade_on_death()
