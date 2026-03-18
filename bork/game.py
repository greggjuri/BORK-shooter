"""B.O.R.K. — main game window and loop."""

import arcade

from bork.boss import Sentinel
from bork.enemy_projectile import EnemyProjectile
from bork.boss_fight import (
    update_boss_dying,
    update_boss_fight,
    update_boss_warning,
    update_victory,
    update_zone_transition,
)
from bork.collision import circle_circle, point_in_circle
from bork.debug_skip import handle_debug_key  # DEBUG ONLY
from bork.constants import (
    COLOR_BACKGROUND,
    COMBO_MILESTONES,
    ENEMY_SIZE,
    PLAYER_SHIP_SIZE,
    PLAYER_START_X,
    PLAYER_START_Y,
    POINTS_BASIC_ENEMY,
    POWERUP_BURST_COLOR,
    POWERUP_SIZE,
    POWERUP_SPAWN_DELAY,
    POWERUP_SPAWN_Y,
    RESPAWN_INVULNERABLE_TIME,
    SCREEN_FLASH_COLOR,
    SCREEN_FLASH_DURATION,
    SCREEN_FLASH_FADE,
    SCREEN_HEIGHT,
    SCREEN_SHAKE_DURATION,
    SCREEN_SHAKE_INTENSITY,
    SCREEN_TITLE,
    SCREEN_WIDTH,
    STARTING_LIVES,
    STATE_BOSS_DYING,
    STATE_BOSS_FIGHT,
    STATE_BOSS_WARNING,
    STATE_GAME_OVER,
    STATE_PLAYING,
    STATE_VICTORY,
    STATE_ZONE_TRANSITION,
    WARNING_DURATION,
    WARNING_FLASH_COLOR,
)
from bork.enemy import Enemy
from bork.explosions import (
    create_enemy_explosion,
    create_player_explosion,
    create_powerup_burst,
)
from bork.hud import HUD
from bork.particles import ParticleSystem
from bork.player import Player
from bork.powerup import Powerup
from bork.projectile import Projectile
from bork.score_popup import ScorePopupManager
from bork.scoring import ScoringSystem
from bork.screen_effects import ScreenFlash, ScreenShake
from bork.starfield import Starfield
from bork.wave_spawner import WaveSpawner
from bork.zone_manager import ZoneManager


