import json
import random
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


# ---------- GAME RULES ----------

def merge_left(row):
    tiles = [value for value in row if value != 0]
    merged = []
    points = 0
    i = 0

    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            value = tiles[i] * 2
            merged.append(value)
            points += value
            i += 2
        else:
            merged.append(tiles[i])
            i += 1

    merged += [0] * (len(row) - len(merged))
    return merged, points


def move_board(board, direction):
    if direction not in ("left", "right", "up", "down"):
        raise ValueError("Unknown direction.")

    new_board = [[0 for _ in range(4)] for _ in range(4)]
    total_points = 0

    for index in range(4):
        if direction in ("left", "right"):
            line = board[index][:]
        else:
            line = [board[r][index] for r in range(4)]

        reverse = direction in ("right", "down")

        if reverse:
            line = line[::-1]

        merged, points = merge_left(line)

        if reverse:
            merged = merged[::-1]

        if direction in ("left", "right"):
            new_board[index] = merged
        else:
            for r in range(4):
                new_board[r][index] = merged[r]

        total_points += points

    return new_board, total_points


def add_random_tile(board):
    empty = [
        (r, c)
        for r in range(4)
        for c in range(4)
        if board[r][c] == 0
    ]

    if not empty:
        return None

    r, c = random.choice(empty)
    value = 2 if random.random() < 0.9 else 4
    board[r][c] = value

    # Return the spawn details so we can record them.
    return {"row": r, "column": c, "value": value}


def has_legal_move(board):
    for direction in ("left", "right", "up", "down"):
        next_board, _ = move_board(board, direction)
        if next_board != board:
            return True
    return False


def copy_board(board):
    # Copy every row so saved snapshots cannot change later.
    return [row[:] for row in board]


def timestamp():
    return datetime.now(timezone.utc).isoformat()


# ---------- COLOURS ----------

BACKGROUND = "#faf8ef"
BOARD_COLOUR = "#bbada0"
TEXT_COLOUR = "#776e65"

TILE_COLOURS = {
    0: "#cdc1b4",
    2: "#eee4da",
    4: "#ede0c8",
    8: "#f2b179",
    16: "#f59563",
    32: "#f67c5f",
    64: "#f65e3b",
    128: "#edcf72",
    256: "#edcc61",
    512: "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
}


# ---------- GAME WINDOW ----------

