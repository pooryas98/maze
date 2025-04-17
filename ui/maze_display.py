import pygame
import config # Import the configuration

# Define colors - REMOVED, now imported from config
# WALL_COLOR = (0, 0, 0)       # Black
# PATH_COLOR = (255, 255, 255) # White

def draw_maze(screen, maze_grid, cell_size, offset_x=0, offset_y=0):
    """Draws the maze grid onto the Pygame screen with offsets."""
    grid_height = len(maze_grid)
    grid_width = len(maze_grid[0]) if grid_height > 0 else 0

    for y in range(grid_height):
        for x in range(grid_width):
            # Apply offset to the drawing position
            draw_x = offset_x + x * cell_size
            draw_y = offset_y + y * cell_size
            rect = pygame.Rect(draw_x, draw_y, cell_size, cell_size)
            if maze_grid[y][x] == '#':
                pygame.draw.rect(screen, config.WALL_COLOR, rect)
            else: # Path
                pygame.draw.rect(screen, config.PATH_COLOR, rect) 