import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def solve_astar_step_by_step(grid, start_node, end_node):
    h = len(grid)
    w = len(grid[0]) if h > 0 else 0

    if not (0 <= start_node[1] < h and 0 <= start_node[0] < w and grid[start_node[1]][start_node[0]] == ' '):
        print(f"Solver Error (A*): Invalid start node {start_node}.")
        yield set(), [], True, None
        return
    if not (0 <= end_node[1] < h and 0 <= end_node[0] < w and grid[end_node[1]][end_node[0]] == ' '):
        print(f"Solver Error (A*): Invalid end node {end_node}.")
        yield set(), [], True, None
        return

    print(f"Solver (A*): Starting search from {start_node} to {end_node}")

    start_h_cost = heuristic(start_node, end_node)
    open_set_heap = [(start_h_cost, 0, start_node, [start_node])]
    heapq.heapify(open_set_heap)

    g_costs = {start_node: 0}

    visited_for_vis = {start_node}

    yield visited_for_vis, [start_node], False, None

    while open_set_heap:
        f_cost, current_g_cost, current_node, current_path_segment = heapq.heappop(open_set_heap)

        if current_g_cost > g_costs.get(current_node, float('inf')):
            continue

        yield visited_for_vis, current_path_segment, False, None

        if current_node == end_node:
            print(f"Solver (A*): Path found to {end_node}.")
            yield visited_for_vis, current_path_segment, True, current_path_segment
            return

        cx, cy = current_node
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            neighbor_node = (nx, ny)

            if 0 <= ny < h and 0 <= nx < w and grid[ny][nx] == ' ':
                new_g_cost = current_g_cost + 1

                if new_g_cost < g_costs.get(neighbor_node, float('inf')):
                    g_costs[neighbor_node] = new_g_cost
                    h_cost = heuristic(neighbor_node, end_node)
                    f_cost = new_g_cost + h_cost

                    new_path_segment = list(current_path_segment)
                    new_path_segment.append(neighbor_node)

                    heapq.heappush(open_set_heap, (f_cost, new_g_cost, neighbor_node, new_path_segment))

                    visited_for_vis.add(neighbor_node)

    print(f"Solver (A*): No path found from {start_node} to {end_node}")
    yield visited_for_vis, [], True, None
