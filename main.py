import pygame
import sys
import argparse

from src.maze_generator import create_maze
from ui.maze_display import draw_maze

# Constants
DEFAULT_WIDTH = 100
DEFAULT_HEIGHT = 100
DEFAULT_CELL_SIZE = 5
BACKGROUND_COLOR = (100, 100, 100) # Grey background outside maze

def main():
    parser = argparse.ArgumentParser(description="Generate and display a maze.")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="Width of the maze in cells.")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="Height of the maze in cells.")
    parser.add_argument("--cell_size", type=int, default=DEFAULT_CELL_SIZE, help="Size of each cell in pixels.")
    args = parser.parse_args()

    maze_width = args.width
    maze_height = args.height
    cell_size = args.cell_size

    # Generate the maze data
    maze_grid = create_maze(maze_width, maze_height)

    # Initialize Pygame
    pygame.init()

    # Calculate screen dimensions based on grid and cell size
    grid_render_height = len(maze_grid)
    grid_render_width = len(maze_grid[0]) if grid_render_height > 0 else 0
    screen_width = grid_render_width * cell_size
    screen_height = grid_render_height * cell_size

    # Set up the display
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"Maze ({maze_width}x{maze_height})")

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        draw_maze(screen, maze_grid, cell_size)

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 