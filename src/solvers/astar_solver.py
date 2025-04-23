import heapq

def heuristic(a, b):
    """
    Manhattan distance heuristic for A* search.
    Calculates the straight-line distance between two points (ignoring walls).
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve_astar_step_by_step(grid):
    """
    Performs a step-by-step A* search on the maze grid, yielding visited nodes.

    Args:
        grid (list[list[str]]): The maze grid where '#' is wall, ' ' is path.
                                 Tries to dynamically find entrance/exit on edges.

    Yields:
        tuple: (visited_set, current_path_segment, is_done, final_path)
            visited_set (set[tuple[int, int]]): Set of (x, y) coordinates visited so far.
            current_path_segment (list[tuple[int, int]]): The path segment being explored (A* path).
            is_done (bool): True if the search is complete (found or failed).
            final_path (list[tuple[int, int]] or None): The complete path if found, else None.
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    if height == 0 or width == 0:
        yield set(), [], True, None # Indicate immediate completion, no path
        return

    # --- Find Entrance and Exit (Same logic as BFS/DFS) ---
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
        print("Solver Error (A*): Could not determine start or end node.")
        yield set(), [], True, None
        return

    print(f"Solver (A*): Start={start_node}, End={end_node}")

    # --- A* Implementation (Step-by-Step) ---
    # Priority queue: stores (f_cost, g_cost, node, path_to_node)
    # f_cost = g_cost + h_cost
    # g_cost = cost from start to current node
    # h_cost = heuristic estimate from current node to end
    open_set = [(0 + heuristic(start_node, end_node), 0, start_node, [start_node])]
    heapq.heapify(open_set)

    # Keep track of the lowest g_cost found for each node
    g_costs = {start_node: 0}

    # Keep track of visited nodes for visualization
    visited = {start_node}
    yield visited, [start_node], False, None # Initial state

    while open_set:
        f_cost, current_g_cost, (current_x, current_y), current_path_segment = heapq.heappop(open_set)

        # Check if we reached the goal
        if (current_x, current_y) == end_node:
            yield visited, current_path_segment, True, current_path_segment # Found the exit
            return # Stop generation

        # Explore neighbors (Up, Down, Left, Right)
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            next_x, next_y = current_x + dx, current_y + dy
            neighbor_node = (next_x, next_y)

            # Check bounds and if it's a path
            if 0 <= next_y < height and 0 <= next_x < width and grid[next_y][next_x] == ' ':
                # Cost to reach this neighbor is current_g_cost + 1 (assuming uniform cost)
                new_g_cost = current_g_cost + 1

                # If this path to neighbor is better than any previous path found
                if neighbor_node not in g_costs or new_g_cost < g_costs[neighbor_node]:
                    g_costs[neighbor_node] = new_g_cost
                    h_cost = heuristic(neighbor_node, end_node)
                    f_cost = new_g_cost + h_cost

                    new_path_segment = list(current_path_segment)
                    new_path_segment.append(neighbor_node)

                    heapq.heappush(open_set, (f_cost, new_g_cost, neighbor_node, new_path_segment))

                    # Add to visited for visualization if not already there
                    if neighbor_node not in visited:
                         visited.add(neighbor_node)
                         # Yield state after adding a node to the open set and visited set
                         yield visited, new_path_segment, False, None


    print(f"Solver (A*): No path found from {start_node} to {end_node}")
    yield visited, [], True, None # Indicate completion, no path found
