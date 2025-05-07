import random
import config

# Define character representations used internally by the generator for grid cells
# This helps decouple it from direct Pygame color drawing during generation.
# Solvers can then also expect these characters.
_WALL_CHAR = '#'
_PATH_CHAR = ' '

def create_maze(logical_width, logical_height):
    """
    Generates a maze grid using a randomized Depth-First Search algorithm (Iterative version).
    The maze is generated on a grid where actual paths are cells, and walls are also cells.
    A logical_width x logical_height maze results in a (2*logical_width+1) x (2*logical_height+1) character grid.

    Args:
        logical_width (int): The number of "open cells" horizontally.
        logical_height (int): The number of "open cells" vertically.

    Returns:
        tuple: (grid, start_node, end_node)
               grid (list of list of str): The character-based maze grid (_WALL_CHAR or _PATH_CHAR).
               start_node (tuple int, int): (x, y) coordinates of the start passage on the grid.
               end_node (tuple int, int): (x, y) coordinates of the end passage on the grid.
               Returns (None, None, None) if dimensions are invalid.
    """
    if not (isinstance(logical_width, int) and isinstance(logical_height, int) and \
            logical_width >= 1 and logical_height >= 1):
        print(f"Error (Maze Generator): Invalid maze dimensions. Width ({logical_width}) and Height ({logical_height}) must be integers >= 1.")
        return None, None, None

    # Calculate dimensions of the character grid
    # gw (grid_width) and gh (grid_height) include border walls.
    grid_w = 2 * logical_width + 1
    grid_h = 2 * logical_height + 1

    # Initialize grid with all walls
    grid = [[_WALL_CHAR for _ in range(grid_w)] for _ in range(grid_h)]

    # Stack for DFS, stores (x, y) coordinates in the character grid
    stack = []

    # Choose a random starting cell in the logical grid, convert to character grid coordinates
    # (sx_logic, sy_logic) are 0-indexed within the logical_width x logical_height space
    start_x_logic = random.randint(0, logical_width - 1)
    start_y_logic = random.randint(0, logical_height - 1)

    # Convert logical cell (start_x_logic, start_y_logic) to character grid cell coordinates
    # Character grid cells are at (2*lx+1, 2*ly+1)
    current_char_x, current_char_y = 2 * start_x_logic + 1, 2 * start_y_logic + 1

    grid[current_char_y][current_char_x] = _PATH_CHAR  # Mark starting cell as path
    stack.append((current_char_x, current_char_y))

    while stack:
        current_char_x, current_char_y = stack[-1]
        unvisited_neighbors = []

        # Check potential neighbors (2 cells away in character grid, representing adjacent logical cells)
        # Directions: (dx, dy) for character grid
        # (0, -2) -> Up, (0, 2) -> Down, (-2, 0) -> Left, (2, 0) -> Right
        for dx_char, dy_char in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            neighbor_char_x, neighbor_char_y = current_char_x + dx_char, current_char_y + dy_char

            # Check if neighbor is within grid bounds (excluding outer border, hence >0 and < grid_dim-1)
            # And if the neighbor cell itself (the target logical cell) is still a wall (unvisited)
            if 0 < neighbor_char_y < grid_h -1 and \
               0 < neighbor_char_x < grid_w -1 and \
               grid[neighbor_char_y][neighbor_char_x] == _WALL_CHAR:
                unvisited_neighbors.append((neighbor_char_x, neighbor_char_y))

        if unvisited_neighbors:
            # Choose a random unvisited neighbor
            next_char_x, next_char_y = random.choice(unvisited_neighbors)

            # Carve path to the neighbor:
            # 1. Mark the wall cell between current and neighbor as path
            wall_to_remove_x = current_char_x + (next_char_x - current_char_x) // 2
            wall_to_remove_y = current_char_y + (next_char_y - current_char_y) // 2
            grid[wall_to_remove_y][wall_to_remove_x] = _PATH_CHAR

            # 2. Mark the neighbor cell itself as path
            grid[next_char_y][next_char_x] = _PATH_CHAR

            # Push neighbor to stack
            stack.append((next_char_x, next_char_y))
        else:
            # No unvisited neighbors, backtrack
            stack.pop()

    # Create openings for start and end nodes on the outer border
    # List potential entry/exit points (cells that are paths and adjacent to border)
    
    # Potential edge cells for openings (these are logical cell coordinates, not char grid)
    # (col, row)
    edge_cells_logical = []
    # Top row (excluding corners, unless 1xN or Nx1)
    for i in range(logical_width): edge_cells_logical.append( (i, 0) )
    # Bottom row
    for i in range(logical_width): edge_cells_logical.append( (i, logical_height - 1) )
    # Left col (excluding already added top/bottom)
    for i in range(1, logical_height - 1): edge_cells_logical.append( (0, i) )
    # Right col
    for i in range(1, logical_height - 1): edge_cells_logical.append( (logical_width - 1, i) )
    
    # Handle very small mazes (1x1, 1xN, Nx1) where distinct edges are few
    if logical_width == 1 and logical_height == 1:
        # For 1x1, start top, end bottom is typical
        start_node_char_grid = (1, 0) # Opening above cell (1,1)
        end_node_char_grid = (1, grid_h - 1) # Opening below cell (1,1)
    elif not edge_cells_logical: # Should not happen if w,h >= 1
        print("Warning (Maze Generator): No edge cells identified. This is unexpected.")
        # Fallback: hardcode for a small case or return error
        start_node_char_grid = (1,0)
        end_node_char_grid = (grid_w-2, grid_h-1)
    else:
        # Ensure two distinct edge cells are chosen
        if len(edge_cells_logical) < 2: # e.g. 1x1 case handled above, this is for safety
             # Pick first, and last if available, or duplicate if only one
            chosen_logical_cells = [edge_cells_logical[0]]
            if len(edge_cells_logical) > 1 :
                chosen_logical_cells.append(edge_cells_logical[-1])
            else: # only one edge cell candidate, e.g. a 1x1 from a different path
                chosen_logical_cells.append(edge_cells_logical[0]) # duplicate, will be same start/end logical cell
        else:
            chosen_logical_cells = random.sample(edge_cells_logical, 2)

        start_logical_x, start_logical_y = chosen_logical_cells[0]
        end_logical_x, end_logical_y = chosen_logical_cells[1]

        # Determine character grid coordinates for openings based on logical edge cell
        def get_opening_coords(lx, ly, char_grid_w, char_grid_h, maze_logic_w, maze_logic_h):
            # Top edge
            if ly == 0: return (2 * lx + 1, 0)
            # Bottom edge
            if ly == maze_logic_h - 1: return (2 * lx + 1, char_grid_h - 1)
            # Left edge
            if lx == 0: return (0, 2 * ly + 1)
            # Right edge
            if lx == maze_logic_w - 1: return (char_grid_w - 1, 2 * ly + 1)
            # Should not be reached if lx,ly is a valid edge cell
            print(f"Warning (Maze Generator): Could not determine opening for logical cell ({lx},{ly})")
            return (2 * lx + 1, 0) # Fallback

        start_node_char_grid = get_opening_coords(start_logical_x, start_logical_y, grid_w, grid_h, logical_width, logical_height)
        end_node_char_grid = get_opening_coords(end_logical_x, end_logical_y, grid_w, grid_h, logical_width, logical_height)

        # Ensure start and end nodes are different if possible; if not, it's a very small maze
        # This check is more critical if the sampling could pick the same *opening point*
        # The chosen_logical_cells sample ensures two different logical cells.
        # If logical_width or logical_height is 1, they might map to points that are very close or "on top of each other" if not careful.
        # The get_opening_coords should handle this correctly by placing on distinct borders.
        # For a 2x1 maze: logical cells (0,0) and (1,0).
        # Start (0,0) -> opening (1,0). End (1,0) -> opening (3,0). These are distinct on top border.
        # If start (0,0) [top border], end (0,0) [left border], then (1,0) and (0,1) - distinct.
        # This seems okay.

    # Carve the start and end openings
    grid[start_node_char_grid[1]][start_node_char_grid[0]] = _PATH_CHAR
    grid[end_node_char_grid[1]][end_node_char_grid[0]] = _PATH_CHAR

    # The `start_node` and `end_node` returned should be these character grid coordinates
    # because the solver will operate on this character grid.
    print(f"Maze Generator: Dimensions logical=({logical_width}x{logical_height}), grid=({grid_w}x{grid_h})")
    print(f"Maze Generator: Start Node (char_grid)={start_node_char_grid}, End Node (char_grid)={end_node_char_grid}")

    return grid, start_node_char_grid, end_node_char_grid

if __name__ == '__main__':
    # Example usage:
    test_w, test_h = 5, 5
    maze, s, e = create_maze(test_w, test_h)
    if maze:
        print(f"Generated {test_w}x{test_h} maze. Start: {s}, End: {e}")
        for row in maze:
            print("".join(row))
    
    test_w_small, test_h_small = 1, 1
    maze_small, s_small, e_small = create_maze(test_w_small, test_h_small)
    if maze_small:
        print(f"\nGenerated {test_w_small}x{test_h_small} maze. Start: {s_small}, End: {e_small}")
        for row in maze_small:
            print("".join(row))

    test_w_rect, test_h_rect = 3, 1
    maze_rect, s_rect, e_rect = create_maze(test_w_rect, test_h_rect)
    if maze_rect:
        print(f"\nGenerated {test_w_rect}x{test_h_rect} maze. Start: {s_rect}, End: {e_rect}")
        for row in maze_rect:
            print("".join(row))