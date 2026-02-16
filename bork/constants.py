# Window
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
SCREEN_TITLE = "B.O.R.K."
TARGET_FPS = 60

# Player
PLAYER_ACCELERATION = 600.0  # pixels/sec^2
PLAYER_FRICTION = 0.88  # velocity multiplier per frame (at 60fps)
PLAYER_MAX_SPEED = 350.0  # pixels/sec
PLAYER_SHIP_SIZE = 20  # half-width of the ship triangle
PLAYER_START_X = 100
PLAYER_START_Y = SCREEN_HEIGHT // 2

# Projectiles
PROJECTILE_SPEED = 700.0  # pixels/sec
PROJECTILE_LENGTH = 16
PROJECTILE_WIDTH = 3
SHOOT_COOLDOWN = 0.18  # seconds between shots

# Starfield
STAR_LAYER_COUNT = 2
STAR_COUNTS = [60, 30]  # back layer (dim/slow), front layer (bright/fast)
STAR_SPEEDS = [40.0, 100.0]  # pixels/sec per layer
STAR_SIZES = [1.5, 2.5]  # radius per layer
STAR_COLORS_ALPHA = [100, 200]  # alpha per layer (0-255)

# Enemies
ENEMY_SPEED = 150.0  # pixels/sec (horizontal, leftward)
ENEMY_SIZE = 15  # half-width for collision and drawing
ENEMY_COLOR = (255, 60, 60)  # distinct red

# Waves
WAVE_START_DELAY = 3.0  # seconds before first wave
WAVE_PAUSE = 2.0  # seconds between waves
ENEMIES_PER_WAVE = 5
ENEMY_SPAWN_SPACING = 0.3  # seconds between each enemy in a wave

# Sine wave pattern
SINE_AMPLITUDE = 80.0  # pixels
SINE_FREQUENCY = 2.0  # oscillations per second

# Spawn Y positions (fraction of screen height)
WAVE_TOP_Y = 0.75
WAVE_BOTTOM_Y = 0.25
WAVE_CENTER_Y = 0.5

# Powerups
POWERUP_SPEED = 100.0  # pixels/sec (slower than enemies)
POWERUP_SIZE = 18  # radius
POWERUP_COLOR = (255, 220, 0)  # yellow
POWERUP_TEXT_COLOR = (0, 0, 0)  # black letter

# Powerup spawn
POWERUP_SPAWN_DELAY = 1.0  # seconds after wave 3 completes
POWERUP_SPAWN_Y = 0.70  # 30% from top = 70% up

# Powerup effects
SPEED_BOOST_MULTIPLIER = 1.35  # 35% speed increase

# Powerup pulse animation
POWERUP_PULSE_SPEED = 4.0  # oscillations per second
POWERUP_PULSE_AMOUNT = 0.15  # scale varies ±15%

# Particles
PARTICLE_POOL_SIZE = 500  # max concurrent particles

# Enemy explosion
ENEMY_EXPLOSION_COUNT = (12, 20)  # min, max particles
ENEMY_EXPLOSION_SPEED = (100, 300)  # px/sec
ENEMY_EXPLOSION_LIFETIME = (0.3, 0.6)  # seconds
ENEMY_EXPLOSION_SIZE = (4, 8)  # start size px
ENEMY_EXPLOSION_COLOR_END = (255, 150, 0)  # fade to orange

# Player explosion
PLAYER_EXPLOSION_COUNT = (30, 50)
PLAYER_EXPLOSION_SPEED = (200, 500)  # px/sec
PLAYER_EXPLOSION_LIFETIME = (0.5, 1.0)  # seconds
PLAYER_EXPLOSION_SIZE = (6, 12)  # start size px
PLAYER_EXPLOSION_COLOR_END = (255, 200, 50)  # fade to yellow-orange

# Powerup burst
POWERUP_BURST_COUNT = (8, 12)
POWERUP_BURST_SPEED = (80, 150)  # px/sec
POWERUP_BURST_LIFETIME = (0.3, 0.4)  # seconds
POWERUP_BURST_SIZE = (3, 5)  # start size px
POWERUP_BURST_COLOR_END = (255, 255, 200)  # fade to light yellow

# Screen flash
SCREEN_FLASH_DURATION = 0.1  # full brightness seconds
SCREEN_FLASH_FADE = 0.2  # fade-out seconds
SCREEN_FLASH_COLOR = (255, 255, 255)  # white

# Screen shake
SCREEN_SHAKE_INTENSITY = 6.0  # pixels
SCREEN_SHAKE_DURATION = 0.3  # seconds

# Game state
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# Colors
COLOR_BACKGROUND = (5, 5, 15)
COLOR_PLAYER = (0, 200, 255)
COLOR_LASER = (255, 80, 80)
COLOR_STAR = (255, 255, 255)
