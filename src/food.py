import random
import pygame
from src.enums import FoodType
import config

class Food:
    def __init__(self):
        self.position: tuple[int, int] = (0, 0)
        self.food_type = FoodType.NORMAL
        self.points = config.NORMAL_FOOD_SCORE

    def randomize(self, occupied_set: set, cols: int, rows: int):
        all_cells = {(c, r) for c in range(cols) for r in range(rows)}
        available = list(all_cells - occupied_set)
        if available:
            self.position = random.choice(available)

    def is_expired(self) -> bool:
        return False


class BonusFood(Food):
    def __init__(self):
        super().__init__()
        self.food_type = FoodType.BONUS
        self.points = config.BONUS_FOOD_SCORE
        self.spawn_time: int = 0
        self.duration_ms: int = config.BONUS_FOOD_DURATION_MS

    def activate(self, occupied_set: set, cols: int, rows: int):
        self.spawn_time = pygame.time.get_ticks()
        self.randomize(occupied_set, cols, rows)

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > self.duration_ms

    def time_remaining_ms(self) -> int:
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0, self.duration_ms - elapsed)
