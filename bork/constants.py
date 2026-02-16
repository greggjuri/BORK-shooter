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

# Destroy effect
DESTROY_FLASH_DURATION = 0.12  # seconds
DESTROY_FLASH_COLOR = (255, 255, 200)

# Game state
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"

# Colors
COLOR_BACKGROUND = (5, 5, 15)
COLOR_PLAYER = (0, 200, 255)
COLOR_LASER = (255, 80, 80)
COLOR_STAR = (255, 255, 255)
