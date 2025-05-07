import pygame
import sys
import argparse
import os

import config
from src.maze_generator import create_maze
from ui.maze_display import MazeDisplay
from ui.settings_window import SettingsWindow
from ui.ui_elements import Button, Label # Other elements used within SettingsWindow

# Solvers
from src.solvers.bfs_solver import solve_bfs_step_by_step
from src.solvers.dfs_solver import solve_dfs_step_by_step
from src.solvers.astar_solver import solve_astar_step_by_step

SOLVER_ALGORITHMS = {
    "BFS": solve_bfs_step_by_step,
    "DFS": solve_dfs_step_by_step,
    "A*": solve_astar_step_by_step,
}

class UIManager:
    """Manages different UI states/screens and global UI elements."""
    def __init__(self, screen):
        self.screen = screen
        self.active_view = "main"  # "main", "settings"
        
        self.control_panel_elements = [] # Elements specific to the control panel
        self.settings_window_instance = None
        self.notification_manager = NotificationManager(screen)

    def add_control_panel_element(self, element):
        self.control_panel_elements.append(element)

    def clear_control_panel_elements(self):
        self.control_panel_elements.clear()

    def set_settings_window(self, window_instance):
        self.settings_window_instance = window_instance

    def show_settings(self, current_maze_params, current_solver):
        if self.settings_window_instance:
            self.settings_window_instance.show(current_maze_params, current_solver)
            self.active_view = "settings"

    def hide_settings(self):
        if self.settings_window_instance:
            self.settings_window_instance.hide()
            self.active_view = "main"

    def update_screen_reference(self, new_screen):
        """Updates screen reference for manager and its children that need it."""
        self.screen = new_screen
        self.notification_manager.screen = new_screen
        if self.settings_window_instance:
            self.settings_window_instance.screen_width = new_screen.get_width()
            self.settings_window_instance.screen_height = new_screen.get_height()
            # Settings window recalculates its own panel position if its show() or internal layout logic is called.


    def handle_event(self, event, mouse_pos):
        consumed = False
        if self.active_view == "settings" and self.settings_window_instance:
            if self.settings_window_instance.handle_event(event, mouse_pos):
                consumed = True
        
        if not consumed and self.active_view == "main": # Only handle control panel if main view
            for element in reversed(self.control_panel_elements):
                if element.visible and not element.disabled:
                    if element.handle_event(event, mouse_pos):
                        consumed = True
                        break
        
        # Notifications always try to handle events (e.g., click to dismiss, not implemented yet)
        if not consumed: # Avoid double consumption if a main UI element handled it.
            self.notification_manager.handle_event(event, mouse_pos)
        
        return consumed

    def update(self, dt, mouse_pos):
        if self.active_view == "settings" and self.settings_window_instance:
            self.settings_window_instance.update(dt, mouse_pos)
        
        # Update control panel elements only if in main view (or always if they should be dynamic)
        # For now, let's assume they are always updated for hover effects etc.
        for element in self.control_panel_elements:
            if element.visible:
                element.update(dt, mouse_pos)
        
        self.notification_manager.update(dt)

    def draw_main_ui(self): # For elements outside maze_display and settings window
        for element in self.control_panel_elements:
            if element.visible:
                element.draw(self.screen)

    def draw_settings_ui(self): # Settings window draws itself and its overlay
        if self.active_view == "settings" and self.settings_window_instance:
            self.settings_window_instance.draw(self.screen)

    def draw_notifications(self):
        self.notification_manager.draw(self.screen)


