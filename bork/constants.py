# ============================================================
# DEBUG ONLY — SET TO False BEFORE RELEASE
# ============================================================
DEBUG_SKIP_ENABLED = True  # TODO: remove debug_skip before release

# Window
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
SCREEN_TITLE = "B.O.R.K."
TARGET_FPS = 60

# Player
PLAYER_ACCELERATION = 600.0  # pixels/sec^2
PLAYER_FRICTION = 0.88  # velocity multiplier per frame (at 60fps)
PLAYER_MAX_SPEED = 200.0  # pixels/sec
PLAYER_SHIP_SIZE = 20  # half-width of the ship triangle
PLAYER_START_X = 100
PLAYER_START_Y = SCREEN_HEIGHT // 2

# Projectiles
PROJECTILE_SPEED = 700.0  # pixels/sec
PROJECTILE_LENGTH = 16
PROJECTILE_WIDTH = 3
SHOOT_COOLDOWN = 0.36  # seconds between shots

# Starfield
STAR_LAYER_COUNT = 2
STAR_COUNTS = [60, 30]  # back layer (dim/slow), front layer (bright/fast)
STAR_SPEEDS = [40.0, 100.0]  # pixels/sec per layer
STAR_SIZES = [1.5, 2.5]  # radius per layer
STAR_COLORS_ALPHA = [100, 200]  # alpha per layer (0-255)

# Nebula background (Zone 2)
NEBULA_CLOUD_COUNT = 5
NEBULA_CLOUD_SPEED = 25.0  # px/sec (slower than slowest star layer)
NEBULA_CLOUD_SIZE_RANGE = (60, 140)  # ellipse radius range
NEBULA_CLOUD_COLORS = (
    (180, 80, 200, 25),
    (220, 80, 180, 30),
    (100, 120, 220, 25),
    (160, 60, 180, 20),
    (120, 100, 240, 28),
)
NEBULA_STAR_TINT = (200, 180, 255)  # slight purple tint for nebula stars

# Enemies
ENEMY_SPEED = 150.0  # pixels/sec (horizontal, leftward)
ENEMY_SIZE = 15  # half-width for collision and drawing
ENEMY_COLOR = (255, 60, 60)  # distinct red

# Enemy bat wing colors
ENEMY_BATWING_BODY_COLOR = (42, 42, 58)  # #2a2a3a — wings
ENEMY_BATWING_HULL_COLOR = (30, 30, 46)  # #1e1e2e — center hull plate
ENEMY_BATWING_PLATE_COLOR = (53, 53, 69)  # #353545 — fuselage
ENEMY_BATWING_STROKE_COLOR = (255, 68, 68)  # red outline
ENEMY_BATWING_EYE_COLOR = (255, 51, 51)  # scanner eye outer
ENEMY_BATWING_EYE_BRIGHT = (255, 102, 102)  # scanner eye inner

# Dart enemy (Zone 2)
ENEMY_DART_SIZE = 10  # collision radius (~65% of bat wing)
ENEMY_DART_BODY_COLOR = (30, 180, 80)  # green hull
ENEMY_DART_ACCENT_COLOR = (80, 255, 130)  # bright green stroke
ENEMY_DART_SCANNER_COLOR = (50, 255, 120)  # scanner eye glow
ENEMY_DART_SHOOTER_CHANCE = 0.35  # 35% of darts can shoot
ENEMY_DART_SHOOT_COOLDOWN = 2.0  # seconds between shots
ENEMY_DART_PROJECTILE_SPEED = 250.0  # px/sec
ENEMY_DART_PROJECTILE_COLOR = (100, 255, 120)  # green

# Enemy wobble
ENEMY_BATWING_WOBBLE_SPEED = 1.5  # oscillations per second
ENEMY_BATWING_WOBBLE_DEGREES = 3.0  # max rotation in degrees
ENEMY_BATWING_BOB_SPEED = 1.0  # vertical bob oscillations per second
ENEMY_BATWING_BOB_PIXELS = 2.0  # max vertical bob offset in pixels

