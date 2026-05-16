import pygame
import config
from src.enums import Theme, FoodType, GameState, Difficulty
from src.snake import Snake
from src.food import Food, BonusFood, SpecialFood
from src.robot_snake import RobotSnake
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

    # ------------------------------------------------------------------
    # Grid + obstacles
    # ------------------------------------------------------------------

    def draw_grid(self, obstacles: "set[tuple[int,int]] | None" = None):
        self.screen.fill(self.colors["background"])
        pygame.draw.rect(self.screen, self.colors["hud"], (0, 0, config.SCREEN_WIDTH, config.HUD_HEIGHT))

        grid_color = self.colors["grid"]
        for col in range(config.GRID_COLS + 1):
            x = col * config.GRID_SIZE
            pygame.draw.line(self.screen, grid_color, (x, config.HUD_HEIGHT), (x, config.SCREEN_HEIGHT))
        for row in range(config.GRID_ROWS + 1):
            y = config.HUD_HEIGHT + row * config.GRID_SIZE
            pygame.draw.line(self.screen, grid_color, (0, y), (config.SCREEN_WIDTH, y))

        if obstacles:
            ob_color = self.colors["obstacle"]
            for col, row in obstacles:
                px, py = self.grid_to_pixel(col, row)
                rect = pygame.Rect(px, py, config.GRID_SIZE, config.GRID_SIZE)
                pygame.draw.rect(self.screen, ob_color, rect)
                # Cross-hatch lines for visual distinction
                pygame.draw.line(self.screen, grid_color, (px, py), (px + config.GRID_SIZE, py + config.GRID_SIZE))
                pygame.draw.line(self.screen, grid_color, (px + config.GRID_SIZE, py), (px, py + config.GRID_SIZE))

    # ------------------------------------------------------------------
    # Snakes
    # ------------------------------------------------------------------

    def draw_snake(self, snake: Snake, invincible: bool = False, now: int = 0):
        pulse = invincible and (now // 150) % 2 == 0
        inv_color = self.colors.get("food_invincibility", (0, 200, 255))
        for i, (col, row) in enumerate(snake.body):
            px, py = self.grid_to_pixel(col, row)
            color = self.colors["snake_head"] if i == 0 else self.colors["snake_body"]
            rect = pygame.Rect(px + 1, py + 1, config.GRID_SIZE - 2, config.GRID_SIZE - 2)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            if pulse:
                pygame.draw.rect(self.screen, inv_color, rect, width=2, border_radius=4)

    def draw_robot_snake(self, robot: RobotSnake):
        if not robot.active:
            return
        for i, (col, row) in enumerate(robot.body):
            px, py = self.grid_to_pixel(col, row)
            color = self.colors["robot_head"] if i == 0 else self.colors["robot_body"]
            rect = pygame.Rect(px + 3, py + 3, config.GRID_SIZE - 6, config.GRID_SIZE - 6)
            pygame.draw.rect(self.screen, color, rect, border_radius=3)

    # ------------------------------------------------------------------
    # Food
    # ------------------------------------------------------------------

    def draw_food(self, food: Food, bonus_food: "BonusFood | None", special_food: "SpecialFood | None" = None):
        # Normal food — filled circle
        px, py = self.grid_to_pixel(*food.position)
        center = (px + config.GRID_SIZE // 2, py + config.GRID_SIZE // 2)
        pygame.draw.circle(self.screen, self.colors["food_normal"], center, config.GRID_SIZE // 2 - 3)

        # Bonus food — circle + inner white circle (blinks when expiring)
        if bonus_food is not None and not bonus_food.is_expired():
            remaining = bonus_food.time_remaining_ms()
            visible = True
            if remaining < 2000:
                visible = (remaining // 300) % 2 == 0
            if visible:
                bpx, bpy = self.grid_to_pixel(*bonus_food.position)
                bcenter = (bpx + config.GRID_SIZE // 2, bpy + config.GRID_SIZE // 2)
                pygame.draw.circle(self.screen, self.colors["food_bonus"], bcenter, config.GRID_SIZE // 2 - 2)
                pygame.draw.circle(self.screen, (255, 255, 255), bcenter, config.GRID_SIZE // 2 - 6)

        # Special food — distinct shapes, blink when expiring
        if special_food is not None and not special_food.is_expired():
            remaining = special_food.time_remaining_ms()
            visible = remaining >= 2000 or (remaining // 300) % 2 == 0
            if visible:
                self._draw_special_food(special_food)

    def _draw_special_food(self, sf: "SpecialFood"):
        spx, spy = self.grid_to_pixel(*sf.position)
        cx = spx + config.GRID_SIZE // 2
        cy = spy + config.GRID_SIZE // 2
        r = config.GRID_SIZE // 2 - 3

        if sf.food_type == FoodType.INVINCIBILITY:
            # Cyan filled circle + small white core
            color = self.colors["food_invincibility"]
            pygame.draw.circle(self.screen, color, (cx, cy), r)
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r - 5)

        elif sf.food_type == FoodType.POISON:
            # Purple filled square with white inner square
            color = self.colors["food_poison"]
            pygame.draw.rect(self.screen, color,
                             pygame.Rect(spx + 2, spy + 2, config.GRID_SIZE - 4, config.GRID_SIZE - 4),
                             border_radius=5)
            inner = 8
            pygame.draw.rect(self.screen, (255, 255, 255),
                             pygame.Rect(spx + inner, spy + inner,
                                         config.GRID_SIZE - inner * 2, config.GRID_SIZE - inner * 2),
                             border_radius=3)

        elif sf.food_type == FoodType.SLOW_MOTION:
            # Light-blue diamond
            color = self.colors["food_slow_motion"]
            points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(self.screen, color, points)
            inner_r = r - 5
            inner_pts = [(cx, cy - inner_r), (cx + inner_r, cy), (cx, cy + inner_r), (cx - inner_r, cy)]
            pygame.draw.polygon(self.screen, (255, 255, 255), inner_pts)

    # ------------------------------------------------------------------
    # Particles
    # ------------------------------------------------------------------

    def draw_particles(self, ps: ParticleSystem):
        ps.draw(self.screen)

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def draw_hud(
        self,
        score: int,
        high_score: int,
        length: int,
        moves: int,
        level: int,
        difficulty: Difficulty,
        invincible: bool = False,
        invincibility_end_ms: float = 0.0,
        slow_motion: bool = False,
        slow_motion_end_ms: float = 0.0,
        now: int = 0,
    ):
        padding = 12

        # Column 1 — score/best
        self.screen.blit(
            self.font_small.render(f"SCORE: {score}", True, self.colors["text"]),
            (padding, 8),
        )
        self.screen.blit(
            self.font_small.render(f"BEST: {high_score}", True, self.colors["text"]),
            (padding, 28),
        )

        # Column 2 — level / length
        self.screen.blit(
            self.font_small.render(f"LVL: {level}", True, self.colors["text"]),
            (170, 8),
        )
        self.screen.blit(
            self.font_small.render(f"LEN: {length}", True, self.colors["text"]),
            (170, 28),
        )

        # Column 3 — difficulty / moves
        diff_color = self._diff_color(difficulty)
        self.screen.blit(
            self.font_small.render(f"DIFF: {difficulty.value.upper()}", True, diff_color),
            (290, 8),
        )
        self.screen.blit(
            self.font_small.render(f"MOVES: {moves}", True, self.colors["text"]),
            (290, 28),
        )

        # Column 4 — active effects
        effect_x = 450
        if invincible:
            secs = max(0, int((invincibility_end_ms - now) / 1000) + 1)
            inv_color = self.colors.get("food_invincibility", (0, 200, 255))
            self.screen.blit(
                self.font_small.render(f"INVINC {secs}s", True, inv_color),
                (effect_x, 8),
            )
        if slow_motion:
            secs = max(0, int((slow_motion_end_ms - now) / 1000) + 1)
            sm_color = self.colors.get("food_slow_motion", (180, 220, 255))
            self.screen.blit(
                self.font_small.render(f"SLOW {secs}s", True, sm_color),
                (effect_x, 28),
            )

        # Title — right-aligned
        title_surf = self.font_medium.render("SNAKE", True, self.colors["snake_head"])
        title_rect = title_surf.get_rect(right=config.SCREEN_WIDTH - padding, centery=config.HUD_HEIGHT // 2)
        self.screen.blit(title_surf, title_rect)

    def _diff_color(self, difficulty: Difficulty) -> tuple:
        mapping = {
            Difficulty.EASY: (100, 220, 100),
            Difficulty.NORMAL: self.colors["food_bonus"],
            Difficulty.HARD: (220, 60, 60),
        }
        return mapping.get(difficulty, self.colors["text"])

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def draw_menu(self, selected_theme: "Theme", wraparound: bool, difficulty: "Difficulty"):
        self.screen.fill(self.colors["background"])

        # Title
        title = self.font_large.render("SNAKE", True, self.colors["snake_head"])
        self.screen.blit(title, title.get_rect(center=(config.SCREEN_WIDTH // 2, 95)))

        subtitle = self.font_small.render("A retro classic", True, self.colors["text"])
        self.screen.blit(subtitle, subtitle.get_rect(center=(config.SCREEN_WIDTH // 2, 148)))

        # Theme selector
        theme_label = self.font_small.render("THEME:  LEFT / RIGHT  to cycle", True, self.colors["text"])
        self.screen.blit(theme_label, theme_label.get_rect(center=(config.SCREEN_WIDTH // 2, 210)))

        from src.enums import Theme as T
        themes = list(T)
        selected_idx = themes.index(selected_theme)
        for i, t in enumerate(themes):
            x_center = config.SCREEN_WIDTH // 2 + (i - len(themes) // 2) * 150 + 75
            color = self.colors["food_bonus"] if i == selected_idx else self.colors["text"]
            surf = self.font_small.render(t.value.upper(), True, color)
            rect = surf.get_rect(center=(x_center, 245))
            self.screen.blit(surf, rect)
            if i == selected_idx:
                pygame.draw.rect(self.screen, color, rect.inflate(8, 4), 1)

        # Difficulty selector
        diff_label = self.font_small.render("DIFFICULTY:  UP / DOWN  to cycle", True, self.colors["text"])
        self.screen.blit(diff_label, diff_label.get_rect(center=(config.SCREEN_WIDTH // 2, 295)))

        difficulties = list(Difficulty)
        sel_diff_idx = difficulties.index(difficulty)
        for i, d in enumerate(difficulties):
            x_center = config.SCREEN_WIDTH // 2 + (i - len(difficulties) // 2) * 180 + 90
            color = self._diff_color(d) if i == sel_diff_idx else self.colors["text"]
            surf = self.font_small.render(d.value.upper(), True, color)
            rect = surf.get_rect(center=(x_center, 330))
            self.screen.blit(surf, rect)
            if i == sel_diff_idx:
                pygame.draw.rect(self.screen, color, rect.inflate(8, 4), 1)

        # Wraparound toggle
        wrap_color = self.colors["food_bonus"] if wraparound else self.colors["text"]
        wrap_surf = self.font_small.render(
            f"WRAPAROUND: {'ON' if wraparound else 'OFF'}  (W to toggle)", True, wrap_color
        )
        self.screen.blit(wrap_surf, wrap_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 375)))

        # Controls
        controls = [
            "ARROW KEYS  — Move snake",
            "P / ESC     — Pause",
            "F           — Toggle FPS counter",
            "Q           — Quit",
        ]
        for i, line in enumerate(controls):
            surf = self.font_small.render(line, True, self.colors["text"])
            self.screen.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH // 2, 430 + i * 26)))

        start_surf = self.font_medium.render("PRESS ENTER TO START", True, self.colors["food_bonus"])
        self.screen.blit(start_surf, start_surf.get_rect(center=(config.SCREEN_WIDTH // 2, 560)))

    # ------------------------------------------------------------------
    # Overlays
    # ------------------------------------------------------------------

    def draw_countdown(self, value: int):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        text = str(value) if value > 0 else "GO!"
        surf = self.font_large.render(text, True, self.colors["food_bonus"])
        self.screen.blit(surf, surf.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)))

    def draw_pause(self):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        paused = self.font_large.render("PAUSED", True, self.colors["text"])
        self.screen.blit(paused, paused.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 30)))

        resume = self.font_small.render("Press P or ESC to resume", True, self.colors["text"])
        self.screen.blit(resume, resume.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 30)))

    def draw_game_over(self, score: int, high_score: int):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        go = self.font_large.render("GAME OVER", True, (220, 50, 50))
        self.screen.blit(go, go.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 80)))

        sc = self.font_medium.render(f"Score: {score}", True, self.colors["text"])
        self.screen.blit(sc, sc.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)))

        hs_text = f"Best: {high_score}"
        if score >= high_score and score > 0:
            hs_text += "  NEW RECORD!"
        hs = self.font_medium.render(hs_text, True, self.colors["food_bonus"])
        self.screen.blit(hs, hs.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 50)))

        restart = self.font_small.render("Press ENTER or R to restart   Q to quit", True, self.colors["text"])
        self.screen.blit(restart, restart.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 110)))

    def draw_fps_counter(self, fps: float):
        surf = self.font_small.render(f"FPS: {fps:.0f}", True, self.colors["text"])
        rect = surf.get_rect(topright=(config.SCREEN_WIDTH - 4, config.SCREEN_HEIGHT - 22))
        self.screen.blit(surf, rect)
