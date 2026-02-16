"""B.O.R.K. — main game window and loop."""

import math

import arcade

from bork.collision import circle_circle, point_in_circle
from bork.constants import (
    COLOR_BACKGROUND,
    DESTROY_FLASH_COLOR,
    DESTROY_FLASH_DURATION,
    ENEMY_SIZE,
    PLAYER_MAX_SPEED,
    PLAYER_SHIP_SIZE,
    PLAYER_START_X,
    PLAYER_START_Y,
    POWERUP_COLLECT_FLASH_COLOR,
    POWERUP_COLLECT_FLASH_DURATION,
    POWERUP_SIZE,
    POWERUP_SPAWN_DELAY,
    POWERUP_SPAWN_Y,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
    SCREEN_WIDTH,
    SPEED_BOOST_MULTIPLIER,
    STATE_GAME_OVER,
    STATE_PLAYING,
)
from bork.enemy import Enemy
from bork.player import Player
from bork.powerup import Powerup
from bork.projectile import Projectile
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
        self.destroy_effects: list[list] = []  # [[x, y, timer, color], ...]
        self.powerups: list[Powerup] = []
        self.powerup_spawn_timer: float = 0.0

    def setup(self) -> None:
        """Initialize game state."""
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.projectiles = []
        self.enemies = []
        self.starfield = Starfield()
        self.wave_spawner = WaveSpawner()
        self.state = STATE_PLAYING
        self.destroy_effects = []
        self.powerups = []
        self.powerup_spawn_timer = 0.0

    def on_update(self, dt: float) -> None:
        """Update all game entities."""
        # Starfield always scrolls (even during game over)
        self.starfield.update(dt)

        # Update destroy effects regardless of state
        for effect in self.destroy_effects:
            effect[2] -= dt
        self.destroy_effects = [e for e in self.destroy_effects if e[2] > 0]

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
        """Remove projectiles and enemies that collide."""
        hit_projectiles: set[int] = set()
        hit_enemies: set[int] = set()

        for pi, proj in enumerate(self.projectiles):
            for ei, enemy in enumerate(self.enemies):
                if ei in hit_enemies:
                    continue
                if point_in_circle(proj.x, proj.y, enemy.x, enemy.y, ENEMY_SIZE):
                    hit_projectiles.add(pi)
                    hit_enemies.add(ei)
                    self.destroy_effects.append(
                        [enemy.x, enemy.y, DESTROY_FLASH_DURATION, DESTROY_FLASH_COLOR]
                    )
                    break  # one projectile can only hit one enemy

        self.projectiles = [
            p for i, p in enumerate(self.projectiles) if i not in hit_projectiles
        ]
        self.enemies = [e for i, e in enumerate(self.enemies) if i not in hit_enemies]

    def _check_enemy_player_collisions(self) -> None:
        """Check if any enemy touches the player."""
        for enemy in self.enemies:
            if circle_circle(
                enemy.x,
                enemy.y,
                ENEMY_SIZE,
                self.player.x,
                self.player.y,
                PLAYER_SHIP_SIZE,
            ):
                self.state = STATE_GAME_OVER
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
                self.destroy_effects.append(
                    [
                        p.x,
                        p.y,
                        POWERUP_COLLECT_FLASH_DURATION,
                        POWERUP_COLLECT_FLASH_COLOR,
                    ]
                )
            else:
                remaining.append(p)
        self.powerups = remaining

    def on_draw(self) -> None:
        """Draw all game entities."""
        self.clear()
        self.starfield.draw()

        for enemy in self.enemies:
            enemy.draw()

        for p in self.powerups:
            p.draw()

        if self.state == STATE_PLAYING:
            self.player.draw()

        for proj in self.projectiles:
            proj.draw()

        # Flash effects (destroy + collect)
        for effect in self.destroy_effects:
            x, y, timer, base_color = effect
            alpha = int(255 * min(timer * 8.0, 1.0))  # fade out
            radius = ENEMY_SIZE * 1.5
            color = (*base_color, alpha)
            arcade.draw_circle_filled(x, y, radius, color)

        # Debug speedometer (temporary)
        speed = math.sqrt(self.player.vx**2 + self.player.vy**2)
        max_spd = PLAYER_MAX_SPEED * self.player.speed_multiplier
        arcade.draw_text(
            f"SPD: {speed:.0f} / {max_spd:.0f}",
            SCREEN_WIDTH - 10,
            10,
            arcade.color.WHITE,
            font_size=12,
            anchor_x="right",
            anchor_y="bottom",
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
                "Press R to restart",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 30,
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
