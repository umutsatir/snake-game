from src.enums import Theme

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
    },
}
