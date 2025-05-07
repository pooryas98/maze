import heapq
# import config # No longer needed

# Define character representations expected in the grid
_WALL_CHAR = '#'
_PATH_CHAR = ' '

def heuristic(a, b):
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve_astar_step_by_step(grid, start_node, end_node):
    if not grid or not grid[0]:
        print("Solver Error (A*): Grid is empty or invalid.")
        yield set(), [], True, None
        return

    h = len(grid)
    w = len(grid[0])

    if not (0 <= start_node[1] < h and 0 <= start_node[0] < w and grid[start_node[1]][start_node[0]] == _PATH_CHAR):
        print(f"Solver Error (A*): Invalid start node {start_node} or it's a wall (expected '{_PATH_CHAR}').")
        yield set(), [], True, None
        return
    if not (0 <= end_node[1] < h and 0 <= end_node[0] < w and grid[end_node[1]][end_node[0]] == _PATH_CHAR):
        print(f"Solver Error (A*): Invalid end node {end_node} or it's a wall (expected '{_PATH_CHAR}').")
        yield set(), [], True, None
        return

    print(f"Solver (A*): Starting search from {start_node} to {end_node} on a {w}x{h} grid.")

    open_set_heap = []
    g_cost_start = 0
    h_cost_start = heuristic(start_node, end_node)
    f_cost_start = g_cost_start + h_cost_start
    heapq.heappush(open_set_heap, (f_cost_start, g_cost_start, start_node, [start_node]))

    g_costs = {start_node: 0}
    nodes_considered_for_vis = {start_node}

    yield nodes_considered_for_vis.copy(), [start_node], False, None 

    while open_set_heap:
        f_cost, current_g_cost, current_node, current_path_segment = heapq.heappop(open_set_heap)

        if current_g_cost > g_costs.get(current_node, float('inf')):
            continue
        
        yield nodes_considered_for_vis.copy(), list(current_path_segment), False, None

        if current_node == end_node:
            print(f"Solver (A*): Path found to {end_node}. Cost: {current_g_cost}, Length: {len(current_path_segment)}")
            yield nodes_considered_for_vis.copy(), list(current_path_segment), True, list(current_path_segment)
            return

        cx, cy = current_node
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            neighbor_node = (nx, ny)

            if 0 <= ny < h and 0 <= nx < w and grid[ny][nx] == _PATH_CHAR: 
                tentative_g_cost = current_g_cost + 1

                if tentative_g_cost < g_costs.get(neighbor_node, float('inf')):
                    g_costs[neighbor_node] = tentative_g_cost
                    h_cost_neighbor = heuristic(neighbor_node, end_node)
                    f_cost_neighbor = tentative_g_cost + h_cost_neighbor
                    
                    new_path_segment = list(current_path_segment)
                    new_path_segment.append(neighbor_node)
                    
                    heapq.heappush(open_set_heap, (f_cost_neighbor, tentative_g_cost, neighbor_node, new_path_segment))
                    nodes_considered_for_vis.add(neighbor_node) 

    print(f"Solver (A*): No path found from {start_node} to {end_node} after considering {len(nodes_considered_for_vis)} nodes.")
    yield nodes_considered_for_vis.copy(), [], True, None