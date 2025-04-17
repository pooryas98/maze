# Configuration settings for the Maze Generator

# --- Maze Defaults ---
DEFAULT_WIDTH = 50       # Default width of the maze in cells
DEFAULT_HEIGHT = 50      # Default height of the maze in cells
# Default cell size in pixels. 0 or less means auto-calculate to fit screen.
DEFAULT_CELL_SIZE = 0

# --- Display Settings ---
# Factor of screen size to use for auto-calculated cell size (e.g., 0.9 means 90%)
AUTO_SIZE_PADDING_FACTOR = 0.90
# Fallback cell size if screen info cannot be obtained
FALLBACK_CELL_SIZE = 10
MIN_CELL_SIZE = 1 # Smallest allowed cell size

# --- Colors (RGB tuples) ---
WALL_COLOR = (0, 0, 0)          # Black
PATH_COLOR = (255, 255, 255)    # White
BACKGROUND_COLOR = (100, 100, 100) # Grey background outside maze 

# --- UI Elements ---
CONTROL_PANEL_HEIGHT = 50      # Height of the panel below the maze for controls
BUTTON_COLOR = (0, 150, 0)     # Green
BUTTON_HOVER_COLOR = (0, 200, 0) # Brighter Green
BUTTON_TEXT_COLOR = (255, 255, 255) # White
BUTTON_PADDING = 10            # Padding around button text 