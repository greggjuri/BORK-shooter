"""B.O.R.K. — main game window and loop."""

import arcade

from bork.collision import circle_circle, point_in_circle
from bork.constants import (
    COLOR_BACKGROUND,
    COMBO_MILESTONES,
    ENEMY_SIZE,
    PLAYER_SHIP_SIZE,
    PLAYER_START_X,
    PLAYER_START_Y,
    POINTS_BASIC_ENEMY,
    POWERUP_COLOR,
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
    SPEED_BOOST_MULTIPLIER,
    STARTING_LIVES,
    STATE_GAME_OVER,
    STATE_PLAYING,
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


class BorkGame(arcade.Window):
    """Main game window managing the core loop."""

    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(COLOR_BACKGROUND)
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

    def setup(self) -> None:
        """Initialize game state."""
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.projectiles = []
        self.enemies = []
        self.starfield = Starfield()
        self.wave_spawner = WaveSpawner()
        self.state = STATE_PLAYING
        self.particle_system = ParticleSystem()
        self.screen_flash = None
        self.screen_shake = None
        self.powerups = []
        self.powerup_spawn_timer = 0.0
        self.scoring = ScoringSystem()
        self.hud = HUD()
        self.score_popups = ScorePopupManager()
        self.lives = STARTING_LIVES

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

        # Update enemies and remove off-screen ones
        for e in self.enemies:
            e.update(dt)
        self.enemies = [e for e in self.enemies if not e.is_off_screen()]

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

    def _check_enemy_player_collisions(self) -> None:
        """Check if any enemy touches the player."""
        if self.player.is_invulnerable:
            return

        for enemy in self.enemies:
            if circle_circle(
                enemy.x,
                enemy.y,
                ENEMY_SIZE,
                self.player.x,
                self.player.y,
                PLAYER_SHIP_SIZE,
            ):
                self.particle_system.add(
                    create_player_explosion(self.player.x, self.player.y)
                )
                self.screen_flash = ScreenFlash(
                    SCREEN_FLASH_COLOR, SCREEN_FLASH_DURATION, SCREEN_FLASH_FADE
                )
                self.screen_shake = ScreenShake(
                    SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_DURATION
                )
                self.lives -= 1
                if self.lives <= 0:
                    self.state = STATE_GAME_OVER
                else:
                    # Respawn player
                    self.player.x = PLAYER_START_X
                    self.player.y = PLAYER_START_Y
                    self.player.vx = 0.0
                    self.player.vy = 0.0
                    self.player.invulnerable_timer = RESPAWN_INVULNERABLE_TIME
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
                # Apply effect (no stacking)
                if self.player.speed_multiplier <= 1.0:
                    self.player.speed_multiplier = SPEED_BOOST_MULTIPLIER
                self.particle_system.add(create_powerup_burst(p.x, p.y, POWERUP_COLOR))
            else:
                remaining.append(p)
        self.powerups = remaining

    def _get_active_powerups(self) -> list[str]:
        """Build list of active powerup names for HUD display."""
        powerups: list[str] = []
        if self.player.speed_multiplier > 1.0:
            powerups.append("speed")
        return powerups

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

        if self.state == STATE_PLAYING:
            self.player.draw()

        for proj in self.projectiles:
            proj.draw()

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
        self.hud.draw(
            self.scoring.score,
            self.scoring.multiplier,
            self.scoring.combo,
            self.lives,
            self._get_active_powerups(),
        )

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

        if self.state == STATE_GAME_OVER and key == arcade.key.R:
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
