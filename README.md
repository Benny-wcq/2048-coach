# 2048 Coach

A playable Python 2048 game with optional move suggestions,
automatic game recording, replay, and decision analysis.

This is my first independent GitHub project, built as a learning
project with AI assistance. I am exploring how algorithms can
support a game I enjoy.

## Why I built it

I have played 2048 for about a year. I wanted to combine something
I enjoy with computer science: a coach that suggests moves while
leaving the player in control.

For me, 2048 is also about enjoying the process. Combining tiles
is satisfying even when a game eventually ends. That experience
inspired this project.

## Features

- Coloured 4×4 board and arrow-key controls
- Standard random tile spawning: 90% 2, 10% 4
- Optional hints based on board evaluation
- Automatic recordings of successful moves
- Replay with forward and backward controls
- Comparison of recorded decisions with the current coach
- Experimental one-move and two-move search benchmarks

## Requirements

- Python 3.10 or newer
- Tkinter available in your Python installation

The project uses Python's standard library. No pip packages
are required.

Check whether Tkinter works:

```bash
python3 -m tkinter
```

A small test window should open. If Tkinter is missing, install
Tk support appropriate for your Python distribution and operating system.

On Windows, you may need to use `py` instead of `python3`.

## Download and play

Clone this repository and enter its folder:

```bash
git clone https://github.com/Benny-wcq/2048-coach.git
cd 2048-coach
```

Start the game with optional hints:

```bash
python3 coach.py
```

Click the game window, then use the arrow keys.
Click **Get Hint** whenever you want advice.

To play without the coach interface:

```bash
python3 game.py
```

## Recordings and replay

Games are saved locally as JSON files inside `games/`.
Each successful move records:

- Direction
- Board before and after
- New tile position and value
- Points earned and total score

Moves that do not change the board are not recorded.
Hint requests are not currently recorded.

To replay a saved game:

```bash
python3 replay.py
```

Click **Open Recording** and choose a JSON file.

To compare your decisions with the current coach:

```bash
python3 analyse.py
```

A disagreement does not prove that the player made a mistake.
Recommendations are recalculated from the recorded boards.

## How the coach works

The interactive coach evaluates each legal move and averages
over possible random tile spawns.

Its evaluation rewards empty cells, neighbouring matching tiles,
and having the largest tile in a corner. It penalises large
differences between neighbouring tile levels.

The weights are experimental. Evaluation values are not predicted
final scores or probabilities.

The separate experiment and benchmark scripts also explore
two-move expectimax search. The interactive coach currently
uses one-move search.

## Experiments

Compare search depths on an example board:

```bash
python3 experiment.py
```

Run automated games:

```bash
python3 benchmark.py
```

The initial benchmark uses one game per coach, capped at
100 moves. This is a short functionality check, not evidence
that one coach is stronger.

In my first local run:

| Search depth | Score at 100 moves | Largest tile | Average decision time |
|---|---:|---:|---:|
| One move | 1,116 | 128 | 1.0 ms |
| Two moves | 1,088 | 128 | 54.3 ms |

Both games reached the move limit before game over.
Timing depends on the computer and environment.

## Files

| File | Purpose |
|---|---|
| `game.py` | Game rules, desktop interface, and recording |
| `coach.py` | Interactive game with optional hints |
| `replay.py` | Step through a saved game |
| `analyse.py` | Inspect disagreements with the coach |
| `experiment.py` | Compare search depths on an example board |
| `benchmark.py` | Run automated comparison games |

## Planned improvements

- Save benchmark results automatically
- Compare coaches across multiple complete games
- Record hint requests
- Add a preferred-corner setting
- Improve explanations and evaluate deeper search
- Explore a browser version for easier sharing

## Acknowledgements

Inspired by Gabriele Cirulli's 2048:
https://github.com/gabrielecirulli/2048

Developed with assistance from ChatGPT for coding, explanations,
and experiment design. This project is a learning prototype and
does not claim a novel or optimal 2048 algorithm.