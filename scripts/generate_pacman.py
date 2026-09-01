import json
import os
import random
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# MONICA // CONTRIBUTION ARCADE
# ============================================================
#
# REAL GITHUB CONTRIBUTIONS
# SMART PAC-MAN TARGETING
# 4-DIRECTION MOVEMENT
# 3-SECOND CONTRIBUTION RECOVERY
# MINIMAL / PREMIUM VISUAL STYLE
#
# ============================================================


# ============================================================
# CANVAS
# ============================================================

WIDTH = 1100
HEIGHT = 330

BACKGROUND = "#0B0F14"
PANEL = "#10151C"
BORDER = "#252D38"

TEXT = "#FFFFFF"
MUTED = "#FFFFFF"
SUBTLE = "#FFFFFF"

# ============================================================
# PAC-MAN
# ============================================================

PACMAN = "#E8D05F"
PACMAN_EATING = "#F0D86F"


# ============================================================
# CONTRIBUTION COLORS
#
# Empty cells are intentionally visible.
# Green levels become progressively stronger.
# ============================================================

CONTRIBUTION_COLORS = [
    "#161B22",   # 0 — empty
    "#0E4429",   # 1 — low
    "#006D32",   # 2 — medium
    "#26A641",   # 3 — high
    "#39D353",   # 4 — peak
]

CELL_OUTLINE = "#161B22"


# ============================================================
# CALENDAR
# ============================================================

COLUMNS = 53
ROWS = 7

CELL_SIZE = 13
GAP = 4
CELL_STEP = CELL_SIZE + GAP

GRID_X = 105
GRID_Y = 105


# ============================================================
# ANIMATION
# ============================================================

# Slightly relaxed Pac-Man speed.
FRAME_DURATION = 110

# Two frames per movement.
SUB_FRAMES = 2

# Contribution returns after approximately 3 seconds.
RECOVERY_SECONDS = 3

RECOVERY_FRAMES = max(
    1,
    round(
        RECOVERY_SECONDS
        * 1000
        / FRAME_DURATION
    )
)

# Number of real contribution targets per animation loop.
TARGET_COUNT = 10

# Keeps the animation deterministic.
RANDOM_SEED = 42


# ============================================================
# FILE PATHS
# ============================================================

OUTPUT_DIR = os.path.join(
    "assets",
    "pacman"
)

DATA_FILE = os.path.join(
    OUTPUT_DIR,
    "contributions.json"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "pacman-contributions.gif"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# FONTS
# ============================================================

def get_font(size):

    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/consola.ttf",
    ]

    for path in candidates:

        if os.path.exists(path):

            return ImageFont.truetype(
                path,
                size
            )

    return ImageFont.load_default()


FONT_TITLE = get_font(18)
FONT_SMALL = get_font(11)


# ============================================================
# LOAD REAL GITHUB DATA
# ============================================================

def load_data():

    if not os.path.exists(DATA_FILE):

        raise FileNotFoundError(
            f"Missing contribution data:\n{DATA_FILE}"
        )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# BUILD CALENDAR
# ============================================================

def build_calendar(data):

    levels = [
        [0 for _ in range(COLUMNS)]
        for _ in range(ROWS)
    ]

    counts = [
        [0 for _ in range(COLUMNS)]
        for _ in range(ROWS)
    ]

    dates = [
        [None for _ in range(COLUMNS)]
        for _ in range(ROWS)
    ]

    weeks = data["weeks"][-COLUMNS:]

    for column, week in enumerate(weeks):

        for day in week["contributionDays"]:

            row = day["weekday"]
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

            if (
                0 <= row < ROWS
                and
                0 <= column < COLUMNS
            ):

                levels[row][column] = level
                counts[row][column] = count
                dates[row][column] = day["date"]

    return levels, counts, dates


# ============================================================
# GET REAL CONTRIBUTION CELLS
# ============================================================

def get_contribution_cells(
    levels,
    counts
):

    cells = []

    for row in range(ROWS):

        for column in range(COLUMNS):

            count = counts[row][column]

            if count > 0:

                cells.append(
                    {
                        "x": column,
                        "y": row,
                        "level": levels[row][column],
                        "count": count,
                    }
                )

    return cells


# ============================================================
# MANHATTAN DISTANCE
# ============================================================

def distance(a, b):

    return (
        abs(a[0] - b[0])
        +
        abs(a[1] - b[1])
    )


# ============================================================
# CHOOSE NEXT CONTRIBUTION
# ============================================================

