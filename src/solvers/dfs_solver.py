from collections import deque

def solve_dfs_step_by_step(grid):
    """
    Performs a step-by-step DFS search on the maze grid, yielding visited nodes.

    Args:
        grid (list[list[str]]): The maze grid where '#' is wall, ' ' is path.
                                 Tries to dynamically find entrance/exit on edges.

    Yields:
        tuple: (visited_set, current_path_segment, is_done, final_path)
            visited_set (set[tuple[int, int]]): Set of (x, y) coordinates visited so far.
            current_path_segment (list[tuple[int, int]]): The path segment being explored (DFS path).
            is_done (bool): True if the search is complete (found or failed).
            final_path (list[tuple[int, int]] or None): The complete path if found, else None.
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    if height == 0 or width == 0:
        yield set(), [], True, None # Indicate immediate completion, no path
        return

    # --- Find Entrance and Exit (Same logic as BFS) ---
    start_node = None
    end_node = None
    possible_starts = []
    possible_ends = []
    # Top edge
    for x in range(1, width - 1):
        if grid[0][x] == ' ': possible_starts.append((x, 0))
    # Bottom edge
    for x in range(1, width - 1):
        if grid[height - 1][x] == ' ': possible_ends.append((x, height - 1))
    # Left edge
    for y in range(1, height - 1):
        if grid[y][0] == ' ': possible_starts.append((0, y))
    # Right edge
    for y in range(1, height - 1):
        if grid[y][width - 1] == ' ': possible_ends.append((width - 1, y))
    # Corners if needed
    if not possible_starts:
        if grid[0][0] == ' ': possible_starts.append((0, 0))
        if grid[height-1][0] == ' ': possible_starts.append((0, height-1))
    if not possible_ends:
         if grid[0][width-1] == ' ': possible_ends.append((width-1, 0))
         if grid[height-1][width-1] == ' ': possible_ends.append((width-1, height-1))

    start_node = possible_starts[0] if possible_starts else None
    end_node = possible_ends[0] if possible_ends else None

    # Fallback
    if start_node is None and grid[1][0] == ' ': start_node = (0, 1)
    if end_node is None and grid[height - 2][width - 1] == ' ': end_node = (width-1, height-2)

    if start_node is None or end_node is None:
        print("Solver Error (DFS): Could not determine start or end node.")
        yield set(), [], True, None
        return

    print(f"Solver (DFS): Start={start_node}, End={end_node}")

    # --- DFS Implementation (Step-by-Step using explicit stack) ---
    stack = [(start_node, [start_node])] # Store (node, path_to_node)
    visited = {start_node}
    yield visited, [start_node], False, None # Initial state

    while stack:
        (current_x, current_y), current_path_segment = stack[-1] # Peek

        if (current_x, current_y) == end_node:
            yield visited, current_path_segment, True, current_path_segment # Found the exit
            return # Stop generation

        found_neighbor = False
        # Explore neighbors (Up, Down, Left, Right) - Order can influence path
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]: # Example order
            next_x, next_y = current_x + dx, current_y + dy

            # Check bounds
            if 0 <= next_y < height and 0 <= next_x < width:
                # Check if it's a path and not visited
                if grid[next_y][next_x] == ' ' and (next_x, next_y) not in visited:
                    visited.add((next_x, next_y))
                    new_path_segment = list(current_path_segment)
                    new_path_segment.append((next_x, next_y))
                    stack.append(((next_x, next_y), new_path_segment))
                    # Yield state after pushing a node onto the stack
                    yield visited, new_path_segment, False, None
                    found_neighbor = True
                    break # Go deeper from the new node

        if not found_neighbor:
            # If no unvisited neighbors, backtrack
            stack.pop()
            # Yield state after backtracking (optional, shows the backtrack visually)
            # If stack is not empty, yield the path of the new top element
            if stack:
                 _, path_at_top = stack[-1]
                 yield visited, path_at_top, False, None
            # else: # Stack is empty, search failed from start_node


    print(f"Solver (DFS): No path found from {start_node} to {end_node}")
    yield visited, [], True, None # Indicate completion, no path found
