import pygame

# Maze Generation & Grid
DEFAULT_WIDTH = 20
DEFAULT_HEIGHT = 20
MAX_MAZE_WIDTH = 100  # Slightly reduced for very large performance, can be increased
MAX_MAZE_HEIGHT = 100 # Slightly reduced for very large performance, can be increased
DEFAULT_CELL_SIZE = 0 # 0 for auto-fit

AUTO_SIZE_PADDING_FACTOR = 0.90 # How much of the screen the maze should use in auto-size
FALLBACK_CELL_SIZE = 10
MIN_CELL_SIZE = 3 # Minimum pixel size for a cell to be somewhat visible

# Core Maze Colors
WALL_COLOR = (30, 30, 40) # Darker wall
PATH_COLOR = (230, 230, 240) # Off-white path
START_NODE_COLOR = (0, 200, 0) # Bright green
END_NODE_COLOR = (200, 0, 0)   # Bright red
MAZE_BACKGROUND_COLOR = (50, 50, 60) # Background for the maze area if it doesn't fill screen

# Solver Visualization Colors
# Using a dictionary for solver-specific colors for clarity and expansion
SOLVER_COLORS = {
    "BFS": {
        "visited": (100, 100, 200, 180),  # Light Blue, with alpha for visited
        "path": (50, 50, 255, 220),     # Darker Blue, with alpha for current path
        "final_path": (0, 0, 255)       # Solid Blue for final path
    },
    "DFS": {
        "visited": (100, 200, 100, 180),  # Light Green
        "path": (50, 255, 50, 220),     # Darker Green
        "final_path": (0, 200, 0)       # Solid Green
    },
    "A*": {
        "visited": (200, 100, 100, 180),  # Light Red
        "path": (255, 50, 50, 220),     # Darker Red
        "final_path": (200, 0, 0)       # Solid Red
    },
    "DEFAULT": { # Fallback if a solver name is not in the dict
        "visited": (180, 180, 180, 180), # Light Gray
        "path": (150, 150, 150, 220),    # Darker Gray
        "final_path": (100, 100, 100)    # Solid Gray
    }
}
# Alpha values (0-255) will be used for visited/path overlays on the maze path color.

# UI Theme - General
APP_BACKGROUND_COLOR = (40, 40, 50) # Overall background for window
TEXT_COLOR = (220, 220, 230)
PRIMARY_ACCENT_COLOR = (0, 150, 220) # A general accent color for highlights, selections
ERROR_COLOR = (255, 80, 80)
SUCCESS_COLOR = (80, 220, 80)
WARNING_COLOR = (255, 180, 0)

# UI Fonts (Placeholders, can be replaced with specific font files)
FONT_NAME = None # Uses Pygame's default system font
FONT_SIZE_SMALL = 20
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 28
FONT_SIZE_XLARGE = 32
FONT_SIZE_TITLE = 36

# Control Panel
CONTROL_PANEL_HEIGHT = 70
CONTROL_PANEL_BACKGROUND_COLOR = (30, 30, 40)
CONTROL_PANEL_BORDER_COLOR = (60, 60, 70)
CONTROL_PANEL_BORDER_THICKNESS = 1

# Buttons (General)
BUTTON_TEXT_COLOR = (240, 240, 240)
BUTTON_FONT_SIZE = FONT_SIZE_MEDIUM
BUTTON_PADDING_X = 15
BUTTON_PADDING_Y = 8
BUTTON_BORDER_RADIUS = 6
BUTTON_BORDER_WIDTH = 1 # 0 for no border, >0 for border

BUTTON_NORMAL_COLOR = (60, 60, 75)
BUTTON_HOVER_COLOR = (80, 80, 95)
BUTTON_ACTIVE_COLOR = (50, 50, 65) # Clicked state
BUTTON_DISABLED_COLOR = (45, 45, 55)
BUTTON_DISABLED_TEXT_COLOR = (100, 100, 110)

BUTTON_ACCENT_NORMAL_COLOR = PRIMARY_ACCENT_COLOR
BUTTON_ACCENT_HOVER_COLOR = (PRIMARY_ACCENT_COLOR[0], min(255, PRIMARY_ACCENT_COLOR[1]+30), min(255, PRIMARY_ACCENT_COLOR[2]+30))
BUTTON_ACCENT_ACTIVE_COLOR = (max(0,PRIMARY_ACCENT_COLOR[0]-20), max(0,PRIMARY_ACCENT_COLOR[1]-20), max(0,PRIMARY_ACCENT_COLOR[2]-20))