def choose_target(
    current,
    contribution_cells,
    visited,
    rng
):

    available = [
        cell
        for cell in contribution_cells
        if (
            cell["x"],
            cell["y"]
        ) not in visited
    ]

    if not available:

        visited.clear()

        available = contribution_cells

    candidates = []

    for cell in available:

        position = (
            cell["x"],
            cell["y"]
        )

        dist = distance(
            current,
            position
        )

        # Stronger contribution cells receive
        # slightly higher priority.
        level_weight = {
            1: 1.0,
            2: 1.4,
            3: 1.9,
            4: 2.6,
        }.get(
            cell["level"],
            1.0
        )

        # Nearby cells are preferred,
        # but distant cells remain possible.
        distance_weight = 1 / (
            1 + dist * 0.08
        )

        weight = (
            level_weight
            * distance_weight
        )

        candidates.append(
            (
                cell,
                weight
            )
        )

    total = sum(
        weight
        for _, weight in candidates
    )

    pick = rng.uniform(
        0,
        total
    )

    running = 0

    for cell, weight in candidates:

        running += weight

        if pick <= running:

            visited.add(
                (
                    cell["x"],
                    cell["y"]
                )
            )

            return cell

    cell = candidates[-1][0]

    visited.add(
        (
            cell["x"],
            cell["y"]
        )
    )

    return cell


# ============================================================
# CREATE 4-DIRECTION PATH
# ============================================================

def create_path(
    start,
    target,
    rng
):

    x, y = start

    target_x, target_y = target

    path = []

    previous_direction = (
        1,
        0
    )

    safety = 0

    while (
        x != target_x
        or y != target_y
    ):

        safety += 1

        if safety > 500:

            break

        directions = [
            (1, 0),     # RIGHT
            (-1, 0),    # LEFT
            (0, 1),     # DOWN
            (0, -1),    # UP
        ]

        possible = []

        for dx, dy in directions:

            nx = x + dx
            ny = y + dy

            if (
                0 <= nx < COLUMNS
                and
                0 <= ny < ROWS
            ):

                possible.append(
                    (
                        dx,
                        dy
                    )
                )

        scored = []

        for direction in possible:

            dx, dy = direction

            nx = x + dx
            ny = y + dy

            new_distance = (
                abs(nx - target_x)
                +
                abs(ny - target_y)
            )

            score = (
                100
                - new_distance * 12
            )

            # Slight preference for continuing forward.
            if direction == previous_direction:

                score += 9

            # Small natural variation.
            score += rng.uniform(
                -6,
                6
            )

            # Occasional small detour.
            if rng.random() < 0.10:

                score += rng.uniform(
                    -15,
                    4
                )

            scored.append(
                (
                    direction,
                    score
                )
            )

        scored.sort(
            key=lambda item: item[1],
            reverse=True
        )

        best_count = min(
            2,
            len(scored)
        )

        direction = rng.choice(
            scored[:best_count]
        )[0]

        dx, dy = direction

        x += dx
        y += dy

        previous_direction = direction

        path.append(
            (
                x,
                y,
                direction
            )
        )

    return path


# ============================================================
# BUILD PAC-MAN JOURNEY
# ============================================================

def create_journey(
    contribution_cells,
    rng
):

    if not contribution_cells:

        return []

    # Pac-Man starts from the left.
    current = (
        0,
        ROWS // 2
    )

    journey = []

    visited = set()

    target_limit = min(
        TARGET_COUNT,
        len(contribution_cells)
    )

    for _ in range(
        target_limit
    ):

        target = choose_target(
            current,
            contribution_cells,
            visited,
            rng
        )

        target_position = (
            target["x"],
            target["y"]
        )

        path = create_path(
            current,
            target_position,
            rng
        )

        journey.extend(
            path
        )

        current = target_position

    return journey


# ============================================================
# DRAW PAC-MAN
# ============================================================

def draw_pacman(
    draw,
    x,
    y,
    direction,
    mouth_open,
    eating
):

    radius = 14

    mouth = (
        30
        if mouth_open
        else 5
    )

    rotations = {
        (1, 0): 0,
        (0, 1): 90,
        (-1, 0): 180,
        (0, -1): 270,
    }

    rotation = rotations.get(
        direction,
        0
    )

    color = (
        PACMAN_EATING
        if eating
        else PACMAN
    )

    draw.pieslice(
        (
            x - radius,
            y - radius,
            x + radius,
            y + radius
        ),
        start=(
            rotation + mouth
        ),
        end=(
            rotation
            + 360
            - mouth
        ),
        fill=color
    )


# ============================================================
# MONTH LABELS
#
# FIXED:
# Prevents labels such as "AUSEP" from overlapping.
# ============================================================

