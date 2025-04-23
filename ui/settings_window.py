import pygame
import config # Access config variables like colors, padding
import math # For mapping slider value

# Basic Input Box Class (can be expanded)
class InputBox:
    def __init__(self, x, y, w, h, initial_text='', font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = config.INPUT_BOX_COLOR
        self.text = initial_text
        self.font = font if font else pygame.font.Font(None, 32)
        self.txt_surface = self.font.render(initial_text, True, config.INPUT_TEXT_COLOR)
        self.active = False
        self.active_color = config.INPUT_BOX_ACTIVE_COLOR
        self.inactive_color = config.INPUT_BOX_COLOR

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.active_color if self.active else self.inactive_color
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.inactive_color
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode.isdigit():
                        self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, config.INPUT_TEXT_COLOR)
        return False

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 0, border_radius=5)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))


# Simple Slider Class
class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, handle_color, track_color):
        self.rect = pygame.Rect(x, y, w, h) # Overall area for interaction/drawing track
        self.min_val = min_val
        self.max_val = max_val
        self._value = initial_val
        self.handle_color = handle_color
        self.track_color = track_color
        self.handle_radius = h // 2 + 2 # Make handle slightly larger than track height
        self.track_height = h // 3
        self.track_y = y + (h - self.track_height) // 2
        self.dragging = False
        self._update_handle_pos() # Calculate initial handle position

    def _update_handle_pos(self):
        """Calculates handle x-position based on value."""
        ratio = (self._value - self.min_val) / (self.max_val - self.min_val) if (self.max_val - self.min_val) != 0 else 0
        self.handle_x = self.rect.x + int(ratio * self.rect.width)

    def handle_event(self, event):
        """Handles mouse events for dragging the slider."""
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if click is on the handle or track area
                handle_rect = pygame.Rect(self.handle_x - self.handle_radius, self.rect.y, self.handle_radius * 2, self.rect.height)
                if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos): # Allow clicking track too
                    self.dragging = True
                    # Update value based on click position immediately
                    new_x = max(self.rect.x, min(event.pos[0], self.rect.right))
                    ratio = (new_x - self.rect.x) / self.rect.width if self.rect.width != 0 else 0
                    self._value = self.min_val + ratio * (self.max_val - self.min_val)
                    self._value = max(self.min_val, min(self._value, self.max_val)) # Clamp value
                    self._update_handle_pos()
                    changed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = max(self.rect.x, min(event.pos[0], self.rect.right))
                ratio = (new_x - self.rect.x) / self.rect.width if self.rect.width != 0 else 0
                self._value = self.min_val + ratio * (self.max_val - self.min_val)
                self._value = max(self.min_val, min(self._value, self.max_val)) # Clamp value
                self._update_handle_pos()
                changed = True
        return changed

    def get_value(self):
        """Returns the current integer value of the slider."""
        return int(round(self._value))

    def set_value(self, value):
        """Sets the slider's value programmatically."""
        self._value = max(self.min_val, min(value, self.max_val))
        self._update_handle_pos()

    def draw(self, screen):
        """Draws the slider track and handle."""
        # Draw track
        track_rect = pygame.Rect(self.rect.x, self.track_y, self.rect.width, self.track_height)
        pygame.draw.rect(screen, self.track_color, track_rect, border_radius=self.track_height // 2)
        # Draw handle
        pygame.draw.circle(screen, self.handle_color, (self.handle_x, self.rect.centery), self.handle_radius)


# --- Settings Window State ---
width_input = None
height_input = None
speed_slider = None # Add slider state
on_speed_change_callback = None # Callback function
save_button_rect = None
cancel_button_rect = None
window_rect = None
font = None
solver_buttons = [] # List to hold solver selection buttons
selected_solver = "BFS" # Default selected solver
SOLVER_OPTIONS = ["BFS", "DFS", "A*"] # Available solver options


# Define speed range for the slider (visual 0-100) and mapping to delay (ms)
SLIDER_MIN_VAL = 0
SLIDER_MAX_VAL = 100
MIN_DELAY_MS = 1  # Fastest speed (increased)
MAX_DELAY_MS = 500 # Slowest speed

def map_slider_to_delay(slider_value):
    """Maps slider value (0-100) to delay in milliseconds (non-linear)."""
    # Use inverse mapping: higher slider value = lower delay (faster)
    ratio = slider_value / (SLIDER_MAX_VAL - SLIDER_MIN_VAL) if (SLIDER_MAX_VAL - SLIDER_MIN_VAL) != 0 else 0
    # Simple linear inverse mapping for now:
    delay = MAX_DELAY_MS - ratio * (MAX_DELAY_MS - MIN_DELAY_MS)
    return int(max(MIN_DELAY_MS, min(delay, MAX_DELAY_MS)))

def map_delay_to_slider(delay_ms):
    """Maps delay in milliseconds back to slider value (0-100)."""
    ratio = (MAX_DELAY_MS - delay_ms) / (MAX_DELAY_MS - MIN_DELAY_MS) if (MAX_DELAY_MS - MIN_DELAY_MS) != 0 else 0
    slider_value = ratio * (SLIDER_MAX_VAL - SLIDER_MIN_VAL)
    return int(max(SLIDER_MIN_VAL, min(round(slider_value), SLIDER_MAX_VAL)))


def init_settings_window(screen_width, screen_height, current_width, current_height,
                         initial_delay_ms, speed_change_callback, current_solver="BFS"): # Add current_solver parameter
    global width_input, height_input, speed_slider, on_speed_change_callback
    global save_button_rect, cancel_button_rect, window_rect, font
    global solver_buttons, selected_solver # Access global solver state

    font = pygame.font.Font(None, 32)
    on_speed_change_callback = speed_change_callback # Store the callback
    selected_solver = current_solver # Set initial selected solver

    # Define window dimensions and position (centered) - Increased height for slider and solver options
    win_width = 350
    win_height = 400 # Further increased height
    win_x = (screen_width - win_width) // 2
    win_y = (screen_height - win_height) // 2
    window_rect = pygame.Rect(win_x, win_y, win_width, win_height)

    # Input boxes
    input_w = 140
    input_h = 32
    padding = 10
    label_width = 100 # Adjusted label width slightly

    width_label = font.render("Width:", True, config.TEXT_COLOR)
    height_label = font.render("Height:", True, config.TEXT_COLOR)
    solver_label = font.render("Solver:", True, config.TEXT_COLOR) # Solver label
    speed_label = font.render("AI Speed:", True, config.TEXT_COLOR) # Speed label


    width_input_x = win_x + label_width + padding
    width_input_y = win_y + padding * 3
    height_input_x = width_input_x
    height_input_y = width_input_y + input_h + padding * 2

    width_input = InputBox(width_input_x, width_input_y, input_w, input_h, str(current_width), font)
    height_input = InputBox(height_input_x, height_input_y, input_w, input_h, str(current_height), font)

    # Solver Selection Buttons
    solver_button_w = 80
    solver_button_h = 30
    solver_button_padding = 5
    total_solver_button_width = (solver_button_w * len(SOLVER_OPTIONS)) + (solver_button_padding * (len(SOLVER_OPTIONS) - 1))
    solver_buttons_start_x = win_x + (win_width - total_solver_button_width) // 2
    solver_buttons_y = height_input_y + input_h + padding * 4 # Position below height input

    solver_buttons = []
    for i, solver_name in enumerate(SOLVER_OPTIONS):
        btn_rect = pygame.Rect(
            solver_buttons_start_x + i * (solver_button_w + solver_button_padding),
            solver_buttons_y,
            solver_button_w,
            solver_button_h
        )
        text_surface = font.render(solver_name, True, config.BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=btn_rect.center)
        solver_buttons.append({
            "name": solver_name,
            "rect": btn_rect,
            "text_surface": text_surface,
            "text_rect": text_rect
        })


    # Slider (position adjusted for solver buttons)
    slider_w = input_w + 50 # Make slider wider
    slider_h = 20
    slider_x = win_x + (win_width - slider_w) // 2 # Center slider horizontally
    slider_y = solver_buttons_y + solver_button_h + padding * 3 # Position below solver buttons
    initial_slider_val = map_delay_to_slider(initial_delay_ms)
    speed_slider = Slider(slider_x, slider_y, slider_w, slider_h,
                          SLIDER_MIN_VAL, SLIDER_MAX_VAL, initial_slider_val,
                          config.SLIDER_HANDLE_COLOR, config.SLIDER_TRACK_COLOR)

    # Buttons (position adjusted for new window height)
    button_w = 100
    button_h = 40
    button_y = win_y + win_height - button_h - padding * 2
    total_button_width = button_w * 2 + padding
    start_button_x = win_x + (win_width - total_button_width) // 2

    save_button_rect = pygame.Rect(start_button_x, button_y, button_w, button_h)
    cancel_button_rect = pygame.Rect(start_button_x + button_w + padding, button_y, button_w, button_h)


def draw_settings_window(screen):
    global solver_buttons, selected_solver # Declare global
    if not font or not width_input or not height_input or not speed_slider or not save_button_rect or not cancel_button_rect or not window_rect or not solver_buttons:
        print("Warning: Settings UI not fully initialized!")
        return

    # Draw background panel
    pygame.draw.rect(screen, config.PANEL_COLOR, window_rect, border_radius=10)
    pygame.draw.rect(screen, config.BORDER_COLOR, window_rect, 2, border_radius=10) # Border

    win_x = window_rect.x

    # Draw Title
    title_surface = font.render("Settings", True, config.TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(window_rect.centerx, window_rect.top + 20))
    screen.blit(title_surface, title_rect)

    # Draw Labels
    padding = 10
    label_width = 100 # Use consistent label width
    width_label_surface = font.render("Width:", True, config.TEXT_COLOR)
    height_label_surface = font.render("Height:", True, config.TEXT_COLOR)
    solver_label_surface = font.render("Solver:", True, config.TEXT_COLOR) # Solver label
    speed_label_surface = font.render("AI Speed:", True, config.TEXT_COLOR) # Speed label

    screen.blit(width_label_surface, (win_x + padding, width_input.rect.y + 5))
    screen.blit(height_label_surface, (win_x + padding, height_input.rect.y + 5))
    screen.blit(solver_label_surface, (win_x + padding, solver_buttons[0]["rect"].y + (solver_buttons[0]["rect"].height - solver_label_surface.get_height()) // 2)) # Position solver label
    # Position speed label above the slider (moved up by font height)
    screen.blit(speed_label_surface, (win_x + padding, speed_slider.rect.y - speed_label_surface.get_height()))

    # Draw Input Boxes
    width_input.draw(screen)
    height_input.draw(screen)

    # Draw Solver Buttons
    mouse_pos = pygame.mouse.get_pos()
    for btn in solver_buttons:
        btn_color = config.BUTTON_HOVER_COLOR if btn["rect"].collidepoint(mouse_pos) else config.BUTTON_COLOR
        # Highlight selected solver button
        if btn["name"] == selected_solver:
             btn_color = (btn_color[0] + 50, btn_color[1] + 50, btn_color[2] + 50) # Make selected button slightly brighter

        pygame.draw.rect(screen, btn_color, btn["rect"], border_radius=5)
        screen.blit(btn["text_surface"], btn["text_rect"])


    # Draw Slider
    speed_slider.draw(screen)
    # Optional: Draw slider value text
    slider_val_text = font.render(f"{speed_slider.get_value()}", True, config.TEXT_COLOR)
    screen.blit(slider_val_text, (speed_slider.rect.right + padding, speed_slider.rect.y + (speed_slider.rect.height - slider_val_text.get_height()) // 2))


    # Draw Action Buttons (Save/Cancel)
    save_hover = save_button_rect.collidepoint(mouse_pos)
    cancel_hover = cancel_button_rect.collidepoint(mouse_pos)

    save_color = config.BUTTON_HOVER_COLOR if save_hover else config.BUTTON_COLOR
    cancel_color = config.BUTTON_HOVER_COLOR if cancel_hover else config.BUTTON_COLOR

    pygame.draw.rect(screen, save_color, save_button_rect, border_radius=5)
    pygame.draw.rect(screen, cancel_color, cancel_button_rect, border_radius=5)

    save_text = font.render("Save", True, config.BUTTON_TEXT_COLOR)
    cancel_text = font.render("Cancel", True, config.BUTTON_TEXT_COLOR)
    save_text_rect = save_text.get_rect(center=save_button_rect.center)
    cancel_text_rect = cancel_text.get_rect(center=cancel_button_rect.center)

    screen.blit(save_text, save_text_rect)
    screen.blit(cancel_text, cancel_text_rect)


def handle_settings_event(event):
    global on_speed_change_callback, selected_solver, solver_buttons # Access global state, add solver_buttons
    if not font or not width_input or not height_input or not speed_slider or not save_button_rect or not cancel_button_rect or not window_rect or not solver_buttons:
         return None # Not initialized

    # Handle events for input boxes
    width_enter = width_input.handle_event(event)
    height_enter = height_input.handle_event(event)

    # Handle events for slider
    slider_changed = speed_slider.handle_event(event)
    if slider_changed and on_speed_change_callback:
        new_delay = map_slider_to_delay(speed_slider.get_value())
        on_speed_change_callback(new_delay) # Call the callback with the new delay value
        # We don't return an action here, the callback handles the immediate effect

    # Check for button clicks
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            # Check solver button clicks
            for btn in solver_buttons:
                if btn["rect"].collidepoint(event.pos):
                    selected_solver = btn["name"]
                    print(f"Selected solver: {selected_solver}")
                    # No action returned, just update state and redraw

            # Check Save/Cancel button clicks
            if save_button_rect.collidepoint(event.pos):
                try:
                    new_width = int(width_input.text)
                    new_height = int(height_input.text)
                    if new_width > 0 and new_height > 0:
                        print(f"Settings saved: Width={new_width}, Height={new_height}, Solver={selected_solver}")
                        # Speed is already handled by callback, just save dimensions and solver
                        return {"action": "save", "width": new_width, "height": new_height, "solver": selected_solver}
                    else:
                        print("Invalid dimensions. Width and Height must be positive.")
                        return None
                except ValueError:
                    print("Invalid input. Please enter numbers for width and height.")
                    return None

            elif cancel_button_rect.collidepoint(event.pos):
                print("Settings canceled.")
                return {"action": "cancel"}

    # Check for Enter key press in input boxes (no action for now)
    if width_enter or height_enter:
        pass

    # Check for Escape key to cancel
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            print("Settings canceled (Escape key).")
            return {"action": "cancel"}

    return None # No save/cancel action completed
