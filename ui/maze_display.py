import pygame
import config # Import the configuration

# Define colors - REMOVED, now imported from config
# WALL_COLOR = (0, 0, 0)       # Black
# PATH_COLOR = (255, 255, 255) # White

def draw_maze(screen, maze_grid, cell_size):
    """Draws the maze grid onto the Pygame screen."""
    grid_height = len(maze_grid)
    grid_width = len(maze_grid[0]) if grid_height > 0 else 0

    for y in range(grid_height):
        for x in range(grid_width):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            if maze_grid[y][x] == '#':
                pygame.draw.rect(screen, config.WALL_COLOR, rect)
            else: # Path
                pygame.draw.rect(screen, config.PATH_COLOR, rect) 