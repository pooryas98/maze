# main.py

import pygame
import sys
import argparse
import config  # Import configuration constants

from src.maze_generator import create_maze
from ui.maze_display import MazeDisplay
from ui.settings_window import SettingsWindow # Import the SettingsWindow class

# Import solver functions (assuming they are in src/solvers/)
from src.solvers.bfs_solver import solve_bfs_step_by_step
from src.solvers.dfs_solver import solve_dfs_step_by_step
from src.solvers.astar_solver import solve_astar_step_by_step

# --- Solver Function Mapping ---
# Map solver names (from config) to their respective functions
SOLVERS = {
    "BFS": solve_bfs_step_by_step,
    "DFS": solve_dfs_step_by_step,
    "A*": solve_astar_step_by_step,
    # Add other solvers here if implemented
}

# --- Helper Function for Layout Updates ---

def _update_layout_elements(screen, screen_width, screen_height, maze_render_width, maze_render_height,
                            cell_size, is_fullscreen, maze_display, buttons, button_defs, button_font):
    """
    Recalculates drawing offsets and button positions based on current screen/maze size.
    Updates the MazeDisplay instance and button rects.
    """
    # Calculate Maze Drawing Offset for Centering
    available_height_for_maze = screen_height - (0 if is_fullscreen else config.CONTROL_PANEL_HEIGHT)
    offset_x = max(0, (screen_width - maze_render_width) // 2)
    offset_y = max(0, (available_height_for_maze - maze_render_height) // 2)

    # Update MazeDisplay instance with new screen, offsets, and potentially cell size
    if maze_display:
        maze_display.screen = screen
        maze_display.offset_x = offset_x
        maze_display.offset_y = offset_y
        maze_display.cell_size = cell_size # Update cell size if it changed

    # --- Recalculate Button Positions ---
    # Calculate standard button dimensions based on font and padding
    max_text_width = 0
    for btn_def in button_defs:
        text_surface = button_font.render(btn_def["text"], True, config.BUTTON_TEXT_COLOR)
        max_text_width = max(max_text_width, text_surface.get_rect().width)

    button_width = max_text_width + config.BUTTON_PADDING * 2
    button_height = button_font.get_height() + config.BUTTON_PADDING * 2
    button_spacing = config.BUTTON_PADDING * 2 # Spacing between buttons

    # Calculate total width needed for all buttons and center them
    total_buttons_width = (button_width * len(button_defs)) + (button_spacing * (len(button_defs) - 1))
    start_x = max(config.BUTTON_PADDING, (screen_width - total_buttons_width) // 2) # Ensure buttons don't overlap left edge
    button_y = screen_height - config.CONTROL_PANEL_HEIGHT + (config.CONTROL_PANEL_HEIGHT - button_height) // 2

    # Update each button's Rect and text position
    for i, btn in enumerate(buttons):
        btn["rect"] = pygame.Rect(
            start_x + i * (button_width + button_spacing),
            button_y,
            button_width,
            button_height
        )
        # Re-render text surface in case font changed (though unlikely here)
        btn["text_surface"] = button_font.render(button_defs[i]["text"], True, config.BUTTON_TEXT_COLOR)
        btn["text_rect"] = btn["text_surface"].get_rect(center=btn["rect"].center)

    # Update window caption
    maze_w = maze_render_width // cell_size if cell_size > 0 else 0
    maze_h = maze_render_height // cell_size if cell_size > 0 else 0
    pygame.display.set_caption(f"Maze ({maze_w}x{maze_h}) - Cell: {cell_size}px - Solver: {config.DEFAULT_SOLVER}") # Update caption later with actual solver

    return offset_x, offset_y


# --- Main Application ---

def main():
    parser = argparse.ArgumentParser(description="Generate and display a maze with AI solving.")
    parser.add_argument("--width", type=int, default=config.DEFAULT_WIDTH,
                        help=f"Width of the maze in cells (1 < width <= {config.MAX_MAZE_WIDTH}).")
    parser.add_argument("--height", type=int, default=config.DEFAULT_HEIGHT,
                        help=f"Height of the maze in cells (1 < height <= {config.MAX_MAZE_HEIGHT}).")
    parser.add_argument("--cell_size", type=int, default=config.DEFAULT_CELL_SIZE,
                        help="Size of each cell in pixels. Default (<=0) fits to screen.")
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode.")
    args = parser.parse_args()

    # Validate initial dimensions from args or config defaults
    maze_width = max(2, min(args.width, config.MAX_MAZE_WIDTH))
    maze_height = max(2, min(args.height, config.MAX_MAZE_HEIGHT))
    user_cell_size = args.cell_size # Store user's preference

    # --- Pygame Initialization ---
    pygame.init()
    pygame.font.init()
    button_font = pygame.font.Font(None, 30) # Font for UI buttons
    settings_ui_font = pygame.font.Font(None, 32) # Font for settings window

    # --- Display Info ---
    try:
        display_info = pygame.display.Info()
        native_screen_w = display_info.current_w
        native_screen_h = display_info.current_h
        print(f"Detected screen resolution: {native_screen_w}x{native_screen_h}")
    except pygame.error as e:
        print(f"Warning: Could not get display info ({e}). Using fallback 800x600.")
        native_screen_w, native_screen_h = 800, 600

    # --- Maze Generation ---
    maze_grid, start_node, end_node = create_maze(maze_width, maze_height)
    if not maze_grid:
        print("Error: Failed to generate maze. Exiting.")
        pygame.quit()
        sys.exit()

    grid_render_height = len(maze_grid)
    grid_render_width = len(maze_grid[0]) if grid_render_height > 0 else 0

    # --- Determine Cell Size ---
    if user_cell_size <= 0: # Auto-calculate optimal size
        target_w = native_screen_w
        # Subtract panel height for vertical calculation ONLY if windowed
        target_h = native_screen_h - (0 if args.fullscreen else config.CONTROL_PANEL_HEIGHT)
        padding = 1.0 if args.fullscreen else config.AUTO_SIZE_PADDING_FACTOR

        # Calculate max cell size based on fitting within padded screen dimensions
        max_cell_w = (target_w * padding) // grid_render_width if grid_render_width > 0 else config.FALLBACK_CELL_SIZE
        max_cell_h = (target_h * padding) // grid_render_height if grid_render_height > 0 else config.FALLBACK_CELL_SIZE

        cell_size = max(config.MIN_CELL_SIZE, int(min(max_cell_w, max_cell_h)))
        print(f"Auto-calculated cell size: {cell_size}px")
    else:
        cell_size = max(config.MIN_CELL_SIZE, user_cell_size)

    # --- Determine Screen/Window Size ---
    maze_render_width = grid_render_width * cell_size
    maze_render_height = grid_render_height * cell_size

    if args.fullscreen:
        screen_width = native_screen_w
        screen_height = native_screen_h
        screen_flags = pygame.FULLSCREEN | pygame.SCALED
    else:
        # Window size is maze + control panel
        screen_width = maze_render_width
        screen_height = maze_render_height + config.CONTROL_PANEL_HEIGHT
        screen_flags = pygame.RESIZABLE

    # --- Screen Setup ---
    print(f"Setting display mode: {screen_width}x{screen_height} Flags: {screen_flags}")
    screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)
    # Update dimensions if OS adjusted them (e.g., fullscreen)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    print(f"Actual screen surface size: {screen_width}x{screen_height}")

    # --- Initialize Maze Display ---
    # Offsets calculated later by _update_layout_elements
    maze_display = MazeDisplay(screen, maze_grid, cell_size, start_node, end_node, 0, 0)
    maze_display.set_ai_solve_delay(config.MAX_DELAY_MS // 2) # Start with medium speed

    # --- Button Definitions ---
    button_defs = [
        {"text": "Regenerate (R)", "key": pygame.K_r, "action": "regenerate"},
        {"text": "Solve (S)", "key": pygame.K_s, "action": "solve"},
        {"text": "Settings (G)", "key": pygame.K_g, "action": "settings"},
        {"text": "Exit (ESC)", "key": pygame.K_ESCAPE, "action": "exit"}
    ]
    buttons = [{"rect": None, "text_surface": None, "text_rect": None, "action": b["action"]} for b in button_defs]

    # --- Calculate Initial Layout ---
    offset_x, offset_y = _update_layout_elements(screen, screen_width, screen_height, maze_render_width, maze_render_height,
                                                 cell_size, args.fullscreen, maze_display, buttons, button_defs, button_font)

    # --- Solver and Settings State ---
    current_solver_name = config.DEFAULT_SOLVER
    settings_window = None # Holds the SettingsWindow instance when open

    # Callback function for the settings window speed slider
    def handle_speed_change(new_delay_ms):
        """Callback to update MazeDisplay's speed."""
        if maze_display:
            maze_display.set_ai_solve_delay(new_delay_ms)

    # --- Game Loop ---
    running = True
    clock = pygame.time.Clock()

    while running:
        dt = clock.tick(60) # Limit frame rate
        mouse_pos = pygame.mouse.get_pos()

        # --- Handle Settings Window ---
        if settings_window:
            action_result = None
            for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                     running = False
                     break
                 # Pass event to settings handler
                 action_result = settings_window.handle_event(event)
                 if action_result: # If save/cancel/escape occurred
                     break
            if not running: break

            if action_result:
                action_type = action_result.get("action")
                if action_type == "save":
                    new_width = action_result["width"]
                    new_height = action_result["height"]
                    new_solver_name = action_result["solver"]
                    print(f"Applying Settings: W={new_width}, H={new_height}, Solver={new_solver_name}")

                    # Update game state
                    maze_width = new_width
                    maze_height = new_height
                    current_solver_name = new_solver_name
                    # Speed is already updated via callback

                    # Regenerate Maze
                    maze_grid, start_node, end_node = create_maze(maze_width, maze_height)
                    if not maze_grid:
                         print("Error generating maze with new dimensions. Keeping old maze.")
                         # Revert settings? Or just close window? For now, just close.
                    else:
                        grid_render_height = len(maze_grid)
                        grid_render_width = len(maze_grid[0])

                        # Recalculate Cell Size (if auto) and Render Dimensions
                        if user_cell_size <= 0:
                            target_w = native_screen_w
                            target_h = native_screen_h - (0 if args.fullscreen else config.CONTROL_PANEL_HEIGHT)
                            padding = 1.0 if args.fullscreen else config.AUTO_SIZE_PADDING_FACTOR
                            max_cell_w = (target_w * padding) // grid_render_width if grid_render_width > 0 else config.FALLBACK_CELL_SIZE
                            max_cell_h = (target_h * padding) // grid_render_height if grid_render_height > 0 else config.FALLBACK_CELL_SIZE
                            cell_size = max(config.MIN_CELL_SIZE, int(min(max_cell_w, max_cell_h)))
                            print(f"Auto-recalculated cell size: {cell_size}px")
                        # else: cell_size remains user specified or previous auto-calc

                        maze_render_width = grid_render_width * cell_size
                        maze_render_height = grid_render_height * cell_size

                        # Update screen size if necessary (windowed mode)
                        if not args.fullscreen:
                            new_screen_width = maze_render_width
                            new_screen_height = maze_render_height + config.CONTROL_PANEL_HEIGHT
                            # Only resize if dimensions actually changed significantly
                            if new_screen_width != screen_width or new_screen_height != screen_height:
                                screen_width = new_screen_width
                                screen_height = new_screen_height
                                screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)
                                print(f"Resized window to: {screen_width}x{screen_height}")


                        # Update Maze Display with new grid, start, end
                        maze_display.set_maze(maze_grid, start_node, end_node)

                        # Update Layout (offsets, buttons) for new dimensions
                        offset_x, offset_y = _update_layout_elements(
                            screen, screen_width, screen_height, maze_render_width, maze_render_height,
                            cell_size, args.fullscreen, maze_display, buttons, button_defs, button_font
                        )
                        # Update caption explicitly with new solver name
                        pygame.display.set_caption(f"Maze ({maze_width}x{maze_height}) - Cell: {cell_size}px - Solver: {current_solver_name}")


                    settings_window = None # Close settings window

                elif action_type == "cancel":
                    # Restore original speed if it was changed
                    handle_speed_change(settings_window.initial_delay_ms)
                    settings_window = None # Close settings window

            # --- Draw Settings Window ---
            if settings_window: # Check if it still exists (wasn't closed by action)
                # Draw semi-transparent overlay
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                # Draw the settings window itself
                settings_window.draw(screen)
                pygame.display.flip()
                continue # Skip rest of main loop while settings are open

        # --- Handle Normal Game Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Pass timer event to MazeDisplay
            if event.type == config.AI_SOLVE_STEP_EVENT:
                maze_display.handle_event(event)

            # Handle window resize events (only in windowed mode)
            if event.type == pygame.VIDEORESIZE and not args.fullscreen:
                screen_width = event.w
                screen_height = event.h
                # Ensure screen size is not smaller than maze + panel
                screen_width = max(screen_width, maze_render_width)
                screen_height = max(screen_height, maze_render_height + config.CONTROL_PANEL_HEIGHT)
                screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)
                print(f"Window resized by user to: {screen_width}x{screen_height}")

                # Update layout for new window size
                offset_x, offset_y = _update_layout_elements(
                     screen, screen_width, screen_height, maze_render_width, maze_render_height,
                     cell_size, args.fullscreen, maze_display, buttons, button_defs, button_font
                )

            # Handle Keyboard Input
            if event.type == pygame.KEYDOWN:
                action = None
                for i, btn_def in enumerate(button_defs):
                    if event.key == btn_def["key"]:
                        action = btn_def["action"]
                        break
                if action == "exit": running = False
                elif action == "regenerate":
                    print("Regenerating maze (Key)...")
                    maze_grid, start_node, end_node = create_maze(maze_width, maze_height)
                    if maze_grid: maze_display.set_maze(maze_grid, start_node, end_node)
                elif action == "solve":
                    print(f"Starting AI solve ({current_solver_name}) (Key)...")
                    solver_func = SOLVERS.get(current_solver_name, solve_bfs_step_by_step) # Fallback needed?
                    maze_display.start_ai_solve(solver_function=solver_func)
                elif action == "settings":
                    print("Opening settings...")
                    settings_window = SettingsWindow(
                        screen_width, screen_height,
                        maze_width, maze_height,
                        maze_display.get_ai_solve_delay(),
                        handle_speed_change, # Pass the callback
                        current_solver_name,
                        settings_ui_font # Pass the font
                    )

            # Handle Mouse Clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    action = None
                    for btn in buttons:
                        if btn["rect"] and btn["rect"].collidepoint(mouse_pos):
                            action = btn["action"]
                            break
                    if action == "exit": running = False
                    elif action == "regenerate":
                        print("Regenerating maze (Button)...")
                        maze_grid, start_node, end_node = create_maze(maze_width, maze_height)
                        if maze_grid: maze_display.set_maze(maze_grid, start_node, end_node)
                    elif action == "solve":
                         print(f"Starting AI solve ({current_solver_name}) (Button)...")
                         solver_func = SOLVERS.get(current_solver_name, solve_bfs_step_by_step)
                         maze_display.start_ai_solve(solver_function=solver_func)
                    elif action == "settings":
                        print("Opening settings...")
                        settings_window = SettingsWindow(
                            screen_width, screen_height,
                            maze_width, maze_height,
                            maze_display.get_ai_solve_delay(),
                            handle_speed_change,
                            current_solver_name,
                            settings_ui_font
                        )

        # --- Drawing ---
        # Background
        screen.fill(config.BACKGROUND_COLOR)

        # Maze
        maze_display.draw()

        # Control Panel Background (only if not fullscreen? Or always draw?)
        # Always draw for consistent look, maze offset handles positioning.
        panel_rect = pygame.Rect(0, screen_height - config.CONTROL_PANEL_HEIGHT, screen_width, config.CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(screen, config.BACKGROUND_COLOR, panel_rect)

        # Draw Buttons
        for i, btn in enumerate(buttons):
             if btn["rect"]: # Ensure rect exists
                 is_hover = btn["rect"].collidepoint(mouse_pos)
                 btn_color = config.BUTTON_HOVER_COLOR if is_hover else config.BUTTON_COLOR
                 pygame.draw.rect(screen, btn_color, btn["rect"], border_radius=5)
                 if btn["text_surface"] and btn["text_rect"]:
                     screen.blit(btn["text_surface"], btn["text_rect"])

        # Update Display
        pygame.display.flip()

    # --- Cleanup ---
    pygame.font.quit()
    pygame.quit()
    print("Exiting application.")
    sys.exit()

if __name__ == "__main__":
    main()