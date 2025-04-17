import pygame
import sys
import argparse
import config # Import the configuration

from src.maze_generator import create_maze
from ui.maze_display import draw_maze

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
    try:
        button_font = pygame.font.SysFont(None, 30) # Use default system font
    except Exception as e:
        print(f"Warning: Could not load system font ({e}). Using default Pygame font.")
        button_font = pygame.font.Font(None, 30) # Fallback Pygame font

    button_text_surface = button_font.render("Regenerate", True, config.BUTTON_TEXT_COLOR)
    button_text_rect = button_text_surface.get_rect()
    # Calculate button rect based on text size plus padding
    button_rect = pygame.Rect(
        0, # Left position (will be centered later)
        # Position button relative to the bottom of the screen
        screen_height - config.CONTROL_PANEL_HEIGHT + (config.CONTROL_PANEL_HEIGHT - button_text_rect.height - config.BUTTON_PADDING * 2) // 2,
        button_text_rect.width + config.BUTTON_PADDING * 2, # Width
        button_text_rect.height + config.BUTTON_PADDING * 2 # Height
    )
    # Center the button horizontally
    button_rect.centerx = screen_width // 2
    # Center the text within the button rect
    button_text_rect.center = button_rect.center

    # --- Game loop ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        button_hover = button_rect.collidepoint(mouse_pos)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r: # Add R key shortcut
                    print("Regenerating maze (R key)...")
                    maze_grid = create_maze(maze_width, maze_height)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and button_hover: # Left mouse click on button
                    print("Regenerating maze (button click)...")
                    maze_grid = create_maze(maze_width, maze_height)
                    # Note: No need to redraw here, the main draw below handles it

        # Draw everything
        screen.fill(config.BACKGROUND_COLOR)

        # Draw the maze itself, using the calculated offsets
        draw_maze(screen, maze_grid, cell_size, offset_x, offset_y)

        # Draw the control panel background covering the bottom area
        panel_rect = pygame.Rect(0, screen_height - config.CONTROL_PANEL_HEIGHT, screen_width, config.CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(screen, config.BACKGROUND_COLOR, panel_rect) # Draw panel background

        # Draw the button (position already calculated relative to panel)
        button_color = config.BUTTON_HOVER_COLOR if button_hover else config.BUTTON_COLOR
        pygame.draw.rect(screen, button_color, button_rect, border_radius=5)
        screen.blit(button_text_surface, button_text_rect)

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.font.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 