# Retro Snake Game

A classic Snake game built with Python and PyGame for the SWE-2 university assignment.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Move snake |
| ENTER | Start / Confirm |
| P / ESC | Pause / Resume |
| R | Restart (from Game Over screen) |
| F | Toggle FPS counter |
| W (in menu) | Toggle wraparound mode |
| LEFT / RIGHT (in menu) | Cycle through themes |
| Q | Quit |

## Features

- **4 visual themes** — Classic, Neon, Desert, Ocean
- **Bonus food** — golden item spawns every 5 foods eaten, worth 50 pts, expires in 8 s and blinks when nearly gone
- **Speed scaling** — move interval decreases as your level rises (every 50 points)
- **Particle effects** — burst of particles on every food pickup
- **Wraparound mode** — snake passes through walls instead of dying
- **High score persistence** — saved to `highscore.txt` automatically
- **Countdown** — 3-2-1-GO! before each game starts
- **FPS counter** — toggle with F

## Sounds

Place WAV files in `assets/sounds/` to enable audio:

| File | Trigger |
|------|---------|
| `eat.wav` | Normal food eaten |
| `eat_bonus.wav` | Bonus food eaten |
| `game_over.wav` | Snake dies |

Missing files are handled gracefully — the game runs silently without them.

## Project Structure

```
snake-game/
├── main.py            # Entry point
├── config.py          # All constants and theme palettes
├── requirements.txt
├── highscore.txt      # Written at runtime
├── assets/sounds/     # Optional WAV files
└── src/
    ├── enums.py        # Direction, GameState, FoodType, Theme, InputAction
    ├── snake.py        # Snake logic
    ├── food.py         # Food + BonusFood
    ├── particle.py     # Particle effects
    ├── renderer.py     # All drawing (stateless w.r.t. game logic)
    ├── sound_manager.py
    ├── input_handler.py
    └── game.py         # Orchestrator + state machine
```

## Requirements

- Python 3.10+
- pygame >= 2.1.0
