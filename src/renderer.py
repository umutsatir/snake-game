import pygame
import config
from src.enums import Theme, FoodType, GameState
from src.snake import Snake
from src.food import Food, BonusFood
from src.particle import ParticleSystem

class Renderer:
    def __init__(self, screen: pygame.Surface, theme: Theme):
        self.screen = screen
        self.show_fps = False
        self.theme = theme
        self.colors = config.THEMES[theme]

        pygame.font.init()
        self.font_large = pygame.font.SysFont("monospace", 48, bold=True)
        self.font_medium = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 18)

    def set_theme(self, theme: Theme):
        self.theme = theme
        self.colors = config.THEMES[theme]

    def toggle_fps(self):
        self.show_fps = not self.show_fps

    def grid_to_pixel(self, col: int, row: int) -> tuple[int, int]:
        return (col * config.GRID_SIZE, config.HUD_HEIGHT + row * config.GRID_SIZE)

    def draw_grid(self):
        self.screen.fill(self.colors["background"])
        # HUD background
        pygame.draw.rect(self.screen, self.colors["hud"], (0, 0, config.SCREEN_WIDTH, config.HUD_HEIGHT))
        # Grid lines
        grid_color = self.colors["grid"]
        for col in range(config.GRID_COLS + 1):
            x = col * config.GRID_SIZE
            pygame.draw.line(self.screen, grid_color, (x, config.HUD_HEIGHT), (x, config.SCREEN_HEIGHT))
        for row in range(config.GRID_ROWS + 1):
            y = config.HUD_HEIGHT + row * config.GRID_SIZE
            pygame.draw.line(self.screen, grid_color, (0, y), (config.SCREEN_WIDTH, y))

    def draw_snake(self, snake: Snake):
        for i, (col, row) in enumerate(snake.body):
            px, py = self.grid_to_pixel(col, row)
            color = self.colors["snake_head"] if i == 0 else self.colors["snake_body"]
            rect = pygame.Rect(px + 1, py + 1, config.GRID_SIZE - 2, config.GRID_SIZE - 2)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)

    def draw_food(self, food: Food, bonus_food: 'BonusFood | None'):
        # Normal food
        px, py = self.grid_to_pixel(*food.position)
        center = (px + config.GRID_SIZE // 2, py + config.GRID_SIZE // 2)
        pygame.draw.circle(self.screen, self.colors["food_normal"], center, config.GRID_SIZE // 2 - 3)

        # Bonus food
        if bonus_food is not None and not bonus_food.is_expired():
            remaining = bonus_food.time_remaining_ms()
            # Blink when < 2000ms remaining
            visible = True
            if remaining < 2000:
                visible = (remaining // 300) % 2 == 0
            if visible:
                bpx, bpy = self.grid_to_pixel(*bonus_food.position)
                bcenter = (bpx + config.GRID_SIZE // 2, bpy + config.GRID_SIZE // 2)
                pygame.draw.circle(self.screen, self.colors["food_bonus"], bcenter, config.GRID_SIZE // 2 - 2)
                # Star-like decoration
                pygame.draw.circle(self.screen, (255, 255, 255), bcenter, config.GRID_SIZE // 2 - 6)

    def draw_particles(self, ps: ParticleSystem):
        ps.draw(self.screen)

    def draw_hud(self, score: int, high_score: int, length: int, moves: int, level: int):
        padding = 12
        # Score
        score_surf = self.font_small.render(f"SCORE: {score}", True, self.colors["text"])
        self.screen.blit(score_surf, (padding, 8))

        # High score
        hs_surf = self.font_small.render(f"BEST: {high_score}", True, self.colors["text"])
        self.screen.blit(hs_surf, (padding, 28))

        # Level
        lvl_surf = self.font_small.render(f"LVL: {level}", True, self.colors["text"])
        self.screen.blit(lvl_surf, (200, 8))

        # Length
        len_surf = self.font_small.render(f"LEN: {length}", True, self.colors["text"])
        self.screen.blit(len_surf, (200, 28))

        # Moves
        mv_surf = self.font_small.render(f"MOVES: {moves}", True, self.colors["text"])
        self.screen.blit(mv_surf, (350, 18))

        # Title
        title_surf = self.font_medium.render("SNAKE", True, self.colors["snake_head"])
        title_rect = title_surf.get_rect(right=config.SCREEN_WIDTH - padding, centery=config.HUD_HEIGHT // 2)
        self.screen.blit(title_surf, title_rect)

    def draw_menu(self, selected_theme: 'Theme', wraparound: bool):
        self.screen.fill(self.colors["background"])

        title = self.font_large.render("SNAKE", True, self.colors["snake_head"])
        title_rect = title.get_rect(center=(config.SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        subtitle = self.font_small.render("A retro classic", True, self.colors["text"])
        sub_rect = subtitle.get_rect(center=(config.SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle, sub_rect)

        # Theme selector
        theme_label = self.font_small.render("THEME: (LEFT/RIGHT to change)", True, self.colors["text"])
        tl_rect = theme_label.get_rect(center=(config.SCREEN_WIDTH // 2, 260))
        self.screen.blit(theme_label, tl_rect)

        from src.enums import Theme as T
        themes = list(T)
        theme_names = [t.value.upper() for t in themes]
        selected_idx = themes.index(selected_theme)

        for i, (t, name) in enumerate(zip(themes, theme_names)):
            x = config.SCREEN_WIDTH // 2 + (i - len(themes) // 2) * 150
            color = self.colors["food_bonus"] if i == selected_idx else self.colors["text"]
            surf = self.font_small.render(name, True, color)
            rect = surf.get_rect(center=(x + 75, 300))
            self.screen.blit(surf, rect)
            if i == selected_idx:
                pygame.draw.rect(self.screen, color, rect.inflate(8, 4), 1)

        # Wraparound toggle
        wrap_color = self.colors["food_bonus"] if wraparound else self.colors["text"]
        wrap_text = f"WRAPAROUND: {'ON' if wraparound else 'OFF'}  (W to toggle)"
        wrap_surf = self.font_small.render(wrap_text, True, wrap_color)
        wrap_rect = wrap_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 360))
        self.screen.blit(wrap_surf, wrap_rect)

        # Controls
        controls = [
            "ARROW KEYS — Move",
            "P / ESC   — Pause",
            "F         — Toggle FPS",
            "Q         — Quit",
        ]
        for i, line in enumerate(controls):
            surf = self.font_small.render(line, True, self.colors["text"])
            rect = surf.get_rect(center=(config.SCREEN_WIDTH // 2, 440 + i * 28))
            self.screen.blit(surf, rect)

        start_surf = self.font_medium.render("PRESS ENTER TO START", True, self.colors["food_bonus"])
        start_rect = start_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 570))
        self.screen.blit(start_surf, start_rect)

    def draw_countdown(self, value: int):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        text = str(value) if value > 0 else "GO!"
        surf = self.font_large.render(text, True, self.colors["food_bonus"])
        rect = surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.screen.blit(surf, rect)

    def draw_pause(self):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        paused = self.font_large.render("PAUSED", True, self.colors["text"])
        rect = paused.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(paused, rect)

        resume = self.font_small.render("Press P or ESC to resume", True, self.colors["text"])
        rr = resume.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(resume, rr)

    def draw_game_over(self, score: int, high_score: int):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        go = self.font_large.render("GAME OVER", True, (220, 50, 50))
        go_rect = go.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(go, go_rect)

        sc = self.font_medium.render(f"Score: {score}", True, self.colors["text"])
        sc_rect = sc.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.screen.blit(sc, sc_rect)

        hs_text = f"Best: {high_score}"
        if score >= high_score and score > 0:
            hs_text += "  NEW RECORD!"
        hs = self.font_medium.render(hs_text, True, self.colors["food_bonus"])
        hs_rect = hs.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hs, hs_rect)

        restart = self.font_small.render("Press ENTER or R to restart   Q to quit", True, self.colors["text"])
        rr = restart.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 110))
        self.screen.blit(restart, rr)

    def draw_fps_counter(self, fps: float):
        surf = self.font_small.render(f"FPS: {fps:.0f}", True, self.colors["text"])
        rect = surf.get_rect(topright=(config.SCREEN_WIDTH - 4, config.SCREEN_HEIGHT - 22))
        self.screen.blit(surf, rect)