class BorkGame(arcade.Window):
    """Main game window managing the core loop."""

    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(COLOR_BACKGROUND)
        self.zone_manager: ZoneManager = ZoneManager()
        self.player: Player | None = None
        self.projectiles: list[Projectile] = []
        self.enemies: list[Enemy] = []
        self.starfield: Starfield | None = None
        self.wave_spawner: WaveSpawner | None = None
        self.keys_pressed: set[int] = set()
        self.state: str = STATE_PLAYING
        self.particle_system: ParticleSystem = ParticleSystem()
        self.screen_flash: ScreenFlash | None = None
        self.screen_shake: ScreenShake | None = None
        self.powerups: list[Powerup] = []
        self.powerup_spawn_timer: float = 0.0
        self.scoring: ScoringSystem = ScoringSystem()
        self.hud: HUD = HUD()
        self.score_popups: ScorePopupManager = ScorePopupManager()
        self.lives: int = STARTING_LIVES
        # Boss state
        self.boss: Sentinel | None = None
        self.enemy_projectiles: list[EnemyProjectile] = []
        self.boss_warning_timer: float = 0.0
        self.player_hit_during_boss: bool = False
        self.victory_timer: float = 0.0
        self.boss_death_explosion_timer: float = 0.0
        self.victory_points_awarded: bool = False
        self.victory_bonus_pts: int = 0
        self.zone_transition_timer: float = 0.0

    def setup(self) -> None:
        """Initialize full game state (new game or restart)."""
        self.zone_manager.reset()
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        config = self.zone_manager.config
        self.starfield = Starfield(config.get("background_style", "deep_space"))
        self.particle_system = ParticleSystem()
        self.screen_flash = None
        self.screen_shake = None
        self.scoring = ScoringSystem()
        self.hud = HUD()
        self.score_popups = ScorePopupManager()
        self.lives = STARTING_LIVES
        self._start_zone()

    def _start_zone(self) -> None:
        """Start (or restart) the current zone. Keeps player, score, and lives."""
        config = self.zone_manager.config
        self.wave_spawner = WaveSpawner(config)
        self.starfield = Starfield(config.get("background_style", "deep_space"))
        self.projectiles = []
        self.enemies = []
        self.powerups = []
        self.powerup_spawn_timer = 0.0
        self.boss = None
        self.enemy_projectiles = []
        self.boss_warning_timer = 0.0
        self.player_hit_during_boss = False
        self.victory_timer = 0.0
        self.boss_death_explosion_timer = 0.0
        self.victory_points_awarded = False
        self.victory_bonus_pts = 0
        self.zone_transition_timer = 0.0
        self.state = STATE_PLAYING

    def on_update(self, dt: float) -> None:
        """Update all game entities."""
        # Starfield always scrolls (even during game over)
        self.starfield.update(dt)

        # Update particles and screen effects regardless of state
        self.particle_system.update(dt)
        if self.screen_flash:
            self.screen_flash.update(dt)
            if self.screen_flash.is_done:
                self.screen_flash = None
        if self.screen_shake:
            self.screen_shake.update(dt)
            if self.screen_shake.is_done:
                self.screen_shake = None

        # Update scoring, HUD, and popups even during game over
        self.scoring.update(dt)
        self.hud.update(dt)
        self.score_popups.update(dt)

        # Boss state dispatch
        if self.state == STATE_BOSS_WARNING:
            update_boss_warning(self, dt)
            return
        if self.state == STATE_BOSS_FIGHT:
            update_boss_fight(self, dt)
            return
        if self.state == STATE_BOSS_DYING:
            update_boss_dying(self, dt)
            return
        if self.state == STATE_VICTORY:
            update_victory(self, dt)
            return
        if self.state == STATE_ZONE_TRANSITION:
            update_zone_transition(self, dt)
            return
        if self.state != STATE_PLAYING:
            return

        self.player.update(dt, self.keys_pressed)
        self.player.shoot_timer -= dt

        # Update projectiles and remove off-screen ones
        for proj in self.projectiles:
            proj.update(dt)
        self.projectiles = [p for p in self.projectiles if not p.is_off_screen()]

        # Spawn enemies from wave spawner
        enemy = self.wave_spawner.update(dt)
        if enemy is not None:
            self.enemies.append(enemy)

        # Check boss trigger
        if self.wave_spawner.boss_triggered:
            self.wave_spawner.boss_triggered = False
            self.state = STATE_BOSS_WARNING
            self.boss_warning_timer = WARNING_DURATION
            self.powerups.clear()
            self.powerup_spawn_timer = 0.0
            self.screen_flash = ScreenFlash(
                WARNING_FLASH_COLOR[:3], 0.1, WARNING_DURATION
            )
            return

        # Update enemies, collect projectiles, remove off-screen
        px, py = self.player.x, self.player.y
        for e in self.enemies:
            proj = e.update(dt, px, py)
            if proj is not None:
                self.enemy_projectiles.append(proj)
        self.enemies = [e for e in self.enemies if not e.is_off_screen()]

        # Update enemy projectiles during normal play
        for ep in self.enemy_projectiles:
            ep.update(dt)
        self.enemy_projectiles = [
            ep for ep in self.enemy_projectiles if not ep.is_off_screen()
        ]

        # Powerup spawn signal from wave spawner
        if self.wave_spawner.powerup_spawn_due:
            self.powerup_spawn_timer = POWERUP_SPAWN_DELAY
            self.wave_spawner.powerup_spawn_due = False

        # Powerup spawn timer
        if self.powerup_spawn_timer > 0:
            self.powerup_spawn_timer -= dt
            if self.powerup_spawn_timer <= 0:
                self.powerups.append(
                    Powerup(
                        SCREEN_WIDTH + POWERUP_SIZE,
                        SCREEN_HEIGHT * POWERUP_SPAWN_Y,
                        "speed",
                    )
                )

        # Update powerups and remove off-screen ones
        for p in self.powerups:
            p.update(dt)
        self.powerups = [p for p in self.powerups if not p.is_off_screen()]

        # Continuous shooting while Space is held
        if arcade.key.SPACE in self.keys_pressed:
            self._try_shoot()

        # Collision: projectiles vs enemies
        self._check_projectile_enemy_collisions()

        # Collision: enemies vs player
        self._check_enemy_player_collisions()

        # Collision: enemy projectiles vs player
        self._check_enemy_projectile_player_collisions()

        # Collision: powerups vs player
        self._check_powerup_player_collisions()

    def _check_projectile_enemy_collisions(self) -> None:
        """Remove projectiles and enemies that collide, award score."""
        hit_projectiles: set[int] = set()
        hit_enemies: set[int] = set()

        for pi, proj in enumerate(self.projectiles):
            for ei, enemy in enumerate(self.enemies):
                if ei in hit_enemies:
                    continue
                if point_in_circle(proj.x, proj.y, enemy.x, enemy.y, ENEMY_SIZE):
                    hit_projectiles.add(pi)
                    hit_enemies.add(ei)
                    self.particle_system.add(create_enemy_explosion(enemy.x, enemy.y))
                    # Score the kill
                    points = self.scoring.register_kill(POINTS_BASIC_ENEMY)
                    self.score_popups.spawn(enemy.x, enemy.y, points)
                    # Check combo milestones
                    milestone = COMBO_MILESTONES.get(self.scoring.combo)
                    if milestone:
                        self.hud.trigger_milestone(milestone)
                    break  # one projectile can only hit one enemy

        self.projectiles = [
            p for i, p in enumerate(self.projectiles) if i not in hit_projectiles
        ]
        self.enemies = [e for i, e in enumerate(self.enemies) if i not in hit_enemies]

    def _damage_player(self) -> None:
        """Apply hit damage: explosion, flash, shake, respawn or game over."""
        self.particle_system.add(
            create_player_explosion(self.player.x, self.player.y)
        )
        self.screen_flash = ScreenFlash(
            SCREEN_FLASH_COLOR, SCREEN_FLASH_DURATION, SCREEN_FLASH_FADE
        )
        self.screen_shake = ScreenShake(SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_DURATION)
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_GAME_OVER
        else:
            self.player.x = PLAYER_START_X
            self.player.y = PLAYER_START_Y
            self.player.vx = 0.0
            self.player.vy = 0.0
            self.player.invulnerable_timer = RESPAWN_INVULNERABLE_TIME
            self.player.downgrade_on_death()

    def _check_enemy_player_collisions(self) -> None:
        """Check if any enemy touches the player."""
        if self.player.is_invulnerable:
            return
        for enemy in self.enemies:
            if circle_circle(
                enemy.x, enemy.y, ENEMY_SIZE,
                self.player.x, self.player.y, PLAYER_SHIP_SIZE,
            ):
                self._damage_player()
                return

    def _check_enemy_projectile_player_collisions(self) -> None:
        """Check if enemy projectiles hit the player during normal gameplay."""
        if self.player.is_invulnerable or not self.enemy_projectiles:
            return
        for ep in self.enemy_projectiles:
            if point_in_circle(ep.x, ep.y, self.player.x, self.player.y, PLAYER_SHIP_SIZE):
                self._damage_player()
                self.enemy_projectiles.clear()
                return

    def _check_powerup_player_collisions(self) -> None:
        """Check if player collects any powerup."""
        remaining: list[Powerup] = []
        for p in self.powerups:
            if circle_circle(
                p.x,
                p.y,
                POWERUP_SIZE,
                self.player.x,
                self.player.y,
                PLAYER_SHIP_SIZE,
            ):
                # Apply tier level-up
                if p.kind == "speed":
                    self.player.speed_level = min(3, self.player.speed_level + 1)
                self.particle_system.add(create_powerup_burst(p.x, p.y, POWERUP_BURST_COLOR))
            else:
                remaining.append(p)
        self.powerups = remaining

    def _get_tier_levels(self) -> tuple[int, int]:
        """Return (speed_level, fire_rate_level) for HUD display."""
        return (self.player.speed_level, self.player.fire_rate_level)

    def on_draw(self) -> None:
        """Draw all game entities."""
        self.clear()

        # Apply screen shake offset
        shake_x, shake_y = 0.0, 0.0
        if self.screen_shake:
            shake_x, shake_y = self.screen_shake.get_offset()
        if shake_x != 0.0 or shake_y != 0.0:
            self.ctx.projection_2d = (
                -shake_x,
                SCREEN_WIDTH - shake_x,
                -shake_y,
                SCREEN_HEIGHT - shake_y,
            )

        self.starfield.draw()

        for enemy in self.enemies:
            enemy.draw()

        for p in self.powerups:
            p.draw()

        # Draw boss (behind player, in front of enemies); hide after final explosion
        if self.boss and self.state in (STATE_BOSS_FIGHT, STATE_BOSS_DYING):
            self.boss.draw()

        if self.state in (STATE_PLAYING, STATE_BOSS_WARNING, STATE_BOSS_FIGHT):
            self.player.draw()

        for proj in self.projectiles:
            proj.draw()

        # Enemy projectiles
        for ep in self.enemy_projectiles:
            ep.draw()

        self.particle_system.draw()

        # Score popups in world space (affected by shake)
        self.score_popups.draw()

        # Reset projection after world drawing
        if shake_x != 0.0 or shake_y != 0.0:
            self.ctx.projection_2d = (0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        # Screen flash overlay (drawn without shake)
        if self.screen_flash:
            self.screen_flash.draw()

        # HUD (drawn without shake)
        spd, rof = self._get_tier_levels()
        self.hud.draw(
            self.scoring.score,
            self.scoring.multiplier,
            self.scoring.combo,
            self.lives,
            spd,
            rof,
            self.zone_manager.current_zone,
        )

        # Boss health bar (HUD layer, no shake)
        if self.boss and self.state in (STATE_BOSS_FIGHT, STATE_BOSS_DYING):
            self.hud.draw_boss_health_bar(
                self.boss.core_hp,
                self.boss.max_hp,
                self.boss.name,
                self.boss.phase,
            )

        # Warning overlay
        if self.state == STATE_BOSS_WARNING:
            self.hud.draw_warning_text(self.boss_warning_timer)

        # Victory overlay
        if self.state == STATE_VICTORY:
            if self.zone_manager.is_final_zone:
                self.hud.draw_game_complete_text(self.scoring.score)
            else:
                config = self.zone_manager.config
                self.hud.draw_victory_text(
                    config["name"],
                    config["boss_points"],
                    self.victory_bonus_pts,
                )

        # Zone transition overlay
        if self.state == STATE_ZONE_TRANSITION:
            self.hud.draw_zone_transition_text(self.zone_manager.config["name"])

        # Game over overlay
        if self.state == STATE_GAME_OVER:
            arcade.draw_text(
                "GAME OVER",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 20,
                arcade.color.WHITE,
                font_size=36,
                anchor_x="center",
                anchor_y="center",
            )
            arcade.draw_text(
                f"Final Score: {self.scoring.score:,}",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 20,
                arcade.color.LIGHT_GRAY,
                font_size=18,
                anchor_x="center",
                anchor_y="center",
            )
            arcade.draw_text(
                "Press R to restart",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 50,
                arcade.color.LIGHT_GRAY,
                font_size=16,
                anchor_x="center",
                anchor_y="center",
            )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Track key presses."""
        self.keys_pressed.add(key)
        handle_debug_key(key, self)  # DEBUG ONLY

        if key == arcade.key.R and self.state in (
            STATE_GAME_OVER, STATE_VICTORY, STATE_ZONE_TRANSITION
        ):
            self.setup()

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Track key releases."""
        self.keys_pressed.discard(key)

    def _try_shoot(self) -> None:
        """Fire a projectile if cooldown allows."""
        if self.player.can_shoot():
            nose_x = self.player.x + PLAYER_SHIP_SIZE
            self.projectiles.append(Projectile(nose_x, self.player.y))
            self.player.reset_shoot_timer()


def main() -> None:
    """Entry point."""
    game = BorkGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
