import pygame
import sys
import argparse
import pygame
import sys
import argparse
import config # Import the configuration

from src.maze_generator import create_maze
# from ui.maze_display import draw_maze # Replaced by MazeDisplay class
from ui.maze_display import MazeDisplay, AI_SOLVE_STEP_EVENT # Import the class and event
# from src.solvers.bfs_solver import find_path_bfs # Solver logic is now handled via MazeDisplay
from ui.settings_window import init_settings_window, draw_settings_window, handle_settings_event # Import settings UI functions

# Constants - REMOVED, now in config.py
# DEFAULT_WIDTH = 100
# DEFAULT_HEIGHT = 100
# DEFAULT_CELL_SIZE = 0 # Change default to 0 to detect if user specified it
# BACKGROUND_COLOR = (100, 100, 100) # Grey background outside maze

def main():
    parser = argparse.ArgumentParser(description="Generate and display a maze.")
    parser.add_argument("--width", type=int, default=config.DEFAULT_WIDTH, help="Width of the maze in cells.")
    parser.add_argument("--height", type=int, default=config.DEFAULT_HEIGHT, help="Height of the maze in cells.")
    parser.add_argument("--cell_size", type=int, default=config.DEFAULT_CELL_SIZE,
                        help="Size of each cell in pixels. Default (<=0) fits to screen.")
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode.") # Add fullscreen flag
    args = parser.parse_args()

    maze_width = args.width
    maze_height = args.height
    user_cell_size = args.cell_size # Store user's preference

    # Initialize Pygame *before* getting display info
    pygame.init()
    pygame.font.init() # Initialize font module

    # Get display info *early* for calculations
    try:
        display_info = pygame.display.Info()
        native_screen_w = display_info.current_w
        native_screen_h = display_info.current_h
        print(f"Detected screen resolution: {native_screen_w}x{native_screen_h}")
    except pygame.error as e:
        print(f"Warning: Could not get display info ({e}). Using fallback resolution 800x600.")
        native_screen_w, native_screen_h = 800, 600 # Fallback resolution

    # --- Maze Generation ---
    maze_grid = create_maze(maze_width, maze_height)
    grid_render_height = len(maze_grid)
    grid_render_width = len(maze_grid[0]) if grid_render_height > 0 else 0

    # --- Determine Cell Size ---
    if user_cell_size <= 0: # If user didn't specify a positive cell size, calculate optimal
        # Target screen area for calculation (full screen or windowed with padding)
        target_w = native_screen_w
        # Subtract panel height for vertical calculation, unless fullscreen (panel overlays)
        target_h = native_screen_h - (0 if args.fullscreen else config.CONTROL_PANEL_HEIGHT)

        # Use padding factor only if windowed
        padding = 1.0 if args.fullscreen else config.AUTO_SIZE_PADDING_FACTOR

        max_cell_w = (target_w * padding) // grid_render_width
        max_cell_h = (target_h * padding) // grid_render_height

        # Use the smaller of the two dimensions to ensure fit
        cell_size = max(config.MIN_CELL_SIZE, int(min(max_cell_w, max_cell_h)))
        print(f"Auto-calculated cell size: {cell_size}px")

    else:
        cell_size = max(config.MIN_CELL_SIZE, user_cell_size) # Ensure user size is at least min

    # --- Determine Screen/Window Size ---
    maze_render_width = grid_render_width * cell_size
    maze_render_height = grid_render_height * cell_size

    if args.fullscreen:
        screen_width = native_screen_w
        screen_height = native_screen_h
        screen_flags = pygame.FULLSCREEN | pygame.SCALED # Use SCALED for better compatibility
    else:
        # Window size is maze + panel
        screen_width = maze_render_width
        screen_height = maze_render_height + config.CONTROL_PANEL_HEIGHT
        screen_flags = pygame.RESIZABLE # Allow window resizing

    # --- Screen Setup ---
    print(f"Setting display mode: {screen_width}x{screen_height} Flags: {screen_flags}")
    screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)
    # Update dimensions if fullscreen might have adjusted them
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    print(f"Actual screen surface size: {screen_width}x{screen_height}")

    pygame.display.set_caption(f"Maze ({maze_width}x{maze_height}) - Cell Size: {cell_size}px")

    # --- Calculate Maze Drawing Offset for Centering ---
    # Available space for maze drawing (Screen height minus panel height)
    available_height_for_maze = screen_height - config.CONTROL_PANEL_HEIGHT
    offset_x = max(0, (screen_width - maze_render_width) // 2)
    offset_y = max(0, (available_height_for_maze - maze_render_height) // 2)

    # --- Initialize Maze Display ---
    maze_display = MazeDisplay(screen, maze_grid, cell_size, offset_x, offset_y)
    ai_solve_delay_ms = 100 # Initial AI solve speed (milliseconds per step)

    # --- Button Setup ---
    button_font = pygame.font.Font(None, 30) # Fallback Pygame font

    # --- Button Definitions ---
    button_defs = [
        {"text": "Regenerate (R)", "key": pygame.K_r},
        {"text": "Solve (S)", "key": pygame.K_s},
        {"text": "Settings (G)", "key": pygame.K_g},
        {"text": "Exit (ESC)", "key": pygame.K_ESCAPE}
    ]

    # Calculate max button width needed
    max_text_width = 0
    for btn in button_defs:
        text_surface = button_font.render(btn["text"], True, config.BUTTON_TEXT_COLOR)
        max_text_width = max(max_text_width, text_surface.get_rect().width)
    
    # Standard button dimensions
    button_width = max_text_width + config.BUTTON_PADDING * 2
    button_height = button_font.get_height() + config.BUTTON_PADDING * 2
    button_padding = config.BUTTON_PADDING * 2

    # Calculate total width needed for all buttons
    total_buttons_width = (button_width * len(button_defs)) + (button_padding * (len(button_defs) - 1))
    
    # Calculate starting position to center buttons
    start_x = (screen_width - total_buttons_width) // 2
    button_y = screen_height - config.CONTROL_PANEL_HEIGHT + (config.CONTROL_PANEL_HEIGHT - button_height) // 2

    # Create button rects and text surfaces
    buttons = []
    for i, btn in enumerate(button_defs):
        btn_rect = pygame.Rect(
            start_x + i * (button_width + button_padding),
            button_y,
            button_width,
            button_height
        )
        text_surface = button_font.render(btn["text"], True, config.BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=btn_rect.center)
        
        buttons.append({
            "rect": btn_rect,
            "text_surface": text_surface,
            "text_rect": text_rect,
            "key": btn["key"]
        })

    # Assign to specific variables for easier reference
    regen_button = buttons[0]
    solve_button = buttons[1]
    settings_button = buttons[2]
    exit_button = buttons[3]

    # --- Solver State (Managed by MazeDisplay) ---
    # solution_path = None # Removed
    # visited_cells = None # Removed
    # solving_in_progress = False # Removed (use maze_display.is_solving())
    # solve_requested = False # Removed

    # --- Settings State ---
    settings_window_open = False # Track if the settings window is open

    # --- Callback for Speed Slider ---
    def handle_speed_change(new_delay):
        nonlocal ai_solve_delay_ms
        print(f"Setting AI solve delay to: {new_delay} ms")
        ai_solve_delay_ms = new_delay
        maze_display.set_ai_solve_delay(ai_solve_delay_ms)

    # --- Game loop ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        # Check button hovers
        regen_button_hover = regen_button["rect"].collidepoint(mouse_pos)
        solve_button_hover = solve_button["rect"].collidepoint(mouse_pos)
        settings_button_hover = settings_button["rect"].collidepoint(mouse_pos)
        exit_button_hover = exit_button["rect"].collidepoint(mouse_pos)

        # --- Handle Settings Window ---
        if settings_window_open:
            action_result = None
            for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                     running = False
                     break # Exit inner loop too
                 # Pass event to settings handler
                 action_result = handle_settings_event(event)
                 if action_result:
                     break # Process action immediately
            if not running: break # Exit outer loop if QUIT received

            if action_result:
                if action_result["action"] == "save":
                    new_width = action_result["width"]
                    new_height = action_result["height"]
                    print(f"Applying new settings: Width={new_width}, Height={new_height}")

                    # --- Update Maze Config and Regenerate ---
                    maze_width = new_width
                    maze_height = new_height
                    # Regenerate maze
                    maze_grid = create_maze(maze_width, maze_height)
                    grid_render_height = len(maze_grid)
                    grid_render_width = len(maze_grid[0]) if grid_render_height > 0 else 0
                    # Clear solver state in display
                    # maze_display.reset_solve_state() # Done by set_maze

                    # --- Recalculate Cell Size and Screen (based on new maze dims) ---
                    if user_cell_size <= 0: # Auto-size
                        target_w = native_screen_w
                        target_h = native_screen_h - (0 if args.fullscreen else config.CONTROL_PANEL_HEIGHT)
                        padding_factor = 1.0 if args.fullscreen else config.AUTO_SIZE_PADDING_FACTOR
                        max_cell_w = (target_w * padding_factor) // grid_render_width
                        max_cell_h = (target_h * padding_factor) // grid_render_height
                        cell_size = max(config.MIN_CELL_SIZE, int(min(max_cell_w, max_cell_h)))
                        print(f"Auto-recalculated cell size: {cell_size}px")
                    else:
                         cell_size = max(config.MIN_CELL_SIZE, user_cell_size)

                    maze_render_width = grid_render_width * cell_size
                    maze_render_height = grid_render_height * cell_size

                    if not args.fullscreen:
                        # Update window size if not fullscreen
                        screen_width = maze_render_width
                        screen_height = maze_render_height + config.CONTROL_PANEL_HEIGHT
                        screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)
                    # else: Fullscreen stays the same size

                    # --- Recalculate Offsets and Buttons ---
                    available_height_for_maze = screen_height - config.CONTROL_PANEL_HEIGHT
                    offset_x = max(0, (screen_width - maze_render_width) // 2)
                    offset_y = max(0, (available_height_for_maze - maze_render_height) // 2)

                    # Update MazeDisplay instance
                    maze_display.set_maze(maze_grid)
                    maze_display.cell_size = cell_size
                    maze_display.offset_x = offset_x
                    maze_display.offset_y = offset_y
                    maze_display.screen = screen # Update screen reference if it changed

                    # Reposition buttons on resize
                    total_buttons_width = (button_width * len(button_defs)) + (button_padding * (len(button_defs) - 1))
                    start_x = (screen_width - total_buttons_width) // 2
                    button_y = screen_height - config.CONTROL_PANEL_HEIGHT + (config.CONTROL_PANEL_HEIGHT - button_height) // 2
                    
                    for i, btn in enumerate(buttons):
                        btn["rect"].left = start_x + i * (button_width + button_padding)
                        btn["rect"].top = button_y
                        btn["text_rect"].center = btn["rect"].center

                    pygame.display.set_caption(f"Maze ({maze_width}x{maze_height}) - Cell Size: {cell_size}px")

                    settings_window_open = False # Close window

                elif action_result["action"] == "cancel":
                    settings_window_open = False # Close window

            # Draw the semi-transparent overlay first
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Darker overlay
            screen.blit(overlay, (0, 0))

            # Draw the actual settings window on top
            draw_settings_window(screen)

            pygame.display.flip() # Update display for settings window
            continue # Skip main game loop processing

        # --- Handle Solver Request (Removed - Handled by MazeDisplay) ---
        # if solve_requested: ...

        # --- Handle Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Pass timer event to MazeDisplay
            if event.type == AI_SOLVE_STEP_EVENT:
                maze_display.handle_event(event)

            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                screen_width = event.w
                screen_height = event.h
                screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)
                # Recalculate offsets and button positions on resize
                available_height_for_maze = screen_height - config.CONTROL_PANEL_HEIGHT
                offset_x = max(0, (screen_width - maze_render_width) // 2)
                offset_y = max(0, (available_height_for_maze - maze_render_height) // 2)

                # Update MazeDisplay instance
                maze_display.screen = screen
                maze_display.offset_x = offset_x
                maze_display.offset_y = offset_y

                # Reposition all buttons on resize
                total_buttons_width = (button_width * len(button_defs)) + (button_padding * (len(button_defs) - 1))
                start_x = (screen_width - total_buttons_width) // 2
                button_y = screen_height - config.CONTROL_PANEL_HEIGHT + (config.CONTROL_PANEL_HEIGHT - button_height) // 2
                
                for i, btn in enumerate(buttons):
                    btn["rect"].left = start_x + i * (button_width + button_padding)
                    btn["rect"].top = button_y
                    btn["text_rect"].center = btn["rect"].center

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r: # Regenerate
                    print("Regenerating maze (R key)...")
                    maze_grid = create_maze(maze_width, maze_height)
                    maze_display.set_maze(maze_grid) # Update display
                    # maze_display.reset_solve_state() # Done by set_maze
                elif event.key == pygame.K_s: # Solve
                    print("Starting AI solve (S key)...")
                    maze_display.start_ai_solve() # Start visualization
                elif event.key == pygame.K_g: # Settings
                    print("Opening settings...")
                    # Initialize the settings window state before opening
                    init_settings_window(screen.get_width(), screen.get_height(),
                                         maze_width, maze_height,
                                         ai_solve_delay_ms, handle_speed_change) # Pass delay and callback
                    settings_window_open = True # Open the settings window
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse click
                    if regen_button_hover:
                        print("Regenerating maze (button click)...")
                        maze_grid = create_maze(maze_width, maze_height)
                        maze_display.set_maze(maze_grid) # Update display
                        # maze_display.reset_solve_state() # Done by set_maze
                    elif solve_button_hover:
                        print("Starting AI solve (button click)...")
                        maze_display.start_ai_solve() # Start visualization
                    elif settings_button_hover:
                        print("Opening settings...")
                        # Initialize the settings window state before opening
                        init_settings_window(screen.get_width(), screen.get_height(),
                                             maze_width, maze_height,
                                             ai_solve_delay_ms, handle_speed_change) # Pass delay and callback
                        settings_window_open = True # Open the settings window
                    elif exit_button_hover:
                        print("Exiting game...")
                        running = False

        # Draw everything
        screen.fill(config.BACKGROUND_COLOR)

        # Draw the maze using the MazeDisplay instance
        maze_display.draw()

        # Draw the control panel background covering the bottom area
        panel_rect = pygame.Rect(0, screen_height - config.CONTROL_PANEL_HEIGHT, screen_width, config.CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(screen, config.BACKGROUND_COLOR, panel_rect) # Draw panel background

        # Draw all buttons
        for btn, hover in zip(buttons, [regen_button_hover, solve_button_hover, settings_button_hover, exit_button_hover]):
            btn_color = config.BUTTON_HOVER_COLOR if hover else config.BUTTON_COLOR
            pygame.draw.rect(screen, btn_color, btn["rect"], border_radius=5)
            screen.blit(btn["text_surface"], btn["text_rect"])

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.font.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
