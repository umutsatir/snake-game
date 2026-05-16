import random
import pygame
import config
from src.enums import Direction, GameState, FoodType, Theme, InputAction, Difficulty
from src.snake import Snake
from src.food import Food, BonusFood, InvincibilityFood, PoisonFood, SlowMotionFood, SpecialFood
from src.robot_snake import RobotSnake
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
        self.difficulty = Difficulty.NORMAL

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
        self.special_food: SpecialFood | None = None
        self.robot_snake: RobotSnake | None = None
        self.obstacles: set[tuple[int, int]] = set()

        # Active timed effects
        self.invincible = False
        self.invincibility_end_ms: float = 0.0
        self.slow_motion = False
        self.slow_motion_end_ms: float = 0.0

        # State machine
        self.state = GameState.MENU
        self.score = 0
        self.level = 1
        self.move_counter = 0
        self.foods_eaten = 0
        self.move_interval_ms: float = config.BASE_MOVE_INTERVAL_MS
        self.robot_move_interval_ms: float = config.DIFFICULTY_SETTINGS[Difficulty.NORMAL]["robot_move_interval_ms"]
        self._move_accumulator: float = 0.0
        self._robot_move_accumulator: float = 0.0

        self.countdown_value = 3
        self._countdown_accumulator: float = 0.0

        self._themes = list(Theme)
        self._difficulties = list(Difficulty)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _diff(self, key: str):
        return config.DIFFICULTY_SETTINGS[self.difficulty][key]

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

            d = self.input_handler.flush_direction()
            if d == Direction.LEFT:
                idx = self._themes.index(self.selected_theme)
                self.selected_theme = self._themes[(idx - 1) % len(self._themes)]
                self.renderer.set_theme(self.selected_theme)
            elif d == Direction.RIGHT:
                idx = self._themes.index(self.selected_theme)
                self.selected_theme = self._themes[(idx + 1) % len(self._themes)]
                self.renderer.set_theme(self.selected_theme)
            elif d == Direction.UP:
                idx = self._difficulties.index(self.difficulty)
                self.difficulty = self._difficulties[(idx - 1) % len(self._difficulties)]
            elif d == Direction.DOWN:
                idx = self._difficulties.index(self.difficulty)
                self.difficulty = self._difficulties[(idx + 1) % len(self._difficulties)]

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
        now = pygame.time.get_ticks()

        # Expire timed effects
        if self.invincible and now >= self.invincibility_end_ms:
            self.invincible = False
        if self.slow_motion and now >= self.slow_motion_end_ms:
            self.slow_motion = False

        slow = config.SLOW_MOTION_FACTOR if self.slow_motion else 1.0
        effective_player_ms = self.move_interval_ms * slow
        effective_robot_ms = self.robot_move_interval_ms * slow

        # Apply buffered direction
        d = self.input_handler.flush_direction()
        if d is not None:
            self.snake.change_direction(d)

        # Player moves
        self._move_accumulator += dt_ms
        while self._move_accumulator >= effective_player_ms:
            self._do_move()
            self._move_accumulator -= effective_player_ms
            if self.state != GameState.PLAYING:
                break

        # Robot snake
        if self.robot_snake is not None:
            if not self.robot_snake.active:
                self.robot_snake.update_respawn(dt_ms, self._occupied_set())
            else:
                self._robot_move_accumulator += dt_ms
                while self._robot_move_accumulator >= effective_robot_ms:
                    self._do_robot_move()
                    self._robot_move_accumulator -= effective_robot_ms

        self.particle_system.update(dt_ms)

    # ------------------------------------------------------------------
    # Per-tick logic
    # ------------------------------------------------------------------

    def _do_move(self):
        moved = self.snake.move(config.GRID_COLS, config.GRID_ROWS)
        self.move_counter += 1

        # Wall collision
        if not moved:
            if self.invincible:
                # Wrap manually so the snake keeps moving
                dx, dy = self.snake.direction.delta
                cur = self.snake.head
                wrapped = ((cur[0] + dx) % config.GRID_COLS, (cur[1] + dy) % config.GRID_ROWS)
                self.snake.body.appendleft(wrapped)
                if self.snake.pending_growth > 0:
                    self.snake.pending_growth -= 1
                else:
                    self.snake.body.pop()
            else:
                self._trigger_game_over()
                return

        # Self-collision
        if self.snake.hits_self() and not self.invincible:
            self._trigger_game_over()
            return

        head = self.snake.head

        # Obstacle collision
        if head in self.obstacles and not self.invincible:
            self._trigger_game_over()
            return

        # Robot snake collision
        if self.robot_snake and self.robot_snake.active and self.robot_snake.occupies(head):
            if self.invincible:
                self.robot_snake.disappear(config.ROBOT_SNAKE_RESPAWN_MS)
            else:
                self._trigger_game_over()
                return

        # Normal food
        if head == self.food.position:
            self._eat_food(self.food)

        # Bonus food
        if self.bonus_food is not None:
            if head == self.bonus_food.position:
                self._eat_food(self.bonus_food)
                self.bonus_food = None
            elif self.bonus_food.is_expired():
                self.bonus_food = None

        # Special food
        if self.special_food is not None:
            if head == self.special_food.position:
                self._eat_special_food(self.special_food)
                self.special_food = None
            elif self.special_food.is_expired():
                self.special_food = None

    def _do_robot_move(self):
        if self.robot_snake is None or not self.robot_snake.active:
            return
        self.robot_snake.move()
        # Robot head lands on player body → robot disappears
        if self.snake and self.robot_snake.active:
            if self.snake.occupies(self.robot_snake.head):
                self.robot_snake.disappear(config.ROBOT_SNAKE_RESPAWN_MS)

    # ------------------------------------------------------------------
    # Food handling
    # ------------------------------------------------------------------

    def _eat_food(self, food: "Food"):
        self.score += food.points
        self.snake.grow(1)
        self.foods_eaten += 1

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
            occupied = self._occupied_set()
            self.food.randomize(occupied, config.GRID_COLS, config.GRID_ROWS)

            if (
                self.foods_eaten % config.BONUS_FOOD_SPAWN_INTERVAL == 0
                and self.bonus_food is None
            ):
                self.bonus_food = BonusFood()
                occupied.add(self.food.position)
                self.bonus_food.activate(occupied, config.GRID_COLS, config.GRID_ROWS)

            if self.special_food is None and random.random() < self._diff("special_food_chance"):
                self._spawn_special_food()

        self._update_level()
        self._update_speed()
        self._sync_obstacles()

    def _eat_special_food(self, food: "SpecialFood"):
        px, py = self.renderer.grid_to_pixel(*food.position)
        cx = px + config.GRID_SIZE // 2
        cy = py + config.GRID_SIZE // 2
        now = pygame.time.get_ticks()

        if food.food_type == FoodType.INVINCIBILITY:
            self.invincible = True
            self.invincibility_end_ms = now + config.INVINCIBILITY_DURATION_MS
            color = self.renderer.colors["food_invincibility"]
            self.particle_system.emit(cx, cy, color, 24, FoodType.BONUS)
            self.sound_manager.play("eat_invincibility")

        elif food.food_type == FoodType.POISON:
            remove = min(config.POISON_SEGMENT_LOSS, len(self.snake.body) - 1)
            for _ in range(remove):
                self.snake.body.pop()
            self.score = max(0, self.score - config.POISON_SCORE_PENALTY)
            color = self.renderer.colors["food_poison"]
            self.particle_system.emit(cx, cy, color, 16, FoodType.NORMAL)
            self.sound_manager.play("eat_poison")

        elif food.food_type == FoodType.SLOW_MOTION:
            self.slow_motion = True
            self.slow_motion_end_ms = now + config.SLOW_MOTION_DURATION_MS
            color = self.renderer.colors["food_slow_motion"]
            self.particle_system.emit(cx, cy, color, 16, FoodType.NORMAL)
            self.sound_manager.play("eat_slow_motion")

    def _spawn_special_food(self):
        cls = random.choice([InvincibilityFood, PoisonFood, SlowMotionFood])
        sf = cls()
        sf.activate(self._occupied_set(), config.GRID_COLS, config.GRID_ROWS)
        self.special_food = sf

    # ------------------------------------------------------------------
    # Level / speed / obstacle progression
    # ------------------------------------------------------------------

    def _update_level(self):
        self.level = self.score // config.LEVEL_UP_THRESHOLD + 1

    def _update_speed(self):
        base = self._diff("base_move_interval_ms")
        min_ms = self._diff("min_move_interval_ms")
        decrement = self._diff("speed_decrement_ms")
        self.move_interval_ms = max(min_ms, base - (self.level - 1) * decrement)

    def _sync_obstacles(self):
        """Add obstacle walls as the player levels up (per-difficulty thresholds)."""
        level_map = config.OBSTACLE_LEVELS.get(self.difficulty, {})
        target = 0
        for min_lvl, count in sorted(level_map.items()):
            if self.level >= min_lvl:
                target = count

        if len(self.obstacles) >= target:
            return

        occupied = self._occupied_set()
        free = [(c, r) for c in range(config.GRID_COLS) for r in range(config.GRID_ROWS)
                if (c, r) not in occupied]
        random.shuffle(free)
        for cell in free[:target - len(self.obstacles)]:
            self.obstacles.add(cell)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _occupied_set(self) -> set:
        occupied: set = set(self.snake.body)
        if self.food:
            occupied.add(self.food.position)
        if self.bonus_food and not self.bonus_food.is_expired():
            occupied.add(self.bonus_food.position)
        if self.special_food and not self.special_food.is_expired():
            occupied.add(self.special_food.position)
        if self.robot_snake and self.robot_snake.active:
            occupied |= set(self.robot_snake.body)
        occupied |= self.obstacles
        return occupied

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
        occupied: set = set(self.snake.body)
        self.food.randomize(occupied, config.GRID_COLS, config.GRID_ROWS)

        self.bonus_food = None
        self.special_food = None
        self.obstacles = set()

        if self._diff("robot_enabled"):
            self.robot_snake = RobotSnake(config.GRID_COLS, config.GRID_ROWS, self.wraparound)
            occupied.add(self.food.position)
            self.robot_snake.spawn(occupied)
        else:
            self.robot_snake = None

        self.robot_move_interval_ms = self._diff("robot_move_interval_ms")

        self.invincible = False
        self.invincibility_end_ms = 0.0
        self.slow_motion = False
        self.slow_motion_end_ms = 0.0

        self.score = 0
        self.level = 1
        self.move_counter = 0
        self.foods_eaten = 0
        self.move_interval_ms = self._diff("base_move_interval_ms")
        self._move_accumulator = 0.0
        self._robot_move_accumulator = 0.0

        self.particle_system.clear()
        self.input_handler.clear()
        self.renderer.set_theme(self.selected_theme)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render(self):
        now = pygame.time.get_ticks()

        if self.state == GameState.MENU:
            self.renderer.draw_menu(self.selected_theme, self.wraparound, self.difficulty)
        else:
            self.renderer.draw_grid(self.obstacles)
            if self.robot_snake:
                self.renderer.draw_robot_snake(self.robot_snake)
            if self.snake:
                self.renderer.draw_snake(self.snake, self.invincible, now)
            if self.food:
                self.renderer.draw_food(self.food, self.bonus_food, self.special_food)
            self.renderer.draw_particles(self.particle_system)
            self.renderer.draw_hud(
                score=self.score,
                high_score=self.high_score,
                length=self.snake.length if self.snake else 0,
                moves=self.move_counter,
                level=self.level,
                difficulty=self.difficulty,
                invincible=self.invincible,
                invincibility_end_ms=self.invincibility_end_ms,
                slow_motion=self.slow_motion,
                slow_motion_end_ms=self.slow_motion_end_ms,
                now=now,
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