# Waves
WAVE_START_DELAY = 3.0  # seconds before first wave
WAVE_PAUSE = 2.0  # seconds between waves
ENEMIES_PER_WAVE = 5
ENEMY_SPAWN_SPACING = 0.3  # seconds between each enemy in a wave

# Sine wave pattern
SINE_AMPLITUDE = 80.0  # pixels
SINE_FREQUENCY = 1.6  # oscillations per second

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

# Powerup tier levels
SPEED_LEVELS = (200.0, 300.0, 420.0)  # max speed per tier (level 1/2/3)
FIRE_RATE_LEVELS = (0.36, 0.24, 0.14)  # shoot cooldown per tier (lower = faster)
POWERUP_LABEL_COLOR = (255, 255, 255, 220)  # white letter on glassy button
POWERUP_BURST_COLOR = (0, 200, 180)  # teal burst on collection

# Powerup pulse animation
POWERUP_PULSE_SPEED = 4.0  # oscillations per second
POWERUP_PULSE_AMOUNT = 0.15  # scale varies ±15%

# Particles
PARTICLE_POOL_SIZE = 1500  # max concurrent particles

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

# Scoring
POINTS_BASIC_ENEMY = 100
MULTIPLIER_INCREMENT = 0.1
MULTIPLIER_MAX = 5.0
MULTIPLIER_DECAY_DELAY = 3.0  # seconds before decay starts
COMBO_WINDOW = 2.0  # seconds between kills to maintain combo

# Combo milestones
COMBO_MILESTONES = {
    5: "NICE!",
    10: "UNSTOPPABLE!",
    20: "GODLIKE!",
}
COMBO_MILESTONE_DURATION = 1.0  # seconds to display milestone text
COMBO_MILESTONE_FADE = 0.5  # seconds to fade out

# Lives
STARTING_LIVES = 3
RESPAWN_INVULNERABLE_TIME = 2.0  # seconds of invulnerability after respawn
INVULNERABLE_BLINK_RATE = 10.0  # blinks per second during invulnerability

# HUD colors
HUD_PRIMARY = (0, 255, 255)  # Cyan - main text and frames
HUD_SECONDARY = (100, 200, 255)  # Light blue - secondary elements
HUD_ACCENT = (255, 220, 100)  # Gold - multiplier/combo highlights
HUD_DIM = (60, 80, 90)  # Dim cyan - inactive/lost lives
HUD_BACKGROUND = (0, 10, 20, 180)  # Dark blue, semi-transparent

# HUD layout
HUD_MARGIN = 20
HUD_SCORE_FONT_SIZE = 24
HUD_LABEL_FONT_SIZE = 12
HUD_MULTI_FONT_SIZE = 16
HUD_COMBO_FONT_SIZE = 14
HUD_LIVES_FONT_SIZE = 16
HUD_POWERUP_FONT_SIZE = 11
HUD_ZONE_FONT_SIZE = 12
HUD_MILESTONE_FONT_SIZE = 28

# HUD tier indicators
HUD_TIER_Y = 30
HUD_TIER_FONT_SIZE = 11
HUD_TIER_ACTIVE_COLOR = (0, 255, 180)  # bright teal for filled pips
HUD_TIER_INACTIVE_COLOR = (40, 60, 70)  # dim for unfilled pips
HUD_TIER_PIP_SIZE = 6  # pip square half-size

# HUD multiplier pulse
HUD_MULTI_PULSE_SPEED = 3.0  # pulses per second when active
HUD_MULTI_PULSE_AMOUNT = 0.3  # alpha varies ±30%

# Score popup
SCORE_POPUP_DURATION = 0.5  # seconds
SCORE_POPUP_RISE_SPEED = 60.0  # pixels per second upward
SCORE_POPUP_FONT_SIZE = 14

# Game state
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_BOSS_WARNING = "boss_warning"
STATE_BOSS_FIGHT = "boss_fight"
STATE_BOSS_DYING = "boss_dying"
STATE_VICTORY = "victory"
STATE_ZONE_TRANSITION = "zone_transition"

