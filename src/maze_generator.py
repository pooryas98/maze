import random

def create_maze(w, h):
    if w <= 0 or h <= 0:
        print("Error: Maze dimensions must be positive.")
        return None, None, None

    gh = 2 * h + 1
    gw = 2 * w + 1
    grid = [['#' for _ in range(gw)] for _ in range(gh)]

    stack = []

    sx, sy = random.randint(0, w - 1), random.randint(0, h - 1)
    gsx, gsy = 2 * sx + 1, 2 * sy + 1

    grid[gsy][gsx] = ' '
    stack.append((gsx, gsy))

    while stack:
        cx, cy = stack[-1]
        neighbors = []

        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 < ny < gh and 0 < nx < gw and grid[ny][nx] == '#':
                 neighbors.append((nx, ny))

        if neighbors:
            next_x, next_y = random.choice(neighbors)

            wall_x, wall_y = cx + (next_x - cx) // 2, cy + (next_y - cy) // 2
            grid[wall_y][wall_x] = ' '
            grid[next_y][next_x] = ' '

            stack.append((next_x, next_y))
        else:
            stack.pop()

    edge_cells = []
    edge_cells.extend([(x, 1) for x in range(1, gw, 2)])
    edge_cells.extend([(x, gh - 2) for x in range(1, gw, 2)])
    edge_cells.extend([(1, y) for y in range(3, gh - 2, 2)])
    edge_cells.extend([(gw - 2, y) for y in range(3, gh - 2, 2)])

    if len(edge_cells) < 2:
         if w == 1 and h == 1:
             start_node = (1, 0)
             end_node = (1, 2)
             grid[0][1] = ' '
             grid[2][1] = ' '
             return grid, start_node, end_node
         elif w == 1:
             start_node = (1, 0)
             end_node = (1, gh - 1)
             grid[0][1] = ' '
             grid[gh - 1][1] = ' '
             return grid, start_node, end_node
         elif h == 1:
             start_node = (0, 1)
             end_node = (gw - 1, 1)
             grid[1][0] = ' '
             grid[1][gw - 1] = ' '
             return grid, start_node, end_node
         else:
             print("Warning: Could not find distinct edge cells for start/end.")
             start_node = (0, 1)
             end_node = (gw - 1, gh - 2)
             grid[1][0] = ' '
             grid[gh - 2][gw - 1] = ' '
             return grid, start_node, end_node

    start_cell_grid_coords, end_cell_grid_coords = random.sample(edge_cells, 2)

    sx, sy = start_cell_grid_coords
    ex, ey = end_cell_grid_coords

    start_node = list(start_cell_grid_coords)
    if sy == 1: start_node[1] -= 1
    elif sy == gh - 2: start_node[1] += 1
    elif sx == 1: start_node[0] -= 1
    elif sx == gw - 2: start_node[0] += 1
    start_node = tuple(start_node)

    end_node = list(end_cell_grid_coords)
    if ey == 1: end_node[1] -= 1
    elif ey == gh - 2: end_node[1] += 1
    elif ex == 1: end_node[0] -= 1
    elif ex == gw - 2: end_node[0] += 1
    end_node = tuple(end_node)

    grid[start_node[1]][start_node[0]] = ' '
    grid[end_node[1]][end_node[0]] = ' '

    print(f"Maze Generator: Start Node={start_node}, End Node={end_node}")

    return grid, start_node, end_node
