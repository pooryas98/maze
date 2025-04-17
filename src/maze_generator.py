import random

def create_maze(width, height):
    """
    Generates a maze using the Randomized Depth-First Search algorithm.

    Args:
        width (int): The width of the maze (number of cells).
        height (int): The height of the maze (number of cells).

    Returns:
        list[list[str]]: A 2D list representing the maze grid.
                         ' ' represents paths, '#' represents walls.
    """
    # Initialize grid with walls
    # Grid dimensions will be (2*height + 1) x (2*width + 1) to accommodate walls
    grid_height = 2 * height + 1
    grid_width = 2 * width + 1
    grid = [['#' for _ in range(grid_width)] for _ in range(grid_height)]

    # Stack for DFS
    stack = []

    # Choose a random starting cell (must be odd coordinates for cell centers)
    start_x, start_y = random.randint(0, width - 1), random.randint(0, height - 1)
    cell_x, cell_y = 2 * start_x + 1, 2 * start_y + 1
    grid[cell_y][cell_x] = ' '  # Mark starting cell as path
    stack.append((cell_x, cell_y))

    while stack:
        current_x, current_y = stack[-1]
        neighbors = []

        # Check potential neighbors (up, down, left, right)
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = current_x + dx, current_y + dy
            # Check bounds and if the neighbor is unvisited (still a wall)
            if 0 < ny < grid_height and 0 < nx < grid_width and grid[ny][nx] == '#':
                 # Check if the cell it leads to is also a wall (ensures it's not already part of the path)
                 if grid[ny][nx] == '#':
                    neighbors.append((nx, ny))

        if neighbors:
            # Choose a random neighbor
            next_x, next_y = random.choice(neighbors)

            # Carve path to the neighbor
            wall_x, wall_y = current_x + (next_x - current_x) // 2, current_y + (next_y - current_y) // 2
            grid[wall_y][wall_x] = ' '  # Remove wall between current and next cell
            grid[next_y][next_x] = ' '  # Mark next cell as path

            # Push the neighbor onto the stack
            stack.append((next_x, next_y))
        else:
            # Backtrack
            stack.pop()

    # Add entry and exit points (optional, placing at top-left and bottom-right)
    grid[1][0] = ' '  # Entrance
    grid[grid_height - 2][grid_width - 1] = ' ' # Exit

    return grid

# Remove the print_maze function
# def print_maze(grid):
#     \"\"\"Prints the maze grid to the console.\"\"\"
#     for row in grid:
#         print("".join(row))

# Remove the main execution block
# if __name__ == "__main__":
#     maze_width = 10
#     maze_height = 10
#     maze = create_maze(maze_width, maze_height)
#     print_maze(maze)