# src/solvers/dfs_solver.py

def solve_dfs_step_by_step(grid, start_node, end_node):
    """
    Performs a step-by-step Depth-First Search (DFS) on the maze grid.

    Args:
        grid (list[list[str]]): The maze grid where '#' is wall, ' ' is path.
        start_node (tuple[int, int]): The (x, y) coordinates of the starting cell.
        end_node (tuple[int, int]): The (x, y) coordinates of the ending cell.

    Yields:
        tuple: (visited_set, current_path_segment, is_done, final_path)
            visited_set (set[tuple[int, int]]): Set of (x, y) coordinates visited so far.
            current_path_segment (list[tuple[int, int]]): The current DFS path being explored.
            is_done (bool): True if the search is complete (found or failed).
            final_path (list[tuple[int, int]] or None): The complete path if found, else None.
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    if not (0 <= start_node[1] < height and 0 <= start_node[0] < width and grid[start_node[1]][start_node[0]] == ' '):
        print(f"Solver Error (DFS): Invalid start node {start_node}.")
        yield set(), [], True, None
        return
    if not (0 <= end_node[1] < height and 0 <= end_node[0] < width and grid[end_node[1]][end_node[0]] == ' '):
        print(f"Solver Error (DFS): Invalid end node {end_node}.")
        yield set(), [], True, None
        return

    print(f"Solver (DFS): Starting search from {start_node} to {end_node}")

    # --- DFS Implementation (Step-by-Step using explicit stack) ---
    stack = [(start_node, [start_node])] # Store (node, path_to_node)
    visited = {start_node}

    # Yield initial state
    yield visited, [start_node], False, None

    while stack:
        (current_x, current_y), current_path_segment = stack[-1] # Peek at the top

        # Check if we reached the goal
        if (current_x, current_y) == end_node:
            print(f"Solver (DFS): Path found to {end_node}.")
            yield visited, current_path_segment, True, current_path_segment # Found the exit
            return # Stop generation

        found_neighbor = False
        # Explore neighbors (Order can influence path: e.g., Up, Right, Down, Left)
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            next_x, next_y = current_x + dx, current_y + dy
            neighbor_node = (next_x, next_y)

            # Check bounds
            if 0 <= next_y < height and 0 <= next_x < width:
                # Check if it's a path and not visited
                if grid[next_y][next_x] == ' ' and neighbor_node not in visited:
                    visited.add(neighbor_node)
                    new_path_segment = list(current_path_segment)
                    new_path_segment.append(neighbor_node)
                    stack.append((neighbor_node, new_path_segment))

                    # Yield state after pushing a new node onto the stack
                    yield visited, new_path_segment, False, None
                    found_neighbor = True
                    break # Break after finding one neighbor to go deeper (DFS nature)

        if not found_neighbor:
            # If no unvisited neighbors were found from the current node, backtrack
            stack.pop()
            # Yield state after backtracking to show the path shortening visually
            if stack:
                 _, path_at_top = stack[-1] # Get the path of the new top element
                 yield visited, path_at_top, False, None
            # else: Stack is empty, search failed from start_node

    # If the stack becomes empty and we haven't returned, no path was found
    print(f"Solver (DFS): No path found from {start_node} to {end_node}")
    yield visited, [], True, None # Indicate completion, no path found