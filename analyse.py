import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from game import (
    BACKGROUND,
    BOARD_COLOUR,
    TEXT_COLOUR,
    TILE_COLOURS,
    move_board,
)
from coach import expected_value_after_spawn


def analyse_position(board, played_direction):
    """Compare legal moves using our current coach's formula."""
    ratings = {}

    for direction in ("left", "right", "up", "down"):
        next_board, points = move_board(board, direction)

        if next_board == board:
            continue

        ratings[direction] = (
            expected_value_after_spawn(next_board)
            + 0.1 * points
        )

    best_direction = max(ratings, key=ratings.get)
    best_value = ratings[best_direction]
    played_value = ratings[played_direction]

    return {
        "recommended": best_direction,
        "ratings": ratings,
        "gap": best_value - played_value,
    }


class GameAnalyser:
    def __init__(self, root):
        self.root = root
        self.items = []
        self.index = 0

        root.title("2048 — Explore Your Decisions")
        root.configure(bg=BACKGROUND)
        root.resizable(False, False)

        tk.Label(
            root,
            text="Explore your decisions",
            font=("Helvetica", 23, "bold"),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
        ).pack(pady=(18, 8))

        self.summary = tk.Label(
            root,
            text="Open a recording to compare your moves with the coach.",
            font=("Helvetica", 12),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
            wraplength=420,
        )
        self.summary.pack(padx=20, pady=8)

        self.canvas = tk.Canvas(
            root,
            width=420,
            height=420,
            bg=BOARD_COLOUR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=24)

        self.details = tk.Label(
            root,
            text="The board shown will be BEFORE your move.",
            font=("Helvetica", 12),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
            wraplength=420,
            justify="left",
        )
        self.details.pack(padx=24, pady=12)

        controls = tk.Frame(root, bg=BACKGROUND)
        controls.pack(pady=(0, 12))

        self.previous_button = tk.Button(
            controls,
            text="← Previous",
            command=lambda: self.step(-1),
            state="disabled",
        )
        self.previous_button.pack(side="left", padx=5)

        self.open_button = tk.Button(
            controls,
            text="Open Recording",
            command=self.open_recording,
        )
        self.open_button.pack(side="left", padx=5)

        self.next_button = tk.Button(
            controls,
            text="Next →",
            command=lambda: self.step(1),
            state="disabled",
        )
        self.next_button.pack(side="left", padx=5)

        tk.Label(
            root,
            text=(
                "A disagreement is not proof of a mistake.\n"
                "These are heuristic estimates, not predicted game scores."
            ),
            font=("Helvetica", 11),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
        ).pack(padx=20, pady=(0, 16))

    def open_recording(self):
        folder = Path(__file__).resolve().parent / "games"

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose a recorded game",
            initialdir=str(folder if folder.exists() else folder.parent),
            filetypes=[("Game recordings", "*.json")],
        )

        if not path:
            return

        try:
            record = json.loads(
                Path(path).read_text(encoding="utf-8")
            )
            moves = record["moves"]

            if not isinstance(moves, list):
                raise ValueError("The moves field must be a list.")

        except (OSError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror("Cannot open recording", str(error))
            return

        self.items = []
        self.index = 0
        self.moves = moves
        self.processed = 0
        self.canvas.delete("all")
        self.details.config(text="Comparing moves…")
        self.open_button.config(state="disabled")
        self.previous_button.config(state="disabled")
        self.next_button.config(state="disabled")

        # Process small batches so the window stays responsive.
        self.root.after(1, self.process_batch)

    def process_batch(self):
        end = min(self.processed + 10, len(self.moves))

        try:
            for i in range(self.processed, end):
                move = self.moves[i]
                result = analyse_position(
                    move["board_before"],
                    move["direction"],
                )

                # Ignore exact ties and tiny rounding differences.
                if result["gap"] > 0.000001:
                    self.items.append({
                        "move": move,
                        "analysis": result,
                    })

        except (KeyError, TypeError, ValueError, IndexError) as error:
            self.open_button.config(state="normal")
            self.summary.config(text="Could not analyse this recording.")
            messagebox.showerror("Analysis error", str(error))
            return

        self.processed = end
        self.summary.config(
            text=f"Analysing {end}/{len(self.moves)} moves…"
        )

        if end < len(self.moves):
            self.root.after(1, self.process_batch)
            return

        # Show the biggest differences in heuristic value first.
        self.items.sort(
            key=lambda item: item["analysis"]["gap"],
            reverse=True,
        )

        self.open_button.config(state="normal")
        self.summary.config(
            text=(
                f"Checked {len(self.moves)} moves. "
                f"Found {len(self.items)} positions where the coach "
                "rates another move higher."
            )
        )

        if self.items:
            self.draw()
        else:
            self.details.config(
                text=(
                    "No strictly higher-rated alternatives were found.\n"
                    "That does not establish that the moves were optimal."
                )
            )

    def step(self, amount):
        if not self.items:
            return

        self.index = max(
            0,
            min(len(self.items) - 1, self.index + amount),
        )
        self.draw()

    def draw(self):
        item = self.items[self.index]
        move = item["move"]
        analysis = item["analysis"]
        board = move["board_before"]

        self.canvas.delete("all")

        for r in range(4):
            for c in range(4):
                value = board[r][c]
                x = 10 + c * 102.5
                y = 10 + r * 102.5

                self.canvas.create_rectangle(
                    x, y, x + 92.5, y + 92.5,
                    fill=TILE_COLOURS.get(value, "#3c3a32"),
                    outline="",
                )

                if value:
                    font_size = 32 if value < 1024 else 24
                    if value >= 100000:
                        font_size = 18

                    self.canvas.create_text(
                        x + 46.25,
                        y + 46.25,
                        text=str(value),
                        font=("Helvetica", font_size, "bold"),
                        fill=TEXT_COLOUR if value <= 4 else "white",
                    )

        ratings_text = "\n".join(
            f"{direction.upper()}: {value:.1f}"
            for direction, value in sorted(
                analysis["ratings"].items(),
                key=lambda pair: pair[1],
                reverse=True,
            )
        )

        self.details.config(
            text=(
                f"Position {self.index + 1}/{len(self.items)} "
                f"— BEFORE move {move['number']}\n"
                f"You played: {move['direction'].upper()}\n"
                f"Coach prefers: {analysis['recommended'].upper()}\n\n"
                f"Estimated values:\n{ratings_text}"
            )
        )

        self.previous_button.config(
            state="normal" if self.index > 0 else "disabled"
        )
        self.next_button.config(
            state=(
                "normal"
                if self.index < len(self.items) - 1
                else "disabled"
            )
        )


if __name__ == "__main__":
    window = tk.Tk()
    analyser = GameAnalyser(window)
    window.mainloop()