# Colors
COLOR_BACKGROUND = (5, 5, 15)
COLOR_PLAYER = (0, 200, 255)
COLOR_LASER = (255, 80, 80)
COLOR_STAR = (255, 255, 255)

# Ship colors
SHIP_BODY_COLOR = (26, 58, 74)  # #1a3a4a — main hull
SHIP_DARK_COLOR = (13, 42, 56)  # #0d2a38 — wing fins
SHIP_ACCENT_COLOR = (0, 34, 51)  # #002233 — engine block
SHIP_COCKPIT_COLOR = (0, 51, 68)  # #003344 — cockpit accent
SHIP_OUTLINE_COLOR = (0, 220, 255)  # bright cyan stroke

# Engine exhaust glow layers (offset_x, width, height, r, g, b, alpha)
# Sorted outermost first so inner layers draw on top.
EXHAUST_LAYERS = (
    (-55, 56, 26, 255, 160, 50, 5),
    (-52, 50, 24, 255, 145, 45, 10),
    (-49, 44, 22, 255, 130, 40, 18),
    (-46, 39, 20, 250, 115, 35, 28),
    (-43, 34, 18, 245, 95, 30, 40),
    (-40, 29, 16, 235, 75, 25, 55),
    (-38, 24, 14, 220, 60, 20, 70),
    (-36, 20, 12, 205, 45, 15, 85),
    (-34, 16, 10, 190, 35, 12, 95),
    (-33, 12, 8, 180, 30, 10, 102),
)

# === Boss System ===

# Boss spawn
BOSS_SPAWN_AFTER_WAVES = 9
WARNING_DURATION = 5.0

# Sentinel stats
SENTINEL_CORE_HP = 50
SENTINEL_CORE_DAMAGE = 2  # damage per hit through core opening
SENTINEL_BODY_DAMAGE = 1  # damage per hit on armor

# Sentinel size
SENTINEL_WIDTH = 200
SENTINEL_HEIGHT = 150
SENTINEL_CORE_SIZE = 40
SENTINEL_OPENING_HEIGHT = 20  # height of the core opening slot

# Sentinel colors
SENTINEL_BODY_COLOR = (60, 65, 75)
SENTINEL_BODY_ACCENT = (0, 200, 220)
SENTINEL_CORE_COLOR = (255, 80, 40)
SENTINEL_CORE_GLOW_COLOR = (255, 200, 100)
SENTINEL_ARMOR_COLOR = (80, 85, 95)
SENTINEL_OPENING_COLOR = (20, 25, 35)  # dark recessed slot color

# Sentinel hull polygon colors
SENTINEL_HULL_COLOR = (42, 42, 58)  # #2a2a3a — outer hull fill
SENTINEL_HULL_STROKE = (136, 136, 170)  # #8888aa — outer hull outline
SENTINEL_PLATE_COLOR = (30, 30, 46)  # #1e1e2e — inner armor plate fill
SENTINEL_PLATE_STROKE = (102, 102, 170)  # #6666aa — inner armor plate outline

# Sentinel engine exhaust glow layers (offset_x, width, height, r, g, b, alpha)
# Sorted outermost first so inner layers draw on top. Extends rightward from engine.
SENTINEL_EXHAUST_LAYERS = (
    (48, 52, 22, 140, 140, 255, 5),
    (44, 46, 20, 130, 130, 250, 8),
    (40, 40, 18, 120, 120, 245, 14),
    (36, 35, 16, 110, 110, 240, 22),
    (32, 30, 14, 100, 100, 235, 32),
    (28, 25, 12, 90, 90, 225, 45),
    (24, 20, 10, 75, 75, 210, 60),
    (21, 16, 8, 60, 60, 200, 75),
    (18, 12, 7, 45, 45, 190, 90),
    (16, 9, 6, 30, 30, 180, 102),
)