class Game2048:
    def __init__(self, root):
        self.root = root
        root.title("2048 Coach — Recording Enabled")
        root.configure(bg=BACKGROUND)
        root.resizable(False, False)

        # Recordings live beside game.py, inside a games folder.
        self.save_folder = Path(__file__).resolve().parent / "games"
        self.record = None
        self.save_path = None

        header = tk.Frame(root, bg=BACKGROUND)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(
            header,
            text="2048",
            font=("Helvetica", 42, "bold"),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
        ).pack(side="left")

        self.score_label = tk.Label(
            header,
            font=("Helvetica", 18, "bold"),
            bg=BOARD_COLOUR,
            fg="white",
            padx=16,
            pady=10,
        )
        self.score_label.pack(side="right")

        tk.Label(
            root,
            text="Use the arrow keys to slide and merge tiles.",
            font=("Helvetica", 13),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
        ).pack(pady=(0, 14))

        self.canvas = tk.Canvas(
            root,
            width=420,
            height=420,
            bg=BOARD_COLOUR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=24)

        self.status_label = tk.Label(
            root,
            font=("Helvetica", 13),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
            wraplength=420,
        )
        self.status_label.pack(pady=(12, 6))

        self.record_label = tk.Label(
            root,
            font=("Helvetica", 11),
            bg=BACKGROUND,
            fg=TEXT_COLOUR,
            wraplength=420,
        )
        self.record_label.pack(pady=(0, 8))

        tk.Button(
            root,
            text="New Game",
            font=("Helvetica", 14, "bold"),
            command=self.new_game,
            padx=16,
            pady=6,
        ).pack(pady=(0, 20))

        root.bind("<KeyPress>", self.handle_key)
        root.protocol("WM_DELETE_WINDOW", self.close_game)
        self.new_game()

    def save_record(self):
        """Save after every successful move."""
        self.record["current_board"] = copy_board(self.board)
        self.record["score"] = self.score

        try:
            self.save_folder.mkdir(parents=True, exist_ok=True)

            # Write a temporary file, then replace the saved file.
            temporary = self.save_path.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(self.record, indent=2),
                encoding="utf-8",
            )
            temporary.replace(self.save_path)

        except OSError as error:
            self.record_label.config(
                text="Recording could not be saved. See the terminal.",
                fg="#b00020",
            )
            print(f"Save failed: {error}")
            return False

        self.record_label.config(
            text=f"Saved • {len(self.record['moves'])} moves • games folder",
            fg="#487044",
        )
        return True

    def finish_record(self, reason):
        if self.record and self.record["status"] == "playing":
            self.record["status"] = reason
            self.record["ended_at"] = timestamp()
        return self.save_record()

    def new_game(self):
        # Save the previous game before starting another.
        if self.record is not None:
            if not self.finish_record("restarted"):
                return

        self.board = [[0 for _ in range(4)] for _ in range(4)]
        self.score = 0
        self.reached_2048 = False

        add_random_tile(self.board)
        add_random_tile(self.board)

        game_id = (
            datetime.now().strftime("%Y%m%d_%H%M%S")
            + "_"
            + uuid4().hex[:8]
        )
        self.save_path = self.save_folder / f"game_{game_id}.json"

        self.record = {
            "format_version": 1,
            "started_at": timestamp(),
            "status": "playing",
            "coordinate_note": "Rows and columns start at 0.",
            "initial_board": copy_board(self.board),
            "moves": [],
        }

        self.save_record()
        print(f"Recording file: {self.save_path}")

        self.status_label.config(
            text="Enjoy the process. One move at a time."
        )
        self.draw_board()
        self.canvas.focus_set()

    def draw_board(self):
        self.canvas.delete("all")
        self.score_label.config(text=f"Score\n{self.score}")

        gap = 10
        cell_size = 92.5

        for r in range(4):
            for c in range(4):
                value = self.board[r][c]
                x = gap + c * (cell_size + gap)
                y = gap + r * (cell_size + gap)

                self.canvas.create_rectangle(
                    x, y, x + cell_size, y + cell_size,
                    fill=TILE_COLOURS.get(value, "#3c3a32"),
                    outline="",
                )

                if value:
                    font_size = 32 if value < 1024 else 24
                    if value >= 100000:
                        font_size = 18

                    self.canvas.create_text(
                        x + cell_size / 2,
                        y + cell_size / 2,
                        text=str(value),
                        font=("Helvetica", font_size, "bold"),
                        fill=TEXT_COLOUR if value <= 4 else "white",
                    )

    def handle_key(self, event):
        directions = {
            "Left": "left",
            "Right": "right",
            "Up": "up",
            "Down": "down",
        }
        direction = directions.get(event.keysym)

        if direction is None:
            return

        if not has_legal_move(self.board):
            self.status_label.config(text="Game over! Start a new game.")
            return "break"

        new_board, points = move_board(self.board, direction)

        if new_board == self.board:
            self.status_label.config(text="Nothing moved. Try another direction.")
            return "break"

        before = copy_board(self.board)
        self.board = new_board
        self.score += points
        spawned_tile = add_random_tile(self.board)

        # Record the complete transition.
        self.record["moves"].append({
            "number": len(self.record["moves"]) + 1,
            "time": timestamp(),
            "direction": direction,
            "board_before": before,
            "spawned_tile": spawned_tile,
            "board_after": copy_board(self.board),
            "points_earned": points,
            "total_score": self.score,
        })

        message = f"+{points} points!" if points else "Keep going!"

        if not self.reached_2048 and any(
            value >= 2048 for row in self.board for value in row
        ):
            self.reached_2048 = True
            message = "You made 2048! Keep playing to go higher."

        if not has_legal_move(self.board):
            message = f"Game over! Final score: {self.score}"
            self.record["status"] = "game_over"
            self.record["ended_at"] = timestamp()

        self.save_record()
        self.status_label.config(text=message)
        self.draw_board()
        return "break"

    def close_game(self):
        # Keep the window open if saving fails, allowing another try.
        if self.finish_record("closed"):
            self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    game = Game2048(window)
    window.mainloop()