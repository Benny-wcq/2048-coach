from game import move_board
from coach import evaluate_board, expected_value_after_spawn


DIRECTIONS = ("left", "right", "up", "down")
POINT_WEIGHT = 0.1


def possible_spawns(board):
    """Generate every possible spawn and its probability."""
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


def best_next_move_value(board):
    """Choose the best second move after seeing the first spawn."""
    values = []

    for direction in DIRECTIONS:
        next_board, points = move_board(board, direction)

        if next_board == board:
            continue

        value = (
            POINT_WEIGHT * points
            + expected_value_after_spawn(next_board)
        )
        values.append(value)

    if not values:
        return evaluate_board(board)

    return max(values)


def compare_moves(board):
    results = []

    for direction in DIRECTIONS:
        next_board, points = move_board(board, direction)

        if next_board == board:
            continue

        # Current coach: one move, then a random spawn.
        one_move_value = (
            POINT_WEIGHT * points
            + expected_value_after_spawn(next_board)
        )

        # New experiment:
        # First move -> spawn -> best second move -> spawn.
        future_value = 0

        for spawned_board, probability in possible_spawns(next_board):
            future_value += (
                probability * best_next_move_value(spawned_board)
            )

        two_move_value = POINT_WEIGHT * points + future_value

        results.append({
            "direction": direction,
            "points": points,
            "one": one_move_value,
            "two": two_move_value,
        })

    return results


board = [
    [2, 0, 0, 0],
    [8, 0, 2, 0],
    [16, 8, 2, 0],
    [64, 16, 8, 2],
]

print("Comparing one-move and two-move look-ahead...\n")

results = compare_moves(board)

print(f"{'Direction':<12}{'Points now':>12}{'One move':>14}{'Two moves':>14}")

for result in results:
    print(
        f"{result['direction'].upper():<12}"
        f"{result['points']:>12}"
        f"{result['one']:>14.1f}"
        f"{result['two']:>14.1f}"
    )

best_one = max(results, key=lambda result: result["one"])
best_two = max(results, key=lambda result: result["two"])

print("\nOne-move recommendation:", best_one["direction"].upper())
print("Two-move recommendation:", best_two["direction"].upper())
print("\nValues are heuristic estimates, not predicted final scores.")