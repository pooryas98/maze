# ui/maze_display.py

import pygame
import config
# Import the custom event (could be moved to config if preferred)
AI_SOLVE_STEP_EVENT = config.AI_SOLVE_STEP_EVENT

class MazeDisplay:
    """Handles drawing the maze grid, start/end points, and visualizing the AI solving process."""

    def __init__(self, screen, maze_grid, cell_size, start_node, end_node, offset_x=0, offset_y=0):
        self.screen = screen
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y

        # Maze and solver state
        self.maze_grid = None
        self.grid_height = 0
        self.grid_width = 0
        self.start_node = None
        self.end_node = None
        self.set_maze(maze_grid, start_node, end_node) # Initialize maze state

        # AI Solving Visualization State
        self._solver_generator = None
        self._visited_cells = set()
        self._current_path_segment = [] # Path segment currently being explored by solver
        self._final_path = None         # The complete solution path, once found
        self._is_solving = False
        self._solve_delay_ms = 100      # Default delay (updated via set_ai_solve_delay)
        self._solver_function = None    # Store the function used for the current solve

    def set_maze(self, maze_grid, start_node, end_node):
        """Updates the maze grid and start/end points being displayed."""
        self.maze_grid = maze_grid
        self.start_node = start_node
        self.end_node = end_node
        if self.maze_grid:
            self.grid_height = len(maze_grid)
            self.grid_width = len(maze_grid[0]) if self.grid_height > 0 else 0
        else:
            self.grid_height = 0
            self.grid_width = 0
        self.reset_solve_state() # Reset visualization if maze changes

    def set_ai_solve_delay(self, delay_ms):
        """Sets the delay between AI solving steps."""
        # Clamp delay to valid range from config
        self._solve_delay_ms = max(config.MIN_DELAY_MS, min(delay_ms, config.MAX_DELAY_MS))
        print(f"AI solve delay set to: {self._solve_delay_ms} ms")
        if self._is_solving:
            # Restart timer with new delay if already solving
            pygame.time.set_timer(AI_SOLVE_STEP_EVENT, self._solve_delay_ms)

    def get_ai_solve_delay(self):
        """Returns the current AI solve delay in milliseconds."""
        return self._solve_delay_ms

    def is_solving(self):
        """Returns True if the AI solver visualization is currently running."""
        return self._is_solving

    def reset_solve_state(self):
        """Resets the visualization state (visited cells, path, etc.)."""
        self.stop_ai_solve() # Ensure timer is stopped
        self._solver_generator = None
        self._visited_cells = set()
        self._current_path_segment = []
        self._final_path = None
        self._is_solving = False
        # Don't reset self._solver_function here, keep the last used one

    def start_ai_solve(self, solver_function):
        """
        Starts the step-by-step AI solving visualization using the provided solver function.

        Args:
            solver_function (callable): The step-by-step solver function
                                        (e.g., solve_bfs_step_by_step) which accepts
                                        (grid, start_node, end_node) and yields states.
        """
        if self._is_solving:
            print("AI Solve requested, but already solving.")
            return # Already solving
        if not self.maze_grid or not self.start_node or not self.end_node:
             print("Cannot start AI solve: Maze grid or start/end node missing.")
             return
        if not callable(solver_function):
            print(f"Error: Provided solver_function is not callable.")
            return

        self.reset_solve_state() # Clear previous state before starting new solve
        self._is_solving = True
        self._solver_function = solver_function # Store the function being used

        try:
            # Create the generator instance, passing required arguments
            self._solver_generator = self._solver_function(self.maze_grid, self.start_node, self.end_node)
            print(f"Starting AI solve visualization (Delay: {self._solve_delay_ms}ms)")
            # Trigger the first step immediately, subsequent steps via timer
            self._ai_solve_step()
            pygame.time.set_timer(AI_SOLVE_STEP_EVENT, self._solve_delay_ms)
        except Exception as e:
            print(f"Error initializing solver generator: {e}")
            self.stop_ai_solve()


    def stop_ai_solve(self):
        """Stops the AI solving visualization timer."""
        pygame.time.set_timer(AI_SOLVE_STEP_EVENT, 0) # Stop the timer
        # Don't reset generator here, _ai_solve_step handles StopIteration
        # Set solving flag to false *after* potentially processing the last step
        self._is_solving = False
        # Keep the final state visible if stopped mid-solve or after completion

    def handle_event(self, event):
        """Handles events relevant to the AI solver, specifically the timer."""
        if event.type == AI_SOLVE_STEP_EVENT and self._is_solving:
            self._ai_solve_step()

    def _ai_solve_step(self):
        """Executes one step of the AI solver generator and updates state."""
        if not self._solver_generator:
            self.stop_ai_solve()
            return

        try:
            # Get the next state from the solver generator
            visited, current_segment, is_done, final_path = next(self._solver_generator)

            # Update visualization state
            self._visited_cells = visited if visited else set()
            self._current_path_segment = current_segment if current_segment else []

            if is_done:
                self._final_path = final_path # Store the final path if found
                self.stop_ai_solve() # Stop the timer, solving is complete
                status = "Path found" if final_path else "No path found"
                print(f"AI Solve finished. Status: {status}")

        except StopIteration:
            # Generator finished (either completed normally or failed without final yield)
            print("AI Solve generator finished (StopIteration).")
            # Ensure state reflects completion if somehow is_done wasn't True on last yield
            if not self._final_path:
                print("   (No final path was yielded)")
            self.stop_ai_solve()
        except Exception as e:
            print(f"Error during AI solve step: {e}")
            import traceback
            traceback.print_exc() # Print stack trace for debugging
            self.stop_ai_solve()


    def draw(self):
        """Draws the maze grid, start/end, visited cells, and solution path."""
        if not self.maze_grid:
            return # Nothing to draw

        # Create sets for efficient lookups during drawing
        # Note: _visited_cells is already a set from the solver
        final_path_set = set(self._final_path) if self._final_path else set()

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # Calculate screen coordinates for the cell
                draw_x = self.offset_x + x * self.cell_size
                draw_y = self.offset_y + y * self.cell_size
                rect = pygame.Rect(draw_x, draw_y, self.cell_size, self.cell_size)
                cell_coords = (x, y) # Grid coordinates of the current cell

                # Determine cell type and color
                if self.maze_grid[y][x] == '#':
                    # It's a wall
                    color = config.WALL_COLOR
                else:
                    # It's a path, start, or end cell
                    if cell_coords == self.start_node:
                        color = config.START_COLOR
                    elif cell_coords == self.end_node:
                        color = config.END_COLOR
                    else:
                        # It's a regular path cell, check solver state
                        if cell_coords in final_path_set:
                            color = config.SOLUTION_PATH_COLOR
                        elif cell_coords in self._visited_cells:
                            color = config.VISITED_COLOR
                            # Optional: Highlight the current search path segment
                            # if self._is_solving and cell_coords in self._current_path_segment:
                            #     color = config.CURRENT_SEARCH_COLOR # Needs definition in config
                        else:
                            # Default path color
                            color = config.PATH_COLOR

                # Draw the rectangle for the cell
                pygame.draw.rect(self.screen, color, rect)