# Sentinel movement
SENTINEL_BATTLE_X = SCREEN_WIDTH - 150
SENTINEL_ENTER_SPEED = 120.0
SENTINEL_TRACK_SPEED = 60
SENTINEL_TRACK_SPEED_P2 = 100
SENTINEL_TRACK_SPEED_P3 = 140
SENTINEL_LUNGE_SPEED = 200
SENTINEL_LUNGE_DURATION = 0.5
SENTINEL_ERRATIC_FREQ = 5.0  # Phase 3 erratic oscillation speed
SENTINEL_ERRATIC_AMP = 30.0  # Phase 3 erratic oscillation amplitude (px)

# Sentinel points
SENTINEL_CORE_POINTS = 5000
SENTINEL_NODAMAGE_BONUS = 2500

# Phase thresholds (fraction of max HP)
SENTINEL_PHASE2_THRESHOLD = 0.66
SENTINEL_PHASE3_THRESHOLD = 0.33

# Attack timing (seconds)
SENTINEL_SPREAD_INTERVAL_P1 = 2.0
SENTINEL_SPREAD_INTERVAL_P2 = 1.5
SENTINEL_AIMED_INTERVAL = 1.0
SENTINEL_BEAM_CHARGE_TIME = 1.0
SENTINEL_BEAM_COOLDOWN = 4.0
SENTINEL_BEAM_HIT_HEIGHT = 20

# Bullet speeds
BOSS_BULLET_SPEED_MEDIUM = 200
BOSS_BULLET_SPEED_FAST = 350

# Boss bullet colors
BOSS_BULLET_COLOR_CYAN = (0, 220, 255)
BOSS_BULLET_COLOR_WHITE = (255, 255, 255)
BOSS_BULLET_COLOR_RED = (255, 60, 60)
BOSS_BEAM_COLOR = (255, 255, 200)

# Boss health bar
BOSS_HP_BAR_WIDTH = 400
BOSS_HP_BAR_HEIGHT = 12
BOSS_HP_BAR_Y = SCREEN_HEIGHT - 55

# === Marauder (Zone 2 Boss) ===

MARAUDER_WIDTH = 150
MARAUDER_HEIGHT = 60
MARAUDER_HP = 160
MARAUDER_ENTER_SPEED = 150.0
MARAUDER_BATTLE_X = SCREEN_WIDTH - 160

# Marauder movement
MARAUDER_PATROL_FREQ = 0.6
MARAUDER_PATROL_AMP = 110

# Marauder phase thresholds (fraction of max HP)
MARAUDER_PHASE2_HP = 0.50
MARAUDER_PHASE3_HP = 0.25

# Marauder shooting
MARAUDER_PROJ_SPEED = 320
MARAUDER_SHOOT_INTERVAL_P1 = 1.8
MARAUDER_SHOOT_INTERVAL_P2 = 1.2
MARAUDER_SHOOT_INTERVAL_P3 = 0.8
MARAUDER_DIAGONAL_INTERVAL = 4.0
MARAUDER_BURST_INTERVAL = 6.0

# Marauder colors
MARAUDER_HULL_COLOR = (40, 45, 55)
MARAUDER_HULL_STROKE = (80, 200, 120)
MARAUDER_PLATE_COLOR = (30, 90, 50)
MARAUDER_PLATE_STROKE = (60, 160, 90)
MARAUDER_NOSE_COLOR = (60, 200, 90)
MARAUDER_PROJ_COLOR = (80, 220, 100)
MARAUDER_HIGHLIGHT_COLOR = (120, 255, 150)
MARAUDER_WEAPON_GLOW_COLOR = (80, 220, 100)

# Marauder core throb
MARAUDER_CORE_THROB_FREQ = 3.0
MARAUDER_CORE_INNER_COLOR = (180, 255, 190)
MARAUDER_CORE_MID_COLOR = (60, 220, 100)
MARAUDER_CORE_OUTER_COLOR = (20, 120, 50)
MARAUDER_CORE_BASE_W = 140
MARAUDER_CORE_BASE_H = 14

