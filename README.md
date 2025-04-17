# Pygame Maze Generator and Solver

This project generates, displays, and solves mazes using Python and Pygame.

## Features

*   Generates mazes using Randomized Depth-First Search (`src/maze_generator.py`).
*   Displays the maze graphically using Pygame (`ui/maze_display.py`).
*   Includes a Breadth-First Search (BFS) solver (`src/solvers/bfs_solver.py`).
*   **Visualizes the AI solving process step-by-step** with adjustable speed.
*   Allows configuration of maze dimensions (width, height) via command-line arguments or a settings window.
*   Includes a **Settings window** (`ui/settings_window.py`) to adjust maze dimensions and AI solving speed.
*   Automatically adjusts cell size to fit the screen (unless overridden).
*   Includes buttons and keyboard shortcuts for generating, solving, and opening settings.

## Project Structure

```
.
├── .gitignore         # Standard Python gitignore
├── config.py             # Configuration (colors, defaults, speeds)
├── main.py               # Main application script (runs the game)
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── src/
│   ├── maze_generator.py # Core maze generation logic
│   └── solvers/
│       └── bfs_solver.py # Breadth-First Search solver logic
└── ui/
    ├── maze_display.py   # Pygame drawing logic & visualization handling
    └── settings_window.py # UI for settings panel (dimensions, speed)
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running

Execute the `main.py` script:

```bash
python main.py
```

### Command-Line Options

*   `--width <number>`: Set the width of the maze in cells (default: 10).
*   `--height <number>`: Set the height of the maze in cells (default: 10).
*   `--cell_size <number>`: Set the size of each cell in pixels. If 0 or less (default), it automatically calculates the best fit for your screen.

Example:

```bash
python main.py --width 25 --height 20 --cell_size 15
```

## Controls

*   **Mouse Click** on "Regenerate" button / **R key**: Generate a new maze.
*   **Mouse Click** on "Solve by AI" button / **S key**: Start the step-by-step AI solving visualization.
*   **Mouse Click** on "Settings" button / **G key**: Open the settings window.
    *   Adjust maze Width/Height.
    *   Adjust AI Speed slider (0=Fast, 100=Slow).
    *   Click Save or Cancel.
*   **ESC key**: Quit the application (or cancel from Settings window).
*   **Window Close Button**: Quit the application.
