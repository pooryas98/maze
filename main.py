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
    # Allow user to specify cell_size, but default indicates auto-calculation
    parser.add_argument("--cell_size", type=int, default=config.DEFAULT_CELL_SIZE,
                        help="Size of each cell in pixels. Default (<=0) fits to screen.")
    args = parser.parse_args()

    maze_width = args.width
    maze_height = args.height
    user_cell_size = args.cell_size # Store user's preference

    # Initialize Pygame *before* getting display info
    pygame.init()
    pygame.font.init() # Initialize font module

    # --- Maze Generation ---
    maze_grid = create_maze(maze_width, maze_height)
    grid_render_height = len(maze_grid)
    grid_render_width = len(maze_grid[0]) if grid_render_height > 0 else 0

    # --- Determine Cell Size ---
    if user_cell_size <= 0: # If user didn't specify a positive cell size, calculate optimal
        try:
            # Get screen dimensions
            display_info = pygame.display.Info()
            screen_w = display_info.current_w
            screen_h = display_info.current_h

            # Calculate max cell size that fits within padding factor of the screen
            padding_factor = config.AUTO_SIZE_PADDING_FACTOR
            max_cell_w = (screen_w * padding_factor) // grid_render_width
            max_cell_h = (screen_h * padding_factor) // grid_render_height

            # Use the smaller of the two dimensions to ensure fit
            cell_size = max(config.MIN_CELL_SIZE, int(min(max_cell_w, max_cell_h))) # Ensure cell size is at least min
            print(f"Auto-calculated cell size: {cell_size}px")

        except pygame.error as e:
            print(f"Warning: Could not get display info ({e}). Using fallback cell size {config.FALLBACK_CELL_SIZE}.")
            cell_size = config.FALLBACK_CELL_SIZE # Fallback if display info fails
    else:
        cell_size = max(config.MIN_CELL_SIZE, user_cell_size) # Ensure user size is at least min

    # --- Screen Setup ---
    # Calculate final screen dimensions based on grid and determined cell size
    maze_render_width = grid_render_width * cell_size
    maze_render_height = grid_render_height * cell_size
    screen_width = maze_render_width
    # Add space for the control panel below the maze
    screen_height = maze_render_height + config.CONTROL_PANEL_HEIGHT

    # Set up the display
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"Maze ({maze_width}x{maze_height}) - Cell Size: {cell_size}px")

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
        maze_render_height + (config.CONTROL_PANEL_HEIGHT - button_text_rect.height - config.BUTTON_PADDING * 2) // 2, # Top position (centered vertically in panel)
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

        # Draw the maze itself (offset vertically by 0, horizontally by 0)
        draw_maze(screen, maze_grid, cell_size)

        # Draw the control panel background (optional, could just be screen background)
        panel_rect = pygame.Rect(0, maze_render_height, screen_width, config.CONTROL_PANEL_HEIGHT)
        # pygame.draw.rect(screen, (50, 50, 50), panel_rect) # Example: Darker grey panel

        # Draw the button
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