import pygame
import config

# Character representations from maze_generator (consistency)
_WALL_CHAR = '#'
_PATH_CHAR = ' '

class MazeDisplay:
    def __init__(self, screen, cell_size_px, offset_x=0, offset_y=0):
        self.screen = screen
        self.cell_size_px = cell_size_px
        self.offset_x = offset_x
        self.offset_y = offset_y

        self.char_grid = None       # The character-based grid ('#', ' ')
        self.grid_render_height = 0 # In cells
        self.grid_render_width = 0  # In cells
        self.start_node_coords = None # (x, y) in char_grid
        self.end_node_coords = None   # (x, y) in char_grid

        # Solver states: { solver_name: {"generator": ..., "visited_coords": set(), ...} }
        self._solver_states = {}
        self._active_solver_names = set() # Names of solvers currently running
        self._is_battle_mode = False

        self._solve_delay_ms = config.MAX_DELAY_MS // 2 # Default medium speed
        self._current_single_solver_name = config.DEFAULT_SOLVER

        # Pre-render static parts of the maze if possible (optimization)
        self._static_maze_surface = None
        self._maze_surface_dirty = True # Flag to re-render static maze part

    def set_maze(self, char_grid, start_node_coords, end_node_coords):
        """Sets a new maze to display."""
        self.char_grid = char_grid
        self.start_node_coords = start_node_coords
        self.end_node_coords = end_node_coords

        if self.char_grid:
            self.grid_render_height = len(self.char_grid)
            self.grid_render_width = len(self.char_grid[0]) if self.grid_render_height > 0 else 0
        else:
            self.grid_render_height = 0
            self.grid_render_width = 0
        
        self.reset_solve_visuals() # Clear solver paths, visited sets
        self._maze_surface_dirty = True # Maze structure changed, needs full redraw

    def update_visual_properties(self, screen, cell_size_px, offset_x, offset_y):
        """Updates display properties like screen, cell size, or offset."""
        needs_redraw = False
        if self.screen != screen:
            self.screen = screen
            needs_redraw = True
        if self.cell_size_px != cell_size_px:
            self.cell_size_px = cell_size_px
            needs_redraw = True
        if self.offset_x != offset_x or self.offset_y != offset_y:
            self.offset_x = offset_x
            self.offset_y = offset_y
            needs_redraw = True
        
        if needs_redraw:
            self._maze_surface_dirty = True # Force re-render of static part

    def set_ai_solve_delay(self, delay_ms):
        self._solve_delay_ms = max(config.MIN_DELAY_MS, min(delay_ms, config.MAX_DELAY_MS))
        print(f"MazeDisplay: AI solve delay set to {self._solve_delay_ms} ms")
        if self.is_solving(): # If actively solving, re-set the timer
            pygame.time.set_timer(config.AI_SOLVE_STEP_EVENT, self._solve_delay_ms)

    def get_ai_solve_delay(self):
        return self._solve_delay_ms

    def is_solving(self):
        return bool(self._active_solver_names)

    def reset_solve_visuals(self):
        """Clears all solver-related visual data but keeps the maze structure."""
        self.stop_ai_solve_timer() # Stop any active solving timer
        self._solver_states = {}
        self._active_solver_names = set()
        self._is_battle_mode = False
        self._current_single_solver_name = config.DEFAULT_SOLVER
        # self._maze_surface_dirty remains true if set_maze called it, false otherwise.
        # This function doesn't inherently make the static maze dirty.

    def start_single_solve(self, solver_function, solver_name):
        if self.is_solving():
            print("MazeDisplay: Solve requested, but already solving.")
            return False # Indicate failure to start
        if not self._is_maze_ready_for_solve():
            return False

        self.reset_solve_visuals() # Clear previous solver states
        self._current_single_solver_name = solver_name
        self._active_solver_names.add(solver_name)
        self._is_battle_mode = False

        try:
            generator = solver_function(self.char_grid, self.start_node_coords, self.end_node_coords)
            self._solver_states[solver_name] = self._create_empty_solver_state(generator)
            print(f"MazeDisplay: Starting single AI solve ({solver_name}), Delay: {self._solve_delay_ms}ms")
            self._ai_solve_step_for_solver(solver_name) # Initial step
            pygame.time.set_timer(config.AI_SOLVE_STEP_EVENT, self._solve_delay_ms)
            return True
        except Exception as e:
            print(f"MazeDisplay: Error initializing solver '{solver_name}': {e}")
            self.reset_solve_visuals()
            return False

    def start_algorithm_battle(self, solver_functions_map):
        if self.is_solving():
            print("MazeDisplay: Algorithm Battle requested, but already solving.")
            return False
        if not self._is_maze_ready_for_solve():
            return False
        if not solver_functions_map or not isinstance(solver_functions_map, dict):
            print("MazeDisplay: Invalid solver_functions_map for Algorithm Battle.")
            return False

        self.reset_solve_visuals()
        self._is_battle_mode = True
        
        valid_solvers_started = 0
        for name, func in solver_functions_map.items():
            if callable(func):
                try:
                    generator = func(self.char_grid, self.start_node_coords, self.end_node_coords)
                    self._solver_states[name] = self._create_empty_solver_state(generator)
                    self._active_solver_names.add(name)
                    self._ai_solve_step_for_solver(name) # Initial step for each
                    valid_solvers_started +=1
                except Exception as e:
                    print(f"MazeDisplay: Error initializing solver '{name}' for battle: {e}")
            else:
                print(f"MazeDisplay: Solver function for '{name}' is not callable. Skipping.")
        
        if valid_solvers_started == 0:
            print("MazeDisplay: No valid solvers started for Algorithm Battle. Stopping.")
            self.reset_solve_visuals()
            return False

        print(f"MazeDisplay: Starting Algorithm Battle for {list(self._active_solver_names)}, Delay: {self._solve_delay_ms}ms")
        pygame.time.set_timer(config.AI_SOLVE_STEP_EVENT, self._solve_delay_ms)
        return True

    def _is_maze_ready_for_solve(self):
        if not self.char_grid or self.start_node_coords is None or self.end_node_coords is None:
            print("MazeDisplay: Cannot start AI solve - maze, start, or end node not set.")
            return False
        return True

    def _create_empty_solver_state(self, generator):
        return {
            "generator": generator,
            "visited_coords": set(),    # Set of (x,y) tuples
            "current_path_coords": [],  # List of (x,y) tuples
            "final_path_coords": None,  # List of (x,y) tuples, or None
            "is_done": False,
            "found_path": False
        }

    def stop_ai_solve_timer(self):
        pygame.time.set_timer(config.AI_SOLVE_STEP_EVENT, 0) # Clear the timer

    def handle_solve_event(self, event):
        """Handles AI_SOLVE_STEP_EVENT."""
        if event.type == config.AI_SOLVE_STEP_EVENT and self.is_solving():
            active_names_copy = list(self._active_solver_names) # Iterate on a copy
            for solver_name in active_names_copy:
                if solver_name in self._active_solver_names: # Check if still active (might be removed by another step)
                    self._ai_solve_step_for_solver(solver_name)
            
            if not self.is_solving(): # If all solvers finished
                print("MazeDisplay: All active solvers have finished.")
                self.stop_ai_solve_timer()
                # Battle mode might have a "winner" determination here if needed

    def _ai_solve_step_for_solver(self, solver_name):
        state = self._solver_states.get(solver_name)
        if not state or state["is_done"] or not state["generator"]:
            self._active_solver_names.discard(solver_name)
            return

        try:
            # Expected yield: visited_coords_set, current_path_list, is_done_bool, final_path_list_or_none
            visited, current_segment, is_done, final_path = next(state["generator"])

            state["visited_coords"] = visited if visited else set()
            state["current_path_coords"] = current_segment if current_segment else []
            state["is_done"] = is_done

            if is_done:
                state["final_path_coords"] = final_path
                state["found_path"] = bool(final_path)
                print(f"MazeDisplay: Solver '{solver_name}' finished. Path found: {state['found_path']}")
                self._active_solver_names.discard(solver_name)
        
        except StopIteration:
            print(f"MazeDisplay: Solver generator for '{solver_name}' finished (StopIteration).")
            state["is_done"] = True
            if not state["final_path_coords"]: # If StopIteration and no path explicitly yielded
                 state["found_path"] = False
                 print(f"   ({solver_name}: No final path was yielded prior to StopIteration)")
            self._active_solver_names.discard(solver_name)
        except Exception as e:
            print(f"MazeDisplay: Error during AI solve step for '{solver_name}': {e}")
            import traceback
            traceback.print_exc()
            state["is_done"] = True # Mark as done to prevent further errors
            self._active_solver_names.discard(solver_name)

    def _draw_static_maze(self):
        """Pre-renders the walls, paths, start, and end nodes to a surface."""
        if not self.char_grid or self.cell_size_px < config.MIN_CELL_SIZE:
            self._static_maze_surface = None
            return

        surface_width = self.grid_render_width * self.cell_size_px
        surface_height = self.grid_render_height * self.cell_size_px
        self._static_maze_surface = pygame.Surface((surface_width, surface_height))
        self._static_maze_surface.fill(config.MAZE_BACKGROUND_COLOR) # Fallback bg

        for r_idx, row in enumerate(self.char_grid):
            for c_idx, cell_char in enumerate(row):
                cell_rect = pygame.Rect(c_idx * self.cell_size_px, r_idx * self.cell_size_px,
                                        self.cell_size_px, self.cell_size_px)
                color = config.WALL_COLOR if cell_char == _WALL_CHAR else config.PATH_COLOR
                
                # Special colors for start/end, drawn on top of path/wall if they are openings
                if (c_idx, r_idx) == self.start_node_coords:
                    color = config.START_NODE_COLOR
                elif (c_idx, r_idx) == self.end_node_coords:
                    color = config.END_NODE_COLOR
                
                pygame.draw.rect(self._static_maze_surface, color, cell_rect)
        
        self._maze_surface_dirty = False
        print("MazeDisplay: Static maze surface re-rendered.")

    def draw(self):
        if not self.char_grid or self.cell_size_px < config.MIN_CELL_SIZE:
            # Optionally draw a placeholder or message if no maze
            return

        if self._maze_surface_dirty or self._static_maze_surface is None:
            self._draw_static_maze()

        if self._static_maze_surface:
            self.screen.blit(self._static_maze_surface, (self.offset_x, self.offset_y))
        else: # Fallback if static surface failed (e.g. too small cell size)
            # Draw manually (less efficient)
            for r_idx, row in enumerate(self.char_grid):
                for c_idx, cell_char in enumerate(row):
                    draw_x = self.offset_x + c_idx * self.cell_size_px
                    draw_y = self.offset_y + r_idx * self.cell_size_px
                    cell_rect = pygame.Rect(draw_x, draw_y, self.cell_size_px, self.cell_size_px)
                    color = config.WALL_COLOR if cell_char == _WALL_CHAR else config.PATH_COLOR
                    if (c_idx, r_idx) == self.start_node_coords: color = config.START_NODE_COLOR
                    elif (c_idx, r_idx) == self.end_node_coords: color = config.END_NODE_COLOR
                    pygame.draw.rect(self.screen, color, cell_rect)


        # --- Draw Solver Visualizations (dynamic part) ---
        # These are drawn on top of the static maze surface
        # Create a temporary surface for alpha blending solver paths to avoid re-drawing base maze
        solver_overlay_width = self.grid_render_width * self.cell_size_px
        solver_overlay_height = self.grid_render_height * self.cell_size_px

        # Optimization: if no solvers active and no final paths, skip overlay
        if not self._solver_states: return

        # Draw visited cells first, then current paths, then final paths
        # Order matters for battle mode visibility.
        
        # 1. Draw visited cells (most subtle)
        for solver_name, state_data in self._solver_states.items():
            if not state_data or not state_data.get("visited_coords"): continue
            
            solver_theme = config.SOLVER_COLORS.get(solver_name, config.SOLVER_COLORS["DEFAULT"])
            visited_color = solver_theme["visited"] # Expected (R, G, B, A)

            for c_idx, r_idx in state_data["visited_coords"]:
                if (c_idx, r_idx) == self.start_node_coords or (c_idx, r_idx) == self.end_node_coords:
                    continue # Don't obscure start/end nodes with visited markers
                
                self._draw_solver_cell_overlay(c_idx, r_idx, visited_color, config.VISITED_CELL_SCALE)

        # 2. Draw current path segments (medium emphasis)
        for solver_name, state_data in self._solver_states.items():
            if not state_data or not state_data.get("current_path_coords") or state_data.get("is_done"):
                continue # Don't draw current path if done (final path will be shown)

            solver_theme = config.SOLVER_COLORS.get(solver_name, config.SOLVER_COLORS["DEFAULT"])
            current_path_color = solver_theme["path"] # Expected (R, G, B, A)

            for c_idx, r_idx in state_data["current_path_coords"]:
                if (c_idx, r_idx) == self.start_node_coords or (c_idx, r_idx) == self.end_node_coords:
                    continue
                self._draw_solver_cell_overlay(c_idx, r_idx, current_path_color, config.CURRENT_PATH_CELL_SCALE)
        
        # 3. Draw final paths (strongest emphasis)
        for solver_name, state_data in self._solver_states.items():
            if not state_data or not state_data.get("final_path_coords"): continue

            solver_theme = config.SOLVER_COLORS.get(solver_name, config.SOLVER_COLORS["DEFAULT"])
            # Final path color usually has no alpha or full alpha, drawn solid
            final_path_color = solver_theme["final_path"] # Expected (R, G, B) or (R,G,B,A)

            for c_idx, r_idx in state_data["final_path_coords"]:
                if (c_idx, r_idx) == self.start_node_coords or (c_idx, r_idx) == self.end_node_coords:
                    continue
                self._draw_solver_cell_overlay(c_idx, r_idx, final_path_color, config.FINAL_PATH_CELL_SCALE)


    def _draw_solver_cell_overlay(self, c_idx, r_idx, color_tuple, scale_factor):
        """Helper to draw a scaled, centered rectangle for solver visualization."""
        full_size = self.cell_size_px
        scaled_size = int(full_size * scale_factor)
        if scaled_size < 1: scaled_size = 1 # Ensure at least 1 pixel

        offset = (full_size - scaled_size) // 2
        
        draw_x = self.offset_x + (c_idx * full_size) + offset
        draw_y = self.offset_y + (r_idx * full_size) + offset
        
        overlay_rect = pygame.Rect(draw_x, draw_y, scaled_size, scaled_size)

        # If color has alpha, use a surface for proper blending
        if len(color_tuple) == 4:
            temp_surface = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
            temp_surface.fill(color_tuple)
            self.screen.blit(temp_surface, overlay_rect.topleft)
        else: # Solid color
            pygame.draw.rect(self.screen, color_tuple, overlay_rect)