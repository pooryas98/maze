import pygame
import sys
import argparse
import config # Import the configuration

from src.maze_generator import create_maze
from ui.maze_display import draw_maze
from src.solvers.bfs_solver import find_path_bfs # Import the solver

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

    # --- Button Setup ---
    button_font = pygame.font.Font(None, 30) # Fallback Pygame font

    # --- Regenerate Button --- 
    regen_button_text_surface = button_font.render("Regenerate (R)", True, config.BUTTON_TEXT_COLOR)
    regen_button_text_rect = regen_button_text_surface.get_rect()
    regen_button_rect = pygame.Rect(
        0, # Left (set later)
        screen_height - config.CONTROL_PANEL_HEIGHT + (config.CONTROL_PANEL_HEIGHT - regen_button_text_rect.height - config.BUTTON_PADDING * 2) // 2,
        regen_button_text_rect.width + config.BUTTON_PADDING * 2,
        regen_button_text_rect.height + config.BUTTON_PADDING * 2
    )

    # --- Solve Button --- 
    solve_button_text_surface = button_font.render("Solve by AI (S)", True, config.BUTTON_TEXT_COLOR)
    solve_button_text_rect = solve_button_text_surface.get_rect()
    solve_button_rect = pygame.Rect(
        0, # Left (set later)
        regen_button_rect.top, # Align vertically with regenerate button
        solve_button_text_rect.width + config.BUTTON_PADDING * 2,
        solve_button_text_rect.height + config.BUTTON_PADDING * 2
    )

    # --- Position Buttons --- 
    total_button_width = regen_button_rect.width + solve_button_rect.width + config.BUTTON_PADDING # Add padding between buttons
    start_x = (screen_width - total_button_width) // 2
    regen_button_rect.left = start_x
    solve_button_rect.left = regen_button_rect.right + config.BUTTON_PADDING

    # Center the text within the buttons
    regen_button_text_rect.center = regen_button_rect.center
    solve_button_text_rect.center = solve_button_rect.center

    # --- Solver State --- 
    solution_path = None
    visited_cells = None
    solving_in_progress = False # Optional: could be used for visual feedback
    solve_requested = False

    # --- Game loop ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        regen_button_hover = regen_button_rect.collidepoint(mouse_pos)
        solve_button_hover = solve_button_rect.collidepoint(mouse_pos)

        # --- Handle Solver Request ---
        if solve_requested:
            print("Solving maze...")
            solving_in_progress = True
            solution_path, visited_cells = find_path_bfs(maze_grid)
            solving_in_progress = False
            solve_requested = False # Reset request flag
            if solution_path:
                print(f"Solution found! Path length: {len(solution_path)}")
            else:
                print("No solution found.")

        # --- Handle Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                screen_width = event.w
                screen_height = event.h
                screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)
                # Recalculate offsets and button positions on resize
                available_height_for_maze = screen_height - config.CONTROL_PANEL_HEIGHT
                offset_x = max(0, (screen_width - maze_render_width) // 2)
                offset_y = max(0, (available_height_for_maze - maze_render_height) // 2)
                start_x = (screen_width - total_button_width) // 2
                regen_button_rect.left = start_x
                regen_button_rect.top = screen_height - config.CONTROL_PANEL_HEIGHT + (config.CONTROL_PANEL_HEIGHT - regen_button_text_rect.height - config.BUTTON_PADDING * 2) // 2
                solve_button_rect.left = regen_button_rect.right + config.BUTTON_PADDING
                solve_button_rect.top = regen_button_rect.top
                regen_button_text_rect.center = regen_button_rect.center
                solve_button_text_rect.center = solve_button_rect.center

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r: # Regenerate
                    print("Regenerating maze (R key)...")
                    maze_grid = create_maze(maze_width, maze_height)
                    solution_path = None # Clear solution on regenerate
                    visited_cells = None
                elif event.key == pygame.K_s: # Solve
                    if not solution_path:
                         solve_requested = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse click
                    if regen_button_hover:
                        print("Regenerating maze (button click)...")
                        maze_grid = create_maze(maze_width, maze_height)
                        solution_path = None # Clear solution on regenerate
                        visited_cells = None
                    elif solve_button_hover:
                         if not solution_path: # Only solve if not already solved
                            solve_requested = True

        # Draw everything
        screen.fill(config.BACKGROUND_COLOR)

        # Draw the maze itself, passing solver data
        draw_maze(screen, maze_grid, cell_size, offset_x, offset_y,
                  solution_path=solution_path, visited_cells=visited_cells)

        # Draw the control panel background covering the bottom area
        panel_rect = pygame.Rect(0, screen_height - config.CONTROL_PANEL_HEIGHT, screen_width, config.CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(screen, config.BACKGROUND_COLOR, panel_rect) # Draw panel background

        # Draw the Regenerate button
        regen_button_color = config.BUTTON_HOVER_COLOR if regen_button_hover else config.BUTTON_COLOR
        pygame.draw.rect(screen, regen_button_color, regen_button_rect, border_radius=5)
        screen.blit(regen_button_text_surface, regen_button_text_rect)

        # Draw the Solve button
        solve_button_color = config.BUTTON_HOVER_COLOR if solve_button_hover else config.BUTTON_COLOR
        pygame.draw.rect(screen, solve_button_color, solve_button_rect, border_radius=5)
        screen.blit(solve_button_text_surface, solve_button_text_rect)

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.font.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 