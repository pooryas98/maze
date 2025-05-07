import pygame
import config
from .ui_elements import Panel, Label, Button, InputBox, Slider

class SettingsWindow:
    """
    A modal window for changing application settings like maze dimensions,
    AI speed, and selected solver.
    Uses UI elements from ui_elements.py.
    """
    def __init__(self, screen_width, screen_height,
                 current_maze_params, current_solver_name,
                 speed_change_callback, # Called live as slider moves
                 on_save_callback,      # Called with new_params_dict, new_solver_name
                 on_cancel_callback):   # Called on explicit cancel or ESC
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Store initial values to revert on cancel or compare on save
        # current_maze_params is expected to be a dict like: {"width": w, "height": h, "delay_ms": d}
        self.initial_maze_params = current_maze_params.copy()
        self.initial_solver_name = current_solver_name

        # These will be modified by UI interactions
        self.current_working_maze_params = current_maze_params.copy() # Use a working copy
        self.current_working_solver = current_solver_name

        # Callbacks
        self.on_speed_change_callback = speed_change_callback
        self.on_save_callback = on_save_callback
        self.on_cancel_callback = on_cancel_callback

        # Window dimensions and positioning
        self.win_w = config.SETTINGS_WINDOW_WIDTH
        self.win_h = config.SETTINGS_WINDOW_HEIGHT
        self.win_x = (self.screen_width - self.win_w) // 2
        self.win_y = (self.screen_height - self.win_h) // 2

        # Main panel for the settings window
        self.panel = Panel(self.win_x, self.win_y, self.win_w, self.win_h,
                           config.SETTINGS_PANEL_COLOR,
                           border_color=config.SETTINGS_BORDER_COLOR,
                           border_width=2, border_radius=8)
        
        self.elements = [] # All UI elements go here for easy event handling and drawing
        self._setup_ui_elements()

        self.visible = False # The window is hidden by default

    def _map_delay_to_slider(self, delay_ms):
        """Converts AI step delay (ms) to a slider value (0-100)."""
        min_delay, max_delay = config.MIN_DELAY_MS, config.MAX_DELAY_MS
        min_slider, max_slider = config.SLIDER_MIN_VAL, config.SLIDER_MAX_VAL
        exponent = config.SLIDER_EXPONENT

        if max_delay == min_delay: return min_slider if delay_ms <= min_delay else max_slider
        if delay_ms <= min_delay: return max_slider
        if delay_ms >= max_delay: return min_slider
        
        delay_ratio_norm = (float(delay_ms) - min_delay) / (max_delay - min_delay)
        inv_exponent = 1.0 / exponent
        slider_ratio_norm = 1.0 - (delay_ratio_norm ** inv_exponent)
        slider_value = min_slider + slider_ratio_norm * (max_slider - min_slider)
        
        return int(max(min_slider, min(round(slider_value), max_slider)))

    def _map_slider_to_delay(self, slider_value):
        """Converts a slider value (0-100) to AI step delay (ms)."""
        min_delay, max_delay = config.MIN_DELAY_MS, config.MAX_DELAY_MS
        min_slider, max_slider = config.SLIDER_MIN_VAL, config.SLIDER_MAX_VAL
        exponent = config.SLIDER_EXPONENT

        if max_slider == min_slider: return min_delay
        
        ratio = (float(slider_value) - min_slider) / (max_slider - min_slider)
        mapped_ratio_for_delay = (1.0 - ratio) ** exponent
        delay = min_delay + mapped_ratio_for_delay * (max_delay - min_delay)
        
        return int(max(min_delay, min(delay, max_delay)))

    def _validate_dimension(self, text_value, min_val, max_val):
        """Validates if a text value is an integer within a given range."""
        try:
            val = int(text_value)
            return min_val <= val <= max_val
        except ValueError:
            # Allow empty string during typing, but it's not valid for saving
            # The InputBox's allow_empty flag might interact here.
            # For dimensions, empty is definitively invalid.
            return False

    def _validate_width(self, text_value):
        return self._validate_dimension(text_value, 2, config.MAX_MAZE_WIDTH)

    def _validate_height(self, text_value):
        return self._validate_dimension(text_value, 2, config.MAX_MAZE_HEIGHT)

    def _setup_ui_elements(self):
        """Creates and positions all UI elements within the settings panel."""
        self.elements.clear()

        # Title
        title_label = Label(self.panel.rect.centerx, self.panel.rect.top + 30, "Settings",
                            config.FONT_SIZE_XLARGE, config.SETTINGS_TITLE_COLOR, alignment="center")
        title_label.rect.centerx = self.panel.rect.centerx # Recenter after width is known
        self.elements.append(title_label)

        # Layout variables
        current_y = self.panel.rect.top + 80
        label_x_offset = 30 # From panel left
        label_x = self.panel.rect.left + label_x_offset
        input_x_offset = 150 # From panel left, for inputs/sliders
        input_x = self.panel.rect.left + input_x_offset
        
        default_input_w = config.INPUT_BOX_WIDTH
        default_input_h = config.INPUT_BOX_HEIGHT
        row_padding_y = 20 # Increased padding between rows

        # --- Maze Width ---
        self.elements.append(Label(label_x, current_y + default_input_h // 2, "Maze Width:",
                                   config.FONT_SIZE_MEDIUM, config.SETTINGS_LABEL_COLOR, alignment="left",
                                   padding=5)) # Padding for Label y-centering
        self.width_input = InputBox(input_x, current_y, default_input_w, default_input_h,
                                    initial_text=str(self.current_working_maze_params["width"]),
                                    max_len=3, numeric_only=True, validation_func=self._validate_width)
        self.elements.append(self.width_input)
        current_y += default_input_h + row_padding_y

        # --- Maze Height ---
        self.elements.append(Label(label_x, current_y + default_input_h // 2, "Maze Height:",
                                   config.FONT_SIZE_MEDIUM, config.SETTINGS_LABEL_COLOR, alignment="left",
                                   padding=5))
        self.height_input = InputBox(input_x, current_y, default_input_w, default_input_h,
                                     initial_text=str(self.current_working_maze_params["height"]),
                                     max_len=3, numeric_only=True, validation_func=self._validate_height)
        self.elements.append(self.height_input)
        current_y += default_input_h + row_padding_y * 1.5 # Extra padding

        # --- AI Speed Slider ---
        self.elements.append(Label(label_x, current_y + default_input_h // 2, "AI Speed:",
                                   config.FONT_SIZE_MEDIUM, config.SETTINGS_LABEL_COLOR, alignment="left",
                                   padding=5))
        slider_w = self.panel.rect.width - input_x_offset - label_x_offset - 60 # panel_width - left_margin - right_margin - value_text_space
        initial_slider_val = self._map_delay_to_slider(self.current_working_maze_params["delay_ms"])
        self.speed_slider = Slider(input_x, current_y, slider_w, default_input_h, # Slider height same as input box
                                   config.SLIDER_MIN_VAL, config.SLIDER_MAX_VAL, initial_slider_val,
                                   on_value_change_callback=self._on_speed_slider_changed,
                                   show_value_text=True)
        self.elements.append(self.speed_slider)
        current_y += default_input_h + row_padding_y * 1.5

        # --- Solver Selection ---
        self.elements.append(Label(label_x, current_y + default_input_h // 2, "Solver:",
                                   config.FONT_SIZE_MEDIUM, config.SETTINGS_LABEL_COLOR, alignment="left",
                                   padding=5))
        self.solver_buttons = []
        solver_btn_w = (slider_w + default_input_w - input_x) // len(config.SOLVER_OPTIONS) - 10 # Distribute width
        solver_btn_w = max(70, solver_btn_w) # Min width
        solver_btn_h = default_input_h - 5
        solver_btn_current_x = input_x
        solver_btn_padding = 10

        for solver_name in config.SOLVER_OPTIONS:
            btn = Button(solver_btn_current_x, current_y + (default_input_h - solver_btn_h) // 2,
                         solver_btn_w, solver_btn_h, solver_name,
                         on_click_callback=self._on_solver_button_clicked, callback_args=[solver_name],
                         font_size=config.FONT_SIZE_SMALL,
                         border_radius=config.BUTTON_BORDER_RADIUS -2)
            self.solver_buttons.append(btn)
            self.elements.append(btn)
            solver_btn_current_x += solver_btn_w + solver_btn_padding
        self._update_solver_button_styles() # Set initial selection style
        current_y += default_input_h + row_padding_y * 2

        # --- Action Buttons (Save, Cancel) ---
        btn_w = 130
        btn_h = 45
        btn_spacing = 25
        total_action_btns_width = btn_w * 2 + btn_spacing
        btns_start_x = self.panel.rect.centerx - total_action_btns_width // 2
        btn_y = self.panel.rect.bottom - btn_h - 30

        self.save_button = Button(btns_start_x, btn_y, btn_w, btn_h, "Save",
                                  on_click_callback=self._trigger_save,
                                  normal_color=config.BUTTON_ACCENT_NORMAL_COLOR,
                                  hover_color=config.BUTTON_ACCENT_HOVER_COLOR,
                                  active_color=config.BUTTON_ACCENT_ACTIVE_COLOR,
                                  font_size=config.FONT_SIZE_LARGE - 2)
        self.elements.append(self.save_button)

        self.cancel_button = Button(btns_start_x + btn_w + btn_spacing, btn_y, btn_w, btn_h, "Cancel",
                                    on_click_callback=self._trigger_cancel,
                                    font_size=config.FONT_SIZE_LARGE - 2)
        self.elements.append(self.cancel_button)
        
        self._force_validate_inputs_and_update_save_button()

    def _on_speed_slider_changed(self, slider_value):
        """Callback when the speed slider's value changes."""
        new_delay = self._map_slider_to_delay(slider_value)
        self.current_working_maze_params["delay_ms"] = new_delay
        if self.on_speed_change_callback:
            self.on_speed_change_callback(new_delay) # Live update
        self._update_save_button_state()

    def _on_solver_button_clicked(self, solver_name):
        """Callback when a solver selection button is clicked."""
        self.current_working_solver = solver_name
        self._update_solver_button_styles()
        self._update_save_button_state()

    def _update_solver_button_styles(self):
        """Updates visual style of solver buttons based on selection."""
        for btn in self.solver_buttons:
            is_selected = (btn.text == self.current_working_solver)
            # Use Button's internal state management or direct color manipulation if needed
            # For simplicity, directly setting colors and forcing an update
            btn.colors["normal"] = config.CHOICE_BOX_SELECTED_COLOR if is_selected else config.CHOICE_BOX_NORMAL_COLOR
            btn.text_color_normal = config.CHOICE_BOX_SELECTED_TEXT_COLOR if is_selected else config.CHOICE_BOX_TEXT_COLOR
            btn.colors["hover"] = pygame.Color(btn.colors["normal"]).lerp(pygame.Color("white"), 0.15) # type: ignore
            btn._update_visual_state() # To apply color changes

    def _force_validate_inputs_and_update_save_button(self):
        """Forces re-validation of input fields and updates save button state."""
        if hasattr(self, 'width_input'): # Check if UI setup
            self.width_input._update_surface_and_validate(run_validation=True)
        if hasattr(self, 'height_input'):
            self.height_input._update_surface_and_validate(run_validation=True)
        self._update_save_button_state()

    def _has_changes(self):
        """Checks if current working settings differ from initial settings."""
        try:
            # Validate and get current input values
            current_w_val = int(self.width_input.get_value())
            current_h_val = int(self.height_input.get_value())
        except ValueError: # If inputs are not valid integers, consider it "unchanged" or handle as error
            return False # Or True, to prompt save if inputs are bad then fixed

        if self.initial_maze_params["width"] != current_w_val: return True
        if self.initial_maze_params["height"] != current_h_val: return True
        if self.initial_maze_params["delay_ms"] != self.current_working_maze_params["delay_ms"]: return True
        if self.initial_solver_name != self.current_working_solver: return True
        return False

    def _update_save_button_state(self):
        """Enables/disables the save button based on input validity and changes."""
        if not hasattr(self, 'save_button'): return # UI not fully setup

        are_inputs_valid = self.width_input.is_valid and self.height_input.is_valid
        # Option 1: Enable save only if valid AND changed
        # has_actual_changes = self._has_changes()
        # self.save_button.set_disabled(not (are_inputs_valid and has_actual_changes))
        
        # Option 2: Enable save if valid (simpler, save action can be a no-op if no changes)
        self.save_button.set_disabled(not are_inputs_valid)

    def _trigger_save(self):
        """Handles the save button click action."""
        self._force_validate_inputs_and_update_save_button() # Final validation

        if not self.save_button.disabled:
            # Compile the new parameters
            new_params = {
                "width": int(self.width_input.get_value()),
                "height": int(self.height_input.get_value()),
                "delay_ms": self.current_working_maze_params["delay_ms"] # From slider via callback
            }
            new_solver = self.current_working_solver

            # Update initial params to these new saved values for next time settings is opened
            self.initial_maze_params = new_params.copy()
            self.initial_solver_name = new_solver
            
            if self.on_save_callback:
                self.on_save_callback(new_params, new_solver)
            self.hide()
        else:
            # Optionally, provide feedback if save is attempted while disabled
            print("Settings: Save button clicked, but inputs are invalid or no changes.")


    def _trigger_cancel(self):
        """Handles the cancel button click or ESC key press."""
        # Revert any live changes (e.g., speed slider) back to initial state when window was opened
        if self.on_speed_change_callback:
            self.on_speed_change_callback(self.initial_maze_params["delay_ms"])
        
        if self.on_cancel_callback:
            self.on_cancel_callback() # Inform main application
        self.hide()

    def show(self, current_maze_params, current_solver_name):
        """Makes the settings window visible and resets its state to current app state."""
        self.visible = True
        # Update initial and working states from current application state
        self.initial_maze_params = current_maze_params.copy()
        self.initial_solver_name = current_solver_name
        self.current_working_maze_params = current_maze_params.copy()
        self.current_working_solver = current_solver_name
        
        # Reset UI elements to reflect these states
        self.width_input.set_value(str(self.current_working_maze_params["width"]), trigger_validation=False)
        self.height_input.set_value(str(self.current_working_maze_params["height"]), trigger_validation=False)
        self.speed_slider.set_value(self._map_delay_to_slider(self.current_working_maze_params["delay_ms"]), trigger_callback=False)
        self._update_solver_button_styles()
        self._force_validate_inputs_and_update_save_button() # Ensure correct initial state

    def hide(self):
        """Makes the settings window invisible."""
        self.visible = False

    def handle_event(self, event, mouse_pos):
        """Processes Pygame events for the settings window and its elements."""
        if not self.visible:
            return False

        consumed_by_element = False
        # Iterate in reverse to give priority to topmost elements (though not strictly needed here)
        for element in reversed(self.elements):
            if element.handle_event(event, mouse_pos):
                consumed_by_element = True
                break # Event handled by one element

        # Post-element handling checks (e.g., input validation affecting save button)
        # These are important if element actions (like typing) should immediately reflect on other elements (like save button)
        if event.type in (pygame.MOUSEBUTTONUP, pygame.KEYDOWN): # Check after key/mouse input
             self._update_save_button_state()


        if not consumed_by_element: # General window-level event handling
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._trigger_cancel()
                    return True # ESC consumed by window
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Check if an input box is currently active. If so, it handles Enter.
                    is_any_input_active = self.width_input.active or self.height_input.active
                    if not is_any_input_active:
                        self._trigger_save() # If no input active, Enter might mean "Save"
                        return True
        return consumed_by_element # Return True if any element consumed the event

    def update(self, dt, mouse_pos):
        """Updates all UI elements in the settings window."""
        if not self.visible:
            return
        for element in self.elements:
            element.update(dt, mouse_pos)

    def draw(self, screen):
        """Draws the settings window and its elements onto the provided surface."""
        if not self.visible:
            return

        # Draw a semi-transparent overlay for modal effect
        overlay_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 180)) # Dark, semi-transparent
        screen.blit(overlay_surface, (0, 0))

        self.panel.draw(screen) # Draw panel background and border
        for element in self.elements: # Draw all child UI elements
            if element.visible: # Redundant check if elements manage own visibility
                element.draw(screen)