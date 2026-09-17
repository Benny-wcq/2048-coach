import random
import time

from game import move_board
from coach import evaluate_board, expected_value_after_spawn


DIRECTIONS = ("left", "right", "up", "down")

# Start small: two-move search can be slow.
GAMES_PER_COACH = 1
MAX_MOVES = 100
POINT_WEIGHT = 0.1


def spawn_tile(board, rng):
    """Use a separate random generator for reproducible games."""
    empty_cells = [
        (r, c)
        for r in range(4)
        for c in range(4)
        if board[r][c] == 0
    ]

    if empty_cells:
        r, c = rng.choice(empty_cells)
        board[r][c] = 2 if rng.random() < 0.9 else 4


def possible_spawns(board):
    empty_cells = [
        (r, c)
        for r in range(4)
        for c in range(4)
        if board[r][c] == 0
    ]

    if not empty_cells:
        yield board, 1.0
        return

    for r, c in empty_cells:
        for value, probability in ((2, 0.9), (4, 0.1)):
            next_board = [row[:] for row in board]
            next_board[r][c] = value
            yield next_board, probability / len(empty_cells)


def best_second_move_value(board):
    values = []

    for direction in DIRECTIONS:
        next_board, points = move_board(board, direction)

        if next_board == board:
            continue

        values.append(
            POINT_WEIGHT * points
            + expected_value_after_spawn(next_board)
        )

    return max(values) if values else evaluate_board(board)


def choose_move(board, depth):
    best_direction = None
    best_value = float("-inf")

    for direction in DIRECTIONS:
        next_board, points = move_board(board, direction)

        if next_board == board:
            continue

        if depth == 1:
            future_value = expected_value_after_spawn(next_board)
        else:
            future_value = sum(
                probability * best_second_move_value(spawned_board)
                for spawned_board, probability
                in possible_spawns(next_board)
            )

        value = POINT_WEIGHT * points + future_value

        if value > best_value:
            best_value = value
            best_direction = direction

    return best_direction


def play_game(depth, seed):
    rng = random.Random(seed)
    board = [[0 for _ in range(4)] for _ in range(4)]
    spawn_tile(board, rng)
    spawn_tile(board, rng)

    score = 0
    moves = 0
    decision_seconds = 0
    decision_count = 0

    print(
        f"\nStarting depth {depth}, seed {seed}...",
        flush=True,
    )

    while moves < MAX_MOVES:
        start = time.perf_counter()
        direction = choose_move(board, depth)
        decision_seconds += time.perf_counter() - start
        decision_count += 1

        if direction is None:
            break

        board, points = move_board(board, direction)
        score += points
        spawn_tile(board, rng)
        moves += 1

        if moves % 10 == 0:
            largest = max(max(row) for row in board)
            print(
                f"  Move {moves}: score={score}, largest={largest}",
                flush=True,
            )

    legal_moves_remain = any(
        move_board(board, direction)[0] != board
        for direction in DIRECTIONS
    )

    return {
        "depth": depth,
        "seed": seed,
        "moves": moves,
        "score": score,
        "largest": max(max(row) for row in board),
        "average_ms": 1000 * decision_seconds / decision_count,
        "status": "Move limit" if legal_moves_remain else "Game over",
    }


def main():
    print("2048 COACH BENCHMARK")
    print(f"Games per coach: {GAMES_PER_COACH}")
    print(f"Maximum moves per game: {MAX_MOVES}")
    print("Depth 2 may take noticeably longer.")
    print("Press Control+C in the terminal to stop.\n")

    results = []

    for seed in range(GAMES_PER_COACH):
        for depth in (1, 2):
            result = play_game(depth, seed)
            results.append(result)

            print(
                f"Finished: depth {depth}, "
                f"score {result['score']}, "
                f"largest tile {result['largest']}, "
                f"{result['status']}",
                flush=True,
            )

    print("\nRESULTS")
    print(
        f"{'Depth':<7}{'Seed':<6}{'Moves':<8}"
        f"{'Score':<9}{'Largest':<9}{'ms/choice':<12}Status"
    )

    for result in results:
        print(
            f"{result['depth']:<7}"
            f"{result['seed']:<6}"
            f"{result['moves']:<8}"
            f"{result['score']:<9}"
            f"{result['largest']:<9}"
            f"{result['average_ms']:<12.1f}"
            f"{result['status']}"
        )

    print("\nThis is a short trial, not proof that either coach is better.")
    print("Move-limit scores are partial-game scores.")


if __name__ == "__main__":
    main()