# Marauder exhaust (10 layers, outermost first)
MARAUDER_EXHAUST_LAYERS = (
    (18, 28, 10, 120, 255, 140, 20),
    (16, 24, 9, 100, 240, 130, 30),
    (14, 21, 8, 80, 220, 120, 45),
    (12, 18, 7, 60, 200, 110, 60),
    (10, 15, 6, 50, 180, 100, 80),
    (8, 13, 5, 40, 160, 90, 100),
    (7, 11, 4, 30, 140, 80, 120),
    (6, 9, 4, 25, 120, 70, 145),
    (5, 7, 3, 22, 100, 60, 165),
    (4, 5, 2, 20, 120, 40, 190),
)

# Marauder points
MARAUDER_POINTS = 7500
MARAUDER_NODAMAGE_BONUS = 3500

# Boss death
BOSS_DEATH_DURATION = 2.5
BOSS_DEATH_SMALL_EXPLOSION_INTERVAL = 0.08
BOSS_DEATH_FINAL_SHAKE_INTENSITY = 40.0
BOSS_DEATH_FINAL_SHAKE_DURATION = 1.5

# Boss explosion (final detonation)
BOSS_EXPLOSION_PARTICLE_COUNT = (180, 250)
BOSS_EXPLOSION_SPEED = (150, 800)
BOSS_EXPLOSION_LIFETIME = (0.8, 2.0)
BOSS_EXPLOSION_SIZE = (10, 28)

# Boss sub-explosion (staggered bursts during death sequence)
BOSS_SUB_EXPLOSION_COUNT = (25, 40)
BOSS_SUB_EXPLOSION_SPEED = (100, 400)
BOSS_SUB_EXPLOSION_LIFETIME = (0.3, 0.8)
BOSS_SUB_EXPLOSION_SIZE = (4, 14)

# Warning
WARNING_FLASH_COLOR = (255, 40, 20, 60)
WARNING_TEXT_COLOR = (255, 60, 40)

# Victory
VICTORY_DISPLAY_DURATION = 3.0
ZONE_TRANSITION_DURATION = 3.0  # seconds to show "ZONE X COMPLETE"

# === Zone System ===

ZONE_COUNT = 3

ZONE_CONFIGS = {
    1: {
        "name": "DEEP SPACE",
        "enemy_type": "batwing",
        "background_style": "deep_space",
        "waves_before_boss": 9,
        "wave_patterns": (
            (WAVE_TOP_Y, "straight"),
            (WAVE_BOTTOM_Y, "straight"),
            (WAVE_CENTER_Y, "sine"),
        ),
        "enemies_per_wave": ENEMIES_PER_WAVE,
        "enemy_speed": ENEMY_SPEED,
        "boss_type": "sentinel",
        "boss_points": SENTINEL_CORE_POINTS,
        "boss_nodamage_bonus": SENTINEL_NODAMAGE_BONUS,
        "powerup_after_wave": 2,
    },
    2: {
        "name": "NEBULA",
        "enemy_type": "dart",
        "background_style": "nebula",
        "waves_before_boss": 12,
        "wave_patterns": (
            (WAVE_TOP_Y, "straight"),
            (WAVE_BOTTOM_Y, "straight"),
            (WAVE_CENTER_Y, "sine"),
            (WAVE_CENTER_Y, "diagonal_cross"),
        ),
        "enemies_per_wave": 6,
        "enemy_speed": 180.0,
        "boss_type": "marauder",
        "boss_points": MARAUDER_POINTS,
        "boss_nodamage_bonus": MARAUDER_NODAMAGE_BONUS,
        "powerup_after_wave": 3,
    },
    3: {
        "name": "ASTEROID BELT",
        "enemy_type": "batwing",
        "background_style": "deep_space",
        "waves_before_boss": 15,
        "wave_patterns": (
            (WAVE_TOP_Y, "straight"),
            (WAVE_BOTTOM_Y, "straight"),
            (WAVE_CENTER_Y, "sine"),
        ),
        "enemies_per_wave": 7,
        "enemy_speed": 210.0,
        "boss_type": "sentinel",
        "boss_points": 10000,
        "boss_nodamage_bonus": 5000,
        "powerup_after_wave": 4,
    },
}
