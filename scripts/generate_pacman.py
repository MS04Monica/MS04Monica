import json
import os
from PIL import Image, ImageDraw

WIDTH = 1000
HEIGHT = 260

BACKGROUND = "#0D0D0F"
PANEL = "#151519"
BORDER = "#29272F"

TEXT = "#E7E4EA"
MUTED = "#92909A"
PACMAN = "#D8C76A"

CONTRIBUTION_COLORS = [
    "#24242A",
    "#3D4A40",
    "#536553",
    "#687B68",
    "#7C9A83",
]

COLUMNS = 53
ROWS = 7

CELL_SIZE = 12
GAP = 5

GRID_X = 80
GRID_Y = 105

PATH_ROW = 3

OUTPUT_DIR = os.path.join("assets", "pacman")
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "pacman-contributions.gif"
)

DATA_FILE = os.path.join(
    OUTPUT_DIR,
    "contributions.json"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_contributions():
    """Load GitHub contribution data."""

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Missing {DATA_FILE}. "
            "Run the GitHub data fetch step first."
        )

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def build_calendar(data):
    """
    Convert GitHub contribution data into a
    7 x 53 calendar grid.
    """

    calendar = [
        [0 for _ in range(COLUMNS)]
        for _ in range(ROWS)
    ]

    weeks = data["weeks"]

    for column, week in enumerate(weeks[-COLUMNS:]):

        for day in week["contributionDays"]:

            row = day["weekday"]

            if 0 <= row < ROWS:
                count = day["contributionCount"]

                if count == 0:
                    level = 0
                elif count <= 2:
                    level = 1
                elif count <= 5:
                    level = 2
                elif count <= 9:
                    level = 3
                else:
                    level = 4

                calendar[row][column] = level

    return calendar


def draw_frame(calendar, pacman_column, mouth_open):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND
    )

    draw = ImageDraw.Draw(image)

    # Header
    draw.text(
        (35, 25),
        "> CONTRIBUTION.ARCADE",
        fill=PACMAN
    )

    draw.text(
        (760, 25),
        "PAC-MAN // LIVE",
        fill=MUTED
    )

    # Main panel
    draw.rounded_rectangle(
        (20, 55, WIDTH - 20, HEIGHT - 20),
        radius=14,
        fill=PANEL,
        outline=BORDER,
        width=1
    )

    # Calendar cells
    for row in range(ROWS):

        for column in range(COLUMNS):

            x = GRID_X + column * (CELL_SIZE + GAP)
            y = GRID_Y + row * (CELL_SIZE + GAP)

            level = calendar[row][column]

            color = CONTRIBUTION_COLORS[level]

            # Pac-Man has eaten this cell.
            if (
                row == PATH_ROW
                and column < int(pacman_column)
            ):
                color = BACKGROUND

            draw.rounded_rectangle(
                (
                    x,
                    y,
                    x + CELL_SIZE,
                    y + CELL_SIZE
                ),
                radius=3,
                fill=color
            )

    # Pac-Man position
    pacman_x = (
        GRID_X
        + pacman_column * (CELL_SIZE + GAP)
        + CELL_SIZE / 2
    )

    pacman_y = (
        GRID_Y
        + PATH_ROW * (CELL_SIZE + GAP)
        + CELL_SIZE / 2
    )

    radius = 11

    mouth_angle = 35 if mouth_open else 8

    draw.pieslice(
        (
            pacman_x - radius,
            pacman_y - radius,
            pacman_x + radius,
            pacman_y + radius
        ),
        start=mouth_angle,
        end=360 - mouth_angle,
        fill=PACMAN
    )

    draw.text(
        (GRID_X, 215),
        "eating contributions →",
        fill=MUTED
    )

    return image


def generate_animation(calendar):

    frames = []

    start_column = 1
    end_column = COLUMNS - 2

    # Smooth Pac-Man movement.
    for column in range(
        start_column,
        end_column
    ):

        for sub_frame in range(3):

            position = (
                column
                + sub_frame / 3
            )

            frame = draw_frame(
                calendar,
                position,
                sub_frame % 2 == 0
            )

            frames.append(frame)

    # Small pause at the end.
    for _ in range(10):

        frames.append(
            draw_frame(
                calendar,
                end_column,
                True
            )
        )

    frames[0].save(
        OUTPUT_FILE,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0
    )

    print()
    print("===================================")
    print(" PAC-MAN CONTRIBUTION CALENDAR")
    print("===================================")
    print()
    print(f"Created: {OUTPUT_FILE}")
    print(f"Frames : {len(frames)}")
    print()
    print("Pac-Man is ready.")


def main():

    data = load_contributions()

    calendar = build_calendar(data)

    generate_animation(calendar)


if __name__ == "__main__":
    main()