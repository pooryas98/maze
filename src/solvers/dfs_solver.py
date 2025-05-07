# Define character representations expected in the grid
_WALL_CHAR = '#'
_PATH_CHAR = ' '

def solve_dfs_step_by_step(grid, start_node, end_node):
    if not grid or not grid[0]:
        print("Solver Error (DFS): Grid is empty or invalid.")
        yield set(), [], True, None
        return

    h = len(grid)
    w = len(grid[0])

    if not (0 <= start_node[1] < h and 0 <= start_node[0] < w and grid[start_node[1]][start_node[0]] == _PATH_CHAR):
        print(f"Solver Error (DFS): Invalid start node {start_node} or it's a wall (expected '{_PATH_CHAR}').")
        yield set(), [], True, None
        return
    if not (0 <= end_node[1] < h and 0 <= end_node[0] < w and grid[end_node[1]][end_node[0]] == _PATH_CHAR):
        print(f"Solver Error (DFS): Invalid end node {end_node} or it's a wall (expected '{_PATH_CHAR}').")
        yield set(), [], True, None
        return

    print(f"Solver (DFS): Starting search from {start_node} to {end_node} on a {w}x{h} grid.")

    stack = [(start_node, [start_node])]  
    visited = {start_node}

    yield visited.copy(), [start_node], False, None 

    while stack:
        (cx, cy), current_path_segment = stack[-1] 

        if (cx, cy) == end_node:
            print(f"Solver (DFS): Path found to {end_node}. Length: {len(current_path_segment)}")
            yield visited.copy(), list(current_path_segment), True, list(current_path_segment)
            return

        found_next_unvisited_neighbor = False
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]: 
            nx, ny = cx + dx, cy + dy
            neighbor_node = (nx, ny)

            if 0 <= ny < h and 0 <= nx < w: 
                if grid[ny][nx] == _PATH_CHAR and neighbor_node not in visited:
                    visited.add(neighbor_node)
                    new_path_segment = list(current_path_segment)
                    new_path_segment.append(neighbor_node)
                    stack.append((neighbor_node, new_path_segment))
                    
                    yield visited.copy(), list(new_path_segment), False, None 
                    found_next_unvisited_neighbor = True
                    break 

        if not found_next_unvisited_neighbor:
            popped_node, popped_path = stack.pop()
            if stack: 
                _, path_at_top = stack[-1]
                yield visited.copy(), list(path_at_top), False, None
            
    print(f"Solver (DFS): No path found from {start_node} to {end_node} after visiting {len(visited)} nodes.")
    yield visited.copy(), [], True, None