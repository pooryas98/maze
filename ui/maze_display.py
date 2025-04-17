import pygame
import config # Import the configuration

# Define colors - REMOVED, now imported from config
# WALL_COLOR = (0, 0, 0)       # Black
# PATH_COLOR = (255, 255, 255) # White

def draw_maze(screen, maze_grid, cell_size, offset_x=0, offset_y=0,
              solution_path=None, visited_cells=None):
    """Draws the maze grid onto the Pygame screen with offsets, visited cells, and solution path."""
    grid_height = len(maze_grid)
    grid_width = len(maze_grid[0]) if grid_height > 0 else 0
    # Convert to sets for efficient lookup
    solution_path_set = set(solution_path) if solution_path else set()
    visited_cells_set = set(visited_cells) if visited_cells else set()

    for y in range(grid_height):
        for x in range(grid_width):
            # Apply offset to the drawing position
            draw_x = offset_x + x * cell_size
            draw_y = offset_y + y * cell_size
            rect = pygame.Rect(draw_x, draw_y, cell_size, cell_size)
            cell_coords = (x, y) # Store coords for lookup

            if maze_grid[y][x] == '#':
                pygame.draw.rect(screen, config.WALL_COLOR, rect)
            else: # Path
                # Determine path color: Solution > Visited > Normal Path
                if cell_coords in solution_path_set:
                    color = config.SOLUTION_PATH_COLOR
                elif cell_coords in visited_cells_set:
                    color = config.VISITED_COLOR
                else:
                    color = config.PATH_COLOR
                pygame.draw.rect(screen, color, rect) 