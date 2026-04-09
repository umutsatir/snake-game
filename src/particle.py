import pygame
import random
import math
from src.enums import FoodType

class Particle:
    def __init__(self, x: float, y: float, color: tuple, food_type: FoodType):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4) if food_type == FoodType.NORMAL else random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.lifetime_ms = random.randint(300, 600) if food_type == FoodType.NORMAL else random.randint(400, 800)
        self.age_ms = 0
        self.radius = random.randint(2, 5) if food_type == FoodType.BONUS else random.randint(2, 4)

    def update(self, dt: float):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # gravity
        self.age_ms += dt

    def is_dead(self) -> bool:
        return self.age_ms >= self.lifetime_ms

    @property
    def alpha(self) -> int:
        return max(0, int(255 * (1 - self.age_ms / self.lifetime_ms)))


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, pixel_x: int, pixel_y: int, color: tuple, count: int, food_type: FoodType):
        for _ in range(count):
            self.particles.append(Particle(pixel_x, pixel_y, color, food_type))

    def update(self, dt: float):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface: pygame.Surface):
        if not self.particles:
            return
        temp = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for p in self.particles:
            r, g, b = p.color
            pygame.draw.circle(temp, (r, g, b, p.alpha), (int(p.x), int(p.y)), p.radius)
        surface.blit(temp, (0, 0))

    def clear(self):
        self.particles.clear()
