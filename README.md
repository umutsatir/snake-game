# Retro Snake Game

A classic Snake game built with Python and PyGame for the CSE444 assignment.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Move snake |
| UP / DOWN (in menu) | Cycle difficulty |
| LEFT / RIGHT (in menu) | Cycle theme |
| W (in menu) | Toggle wraparound mode |
| ENTER | Start / Confirm |
| P / ESC | Pause / Resume |
| R | Restart (from Game Over screen) |
| F | Toggle FPS counter |
| Q | Quit |

## Features

### Core
- **4 visual themes** — Classic, Neon, Desert, Ocean
- **Bonus food** — golden item spawns every 5 foods eaten, worth 50 pts, expires in 8 s and blinks when nearly gone
- **Speed scaling** — move interval decreases as your level rises (every 50 points)
- **Particle effects** — burst of particles on every food pickup
- **Wraparound mode** — snake passes through walls instead of dying
- **High score persistence** — saved to `highscore.txt` automatically
- **Countdown** — 3-2-1-GO! before each game starts

### Difficulty System
Select difficulty from the main menu (UP/DOWN).

| Difficulty | Base Speed | Min Speed | Robot Snake | Special Food Chance |
|------------|-----------|-----------|-------------|---------------------|
| Easy       | Slow       | Slower    | Disabled    | 15 % |
| Normal     | Default    | Fast      | Active      | 15 % |
| Hard       | Fast       | Very fast | Active & faster | 20 % |

**Progressive challenges** — Obstacle walls appear on the grid as you level up (Normal: level 3+, Hard: level 2+).

### Robot Snake
An orange AI-controlled snake wanders randomly around the grid.

| Collision | Outcome |
|-----------|---------|
| Player head → robot body | **Game Over** |
| Player head → robot body (while invincible) | Robot disappears for 30 s |
| Robot head → player body | Robot disappears for 30 s, then respawns |

- Robot starts at length 5 and never grows
- Disabled in Easy difficulty
- Respects the wraparound setting
- Faster and more aggressive in Hard mode

### Special Foods
Spawn with 15–20 % chance after eating a normal food item. Each expires after 6 seconds and blinks in the final 2 seconds.

| Icon | Type | Effect |
|------|------|--------|
| Cyan circle | **Invincibility** | 5 s immunity to walls, self, and obstacles. Hitting the robot while invincible makes it vanish. Snake pulses visually. |
| Purple square | **Poison** | Removes 3 tail segments (min length 1) and deducts 30 points. |
| Light-blue diamond | **Slow Motion** | Halves speed of all snakes for 5 s. Active effects shown in HUD. |

Active effect timers are displayed in the HUD during gameplay.

## Sounds

Place WAV files in `assets/sounds/` to enable audio. Missing files fall back to procedural synthesis.

| File | Trigger |
|------|---------|
| `eat.wav` | Normal food eaten |
| `eat_bonus.wav` | Bonus food eaten |
| `game_over.wav` | Snake dies |
| `eat_invincibility.wav` | Invincibility food eaten |
| `eat_poison.wav` | Poison food eaten |
| `eat_slow_motion.wav` | Slow-motion food eaten |

## Project Structure

```
snake-game/
├── main.py               # Entry point
├── config.py             # All constants, difficulty settings, theme palettes
├── requirements.txt
├── highscore.txt         # Written at runtime
├── assets/sounds/        # Optional WAV files
└── src/
    ├── enums.py          # Direction, GameState, FoodType, Theme, Difficulty, InputAction
    ├── snake.py          # Player snake logic
    ├── robot_snake.py    # AI wandering snake
    ├── food.py           # Food, BonusFood, SpecialFood subclasses
    ├── particle.py       # Particle effects
    ├── renderer.py       # All drawing (stateless w.r.t. game logic)
    ├── sound_manager.py  # Procedural + file-based sounds
    ├── input_handler.py  # Keyboard input buffering
    └── game.py           # Orchestrator + state machine
```

## Requirements

- Python 3.10+
- pygame >= 2.1.0
