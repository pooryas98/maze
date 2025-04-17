# Pygame Maze Generator

This project generates and displays a maze using Python and Pygame.

## Features

*   Generates mazes using Randomized Depth-First Search.
*   Displays the maze graphically using Pygame.
*   Allows configuration of maze dimensions (width, height) via command-line arguments.
*   Automatically adjusts cell size to fit the screen (unless overridden).
*   Includes a "Regenerate" button and 'R' key shortcut to create new mazes.

## Project Structure

```
.
├── .gitignore         # Standard Python gitignore
├── config.py          # Configuration (colors, defaults)
├── main.py            # Main application script (runs the game)
├── README.md          # This file
├── requirements.txt   # Python dependencies
├── src/
│   └── maze_generator.py # Core maze generation logic
└── ui/
    └── maze_display.py   # Pygame drawing logic
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

*   **Mouse Click** on "Regenerate" button: Generate a new maze.
*   **R key**: Generate a new maze.
*   **ESC key**: Quit the application.
*   **Window Close Button**: Quit the application. 