from PIL import Image, ImageDraw
import math
import os

# =========================
# PAC-MAN CONTRIBUTION DEMO
# =========================

WIDTH = 1000
HEIGHT = 260

BACKGROUND = "#0D0D0F"
PANEL = "#151519"
BORDER = "#29272F"

TEXT = "#E7E4EA"
MUTED = "#92909A"

# Contribution colors
EMPTY = "#24242A"
LEVEL_1 = "#3D4A40"
LEVEL_2 = "#536553"
LEVEL_3 = "#687B68"
LEVEL_4 = "#7C9A83"

PACMAN = "#D8C76A"

# Calendar dimensions
COLUMNS = 53
ROWS = 7

CELL_SIZE = 12
GAP = 5

GRID_X = 80
GRID_Y = 105

PATH_ROW = 3

OUTPUT_DIR = os.path.join("assets", "pacman")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pacman-contributions.gif")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------
# Create demo contributions
# -------------------------

contributions = []

for row in range(ROWS):
    current_row = []

    for column in range(COLUMNS):

        value = (column * 7 + row * 13) % 11

        if value < 4:
            level = 0
        elif value < 6:
            level = 1
        elif value < 8:
            level = 2
        elif value < 10:
            level = 3
        else:
            level = 4

        current_row.append(level)

    contributions.append(current_row)


COLORS = [
    EMPTY,
    LEVEL_1,
    LEVEL_2,
    LEVEL_3,
    LEVEL_4,
]


# -------------------------
# Draw one frame
# -------------------------

def draw_frame(pacman_column, mouth_open):

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

    # Calendar
    for row in range(ROWS):

        for column in range(COLUMNS):

            x = GRID_X + column * (CELL_SIZE + GAP)
            y = GRID_Y + row * (CELL_SIZE + GAP)

            color = COLORS[contributions[row][column]]

            # Pac-Man has eaten this cell
            if column < int(pacman_column) and row == PATH_ROW:
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

    # -------------------------
    # Pac-Man
    # -------------------------

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

    # Mouth animation
    if mouth_open:
        mouth_angle = 35
    else:
        mouth_angle = 8

    start_angle = mouth_angle
    end_angle = 360 - mouth_angle

    draw.pieslice(
        (
            pacman_x - radius,
            pacman_y - radius,
            pacman_x + radius,
            pacman_y + radius
        ),
        start=start_angle,
        end=end_angle,
        fill=PACMAN
    )

    # Small caption
    draw.text(
        (GRID_X, 215),
        "eating contributions →",
        fill=MUTED
    )

    return image


# -------------------------
# Generate animation
# -------------------------

frames = []

start_column = 1
end_column = COLUMNS - 2

# Smooth movement
for column in range(start_column, end_column):

    for sub_frame in range(3):

        position = column + (sub_frame / 3)

        frame = draw_frame(
            position,
            sub_frame % 2 == 0
        )

        frames.append(frame)


# Pause at the end
for _ in range(10):
    frames.append(
        draw_frame(
            end_column,
            True
        )
    )


# -------------------------
# Save GIF
# -------------------------

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