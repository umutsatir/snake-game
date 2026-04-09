import os
import math
import array
import pygame
import config


def _generate_sound(sample_rate: int, frames: list[tuple[float, float, float]]) -> pygame.mixer.Sound:
    """
    Build a pygame Sound from a list of (frequency_hz, duration_s, amplitude) segments.
    Uses a simple sine wave with a short fade-out per segment to avoid clicks.
    """
    samples = array.array("h")  # signed 16-bit
    max_val = 32767

    for freq, duration, amplitude in frames:
        n = int(sample_rate * duration)
        fade_samples = min(int(sample_rate * 0.01), n)  # 10 ms fade-out
        for i in range(n):
            t = i / sample_rate
            val = amplitude * math.sin(2 * math.pi * freq * t)
            # fade out at the end of each segment
            if i >= n - fade_samples:
                val *= (n - i) / fade_samples
            samples.append(int(val * max_val))

    return pygame.mixer.Sound(buffer=samples)


def _make_eat() -> pygame.mixer.Sound:
    """Short upward chirp — classic 8-bit pickup blip."""
    rate = 44100
    return _generate_sound(rate, [
        (440, 0.04, 0.4),
        (660, 0.04, 0.4),
    ])


def _make_eat_bonus() -> pygame.mixer.Sound:
    """Ascending arpeggio — brighter, longer reward sound."""
    rate = 44100
    return _generate_sound(rate, [
        (523, 0.06, 0.5),
        (659, 0.06, 0.5),
        (784, 0.06, 0.5),
        (1047, 0.10, 0.5),
    ])


def _make_game_over() -> pygame.mixer.Sound:
    """Descending tone — low and grim."""
    rate = 44100
    return _generate_sound(rate, [
        (330, 0.12, 0.6),
        (262, 0.12, 0.6),
        (196, 0.20, 0.6),
        (130, 0.25, 0.5),
    ])


class SoundManager:
    def __init__(self):
        self.sounds: dict = {}
        self.enabled = False

    def load(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.enabled = True
        except Exception:
            self.enabled = False
            return

        # Try loading from files first; fall back to procedural generation.
        generators = {
            "eat": _make_eat,
            "eat_bonus": _make_eat_bonus,
            "game_over": _make_game_over,
        }
        for name, make_fn in generators.items():
            path = os.path.join(config.SOUND_DIR, f"{name}.wav")
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception:
                try:
                    self.sounds[name] = make_fn()
                except Exception:
                    self.sounds[name] = None

    def play(self, name: str):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()
