# src/maze_generator.py

import random

def create_maze(width, height):
    """
    Generates a maze using the Randomized Depth-First Search algorithm.
    Also determines unique start and end points on the edges.

    Args:
        width (int): The width of the maze (number of cells).
        height (int): The height of the maze (number of cells).

    Returns:
        tuple: (list[list[str]], tuple[int, int], tuple[int, int])
               - The 2D list representing the maze grid (' ' for path, '#' for wall).
               - The (x, y) coordinates of the start cell in the grid.
               - The (x, y) coordinates of the end cell in the grid.
               Returns (None, None, None) if width or height is too small.
    """
    if width <= 0 or height <= 0:
        print("Error: Maze dimensions must be positive.")
        return None, None, None

    # Grid dimensions include walls
    grid_height = 2 * height + 1
    grid_width = 2 * width + 1
    grid = [['#' for _ in range(grid_width)] for _ in range(grid_height)]

    # Stack for DFS traversal
    stack = []

    # Choose a random starting cell (internal cell grid coordinates 0..width-1, 0..height-1)
    start_cell_x, start_cell_y = random.randint(0, width - 1), random.randint(0, height - 1)
    # Convert to grid coordinates (where paths exist)
    start_grid_x, start_grid_y = 2 * start_cell_x + 1, 2 * start_cell_y + 1

    grid[start_grid_y][start_grid_x] = ' '  # Mark starting cell as path
    stack.append((start_grid_x, start_grid_y))

    # --- Randomized DFS for maze generation ---
    while stack:
        current_x, current_y = stack[-1]
        neighbors = []

        # Check potential neighbors (cells 2 units away in grid coordinates)
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = current_x + dx, current_y + dy
            # Check bounds (stay within the path grid) and if the neighbor cell is unvisited
            if 0 < ny < grid_height and 0 < nx < grid_width and grid[ny][nx] == '#':
                 neighbors.append((nx, ny)) # Add the cell coordinates

        if neighbors:
            # Choose a random neighbor cell
            next_x, next_y = random.choice(neighbors)

            # Carve path to the neighbor: remove wall between current and next cell
            wall_x, wall_y = current_x + (next_x - current_x) // 2, current_y + (next_y - current_y) // 2
            grid[wall_y][wall_x] = ' '  # Remove wall
            grid[next_y][next_x] = ' '  # Mark next cell as path

            # Push the neighbor cell onto the stack
            stack.append((next_x, next_y))
        else:
            # Backtrack if no unvisited neighbors
            stack.pop()

    # --- Create Entry and Exit Points ---
    # Define potential edge cells (in grid coordinates)
    edge_cells = []
    # Top edge (y=1)
    edge_cells.extend([(x, 1) for x in range(1, grid_width, 2)])
    # Bottom edge (y=grid_height-2)
    edge_cells.extend([(x, grid_height - 2) for x in range(1, grid_width, 2)])
    # Left edge (x=1)
    edge_cells.extend([(1, y) for y in range(3, grid_height - 2, 2)]) # Avoid overlapping corners
    # Right edge (x=grid_width-2)
    edge_cells.extend([(grid_width - 2, y) for y in range(3, grid_height - 2, 2)])

    # Ensure there are enough edge cells to pick from
    if len(edge_cells) < 2:
         # Fallback for very small mazes (e.g., 1x1) - use corners if necessary
         if width == 1 and height == 1:
             start_node = (1, 0) # Top wall opening
             end_node = (1, 2)   # Bottom wall opening
             grid[0][1] = ' '
             grid[2][1] = ' '
             return grid, start_node, end_node
         elif width == 1: # 1xN
             start_node = (1, 0) # Top wall opening
             end_node = (1, grid_height - 1) # Bottom wall opening
             grid[0][1] = ' '
             grid[grid_height - 1][1] = ' '
             return grid, start_node, end_node
         elif height == 1: # Nx1
             start_node = (0, 1) # Left wall opening
             end_node = (grid_width - 1, 1) # Right wall opening
             grid[1][0] = ' '
             grid[1][grid_width - 1] = ' '
             return grid, start_node, end_node
         else:
             # This case shouldn't happen with the calculation above, but as a safeguard
             print("Warning: Could not find distinct edge cells for start/end.")
             # Use the old fixed points as a last resort
             start_node = (0, 1)
             end_node = (grid_width - 1, grid_height - 2)
             grid[1][0] = ' '
             grid[grid_height - 2][grid_width - 1] = ' '
             return grid, start_node, end_node


    # Choose two distinct random edge cells
    start_cell_grid_coords, end_cell_grid_coords = random.sample(edge_cells, 2)

    # Determine corresponding wall opening coordinates
    sx, sy = start_cell_grid_coords
    ex, ey = end_cell_grid_coords

    start_node = list(start_cell_grid_coords) # Use list for mutability
    if sy == 1: start_node[1] -= 1 # Top edge -> open wall at y=0
    elif sy == grid_height - 2: start_node[1] += 1 # Bottom edge -> open wall at y=grid_height-1
    elif sx == 1: start_node[0] -= 1 # Left edge -> open wall at x=0
    elif sx == grid_width - 2: start_node[0] += 1 # Right edge -> open wall at x=grid_width-1
    start_node = tuple(start_node) # Convert back to tuple

    end_node = list(end_cell_grid_coords)
    if ey == 1: end_node[1] -= 1 # Top edge
    elif ey == grid_height - 2: end_node[1] += 1 # Bottom edge
    elif ex == 1: end_node[0] -= 1 # Left edge
    elif ex == grid_width - 2: end_node[0] += 1 # Right edge
    end_node = tuple(end_node)

    # Carve openings in the outer wall
    grid[start_node[1]][start_node[0]] = ' '
    grid[end_node[1]][end_node[0]] = ' '

    print(f"Maze Generator: Start Node={start_node}, End Node={end_node}")

    return grid, start_node, end_node