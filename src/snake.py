from collections import deque
from src.enums import Direction

class Snake:
    def __init__(self, start_col: int, start_row: int, length: int = 3, wraparound: bool = False):
        self.wraparound = wraparound
        self._init(start_col, start_row, length)

    def _init(self, start_col: int, start_row: int, length: int):
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.pending_growth = 0
        self.body: deque[tuple[int, int]] = deque()
        for i in range(length):
            self.body.append((start_col - i, start_row))

    def reset(self, start_col: int, start_row: int, length: int = 3, wraparound: bool = False):
        self.wraparound = wraparound
        self._init(start_col, start_row, length)

    @property
    def head(self) -> tuple[int, int]:
        return self.body[0]

    @property
    def length(self) -> int:
        return len(self.body)

    def change_direction(self, d: Direction):
        if d != self.direction.opposite:
            self.next_direction = d

    def grow(self, amount: int = 1):
        self.pending_growth += amount

    def move(self, cols: int, rows: int) -> bool:
        """Move snake one step. Returns False if wall collision (when not wraparound)."""
        self.direction = self.next_direction
        dx, dy = self.direction.delta
        new_head = (self.head[0] + dx, self.head[1] + dy)

        if self.wraparound:
            new_head = (new_head[0] % cols, new_head[1] % rows)
        else:
            if new_head[0] < 0 or new_head[0] >= cols or new_head[1] < 0 or new_head[1] >= rows:
                return False

        self.body.appendleft(new_head)
        if self.pending_growth > 0:
            self.pending_growth -= 1
        else:
            self.body.pop()
        return True

    def hits_wall(self, cols: int, rows: int) -> bool:
        x, y = self.head
        return x < 0 or x >= cols or y < 0 or y >= rows

    def hits_self(self) -> bool:
        head = self.head
        return head in list(self.body)[1:]

    def occupies(self, pos: tuple[int, int]) -> bool:
        return pos in self.body