class NotificationManager:
    def __init__(self, screen):
        self.screen = screen
        self.notifications = []
        self.font = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_SMALL)

    def add_notification(self, text, type="info", duration_ms=None):
        if len(self.notifications) >= config.NOTIFICATION_MAX_DISPLAY:
            self.notifications.pop(0)

        text_surface = self.font.render(text, True, config.NOTIFICATION_TEXT_COLOR)
        
        bg_width = config.NOTIFICATION_AREA_WIDTH
        bg_height = config.NOTIFICATION_HEIGHT
        padding = config.NOTIFICATION_PADDING
        
        x = self.screen.get_width() - bg_width - padding
        # Y position will be calculated in update based on current notifications
        rect = pygame.Rect(x, padding, bg_width, bg_height) # Initial Y
        
        notif_duration = duration_ms if duration_ms is not None else config.NOTIFICATION_DURATION_MS

        notif = {
            "text_surface": text_surface, "type": type, "rect": rect,
            "start_time": pygame.time.get_ticks(), "alpha": 255.0,
            "bar_color": config.NOTIFICATION_INFO_BAR_COLOR,
            "duration": notif_duration,
            "fade_duration": config.NOTIFICATION_FADE_DURATION_MS
        }
        if type == "success": notif["bar_color"] = config.SUCCESS_COLOR
        elif type == "error": notif["bar_color"] = config.ERROR_COLOR
        
        self.notifications.append(notif)
        self._recalculate_notification_positions() # Update Y positions
        print(f"Notification: [{type.upper()}] {text}")

    def _recalculate_notification_positions(self):
        padding = config.NOTIFICATION_PADDING
        bg_height = config.NOTIFICATION_HEIGHT
        screen_width = self.screen.get_width() # Get current screen width for X pos
        bg_width = config.NOTIFICATION_AREA_WIDTH


        for i, notif in enumerate(self.notifications):
            notif["rect"].x = screen_width - bg_width - padding
            notif["rect"].y = padding + (i * (bg_height + padding // 2))


    def handle_event(self, event, mouse_pos):
        pass # Placeholder for future interactions like click-to-dismiss

    def update(self, dt): # dt is not used here, uses pygame.time.get_ticks()
        current_time = pygame.time.get_ticks()
        notifications_to_keep = []
        changed_count = (len(self.notifications) > 0) # Assume change if there are notifications, to trigger recalc if one is removed

        for notif in self.notifications:
            elapsed = current_time - notif["start_time"]
            
            if elapsed > notif["duration"] + notif["fade_duration"]:
                # Will be removed, don't add to keep list
                continue 
            
            if elapsed > notif["duration"]: # Start fading
                fade_progress = (elapsed - notif["duration"]) / float(notif["fade_duration"])
                notif["alpha"] = 255.0 * (1.0 - fade_progress)
                notif["alpha"] = max(0.0, min(255.0, notif["alpha"])) # Clamp alpha
            
            notifications_to_keep.append(notif)
        
        if len(notifications_to_keep) != len(self.notifications): # If count actually changed
            self.notifications = notifications_to_keep
            self._recalculate_notification_positions() # Recalculate Y positions
        elif changed_count and not self.notifications: # Went from some to none
             self._recalculate_notification_positions() # Clear old positions effectively if needed


    def draw(self, surface):
        for notif in self.notifications:
            temp_surf = pygame.Surface(notif["rect"].size, pygame.SRCALPHA)
            
            bg_base_color = config.NOTIFICATION_BG_COLOR
            # Ensure bg_base_color has an alpha component before slicing
            base_alpha_val = bg_base_color[3] if len(bg_base_color) == 4 else 255 
            current_alpha_bg = int(base_alpha_val * (notif["alpha"] / 255.0))
            bg_color_with_alpha = (*bg_base_color[:3], current_alpha_bg)
            
            pygame.draw.rect(temp_surf, bg_color_with_alpha, temp_surf.get_rect(), border_radius=5)

            bar_base_color = notif["bar_color"]
            base_alpha_bar = bar_base_color[3] if len(bar_base_color) == 4 else 255
            current_alpha_bar = int(base_alpha_bar * (notif["alpha"]/255.0))
            bar_color_with_alpha = (*bar_base_color[:3], current_alpha_bar)

            bar_rect = pygame.Rect(0, 0, 5, temp_surf.get_height())
            pygame.draw.rect(temp_surf, bar_color_with_alpha, bar_rect, border_top_left_radius=5, border_bottom_left_radius=5)

            text_x = bar_rect.width + config.NOTIFICATION_PADDING // 2
            text_y = (temp_surf.get_height() - notif["text_surface"].get_height()) // 2
            
            notif_text_surf_copy = notif["text_surface"].copy()
            notif_text_surf_copy.set_alpha(int(notif["alpha"])) # Text alpha matches notification alpha
            temp_surf.blit(notif_text_surf_copy, (text_x, text_y))
            
            surface.blit(temp_surf, notif["rect"].topleft)


class MazeVisualizerApp:
    def __init__(self, screen_width, screen_height, start_fullscreen, cli_maze_w, cli_maze_h):
        pygame.init()
        pygame.font.init()

        self.initial_screen_width = screen_width
        self.initial_screen_height = screen_height
        self.is_fullscreen = start_fullscreen
        
        self._setup_screen() # Sets self.screen, self.screen_width, self.screen_height

        pygame.display.set_caption("Pygame Maze Visualizer")
        self.clock = pygame.time.Clock()
        self.running = True

        # Maze parameters
        self.maze_logical_width = cli_maze_w
        self.maze_logical_height = cli_maze_h
        self.current_solver_name = config.DEFAULT_SOLVER
        self.ai_solve_delay_ms = config.MAX_DELAY_MS // 2

        # Core components
        self.ui_manager = UIManager(self.screen)
        self.maze_display = MazeDisplay(self.screen, config.DEFAULT_CELL_SIZE)
        
        self._setup_control_panel_elements()
        self._setup_settings_window_instance()
        self._generate_new_maze_and_configure_display()

        # Solver Time Display
        self.solve_timer_start_ticks = None
        self.solve_time_elapsed_s = 0.0
        # self.timer_display_label is part of control_panel_elements

    def _setup_screen(self):
        display_flags = pygame.RESIZABLE
        current_w, current_h = self.initial_screen_width, self.initial_screen_height

        if self.is_fullscreen:
            try:
                info = pygame.display.Info()
                current_w, current_h = info.current_w, info.current_h
                display_flags = pygame.FULLSCREEN | pygame.SCALED
            except pygame.error:
                print("Warning: Could not get display info for fullscreen. Using provided/default size.")
                display_flags = pygame.FULLSCREEN # Fallback
        
        self.screen = pygame.display.set_mode((current_w, current_h), display_flags)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        if hasattr(self, 'ui_manager'): # If UIManager exists (on resize)
            self.ui_manager.update_screen_reference(self.screen)

    def _recalculate_layouts_on_resize(self):
        """Called after a screen resize event."""
        # Screen surface itself is recreated by Pygame on VIDEORESIZE event handling in main loop.
        # Here, we just update our stored width/height and tell components.
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.ui_manager.update_screen_reference(self.screen) # Update UIManager and its children screen refs
        
        grid_char_w = self.maze_display.grid_render_width
        grid_char_h = self.maze_display.grid_render_height
        cell_size, offset_x, offset_y = self._calculate_cell_size_and_offsets(grid_char_w, grid_char_h)
        self.maze_display.update_visual_properties(self.screen, cell_size, offset_x, offset_y)
        
        self._setup_control_panel_elements() # Re-creates and positions buttons
        
        if self.ui_manager.settings_window_instance:
            sw_instance = self.ui_manager.settings_window_instance
            sw_instance.panel.rect.topleft = ( (self.screen_width - sw_instance.win_w) // 2,
                                                (self.screen_height - sw_instance.win_h) // 2 )
            if sw_instance.visible: # Only re-layout internals if visible, otherwise show() will do it.
                 sw_instance._setup_ui_elements()

        self.ui_manager.notification_manager._recalculate_notification_positions()

        pygame.display.set_caption(
             f"Maze ({self.maze_logical_width}x{self.maze_logical_height}) Cell:{cell_size}px Solver:{self.current_solver_name}"
        )


    def _calculate_cell_size_and_offsets(self, grid_char_width, grid_char_height):
        if grid_char_width == 0 or grid_char_height == 0:
            return config.FALLBACK_CELL_SIZE, 0, 0

        available_h = self.screen_height - config.CONTROL_PANEL_HEIGHT
        available_w = self.screen_width
        padded_w = available_w * config.AUTO_SIZE_PADDING_FACTOR
        padded_h = available_h * config.AUTO_SIZE_PADDING_FACTOR
        
        cs_w = padded_w // grid_char_width if grid_char_width > 0 else config.FALLBACK_CELL_SIZE
        cs_h = padded_h // grid_char_height if grid_char_height > 0 else config.FALLBACK_CELL_SIZE
        cell_size = max(config.MIN_CELL_SIZE, int(min(cs_w, cs_h)))

        maze_render_width_px = grid_char_width * cell_size
        maze_render_height_px = grid_char_height * cell_size
        offset_x = (available_w - maze_render_width_px) // 2
        offset_y = (available_h - maze_render_height_px) // 2
        
        return cell_size, offset_x, offset_y

    def _generate_new_maze_and_configure_display(self):
        self.maze_display.reset_solve_visuals()
        self._stop_solve_timer_display()

        char_grid, start_node, end_node = create_maze(self.maze_logical_width, self.maze_logical_height)
        if not char_grid:
            self.ui_manager.notification_manager.add_notification("Failed to generate maze!", "error")
            return

        grid_char_h = len(char_grid)
        grid_char_w = len(char_grid[0])
        cell_size_px, offset_x, offset_y = self._calculate_cell_size_and_offsets(grid_char_w, grid_char_h)

        self.maze_display.set_maze(char_grid, start_node, end_node)
        self.maze_display.update_visual_properties(self.screen, cell_size_px, offset_x, offset_y)
        self.maze_display.set_ai_solve_delay(self.ai_solve_delay_ms)
        
        pygame.display.set_caption(
            f"Maze ({self.maze_logical_width}x{self.maze_logical_height}) Cell:{cell_size_px}px Solver:{self.current_solver_name}"
        )


    def _setup_control_panel_elements(self):
        self.ui_manager.clear_control_panel_elements()
        cp_height = config.CONTROL_PANEL_HEIGHT
        cp_y = self.screen_height - cp_height
        
        btn_height = int(cp_height * 0.7)
        btn_padding_y = (cp_height - btn_height) // 2
        btn_spacing_x = 15
        current_btn_x = btn_spacing_x

        buttons_config = [
            {"text": "Regen (R)", "action": self.on_regenerate_clicked, "tooltip": "Generate a new maze"},
            {"text": f"Solve (S)", "action": self.on_solve_clicked, "id": "solve_button", "tooltip": f"Solve with {self.current_solver_name}"},
            {"text": "Battle (B)", "action": self.on_battle_clicked, "tooltip": "All algorithms race to solve"},
            {"text": "Save Img (P)", "action": self.on_save_maze_clicked, "tooltip": "Save current view as PNG"},
            {"text": "Settings (G)", "action": self.on_settings_clicked, "tooltip": "Open settings panel"},
        ]
        temp_font = pygame.font.Font(config.FONT_NAME, config.BUTTON_FONT_SIZE)

        for b_conf in buttons_config:
            actual_text = b_conf["text"]
            if b_conf.get("id") == "solve_button": 
                actual_text = f"Solve: {self.current_solver_name} (S)"
                b_conf["tooltip"] = f"Solve with {self.current_solver_name} algorithm"

            text_w = temp_font.render(actual_text, True, config.BUTTON_TEXT_COLOR).get_width()
            btn_w = text_w + 2 * config.BUTTON_PADDING_X
            
            btn = Button(current_btn_x, cp_y + btn_padding_y, btn_w, btn_height, actual_text,
                         on_click_callback=b_conf["action"], tooltip=b_conf.get("tooltip"))
            if "id" in b_conf: btn.id = b_conf["id"]
            
            self.ui_manager.add_control_panel_element(btn)
            current_btn_x += btn_w + btn_spacing_x
            
        self.timer_display_label = Label(current_btn_x, cp_y + cp_height // 2, "Time: 0.00s",
                                         config.TIMER_FONT_SIZE, config.TIMER_TEXT_COLOR, alignment="left")
        self.timer_display_label.rect.centery = cp_y + cp_height // 2
        self.timer_display_label.rect.left = current_btn_x + btn_spacing_x 
        self.ui_manager.add_control_panel_element(self.timer_display_label)

    def _update_solve_button_text_and_tooltip(self):
        for elem in self.ui_manager.control_panel_elements:
            if hasattr(elem, 'id') and elem.id == "solve_button" and isinstance(elem, Button):
                new_text = f"Solve: {self.current_solver_name} (S)"
                elem.set_text(new_text) # Button's set_text should handle re-rendering
                elem.set_tooltip(f"Solve with {self.current_solver_name} algorithm")
                # Adjusting button width dynamically after text change can be complex
                # For now, assume the initial width calculation is sufficient or use fixed-width buttons.
                # If precise resizing is needed, _setup_control_panel_elements would have to be recalled.
                break

    def _setup_settings_window_instance(self):
        maze_params_for_settings = {"width": self.maze_logical_width, "height": self.maze_logical_height, "delay_ms": self.ai_solve_delay_ms}
        self.settings_window_instance = SettingsWindow(
            self.screen_width, self.screen_height, maze_params_for_settings, self.current_solver_name,
            self.on_settings_speed_changed, self.on_settings_saved, self.on_settings_canceled
        )
        self.ui_manager.set_settings_window(self.settings_window_instance)

    # --- Action Callbacks ---
    def on_regenerate_clicked(self):
        self._generate_new_maze_and_configure_display()
        self.ui_manager.notification_manager.add_notification(f"Generated {self.maze_logical_width}x{self.maze_logical_height} maze.", "info")


    def on_solve_clicked(self):
        if self.maze_display.is_solving():
            self.maze_display.reset_solve_visuals()
            self._stop_solve_timer_display()
            self.ui_manager.notification_manager.add_notification("Solver stopped.", "info")
        else:
            solver_func = SOLVER_ALGORITHMS.get(self.current_solver_name)
            if solver_func:
                if self.maze_display.start_single_solve(solver_func, self.current_solver_name):
                    self._start_solve_timer_display()
                    self.ui_manager.notification_manager.add_notification(f"Solving with {self.current_solver_name}...", "info")
                else:
                    self.ui_manager.notification_manager.add_notification(f"Failed to start {self.current_solver_name}.", "error")
            else:
                self.ui_manager.notification_manager.add_notification(f"Solver '{self.current_solver_name}' not found.", "error")

    def on_battle_clicked(self):
        if self.maze_display.is_solving():
            self.maze_display.reset_solve_visuals()
            self._stop_solve_timer_display()
            self.ui_manager.notification_manager.add_notification("Solver stopped.", "info")
        else:
            if self.maze_display.start_algorithm_battle(SOLVER_ALGORITHMS):
                self._start_solve_timer_display()
                self.ui_manager.notification_manager.add_notification("Algorithm Battle started!", "info")
            else:
                self.ui_manager.notification_manager.add_notification("Failed to start Algorithm Battle.", "error")

    def on_save_maze_clicked(self):
        try:
            solver_part = "idle"
            if self.maze_display.is_solving():
                if self.maze_display._is_battle_mode:
                    solver_part = "battle"
                elif self.maze_display._current_single_solver_name:
                    solver_part = self.maze_display._current_single_solver_name.replace("*","star") # Sanitize A*
            
            timestamp = pygame.time.get_ticks() 
            filename = f"maze_{self.maze_logical_width}x{self.maze_logical_height}_{solver_part}_{timestamp}.png"
            
            screenshots_dir = "screenshots"
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            
            filepath = os.path.join(screenshots_dir, filename)
            pygame.image.save(self.screen, filepath)
            self.ui_manager.notification_manager.add_notification(f"Saved as {filepath}", "success")
        except Exception as e:
            self.ui_manager.notification_manager.add_notification(f"Error saving image: {e}", "error")


    def on_settings_clicked(self):
        maze_params = {"width": self.maze_logical_width, "height": self.maze_logical_height, "delay_ms": self.ai_solve_delay_ms}
        self.ui_manager.show_settings(maze_params, self.current_solver_name)

    # --- Settings Window Callbacks ---
    def on_settings_speed_changed(self, new_delay_ms):
        self.ai_solve_delay_ms = new_delay_ms
        self.maze_display.set_ai_solve_delay(new_delay_ms)

    def on_settings_saved(self, new_maze_params, new_solver_name):
        changed_dims = (self.maze_logical_width != new_maze_params["width"] or
                        self.maze_logical_height != new_maze_params["height"])
        
        self.maze_logical_width = new_maze_params["width"]
        self.maze_logical_height = new_maze_params["height"]
        self.ai_solve_delay_ms = new_maze_params["delay_ms"] 
        self.current_solver_name = new_solver_name

        self._update_solve_button_text_and_tooltip()
        if changed_dims: 
            self._generate_new_maze_and_configure_display()
            self.ui_manager.notification_manager.add_notification("Settings saved. Maze regenerated.", "success")
        else:
            self.maze_display.set_ai_solve_delay(self.ai_solve_delay_ms) 
            pygame.display.set_caption( 
                f"Maze ({self.maze_logical_width}x{self.maze_logical_height}) Cell:{self.maze_display.cell_size_px}px Solver:{self.current_solver_name}"
            )
            self.ui_manager.notification_manager.add_notification("Settings saved.", "success")

        self.ui_manager.hide_settings()

    def on_settings_canceled(self):
        # Revert live AI speed change if settings window was live updating it
        # The SettingsWindow's _trigger_cancel should handle reverting its working_params
        # to initial_params for things like speed if it was live-updating.
        # We need to ensure our app's actual `ai_solve_delay_ms` is reset to what it was
        # *before* the settings window was opened.
        # The settings window `show()` method takes the *current* app state.
        # So, when settings are cancelled, we should revert to the state captured by `settings_window_instance.initial_maze_params["delay_ms"]`
        if self.ui_manager.settings_window_instance:
             initial_delay_before_settings = self.ui_manager.settings_window_instance.initial_maze_params["delay_ms"]
             if self.ai_solve_delay_ms != initial_delay_before_settings:
                 self.ai_solve_delay_ms = initial_delay_before_settings
                 self.maze_display.set_ai_solve_delay(self.ai_solve_delay_ms)

        self.ui_manager.hide_settings()
        self.ui_manager.notification_manager.add_notification("Settings canceled.", "info")
    
    # --- Solve Timer Display ---
    def _start_solve_timer_display(self):
        self.solve_timer_start_ticks = pygame.time.get_ticks()
        self.solve_time_elapsed_s = 0.0
        if self.timer_display_label:
            self.timer_display_label.color = config.TIMER_TEXT_COLOR # Reset color
            self.timer_display_label.set_text(f"Time: {self.solve_time_elapsed_s:.2f}s") # Reset text


    def _update_solve_timer_display_text(self):
        if self.solve_timer_start_ticks is not None: 
            self.solve_time_elapsed_s = (pygame.time.get_ticks() - self.solve_timer_start_ticks) / 1000.0
            if self.timer_display_label:
                self.timer_display_label.set_text(f"Time: {self.solve_time_elapsed_s:.2f}s")
        
        if self.solve_timer_start_ticks is not None and not self.maze_display.is_solving():
            self.solve_timer_start_ticks = None 
            
            any_path_found = False
            if self.maze_display._is_battle_mode:
                for state in self.maze_display._solver_states.values():
                    if state.get("found_path", False): any_path_found = True; break
            elif self.maze_display._current_single_solver_name: 
                solver_state = self.maze_display._solver_states.get(self.maze_display._current_single_solver_name)
                if solver_state and solver_state.get("found_path", False):
                    any_path_found = True
            
            if self.timer_display_label:
                self.timer_display_label.set_text(f"Done: {self.solve_time_elapsed_s:.2f}s")
                self.timer_display_label.color = config.SUCCESS_COLOR if any_path_found else config.WARNING_COLOR


    def _stop_solve_timer_display(self):
        self.solve_timer_start_ticks = None
        self.solve_time_elapsed_s = 0.0
        if self.timer_display_label:
            self.timer_display_label.set_text("Time: 0.00s")
            self.timer_display_label.color = config.TIMER_TEXT_COLOR


    def run(self):
        while self.running:
            dt_sec = self.clock.tick(config.FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                    # Pygame already updated self.screen, just need to tell our components
                    self._recalculate_layouts_on_resize()


                if event.type == config.AI_SOLVE_STEP_EVENT:
                    self.maze_display.handle_solve_event(event)

                consumed_by_ui = self.ui_manager.handle_event(event, mouse_pos)

                if not consumed_by_ui and event.type == pygame.KEYDOWN:
                    if self.ui_manager.active_view == "main": 
                        if event.key == pygame.K_r: self.on_regenerate_clicked()
                        elif event.key == pygame.K_s: self.on_solve_clicked()
                        elif event.key == pygame.K_b: self.on_battle_clicked()
                        elif event.key == pygame.K_p: self.on_save_maze_clicked()
                        elif event.key == pygame.K_g: self.on_settings_clicked()
                    
                    if event.key == pygame.K_ESCAPE:
                        if self.ui_manager.active_view == "settings":
                           # Settings window handles its own ESC via its handle_event.
                           # If it didn't consume (which it should), then we do nothing extra here.
                           pass
                        else: 
                            self.running = False


            self.ui_manager.update(dt_sec, mouse_pos)
            self._update_solve_timer_display_text()

            self.screen.fill(config.APP_BACKGROUND_COLOR)
            
            cp_rect = pygame.Rect(0, self.screen_height - config.CONTROL_PANEL_HEIGHT,
                                  self.screen_width, config.CONTROL_PANEL_HEIGHT)
            pygame.draw.rect(self.screen, config.CONTROL_PANEL_BACKGROUND_COLOR, cp_rect)
            if config.CONTROL_PANEL_BORDER_THICKNESS > 0:
                 pygame.draw.rect(self.screen, config.CONTROL_PANEL_BORDER_COLOR, cp_rect,
                                  width=config.CONTROL_PANEL_BORDER_THICKNESS, border_radius=2)

            self.maze_display.draw()
            self.ui_manager.draw_main_ui() 
            self.ui_manager.draw_settings_ui() 
            self.ui_manager.draw_notifications()
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pygame Maze Generator and Solver")
    parser.add_argument("--width", type=int, default=config.DEFAULT_WIDTH,
                        help=f"Initial maze width (cells). Default: {config.DEFAULT_WIDTH}")
    parser.add_argument("--height", type=int, default=config.DEFAULT_HEIGHT,
                        help=f"Initial maze height (cells). Default: {config.DEFAULT_HEIGHT}")
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode")
    
    args = parser.parse_args()

    cli_maze_w = max(2, min(args.width, config.MAX_MAZE_WIDTH))
    cli_maze_h = max(2, min(args.height, config.MAX_MAZE_HEIGHT))

    base_window_w, base_window_h = 1024, 768 
    
    app = MazeVisualizerApp(screen_width=base_window_w, screen_height=base_window_h,
                            start_fullscreen=args.fullscreen,
                            cli_maze_w = cli_maze_w, cli_maze_h = cli_maze_h)
    app.run()