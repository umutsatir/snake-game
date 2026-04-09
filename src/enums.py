from enum import Enum

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def delta(self):
        return self.value

    @property
    def opposite(self):
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]

class GameState(Enum):
    MENU = "menu"
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class FoodType(Enum):
    NORMAL = "normal"
    BONUS = "bonus"

class Theme(Enum):
    CLASSIC = "classic"
    NEON = "neon"
    DESERT = "desert"
    OCEAN = "ocean"

class InputAction(Enum):
    QUIT = "quit"
    PAUSE = "pause"
    RESTART = "restart"
    CONFIRM = "confirm"
    TOGGLE_FPS = "toggle_fps"
    TOGGLE_WRAPAROUND = "toggle_wraparound"
