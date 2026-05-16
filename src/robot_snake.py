import random
from collections import deque
from src.enums import Direction

_ALL_DIRECTIONS = list(Direction)


class RobotSnake:
    """AI-controlled snake that wanders randomly, respawns after collisions."""

    INITIAL_LENGTH = 5

    def __init__(self, cols: int, rows: int, wraparound: bool = False):
        self.cols = cols
        self.rows = rows
        self.wraparound = wraparound
        self.body: deque[tuple[int, int]] = deque()
        self.direction = Direction.RIGHT
        self.active = False
        self.respawn_timer_ms: float = 0.0
        self._ticks_until_turn = 0
        self._turn_interval = 4

    # ------------------------------------------------------------------
    # Spawn / despawn
    # ------------------------------------------------------------------

    def spawn(self, occupied: set):
        """Place the robot snake at a random unoccupied location."""
        for _ in range(300):
            col = random.randint(0, self.cols - 1)
            row = random.randint(0, self.rows - 1)
            direction = random.choice(_ALL_DIRECTIONS)
            # Tail extends opposite to head direction
            dx, dy = direction.opposite.delta
            positions = []
            valid = True
            for i in range(self.INITIAL_LENGTH):
                pos = (col + dx * i, row + dy * i)
                if not (0 <= pos[0] < self.cols and 0 <= pos[1] < self.rows):
                    valid = False
                    break
                if pos in occupied:
                    valid = False
                    break
                positions.append(pos)
            if valid:
                self.body = deque(positions)
                self.direction = direction
                self._ticks_until_turn = random.randint(3, 6)
                self.active = True
                return

        # Fallback: place head on any free cell, truncate to 1
        free = [(c, r) for c in range(self.cols) for r in range(self.rows) if (c, r) not in occupied]
        if free:
            self.body = deque([random.choice(free)])
            self.direction = Direction.RIGHT
            self.active = True

    def disappear(self, respawn_ms: float):
        self.active = False
        self.body.clear()
        self.respawn_timer_ms = respawn_ms

    def update_respawn(self, dt_ms: float, occupied: set) -> bool:
        """Tick down respawn timer. Returns True when the robot just respawned."""
        if self.active:
            return False
        self.respawn_timer_ms -= dt_ms
        if self.respawn_timer_ms <= 0:
            self.spawn(occupied)
            return True
        return False

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    @property
    def head(self) -> tuple[int, int]:
        return self.body[0]

    def move(self) -> bool:
        """Move one step. Returns False only if completely stuck (no wraparound + cornered)."""
        self._ticks_until_turn -= 1
        if self._ticks_until_turn <= 0:
            self._turn_interval = random.randint(3, 7)
            self._ticks_until_turn = self._turn_interval
            self._pick_random_direction()

        # If current direction leads to a wall, steer away
        if not self.wraparound and self._next_pos_hits_wall(self.direction):
            if not self._steer_clear():
                return False

        dx, dy = self.direction.delta
        new_head = (self.head[0] + dx, self.head[1] + dy)
        if self.wraparound:
            new_head = (new_head[0] % self.cols, new_head[1] % self.rows)

        self.body.appendleft(new_head)
        self.body.pop()  # constant length — no growth
        return True

    def _next_pos_hits_wall(self, direction: Direction) -> bool:
        dx, dy = direction.delta
        nx, ny = self.head[0] + dx, self.head[1] + dy
        return not (0 <= nx < self.cols and 0 <= ny < self.rows)

    def _pick_random_direction(self):
        options = [d for d in _ALL_DIRECTIONS if d != self.direction.opposite]
        self.direction = random.choice(options)

    def _steer_clear(self) -> bool:
        """Find any direction that avoids an immediate wall. Returns False if none exists."""
        options = [d for d in _ALL_DIRECTIONS if d != self.direction.opposite]
        random.shuffle(options)
        for d in options:
            if not self._next_pos_hits_wall(d):
                self.direction = d
                return True
        # Last resort: allow reverse
        if not self._next_pos_hits_wall(self.direction.opposite):
            self.direction = self.direction.opposite
            return True
        return False

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def occupies(self, pos: tuple[int, int]) -> bool:
        return pos in self.body
