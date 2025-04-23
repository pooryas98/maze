import pygame
import config
AI_SOLVE_STEP_EVENT = config.AI_SOLVE_STEP_EVENT

class MazeDisplay:
    def __init__(self, screen, maze_grid, cell_size, start_node, end_node, offset_x=0, offset_y=0):
        self.screen = screen
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.maze_grid = None
        self.grid_height = 0
        self.grid_width = 0
        self.start_node = None
        self.end_node = None
        self.set_maze(maze_grid, start_node, end_node)

        self._solver_generator = None
        self._visited_cells = set()
        self._current_path_segment = []
        self._final_path = None
        self._is_solving = False
        self._solve_delay_ms = 100
        self._solver_function = None

    def set_maze(self, maze_grid, start_node, end_node):
        self.maze_grid = maze_grid
        self.start_node = start_node
        self.end_node = end_node
        if self.maze_grid:
            self.grid_height = len(maze_grid)
            self.grid_width = len(maze_grid[0]) if self.grid_height > 0 else 0
        else:
            self.grid_height = 0
            self.grid_width = 0
        self.reset_solve_state()

    def set_ai_solve_delay(self, delay_ms):
        self._solve_delay_ms = max(config.MIN_DELAY_MS, min(delay_ms, config.MAX_DELAY_MS))
        print(f"AI solve delay set to: {self._solve_delay_ms} ms")
        if self._is_solving:
            pygame.time.set_timer(AI_SOLVE_STEP_EVENT, self._solve_delay_ms)

    def get_ai_solve_delay(self):
        return self._solve_delay_ms

    def is_solving(self):
        return self._is_solving

    def reset_solve_state(self):
        self.stop_ai_solve()
        self._solver_generator = None
        self._visited_cells = set()
        self._current_path_segment = []
        self._final_path = None
        self._is_solving = False

    def start_ai_solve(self, solver_function):
        if self._is_solving:
            print("AI Solve requested, but already solving.")
            return
        if not self.maze_grid or not self.start_node or not self.end_node:
             print("Cannot start AI solve: Maze grid or start/end node missing.")
             return
        if not callable(solver_function):
            print(f"Error: Provided solver_function is not callable.")
            return

        self.reset_solve_state()
        self._is_solving = True
        self._solver_function = solver_function

        try:
            self._solver_generator = self._solver_function(self.maze_grid, self.start_node, self.end_node)
            print(f"Starting AI solve visualization (Delay: {self._solve_delay_ms}ms)")
            self._ai_solve_step()
            pygame.time.set_timer(AI_SOLVE_STEP_EVENT, self._solve_delay_ms)
        except Exception as e:
            print(f"Error initializing solver generator: {e}")
            self.stop_ai_solve()

    def stop_ai_solve(self):
        pygame.time.set_timer(AI_SOLVE_STEP_EVENT, 0)
        self._is_solving = False

    def handle_event(self, event):
        if event.type == AI_SOLVE_STEP_EVENT and self._is_solving:
            self._ai_solve_step()

    def _ai_solve_step(self):
        if not self._solver_generator:
            self.stop_ai_solve()
            return

        try:
            visited, current_segment, is_done, final_path = next(self._solver_generator)

            self._visited_cells = visited if visited else set()
            self._current_path_segment = current_segment if current_segment else []

            if is_done:
                self._final_path = final_path
                self.stop_ai_solve()
                status = "Path found" if final_path else "No path found"
                print(f"AI Solve finished. Status: {status}")

        except StopIteration:
            print("AI Solve generator finished (StopIteration).")
            if not self._final_path:
                print("   (No final path was yielded)")
            self.stop_ai_solve()
        except Exception as e:
            print(f"Error during AI solve step: {e}")
            import traceback
            traceback.print_exc()
            self.stop_ai_solve()

    def draw(self):
        if not self.maze_grid:
            return

        final_path_set = set(self._final_path) if self._final_path else set()

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                draw_x = self.offset_x + x * self.cell_size
                draw_y = self.offset_y + y * self.cell_size
                rect = pygame.Rect(draw_x, draw_y, self.cell_size, self.cell_size)
                cell_coords = (x, y)

                if self.maze_grid[y][x] == '#':
                    color = config.WALL_COLOR
                else:
                    if cell_coords == self.start_node:
                        color = config.START_COLOR
                    elif cell_coords == self.end_node:
                        color = config.END_COLOR
                    else:
                        if cell_coords in final_path_set:
                            color = config.SOLUTION_PATH_COLOR
                        elif cell_coords in self._visited_cells:
                            color = config.VISITED_COLOR
                        else:
                            color = config.PATH_COLOR

                pygame.draw.rect(self.screen, color, rect)
