def solve_dfs_step_by_step(grid, start_node, end_node):
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    if not (0 <= start_node[1] < h and 0 <= start_node[0] < w and grid[start_node[1]][start_node[0]] == ' '):
        print(f"Solver Error (DFS): Invalid start node {start_node}.")
        yield set(), [], True, None
        return
    if not (0 <= end_node[1] < h and 0 <= end_node[0] < w and grid[end_node[1]][end_node[0]] == ' '):
        print(f"Solver Error (DFS): Invalid end node {end_node}.")
        yield set(), [], True, None
        return

    print(f"Solver (DFS): Starting search from {start_node} to {end_node}")

    stack = [(start_node, [start_node])]
    visited = {start_node}

    yield visited, [start_node], False, None

    while stack:
        (cx, cy), current_path_segment = stack[-1]

        if (cx, cy) == end_node:
            print(f"Solver (DFS): Path found to {end_node}.")
            yield visited, current_path_segment, True, current_path_segment
            return

        found_neighbor = False
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            neighbor_node = (nx, ny)

            if 0 <= ny < h and 0 <= nx < w:
                if grid[ny][nx] == ' ' and neighbor_node not in visited:
                    visited.add(neighbor_node)
                    new_path_segment = list(current_path_segment)
                    new_path_segment.append(neighbor_node)
                    stack.append((neighbor_node, new_path_segment))

                    yield visited, new_path_segment, False, None
                    found_neighbor = True
                    break

        if not found_neighbor:
            stack.pop()
            if stack:
                 _, path_at_top = stack[-1]
                 yield visited, path_at_top, False, None

    print(f"Solver (DFS): No path found from {start_node} to {end_node}")
    yield visited, [], True, None
