from collections import deque
import pygame
from src.enums import Direction, InputAction


class InputHandler:
    def __init__(self):
        self.direction_buffer: deque[Direction] = deque(maxlen=2)

    def process_event(self, event: pygame.event.Event) -> "InputAction | None":
        if event.type == pygame.QUIT:
            return InputAction.QUIT

        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_UP:
                self.direction_buffer.append(Direction.UP)
            elif key == pygame.K_DOWN:
                self.direction_buffer.append(Direction.DOWN)
            elif key == pygame.K_LEFT:
                self.direction_buffer.append(Direction.LEFT)
            elif key == pygame.K_RIGHT:
                self.direction_buffer.append(Direction.RIGHT)
            elif key == pygame.K_p or key == pygame.K_ESCAPE:
                return InputAction.PAUSE
            elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                return InputAction.CONFIRM
            elif key == pygame.K_r:
                return InputAction.RESTART
            elif key == pygame.K_f:
                return InputAction.TOGGLE_FPS
            elif key == pygame.K_q:
                return InputAction.QUIT

        return None

    def process_menu_event(self, event: pygame.event.Event) -> "InputAction | None":
        """Process events in the menu — W toggles wraparound, LEFT/RIGHT cycle themes."""
        if event.type == pygame.QUIT:
            return InputAction.QUIT
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_w:
                return InputAction.TOGGLE_WRAPAROUND
            elif key == pygame.K_LEFT or key == pygame.K_a:
                self.direction_buffer.append(Direction.LEFT)
            elif key == pygame.K_RIGHT or key == pygame.K_d:
                self.direction_buffer.append(Direction.RIGHT)
            elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                return InputAction.CONFIRM
            elif key == pygame.K_q or key == pygame.K_ESCAPE:
                return InputAction.QUIT
            elif key == pygame.K_f:
                return InputAction.TOGGLE_FPS
        return None

    def flush_direction(self) -> "Direction | None":
        if self.direction_buffer:
            return self.direction_buffer.popleft()
        return None

    def clear(self):
        self.direction_buffer.clear()
