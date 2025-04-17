import pygame
import config
from src.solvers.bfs_solver import solve_bfs_step_by_step # Import the step-by-step solver

# Define a custom event for the AI solver timer
AI_SOLVE_STEP_EVENT = pygame.USEREVENT + 1

class MazeDisplay:
    """Handles drawing the maze and visualizing the AI solving process."""

    def __init__(self, screen, maze_grid, cell_size, offset_x=0, offset_y=0):
        self.screen = screen
        self.maze_grid = maze_grid
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.grid_height = len(maze_grid)
        self.grid_width = len(maze_grid[0]) if self.grid_height > 0 else 0

        # AI Solving State
        self._solver_generator = None
        self._visited_cells = set()
        self._current_path_segment = [] # Path segment being explored by solver
        self._final_path = None # The complete solution path, once found
        self._is_solving = False
        self._solve_delay_ms = 100 # Default delay (milliseconds)

    def set_maze(self, maze_grid):
        """Updates the maze grid being displayed."""
        self.maze_grid = maze_grid
        self.grid_height = len(maze_grid)
        self.grid_width = len(maze_grid[0]) if self.grid_height > 0 else 0
        self.reset_solve_state() # Reset visualization if maze changes

    def set_ai_solve_delay(self, delay_ms):
        """Sets the delay between AI solving steps."""
        self._solve_delay_ms = max(1, delay_ms) # Ensure delay is at least 1ms
        if self._is_solving:
            # Restart timer with new delay if already solving
            pygame.time.set_timer(AI_SOLVE_STEP_EVENT, self._solve_delay_ms)

    def is_solving(self):
        """Returns True if the AI solver visualization is currently running."""
        return self._is_solving

    def reset_solve_state(self):
        """Resets the visualization state."""
        self.stop_ai_solve() # Ensure timer is stopped
        self._solver_generator = None
        self._visited_cells = set()
        self._current_path_segment = []
        self._final_path = None
        self._is_solving = False

    def start_ai_solve(self, solver_function=solve_bfs_step_by_step):
        """Starts the step-by-step AI solving visualization."""
        if self._is_solving:
            return # Already solving

        self.reset_solve_state() # Clear previous state
        self._is_solving = True
        self._solver_generator = solver_function(self.maze_grid)
        print(f"Starting AI solve visualization with delay: {self._solve_delay_ms}ms")
        # Trigger the first step immediately, then subsequent steps via timer
        self._ai_solve_step()
        pygame.time.set_timer(AI_SOLVE_STEP_EVENT, self._solve_delay_ms)

    def stop_ai_solve(self):
        """Stops the AI solving visualization."""
        pygame.time.set_timer(AI_SOLVE_STEP_EVENT, 0) # Stop the timer
        self._is_solving = False
        # Keep the final state visible if stopped mid-solve or after completion
        # self.reset_solve_state() # Optional: uncomment to clear visualization on stop

    def handle_event(self, event):
        """Handles events relevant to the AI solver, specifically the timer."""
        if event.type == AI_SOLVE_STEP_EVENT and self._is_solving:
            self._ai_solve_step()

    def _ai_solve_step(self):
        """Executes one step of the AI solver generator."""
        if not self._solver_generator or not self._is_solving:
            self.stop_ai_solve()
            return

        try:
            visited, current_segment, is_done, final_path = next(self._solver_generator)
            self._visited_cells = visited
            self._current_path_segment = current_segment # Show the path being explored

            if is_done:
                self._final_path = final_path # Store the final path if found
                self.stop_ai_solve()
                print(f"AI Solve finished. Path found: {'Yes' if final_path else 'No'}")

        except StopIteration:
            # Generator finished unexpectedly (should be handled by is_done flag)
            self.stop_ai_solve()
            print("AI Solve generator finished.")
        except Exception as e:
            print(f"Error during AI solve step: {e}")
            self.stop_ai_solve()

        # Request redraw (assuming main loop handles drawing) - or draw directly if needed
        # self.draw() # If drawing isn't handled by main loop based on state

    def draw(self):
        """Draws the maze grid onto the Pygame screen with offsets, visited cells, and solution path."""
        # Convert to sets for efficient lookup (can be optimized if state doesn't change between draws)
        final_path_set = set(self._final_path) if self._final_path else set()
        # Visited cells are already a set in the state

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # Apply offset to the drawing position
                draw_x = self.offset_x + x * self.cell_size
                draw_y = self.offset_y + y * self.cell_size
                rect = pygame.Rect(draw_x, draw_y, self.cell_size, self.cell_size)
                cell_coords = (x, y) # Store coords for lookup

                if self.maze_grid[y][x] == '#':
                    pygame.draw.rect(self.screen, config.WALL_COLOR, rect)
                else: # Path
                    # Determine path color: Final Solution > Visited > Normal Path
                    if cell_coords in final_path_set:
                        color = config.SOLUTION_PATH_COLOR
                    elif cell_coords in self._visited_cells:
                        # Optionally color the current segment differently during solve
                        # if self._is_solving and cell_coords in set(self._current_path_segment):
                        #     color = config.CURRENT_SEARCH_COLOR # Need to define this in config
                        # else:
                        color = config.VISITED_COLOR
                    else:
                        color = config.PATH_COLOR
                    pygame.draw.rect(self.screen, color, rect)

# Keep the old function signature for potential compatibility, but make it use the class
# Or remove it if main.py is updated to use the class directly.
# For now, let's comment it out to encourage using the class.
#
# def draw_maze(screen, maze_grid, cell_size, offset_x=0, offset_y=0,
#               solution_path=None, visited_cells=None):
#     """Legacy drawing function wrapper (consider removing)."""
#     # This function is now less useful as state is managed by the class.
#     # If needed, it would create a temporary MazeDisplay instance.
#     temp_display = MazeDisplay(screen, maze_grid, cell_size, offset_x, offset_y)
#     temp_display._final_path = solution_path # Manually set state for legacy call
#     temp_display._visited_cells = set(visited_cells) if visited_cells else set()
#     temp_display.draw()
