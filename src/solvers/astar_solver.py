# src/solvers/astar_solver.py

import heapq

def heuristic(a, b):
    """
    Manhattan distance heuristic for A* search.
    Calculates the grid distance between two points (ignoring walls).
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve_astar_step_by_step(grid, start_node, end_node):
    """
    Performs a step-by-step A* search on the maze grid.

    Args:
        grid (list[list[str]]): The maze grid where '#' is wall, ' ' is path.
        start_node (tuple[int, int]): The (x, y) coordinates of the starting cell.
        end_node (tuple[int, int]): The (x, y) coordinates of the ending cell.

    Yields:
        tuple: (visited_set, current_best_path, is_done, final_path)
            visited_set (set[tuple[int, int]]): Set of (x, y) coordinates considered (in open or closed set).
            current_best_path (list[tuple[int, int]]): The path segment leading to the node just expanded.
            is_done (bool): True if the search is complete (found or failed).
            final_path (list[tuple[int, int]] or None): The complete path if found, else None.
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    if not (0 <= start_node[1] < height and 0 <= start_node[0] < width and grid[start_node[1]][start_node[0]] == ' '):
        print(f"Solver Error (A*): Invalid start node {start_node}.")
        yield set(), [], True, None
        return
    if not (0 <= end_node[1] < height and 0 <= end_node[0] < width and grid[end_node[1]][end_node[0]] == ' '):
        print(f"Solver Error (A*): Invalid end node {end_node}.")
        yield set(), [], True, None
        return

    print(f"Solver (A*): Starting search from {start_node} to {end_node}")

    # --- A* Implementation (Step-by-Step) ---
    # Priority queue: stores (f_cost, g_cost, node, path_to_node)
    # f_cost = g_cost + h_cost
    # g_cost = cost from start to current node
    # h_cost = heuristic estimate from current node to end
    start_h_cost = heuristic(start_node, end_node)
    open_set_heap = [(start_h_cost, 0, start_node, [start_node])] # (f_cost, g_cost, node, path)
    heapq.heapify(open_set_heap)

    # Keep track of the lowest g_cost found to reach each node (closed set implicitly)
    g_costs = {start_node: 0}

    # Keep track of all nodes ever added to the open set for visualization
    visited_for_vis = {start_node}

    # Yield initial state
    yield visited_for_vis, [start_node], False, None

    while open_set_heap:
        f_cost, current_g_cost, current_node, current_path_segment = heapq.heappop(open_set_heap)

        # Optimization: If we pulled a node from the queue but found a shorter path
        # to it already, skip processing this one.
        if current_g_cost > g_costs.get(current_node, float('inf')):
            continue

        # Yield the state representing the node being expanded
        yield visited_for_vis, current_path_segment, False, None

        # Check if we reached the goal
        if current_node == end_node:
            print(f"Solver (A*): Path found to {end_node}.")
            yield visited_for_vis, current_path_segment, True, current_path_segment # Found the exit
            return # Stop generation

        current_x, current_y = current_node
        # Explore neighbors (Up, Down, Left, Right)
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            next_x, next_y = current_x + dx, current_y + dy
            neighbor_node = (next_x, next_y)

            # Check bounds and if it's a path
            if 0 <= next_y < height and 0 <= next_x < width and grid[next_y][next_x] == ' ':
                # Cost to reach this neighbor is current_g_cost + 1 (assuming uniform cost)
                new_g_cost = current_g_cost + 1

                # If this path to neighbor is better than any previous path found OR neighbor not seen yet
                if new_g_cost < g_costs.get(neighbor_node, float('inf')):
                    # Update cost and path
                    g_costs[neighbor_node] = new_g_cost
                    h_cost = heuristic(neighbor_node, end_node)
                    f_cost = new_g_cost + h_cost

                    new_path_segment = list(current_path_segment) # Copy path
                    new_path_segment.append(neighbor_node)

                    # Add to priority queue
                    heapq.heappush(open_set_heap, (f_cost, new_g_cost, neighbor_node, new_path_segment))

                    # Add to visited set for visualization
                    visited_for_vis.add(neighbor_node)
                    # No yield here, yield happens when node is *popped* from heap

    # If the loop finishes, the open set is empty, meaning no path found
    print(f"Solver (A*): No path found from {start_node} to {end_node}")
    yield visited_for_vis, [], True, None # Indicate completion, no path found