def draw_month_labels(
    draw,
    dates
):

    month_names = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]

    month_positions = []

    last_month = None

    for column in range(COLUMNS):

        date = None

        for row in range(ROWS):

            if dates[row][column]:

                date = dates[row][column]

                break

        if not date:

            continue

        month_key = date[:7]

        if month_key == last_month:

            continue

        last_month = month_key

        month_number = int(
            date[5:7]
        )

        month_label = month_names[
            month_number - 1
        ]

        month_positions.append(
            (
                column,
                month_label
            )
        )

    # --------------------------------------------------------
    # Draw labels with minimum spacing.
    # --------------------------------------------------------

    last_x = -100

    for column, label in month_positions:

        x = (
            GRID_X
            + column * CELL_STEP
        )

        # Prevent visual collisions.
        if x - last_x < 34:

            continue

        draw.text(
            (
                x,
                80
            ),
            label,
            font=FONT_SMALL,
            fill=MUTED
        )

        last_x = x


# ============================================================
# DRAW COMPLETE FRAME
# ============================================================

def draw_frame(
    levels,
    dates,
    position,
    direction,
    eaten,
    total_contributions,
    mouth_open
):

    image = Image.new(
        "RGB",
        (
            WIDTH,
            HEIGHT
        ),
        BACKGROUND
    )

    draw = ImageDraw.Draw(
        image
    )

    # ========================================================
    # HEADER
    # ========================================================

    draw.text(
        (
            45,
            28
        ),
        "> contribution.arcade",
        font=FONT_TITLE,
        fill=TEXT
    )

    draw.text(
        (
            865,
            31
        ),
        f"{total_contributions} contributions",
        font=FONT_SMALL,
        fill=MUTED
    )

    # ========================================================
    # MAIN PANEL
    # ========================================================

      # ========================================================
    # MAIN PANEL
    # ========================================================

    draw.rounded_rectangle(
        (
            25,
            68,
            WIDTH - 25,
            HEIGHT - 25
        ),
        radius=18,
        fill=PANEL,
        outline=BORDER,
        width=1
    )

    # ========================================================
    # MONTH LABELS
    # ========================================================

    draw_month_labels(
        draw,
        dates
    )

    # ========================================================
    # WEEKDAY LABELS
    # ========================================================

    weekdays = [
        "MON",
        "TUE",
        "WED",
        "THU",
        "FRI",
        "SAT",
        "SUN",
    ]

    for row, weekday in enumerate(
        weekdays
    ):

        y = (
            GRID_Y
            + row * CELL_STEP
        )

        draw.text(
            (
                40,
                y + 1
            ),
            weekday,
            font=FONT_SMALL,
            fill=MUTED
        )

    # ========================================================
    # CONTRIBUTION GRID
    # ========================================================

    for row in range(ROWS):

        for column in range(COLUMNS):

            x = (
                GRID_X
                + column * CELL_STEP
            )

            y = (
                GRID_Y
                + row * CELL_STEP
            )

            level = levels[
                row
            ][
                column
            ]

            color = (
                CONTRIBUTION_COLORS[
                    level
                ]
            )

            # ------------------------------------------------
            # Temporarily eaten contribution.
            # ------------------------------------------------

            if (
                column,
                row
            ) in eaten:

                color = (
                    CONTRIBUTION_COLORS[0]
                )

            # ------------------------------------------------
            # Every square gets a subtle outline.
            # This makes the empty grid visible without
            # turning it into a spreadsheet.
            # ------------------------------------------------

            draw.rounded_rectangle(
                (
                    x,
                    y,
                    x + CELL_SIZE,
                    y + CELL_SIZE
                ),
                radius=3,
                fill=color,
                outline=CELL_OUTLINE,
                width=1
            )

    # ========================================================
    # PAC-MAN
    # ========================================================

    current_x, current_y = position

    pacman_x = (
        GRID_X
        + current_x * CELL_STEP
        + CELL_SIZE / 2
    )

    pacman_y = (
        GRID_Y
        + current_y * CELL_STEP
        + CELL_SIZE / 2
    )

    eating = (
        round(current_x),
        round(current_y)
    ) in eaten

    draw_pacman(
        draw,
        pacman_x,
        pacman_y,
        direction,
        mouth_open,
        eating
    )

    # ========================================================
    # FOOTER
    # ========================================================

    draw.text(
        (
            GRID_X,
            HEIGHT - 48
        ),
        "PAC-MAN  /  CONTRIBUTION MODE",
        font=FONT_SMALL,
        fill=SUBTLE
    )

    return image


# ============================================================
# GENERATE ANIMATION
# ============================================================

