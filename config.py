# config.py

import pygame

# Configuration settings for the Maze Generator and Solver

# --- Maze Defaults ---
DEFAULT_WIDTH = 20      # Default width of the maze in cells
DEFAULT_HEIGHT = 20     # Default height of the maze in cells
MAX_MAZE_WIDTH = 150    # Max allowed width for user input
MAX_MAZE_HEIGHT = 150   # Max allowed height for user input
# Default cell size in pixels. 0 or less means auto-calculate to fit screen.
DEFAULT_CELL_SIZE = 0

# --- Display Settings ---
# Factor of screen size to use for auto-calculated cell size (e.g., 0.9 means 90%)
AUTO_SIZE_PADDING_FACTOR = 0.90
# Fallback cell size if screen info cannot be obtained
FALLBACK_CELL_SIZE = 10
MIN_CELL_SIZE = 1       # Smallest allowed cell size

# --- Colors (RGB tuples) ---
WALL_COLOR = (0, 0, 0)              # Black
PATH_COLOR = (255, 255, 255)        # White
BACKGROUND_COLOR = (100, 100, 100) # Grey background outside maze
START_COLOR = (0, 255, 0)           # Bright Green for start cell
END_COLOR = (255, 0, 0)             # Bright Red for end cell

# --- Solver Colors ---
SOLUTION_PATH_COLOR = (0, 0, 255)   # Blue
VISITED_COLOR = (173, 216, 230)     # Light Blue (for visited cells not on final path)
CURRENT_SEARCH_COLOR = (255, 165, 0) # Orange (Optional: For current search path) - Currently unused but available

# --- Solver Settings ---
# Define available solvers - Keys are display names, values can be identifiers if needed
SOLVER_OPTIONS = ["BFS", "DFS", "A*"]
DEFAULT_SOLVER = "BFS"

# --- UI Elements ---
CONTROL_PANEL_HEIGHT = 60      # Increased height for better button spacing
BUTTON_COLOR = (0, 150, 0)     # Green
BUTTON_HOVER_COLOR = (0, 200, 0) # Brighter Green
BUTTON_TEXT_COLOR = (255, 255, 255) # White
BUTTON_PADDING = 10            # Padding around button text
TEXT_COLOR = (230, 230, 230) # Light grey/white for general text

# --- Settings Window Colors & Params ---
SETTINGS_PANEL_WIDTH = 380
SETTINGS_PANEL_HEIGHT = 450
SETTINGS_PANEL_COLOR = (40, 40, 50)      # Darker panel background
SETTINGS_BORDER_COLOR = (80, 80, 90)    # Border for the panel
SETTINGS_INPUT_BOX_COLOR = (60, 60, 70) # Input box background
SETTINGS_INPUT_BOX_ACTIVE_COLOR = (70, 70, 85) # Input box background when active
SETTINGS_INPUT_TEXT_COLOR = (220, 220, 220) # Text inside input boxes
SETTINGS_LABEL_COLOR = TEXT_COLOR        # Label text color
SETTINGS_SLIDER_HANDLE_COLOR = (0, 180, 0) # Green handle for slider
SETTINGS_SLIDER_TRACK_COLOR = (80, 80, 90) # Track color for slider
SETTINGS_INVALID_INPUT_COLOR = (255, 100, 100) # Color for invalid input text

# --- AI Speed Slider Settings ---
SLIDER_MIN_VAL = 0
SLIDER_MAX_VAL = 100
MIN_DELAY_MS = 1      # Fastest speed (milliseconds per step)
MAX_DELAY_MS = 500    # Slowest speed
# Exponent for non-linear mapping (1=linear, >1 makes slow end slower, <1 makes fast end faster)
# 2 or 3 usually gives a good feel.
SLIDER_EXPONENT = 3.0

# --- Pygame Events ---
# Custom event for the AI solver timer
AI_SOLVE_STEP_EVENT = pygame.USEREVENT + 1