# Settings Window
SETTINGS_WINDOW_WIDTH = 450
SETTINGS_WINDOW_HEIGHT = 550 # Increased to accommodate more refined UI
SETTINGS_PANEL_COLOR = (45, 45, 55) # Slightly different from app bg
SETTINGS_BORDER_COLOR = (70, 70, 80)
SETTINGS_TITLE_COLOR = TEXT_COLOR
SETTINGS_LABEL_COLOR = (200, 200, 210)

# InputBox (in Settings)
INPUT_BOX_WIDTH = 120
INPUT_BOX_HEIGHT = 38
INPUT_BOX_BG_COLOR = (60, 60, 75)
INPUT_BOX_ACTIVE_BG_COLOR = (70, 70, 85) # When focused
INPUT_BOX_BORDER_COLOR = (90, 90, 105)
INPUT_BOX_ACTIVE_BORDER_COLOR = PRIMARY_ACCENT_COLOR
INPUT_BOX_TEXT_COLOR = TEXT_COLOR
INPUT_BOX_INVALID_BG_COLOR = (85, 50, 50)
INPUT_BOX_INVALID_BORDER_COLOR = ERROR_COLOR
INPUT_BOX_FONT_SIZE = FONT_SIZE_MEDIUM

# Slider (in Settings)
SLIDER_TRACK_COLOR = (70, 70, 85)
SLIDER_TRACK_HEIGHT_RATIO = 0.25 # Ratio of slider height
SLIDER_HANDLE_COLOR = PRIMARY_ACCENT_COLOR
SLIDER_HANDLE_HOVER_COLOR = BUTTON_ACCENT_HOVER_COLOR
SLIDER_HANDLE_RADIUS_FACTOR = 0.8 # Factor of slider height / 2
SLIDER_VALUE_TEXT_COLOR = TEXT_COLOR

# Solver Selection (in Settings, e.g., for Radio Buttons or Dropdown)
CHOICE_BOX_NORMAL_COLOR = (60, 60, 75)
CHOICE_BOX_HOVER_COLOR = (75, 75, 90)
CHOICE_BOX_SELECTED_COLOR = PRIMARY_ACCENT_COLOR
CHOICE_BOX_SELECTED_TEXT_COLOR = (255,255,255)
CHOICE_BOX_TEXT_COLOR = TEXT_COLOR

# Timer / Status Info
TIMER_TEXT_COLOR = TEXT_COLOR
TIMER_FONT_SIZE = FONT_SIZE_MEDIUM

# Event Timers
AI_SOLVE_STEP_EVENT = pygame.USEREVENT + 1

# Solver Logic Config
SOLVER_OPTIONS = ["BFS", "DFS", "A*"]
DEFAULT_SOLVER = "BFS"

# AI Speed Control (used by Slider in Settings)
SLIDER_MIN_VAL = 0      # Represents fastest speed
SLIDER_MAX_VAL = 100    # Represents slowest speed
MIN_DELAY_MS = 1        # Fastest actual delay for solver step
MAX_DELAY_MS = 500      # Slowest actual delay for solver step
SLIDER_EXPONENT = 3.0   # For non-linear mapping of slider to delay

# Screen & Display
FPS = 60

# For drawing solver paths - how much smaller the inner rects are
VISITED_CELL_SCALE = 0.6 # For the "visited" overlay
CURRENT_PATH_CELL_SCALE = 0.5 # For the "current search path" overlay
FINAL_PATH_CELL_SCALE = 0.7 # For the "final solution path" overlay

# UI Element IDs (example, might not be needed if we pass objects)
UI_ID_BTN_REGENERATE = "btn_regenerate"
UI_ID_BTN_SOLVE = "btn_solve"
UI_ID_BTN_BATTLE = "btn_battle"
UI_ID_BTN_SETTINGS = "btn_settings"
UI_ID_BTN_EXIT = "btn_exit" # Not a button, but for consistency
UI_ID_BTN_SAVE_MAZE = "btn_save_maze"

# Notification System (New)
NOTIFICATION_MAX_DISPLAY = 3
NOTIFICATION_DURATION_MS = 3000 # How long a notification stays
NOTIFICATION_FADE_DURATION_MS = 500
NOTIFICATION_AREA_WIDTH = 300
NOTIFICATION_HEIGHT = 50
NOTIFICATION_PADDING = 10
NOTIFICATION_BG_COLOR = (50, 50, 65, 220) # Background with alpha
NOTIFICATION_TEXT_COLOR = TEXT_COLOR
NOTIFICATION_SUCCESS_BAR_COLOR = SUCCESS_COLOR
NOTIFICATION_ERROR_BAR_COLOR = ERROR_COLOR
NOTIFICATION_INFO_BAR_COLOR = PRIMARY_ACCENT_COLOR