def generate_animation(
    levels,
    dates,
    contribution_cells,
    total_contributions
):

    rng = random.Random(
        RANDOM_SEED
    )

    print()
    print(
        "Building Pac-Man journey..."
    )

    journey = create_journey(
        contribution_cells,
        rng
    )

    if not journey:

        raise RuntimeError(
            "No contribution cells found."
        )

    print(
        f"Real contribution cells: "
        f"{len(contribution_cells)}"
    )

    print(
        f"Journey movements: "
        f"{len(journey)}"
    )

    print()

    frames = []

    # --------------------------------------------------------
    # Stores:
    #
    # (column, row) -> frame number
    #
    # This controls the 3-second recovery.
    # --------------------------------------------------------

    eaten = {}

    # ========================================================
    # CREATE MOVEMENT FRAMES
    # ========================================================

    for step_number, step in enumerate(
        journey
    ):

        if (
            step_number == 0
            or step_number % 25 == 0
        ):

            print(
                f"Rendering movement "
                f"{step_number + 1}/"
                f"{len(journey)}..."
            )

        column, row, direction = step

        # ----------------------------------------------------
        # Eat ONLY an actual contribution.
        # ----------------------------------------------------

        if levels[row][column] > 0:

            eaten[
                (
                    column,
                    row
                )
            ] = len(frames)

        # ----------------------------------------------------
        # Restore cells after approximately 3 seconds.
        # ----------------------------------------------------

        expired = []

        for cell, eaten_frame in eaten.items():

            if (
                len(frames)
                - eaten_frame
                >= RECOVERY_FRAMES
            ):

                expired.append(
                    cell
                )

        for cell in expired:

            del eaten[cell]

        # ----------------------------------------------------
        # Smooth movement.
        # ----------------------------------------------------

        previous_x = (
            column
            - direction[0]
        )

        previous_y = (
            row
            - direction[1]
        )

        for sub_frame in range(
            SUB_FRAMES
        ):

            progress = (
                sub_frame
                / SUB_FRAMES
            )

            display_x = (
                previous_x
                + direction[0]
                * progress
            )

            display_y = (
                previous_y
                + direction[1]
                * progress
            )

            frame = draw_frame(
                levels,
                dates,
                (
                    display_x,
                    display_y
                ),
                direction,
                eaten,
                total_contributions,
                sub_frame == 0
            )

            frames.append(
                frame
            )

    # ========================================================
    # FINAL FRAME
    # ========================================================

    column, row, direction = journey[-1]

    frames.append(
        draw_frame(
            levels,
            dates,
            (
                column,
                row
            ),
            direction,
            eaten,
            total_contributions,
            True
        )
    )

    # ========================================================
    # FAST GIF ENCODING
    # ========================================================

    print()
    print(
        f"Total frames: {len(frames)}"
    )

    print(
        "Encoding GIF..."
    )

    gif_frames = []

    for index, frame in enumerate(
        frames
    ):

        if (
            index == 0
            or index % 50 == 0
        ):

            print(
                f"Encoding frame "
                f"{index + 1}/"
                f"{len(frames)}..."
            )

        gif_frames.append(
            frame.quantize(
                colors=48,
                method=Image.Quantize.FASTOCTREE
            )
        )

    # ========================================================
    # SAVE
    # ========================================================

    print()
    print(
        "Saving GIF..."
    )

    gif_frames[0].save(
        OUTPUT_FILE,
        save_all=True,
        append_images=gif_frames[1:],
        duration=FRAME_DURATION,
        loop=0,
        optimize=False
    )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    file_size = os.path.getsize(
        OUTPUT_FILE
    )

    file_size_mb = (
        file_size
        / 1024
        / 1024
    )

    print()
    print(
        "========================================"
    )
    print(
        " MONICA // CONTRIBUTION ARCADE"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"GitHub contributions: "
        f"{total_contributions}"
    )

    print(
        f"Real contribution cells: "
        f"{len(contribution_cells)}"
    )

    print(
        f"Journey movements: "
        f"{len(journey)}"
    )

    print(
        f"Animation frames: "
        f"{len(frames)}"
    )

    print(
        f"Frame duration: "
        f"{FRAME_DURATION} ms"
    )

    print(
        f"Cell recovery: "
        f"~{RECOVERY_SECONDS} seconds"
    )

    print(
        "Movement: ↑ ↓ ← →"
    )

    print(
        "Targeting: REAL contribution cells"
    )

    print(
        f"GIF size: "
        f"{file_size_mb:.2f} MB"
    )

    print()
    print(
        f"Created: {OUTPUT_FILE}"
    )

    print()
    print(
        "Pac-Man is ready. →"
    )

    print()


# ============================================================
# MAIN
# ============================================================

def main():

    data = load_data()

    total_contributions = data[
        "totalContributions"
    ]

    levels, counts, dates = (
        build_calendar(data)
    )

    contribution_cells = (
        get_contribution_cells(
            levels,
            counts
        )
    )

    generate_animation(
        levels,
        dates,
        contribution_cells,
        total_contributions
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()