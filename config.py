from src.enums import Theme, Difficulty

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
GRID_SIZE = 32
GRID_COLS = 20
GRID_ROWS = 18
HUD_HEIGHT = 64

FPS = 60
BASE_MOVE_INTERVAL_MS = 200
MIN_MOVE_INTERVAL_MS = 60
SPEED_DECREMENT_MS = 10
COUNTDOWN_INTERVAL_MS = 800
BONUS_FOOD_DURATION_MS = 8000
BONUS_FOOD_SPAWN_INTERVAL = 5

NORMAL_FOOD_SCORE = 10
BONUS_FOOD_SCORE = 50
LEVEL_UP_THRESHOLD = 50

HIGHSCORE_FILE = "highscore.txt"
SOUND_DIR = "assets/sounds"

# Robot snake
ROBOT_SNAKE_LENGTH = 5
ROBOT_SNAKE_RESPAWN_MS = 30000

# Special food
SPECIAL_FOOD_DURATION_MS = 6000
INVINCIBILITY_DURATION_MS = 5000
SLOW_MOTION_DURATION_MS = 5000
SLOW_MOTION_FACTOR = 2.0      # multiply move interval (half speed)
POISON_SEGMENT_LOSS = 3
POISON_SCORE_PENALTY = 30

# Per-difficulty settings
DIFFICULTY_SETTINGS = {
    Difficulty.EASY: {
        "base_move_interval_ms": 250,
        "min_move_interval_ms": 100,
        "speed_decrement_ms": 8,
        "robot_enabled": False,
        "robot_move_interval_ms": 300,
        "special_food_chance": 0.15,
    },
    Difficulty.NORMAL: {
        "base_move_interval_ms": 200,
        "min_move_interval_ms": 60,
        "speed_decrement_ms": 10,
        "robot_enabled": True,
        "robot_move_interval_ms": 250,
        "special_food_chance": 0.15,
    },
    Difficulty.HARD: {
        "base_move_interval_ms": 150,
        "min_move_interval_ms": 40,
        "speed_decrement_ms": 12,
        "robot_enabled": True,
        "robot_move_interval_ms": 180,
        "special_food_chance": 0.20,
    },
}

# Obstacle walls: {difficulty: {min_level: wall_count}}
OBSTACLE_LEVELS = {
    Difficulty.EASY: {},
    Difficulty.NORMAL: {3: 4, 6: 8},
    Difficulty.HARD: {2: 4, 4: 8, 6: 12},
}

THEMES = {
    Theme.CLASSIC: {
        "background": (0, 0, 0),
        "grid": (20, 20, 20),
        "snake_head": (0, 220, 0),
        "snake_body": (0, 160, 0),
        "food_normal": (220, 50, 50),
        "food_bonus": (255, 215, 0),
        "text": (255, 255, 255),
        "hud": (30, 30, 30),
        "particle": (255, 200, 0),
        "robot_head": (210, 105, 30),
        "robot_body": (160, 75, 20),
        "food_invincibility": (0, 200, 255),
        "food_poison": (160, 0, 210),
        "food_slow_motion": (180, 220, 255),
        "obstacle": (100, 80, 60),
    },
    Theme.NEON: {
        "background": (10, 0, 20),
        "grid": (25, 5, 40),
        "snake_head": (0, 255, 180),
        "snake_body": (0, 180, 130),
        "food_normal": (255, 50, 150),
        "food_bonus": (255, 255, 0),
        "text": (200, 200, 255),
        "hud": (20, 0, 40),
        "particle": (0, 255, 255),
        "robot_head": (255, 100, 50),
        "robot_body": (200, 60, 20),
        "food_invincibility": (0, 220, 255),
        "food_poison": (210, 0, 255),
        "food_slow_motion": (200, 240, 255),
        "obstacle": (80, 0, 120),
    },
    Theme.DESERT: {
        "background": (50, 30, 10),
        "grid": (65, 45, 20),
        "snake_head": (180, 220, 80),
        "snake_body": (140, 170, 60),
        "food_normal": (220, 100, 30),
        "food_bonus": (255, 220, 50),
        "text": (240, 220, 180),
        "hud": (70, 50, 20),
        "particle": (255, 180, 50),
        "robot_head": (185, 85, 20),
        "robot_body": (145, 65, 15),
        "food_invincibility": (0, 190, 220),
        "food_poison": (145, 0, 185),
        "food_slow_motion": (200, 230, 255),
        "obstacle": (110, 75, 35),
    },
    Theme.OCEAN: {
        "background": (0, 20, 50),
        "grid": (0, 30, 65),
        "snake_head": (0, 200, 220),
        "snake_body": (0, 150, 180),
        "food_normal": (220, 80, 80),
        "food_bonus": (255, 200, 0),
        "text": (180, 230, 255),
        "hud": (0, 10, 40),
        "particle": (100, 220, 255),
        "robot_head": (220, 120, 0),
        "robot_body": (170, 90, 0),
        "food_invincibility": (0, 230, 255),
        "food_poison": (175, 0, 225),
        "food_slow_motion": (210, 240, 255),
        "obstacle": (0, 60, 100),
    },
}
