import math
import tkinter as tk

from game import (
    Game2048,
    BACKGROUND,
    TEXT_COLOUR,
    move_board,
    has_legal_move,
)


# ---------- BOARD EVALUATION ----------

def evaluate_board(board):
    """Estimate how promising a board is. Higher is better."""
    if not has_legal_move(board):
        return -10000

    empty_cells = sum(
        value == 0
        for row in board
        for value in row
    )

    merge_pairs = 0
    roughness = 0

    for r in range(4):
        for c in range(4):
            value = board[r][c]

            if value == 0:
                continue

            # Examine the neighbour to the right and below.
            # This counts each pair only once.
            neighbours = []

            if c < 3:
                neighbours.append(board[r][c + 1])

            if r < 3:
                neighbours.append(board[r + 1][c])

            for neighbour in neighbours:
                if neighbour == 0:
                    continue

                if value == neighbour:
                    merge_pairs += 1

                roughness += abs(
                    math.log2(value) - math.log2(neighbour)
                )

    largest = max(max(row) for row in board)
    corners = [
        board[0][0],
        board[0][3],
        board[3][0],
        board[3][3],
    ]

    corner_bonus = (
        math.log2(largest)
        if largest > 0 and largest in corners
        else 0
    )

    # Experimental weights, not proven optimal values.
    return (
        100 * empty_cells
        + 20 * merge_pairs
        + 30 * corner_bonus
        - 5 * roughness
    )


def expected_value_after_spawn(board):
    """Average the evaluation over every possible new tile."""
    empty_cells = [
        (r, c)
        for r in range(4)
        for c in range(4)
        if board[r][c] == 0
    ]

    if not empty_cells:
        return evaluate_board(board)

    expected_value = 0

    for r, c in empty_cells:
        for tile, probability in ((2, 0.9), (4, 0.1)):
            possible_board = [row[:] for row in board]
            possible_board[r][c] = tile

            expected_value += (
                probability
                / len(empty_cells)
                * evaluate_board(possible_board)
            )

    return expected_value


def choose_hint(board):
    """Compare every legal direction without changing the game."""
    candidates = []

    for direction in ("left", "right", "up", "down"):
        next_board, points = move_board(board, direction)

        if next_board == board:
            continue

        value = (
            expected_value_after_spawn(next_board)
            + 0.1 * points
        )

        candidates.append((value, direction, next_board, points))

    if not candidates:
        return "No legal moves remain. Start a new game."

    # In an exact tie, use the first direction considered.
    _, direction, next_board, points = max(
        candidates,
        key=lambda candidate: candidate[0],
    )

    empty_before_spawn = sum(
        value == 0
        for row in next_board
        for value in row
    )

    # A successful move is followed by one new tile.
    empty_after_spawn = max(0, empty_before_spawn - 1)

    return (
        f"Suggested move: {direction.upper()}\n"
        f"Earns {points} points immediately; leaves "
        f"{empty_after_spawn} empty cells after the new tile.\n"
        "Highest estimate using space, nearby matches, "
        "corner position, and tile arrangement."
    )


# ---------- ADD A COACH TO YOUR EXISTING GAME ----------

class CoachGame(Game2048):
    def __init__(self, root):
        super().__init__(root)

        root.title("2048 Coach — Your First Hint Algorithm")

        self.hint_label = tk.Label(
            root,
            text="Click Get Hint whenever you want advice.",
            font=("Helvetica", 12),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
            wraplength=410,
        )
        self.hint_label.pack(padx=24, pady=(0, 8))

        tk.Button(
            root,
            text="Get Hint",
            font=("Helvetica", 14, "bold"),
            command=self.show_hint,
            padx=16,
            pady=6,
        ).pack(pady=(0, 16))

    def show_hint(self):
        self.hint_label.config(text=choose_hint(self.board))
        self.canvas.focus_set()

    def draw_board(self):
        super().draw_board()

        # Clear old advice whenever the board changes.
        if hasattr(self, "hint_label"):
            self.hint_label.config(
                text="Click Get Hint whenever you want advice."
            )


if __name__ == "__main__":
    window = tk.Tk()
    game = CoachGame(window)
    window.mainloop()