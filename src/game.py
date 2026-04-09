import pygame
import config
from src.enums import Direction, GameState, FoodType, Theme, InputAction
from src.snake import Snake
from src.food import Food, BonusFood
from src.particle import ParticleSystem
from src.renderer import Renderer
from src.sound_manager import SoundManager
from src.input_handler import InputHandler


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()

        self.selected_theme = Theme.CLASSIC
        self.wraparound = False

        self.renderer = Renderer(self.screen, self.selected_theme)
        self.sound_manager = SoundManager()
        self.sound_manager.load()
        self.input_handler = InputHandler()
        self.particle_system = ParticleSystem()

        self.high_score = self._load_high_score()

        # Game objects — initialised in _new_game()
        self.snake: Snake | None = None
        self.food: Food | None = None
        self.bonus_food: BonusFood | None = None

        # State machine
        self.state = GameState.MENU
        self.score = 0
        self.level = 1
        self.move_counter = 0
        self.foods_eaten = 0
        self.move_interval_ms: float = config.BASE_MOVE_INTERVAL_MS
        self._move_accumulator: float = 0.0

        self.countdown_value = 3
        self._countdown_accumulator: float = 0.0

        self._themes = list(Theme)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self):
        running = True
        while running:
            dt_ms = self.clock.tick(config.FPS)

            for event in pygame.event.get():
                action = self._handle_event(event)
                if action == InputAction.QUIT:
                    running = False
                    break

            if not running:
                break

            self._update(dt_ms)
            self._render()
            pygame.display.flip()

        pygame.quit()

    # ------------------------------------------------------------------
    # Event dispatch
    # ------------------------------------------------------------------

    def _handle_event(self, event) -> "InputAction | None":
        if self.state == GameState.MENU:
            action = self.input_handler.process_menu_event(event)
            if action == InputAction.CONFIRM:
                self._start_new_game()
            elif action == InputAction.TOGGLE_WRAPAROUND:
                self.wraparound = not self.wraparound
            elif action == InputAction.TOGGLE_FPS:
                self.renderer.toggle_fps()
            elif action == InputAction.QUIT:
                return InputAction.QUIT
            # LEFT / RIGHT buffered in process_menu_event — consume here
            d = self.input_handler.flush_direction()
            if d == Direction.LEFT:
                idx = self._themes.index(self.selected_theme)
                self.selected_theme = self._themes[(idx - 1) % len(self._themes)]
                self.renderer.set_theme(self.selected_theme)
            elif d == Direction.RIGHT:
                idx = self._themes.index(self.selected_theme)
                self.selected_theme = self._themes[(idx + 1) % len(self._themes)]
                self.renderer.set_theme(self.selected_theme)

        elif self.state == GameState.COUNTDOWN:
            action = self.input_handler.process_event(event)
            if action == InputAction.QUIT:
                return InputAction.QUIT

        elif self.state == GameState.PLAYING:
            action = self.input_handler.process_event(event)
            if action == InputAction.QUIT:
                return InputAction.QUIT
            elif action == InputAction.PAUSE:
                self.state = GameState.PAUSED
            elif action == InputAction.TOGGLE_FPS:
                self.renderer.toggle_fps()

        elif self.state == GameState.PAUSED:
            action = self.input_handler.process_event(event)
            if action == InputAction.QUIT:
                return InputAction.QUIT
            elif action == InputAction.PAUSE:
                self.state = GameState.PLAYING
            elif action == InputAction.TOGGLE_FPS:
                self.renderer.toggle_fps()

        elif self.state == GameState.GAME_OVER:
            action = self.input_handler.process_event(event)
            if action == InputAction.QUIT:
                return InputAction.QUIT
            elif action in (InputAction.CONFIRM, InputAction.RESTART):
                self._start_new_game()
            elif action == InputAction.TOGGLE_FPS:
                self.renderer.toggle_fps()

        return None

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt_ms: float):
        if self.state == GameState.COUNTDOWN:
            self._update_countdown(dt_ms)
        elif self.state == GameState.PLAYING:
            self._update_playing(dt_ms)

    def _update_countdown(self, dt_ms: float):
        self._countdown_accumulator += dt_ms
        if self._countdown_accumulator >= config.COUNTDOWN_INTERVAL_MS:
            self._countdown_accumulator -= config.COUNTDOWN_INTERVAL_MS
            self.countdown_value -= 1
            if self.countdown_value < 0:
                self.state = GameState.PLAYING
                self._move_accumulator = 0.0

    def _update_playing(self, dt_ms: float):
        # Apply buffered direction input
        d = self.input_handler.flush_direction()
        if d is not None:
            self.snake.change_direction(d)

        # Accumulator-based move ticks (decoupled from render rate)
        self._move_accumulator += dt_ms
        while self._move_accumulator >= self.move_interval_ms:
            self._do_move()
            self._move_accumulator -= self.move_interval_ms
            if self.state != GameState.PLAYING:
                break

        self.particle_system.update(dt_ms)

    def _do_move(self):
        moved = self.snake.move(config.GRID_COLS, config.GRID_ROWS)
        self.move_counter += 1

        if not moved or self.snake.hits_self():
            self._trigger_game_over()
            return

        head = self.snake.head

        if head == self.food.position:
            self._eat_food(self.food)
        elif self.bonus_food is not None and head == self.bonus_food.position:
            self._eat_food(self.bonus_food)
            self.bonus_food = None
        elif self.bonus_food is not None and self.bonus_food.is_expired():
            self.bonus_food = None

    def _eat_food(self, food: "Food"):
        self.score += food.points
        self.snake.grow(1)
        self.foods_eaten += 1

        # Particle burst
        px, py = self.renderer.grid_to_pixel(*food.position)
        cx = px + config.GRID_SIZE // 2
        cy = py + config.GRID_SIZE // 2
        count = 20 if food.food_type == FoodType.BONUS else 12
        color = (
            self.renderer.colors["food_bonus"]
            if food.food_type == FoodType.BONUS
            else self.renderer.colors["particle"]
        )
        self.particle_system.emit(cx, cy, color, count, food.food_type)

        if food.food_type == FoodType.BONUS:
            self.sound_manager.play("eat_bonus")
        else:
            self.sound_manager.play("eat")
            occupied = set(self.snake.body)
            self.food.randomize(occupied, config.GRID_COLS, config.GRID_ROWS)
            # Spawn bonus food every N normal foods
            if (
                self.foods_eaten % config.BONUS_FOOD_SPAWN_INTERVAL == 0
                and self.bonus_food is None
            ):
                self.bonus_food = BonusFood()
                occupied.add(self.food.position)
                self.bonus_food.activate(occupied, config.GRID_COLS, config.GRID_ROWS)

        self._update_level()
        self._update_speed()

    def _update_level(self):
        self.level = self.score // config.LEVEL_UP_THRESHOLD + 1

    def _update_speed(self):
        self.move_interval_ms = max(
            config.MIN_MOVE_INTERVAL_MS,
            config.BASE_MOVE_INTERVAL_MS - (self.level - 1) * config.SPEED_DECREMENT_MS,
        )

    def _trigger_game_over(self):
        self.state = GameState.GAME_OVER
        self.sound_manager.play("game_over")
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    # ------------------------------------------------------------------
    # Game initialisation / reset
    # ------------------------------------------------------------------

    def _start_new_game(self):
        self._new_game()
        self.state = GameState.COUNTDOWN
        self.countdown_value = 3
        self._countdown_accumulator = 0.0

    def _new_game(self):
        start_col = config.GRID_COLS // 2
        start_row = config.GRID_ROWS // 2
        self.snake = Snake(start_col, start_row, length=3, wraparound=self.wraparound)

        self.food = Food()
        occupied = set(self.snake.body)
        self.food.randomize(occupied, config.GRID_COLS, config.GRID_ROWS)

        self.bonus_food = None
        self.score = 0
        self.level = 1
        self.move_counter = 0
        self.foods_eaten = 0
        self.move_interval_ms = config.BASE_MOVE_INTERVAL_MS
        self._move_accumulator = 0.0

        self.particle_system.clear()
        self.input_handler.clear()
        self.renderer.set_theme(self.selected_theme)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self):
        if self.state == GameState.MENU:
            self.renderer.draw_menu(self.selected_theme, self.wraparound)

        else:
            self.renderer.draw_grid()
            if self.snake:
                self.renderer.draw_snake(self.snake)
            if self.food:
                self.renderer.draw_food(self.food, self.bonus_food)
            self.renderer.draw_particles(self.particle_system)
            self.renderer.draw_hud(
                self.score,
                self.high_score,
                self.snake.length if self.snake else 0,
                self.move_counter,
                self.level,
            )

            if self.state == GameState.COUNTDOWN:
                self.renderer.draw_countdown(self.countdown_value)
            elif self.state == GameState.PAUSED:
                self.renderer.draw_pause()
            elif self.state == GameState.GAME_OVER:
                self.renderer.draw_game_over(self.score, self.high_score)

        if self.renderer.show_fps:
            self.renderer.draw_fps_counter(self.clock.get_fps())

    # ------------------------------------------------------------------
    # High-score persistence
    # ------------------------------------------------------------------

    def _load_high_score(self) -> int:
        try:
            with open(config.HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def _save_high_score(self):
        try:
            with open(config.HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except OSError:
            pass
