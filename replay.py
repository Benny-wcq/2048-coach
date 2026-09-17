import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

# Reuse the colours from your game.
# Importing game does not start its window because of its
# "if __name__ == '__main__'" guard.
from game import BACKGROUND, BOARD_COLOUR, TEXT_COLOUR, TILE_COLOURS


class Replay:
    def __init__(self, root):
        self.root = root
        self.record = None
        self.position = 0

        root.title("2048 — Replay My Game")
        root.configure(bg=BACKGROUND)
        root.resizable(False, False)

        tk.Label(
            root,
            text="Your game replay",
            font=("Helvetica", 24, "bold"),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
        ).pack(pady=(20, 10))

        self.info = tk.Label(
            root,
            text="Open a recording to begin.",
            font=("Helvetica", 13),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
        )
        self.info.pack(pady=10)

        self.canvas = tk.Canvas(
            root,
            width=420,
            height=420,
            bg=BOARD_COLOUR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=24)

        controls = tk.Frame(root, bg=BACKGROUND)
        controls.pack(pady=16)

        self.previous_button = tk.Button(
            controls,
            text="← Previous",
            command=lambda: self.step(-1),
            state="disabled",
        )
        self.previous_button.pack(side="left", padx=8)

        tk.Button(
            controls,
            text="Open Recording",
            command=self.open_recording,
        ).pack(side="left", padx=8)

        self.next_button = tk.Button(
            controls,
            text="Next →",
            command=lambda: self.step(1),
            state="disabled",
        )
        self.next_button.pack(side="left", padx=8)

        root.bind("<Left>", lambda event: self.step(-1))
        root.bind("<Right>", lambda event: self.step(1))

    def open_recording(self):
        folder = Path(__file__).resolve().parent / "games"

        path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose your recorded game",
            initialdir=str(folder if folder.exists() else folder.parent),
            filetypes=[("Game recordings", "*.json")],
        )

        if not path:
            return

        try:
            record = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(record, dict):
                raise ValueError("This is not a game recording.")
            if "initial_board" not in record or "moves" not in record:
                raise ValueError("This file is missing game history.")
        except (OSError, ValueError) as error:
            messagebox.showerror("Could not open recording", str(error))
            return

        self.record = record
        self.position = 0
        self.draw()

    def step(self, amount):
        if self.record is None:
            return

        self.position = max(
            0,
            min(len(self.record["moves"]), self.position + amount),
        )
        self.draw()

    def draw(self):
        moves = self.record["moves"]

        if self.position == 0:
            board = self.record["initial_board"]
            description = f"Starting board • 0/{len(moves)} moves • Score: 0"
        else:
            move = moves[self.position - 1]
            board = move["board_after"]
            description = (
                f"Move {self.position}/{len(moves)}: "
                f"{move['direction'].upper()} • "
                f"+{move['points_earned']} • "
                f"Score: {move['total_score']}"
            )

        self.info.config(text=description)
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

        self.previous_button.config(
            state="normal" if self.position > 0 else "disabled"
        )
        self.next_button.config(
            state="normal" if self.position < len(moves) else "disabled"
        )


if __name__ == "__main__":
    window = tk.Tk()
    replay = Replay(window)
    window.mainloop()