import pygame
import config # Access config variables like colors, padding

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
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.active_color if self.active else self.inactive_color
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # print(self.text) # Or handle validation/submission
                    self.active = False
                    self.color = self.inactive_color
                    # Return True to indicate Enter was pressed (optional)
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Allow only digits
                    if event.unicode.isdigit():
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, config.INPUT_TEXT_COLOR)
        return False # Default: Enter not pressed

    def update(self):
        # Resize the box if the text is too long.
        # width = max(200, self.txt_surface.get_width()+10)
        # self.rect.w = width
        pass # No dynamic width for now

    def draw(self, screen):
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 0, border_radius=5)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))


# --- Settings Window State ---
width_input = None
height_input = None
save_button_rect = None
cancel_button_rect = None
window_rect = None # Add global for the main window rect
font = None
# needs_redraw = True # Flag to redraw only when necessary (REMOVED FOR TESTING)

def init_settings_window(screen_width, screen_height, current_width, current_height):
    # global width_input, height_input, save_button_rect, cancel_button_rect, window_rect, font, needs_redraw # Removed needs_redraw
    global width_input, height_input, save_button_rect, cancel_button_rect, window_rect, font
    font = pygame.font.Font(None, 32) # Use a consistent font

    # Define window dimensions and position (centered)
    win_width = 350
    win_height = 250
    win_x = (screen_width - win_width) // 2
    win_y = (screen_height - win_height) // 2
    # Store the calculated window rect globally
    window_rect = pygame.Rect(win_x, win_y, win_width, win_height)

    # Input boxes
    input_w = 140
    input_h = 32
    padding = 10
    label_width = 80

    width_label = font.render("Width:", True, config.TEXT_COLOR)
    height_label = font.render("Height:", True, config.TEXT_COLOR)

    width_input_x = win_x + label_width + padding
    width_input_y = win_y + padding * 3
    height_input_x = width_input_x
    height_input_y = width_input_y + input_h + padding * 2

    width_input = InputBox(width_input_x, width_input_y, input_w, input_h, str(current_width), font)
    height_input = InputBox(height_input_x, height_input_y, input_w, input_h, str(current_height), font)

    # Buttons
    button_w = 100
    button_h = 40
    button_y = win_y + win_height - button_h - padding * 2
    total_button_width = button_w * 2 + padding
    start_button_x = win_x + (win_width - total_button_width) // 2

    save_button_rect = pygame.Rect(start_button_x, button_y, button_w, button_h)
    cancel_button_rect = pygame.Rect(start_button_x + button_w + padding, button_y, button_w, button_h)

    # needs_redraw = True # Force initial draw (REMOVED FOR TESTING)

def draw_settings_window(screen):
    # global needs_redraw # (REMOVED FOR TESTING)
    # if not needs_redraw: # (REMOVED FOR TESTING)
    #     return # Don't redraw if nothing changed # (REMOVED FOR TESTING)

    # Use the globally stored window_rect
    if not font or not width_input or not height_input or not save_button_rect or not cancel_button_rect or not window_rect:
        print("Warning: Settings UI not initialized or window_rect missing!")
        return

    # Draw background panel using the stored rect
    pygame.draw.rect(screen, config.PANEL_COLOR, window_rect, border_radius=10)
    pygame.draw.rect(screen, config.BORDER_COLOR, window_rect, 2, border_radius=10) # Border

    # Use window_rect for positioning other elements relative to the panel
    win_x = window_rect.x # Get x from the stored rect

    # Draw Title
    title_surface = font.render("Settings", True, config.TEXT_COLOR)
    title_rect = title_surface.get_rect(center=(window_rect.centerx, window_rect.top + 20))
    screen.blit(title_surface, title_rect)

    # Draw Labels (position relative to the panel's win_x)
    label_width = 80
    padding = 10
    width_label_surface = font.render("Width:", True, config.TEXT_COLOR)
    height_label_surface = font.render("Height:", True, config.TEXT_COLOR)
    screen.blit(width_label_surface, (win_x + padding, width_input.rect.y + 5))
    screen.blit(height_label_surface, (win_x + padding, height_input.rect.y + 5))


    # Draw Input Boxes
    width_input.draw(screen)
    height_input.draw(screen)

    # Draw Buttons
    mouse_pos = pygame.mouse.get_pos()
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

    # needs_redraw = False # Drawing is complete for this frame (REMOVED FOR TESTING)


def handle_settings_event(event):
    # global needs_redraw # (REMOVED FOR TESTING)
    if not width_input or not height_input or not save_button_rect or not cancel_button_rect:
        return None # Not initialized

    # Handle events for input boxes
    width_enter = width_input.handle_event(event)
    height_enter = height_input.handle_event(event)

    # if width_input.active or height_input.active: # (REMOVED FOR TESTING)
    #     needs_redraw = True # Redraw if input is active (typing or state change) # (REMOVED FOR TESTING)

    # Check for button clicks
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            if save_button_rect.collidepoint(event.pos):
                # needs_redraw = True # (REMOVED FOR TESTING)
                try:
                    new_width = int(width_input.text)
                    new_height = int(height_input.text)
                    # Add validation if needed (e.g., min/max size)
                    if new_width > 0 and new_height > 0:
                        print(f"Settings saved: Width={new_width}, Height={new_height}")
                        return {"action": "save", "width": new_width, "height": new_height}
                    else:
                        print("Invalid dimensions. Width and Height must be positive.")
                        # Optionally provide user feedback here (e.g., change input box color)
                        return None # Indicate error or no action
                except ValueError:
                    print("Invalid input. Please enter numbers for width and height.")
                    # Optionally provide user feedback
                    return None # Indicate error or no action

            elif cancel_button_rect.collidepoint(event.pos):
                # needs_redraw = True # (REMOVED FOR TESTING)
                print("Settings canceled.")
                return {"action": "cancel"}

    # Check for Enter key press in input boxes (could trigger save)
    if width_enter or height_enter:
        # Decide if Enter should trigger save (e.g., if both inputs are valid)
        # For simplicity, we'll require clicking the Save button for now.
        pass

    # Check for Escape key to cancel
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            # needs_redraw = True # (REMOVED FOR TESTING)
            print("Settings canceled (Escape key).")
            return {"action": "cancel"}

    return None # No action completed
