import pygame
import config
import math

# Helper function for text rendering
def render_text(text, font_size, color, font_name=None, antialias=True):
    """Renders text and returns the surface and its rect."""
    font = pygame.font.Font(font_name or config.FONT_NAME, font_size)
    text_surface = font.render(text, antialias, color)
    return text_surface, text_surface.get_rect()

class UIElement:
    """Base class for all UI elements."""
    def __init__(self, x, y, w, h, parent_surface=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.parent_surface = parent_surface # For relative positioning or drawing context
        self.visible = True
        self.disabled = False
        self.tooltip_text = None
        self.id = None # Optional identifier

    def handle_event(self, event, mouse_pos):
        """Handles a single Pygame event. Returns True if event was consumed."""
        return False # Base implementation consumes no events

    def update(self, dt, mouse_pos):
        """Updates element state (e.g., for animations, hover effects)."""
        pass # Base implementation does nothing

    def draw(self, surface):
        """Draws the element on the given surface."""
        if not self.visible:
            return # Don't draw if not visible

    def set_tooltip(self, text):
        self.tooltip_text = text

    def set_visibility(self, visible):
        self.visible = visible

    def set_disabled(self, disabled):
        self.disabled = disabled
        # Potentially trigger a visual update if state changes appearance
        self._on_disabled_changed()

    def _on_disabled_changed(self):
        """Called when disabled state changes, for subclasses to update appearance."""
        pass

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos) if self.visible and not self.disabled else False


class Label(UIElement):
    def __init__(self, x, y, text, font_size, color,
                 font_name=None, antialias=True, alignment="left",
                 bg_color=None, padding=0, parent_surface=None, fixed_width=None, fixed_height=None): # Added fixed_width/height
        
        self.text = text
        self.font_size = font_size
        self.font_name = font_name or config.FONT_NAME
        self._color = color # Store as private to use property
        self.antialias = antialias
        self.alignment = alignment # "left", "center", "right"
        self.bg_color = bg_color
        self.padding = padding

        self._font = pygame.font.Font(self.font_name, self.font_size)
        # Render initially to get dimensions
        self._text_surface = self._font.render(self.text, self.antialias, self._color)
        
        text_w_with_padding = self._text_surface.get_width() + 2 * padding
        text_h_with_padding = self._text_surface.get_height() + 2 * padding

        # Use fixed dimensions if provided, otherwise fit to text
        actual_w = fixed_width if fixed_width is not None else text_w_with_padding
        actual_h = fixed_height if fixed_height is not None else text_h_with_padding
        
        super().__init__(x, y, actual_w, actual_h, parent_surface)
        self._realign_text()

    def _render_and_realign(self):
        """Internal method to re-render text and realign."""
        self._text_surface = self._font.render(self.text, self.antialias, self._color)
        # If label size is not fixed, it could adapt to new text here.
        # For now, assuming fixed size after init or external management.
        self._realign_text()

    def _realign_text(self):
        """Adjusts the position of the text surface within the label's rect based on alignment."""
        self.text_rect = self._text_surface.get_rect() # Get rect of the current text_surface
        
        # Position text_rect relative to self.rect (the Label's bounding box)
        if self.alignment == "left":
            self.text_rect.topleft = (self.rect.x + self.padding, self.rect.y + self.padding)
        elif self.alignment == "center":
            self.text_rect.center = self.rect.center
        elif self.alignment == "right":
            self.text_rect.topright = (self.rect.right - self.padding, self.rect.y + self.padding)
        
        # Ensure text doesn't overflow padding within the self.rect
        self.text_rect.clamp_ip(self.rect.inflate(-2*self.padding, -2*self.padding))


    def set_text(self, new_text):
        if self.text != new_text:
            self.text = new_text
            self._render_and_realign()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, new_color):
        if self._color != new_color:
            self._color = new_color
            self._render_and_realign()


    def set_position(self, x, y): # Overload to also realign text
        self.rect.topleft = (x,y)
        self._realign_text() # Text position is relative to label's rect

    def draw(self, surface):
        if not self.visible:
            return
        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect)
        surface.blit(self._text_surface, self.text_rect)


class Button(UIElement):
    def __init__(self, x, y, w, h, text,
                 on_click_callback=None, callback_args=None,
                 font_size=config.BUTTON_FONT_SIZE,
                 text_color=config.BUTTON_TEXT_COLOR,
                 normal_color=config.BUTTON_NORMAL_COLOR,
                 hover_color=config.BUTTON_HOVER_COLOR,
                 active_color=config.BUTTON_ACTIVE_COLOR,
                 disabled_color=config.BUTTON_DISABLED_COLOR,
                 disabled_text_color = config.BUTTON_DISABLED_TEXT_COLOR,
                 border_radius=config.BUTTON_BORDER_RADIUS,
                 border_width=config.BUTTON_BORDER_WIDTH,
                 tooltip=None, parent_surface=None):
        super().__init__(x, y, w, h, parent_surface)
        
        self.text = text
        self.on_click_callback = on_click_callback
        self.callback_args = callback_args if callback_args is not None else []

        self.font_size = font_size
        self.text_color_normal = text_color
        self.text_color_disabled = disabled_text_color
        
        self.colors = {
            "normal": normal_color,
            "hover": hover_color,
            "active": active_color, # Clicked
            "disabled": disabled_color
        }
        self.border_radius = border_radius
        self.border_width = border_width # If > 0, a border of this color will be drawn slightly darker

        self._font = pygame.font.Font(config.FONT_NAME, self.font_size)
        self._current_bg_color = self.colors["normal"]
        self._current_text_color = self.text_color_normal
        
        self.is_hovered_state = False
        self.is_pressed_state = False # Mouse button is down on the button
        
        self._update_visual_state() # Initial render
        if tooltip: self.set_tooltip(tooltip)

    def _render_text_surface_internal(self): # Renamed to avoid conflict if subclass uses _render_text_surface
        self.text_surface = self._font.render(self.text, True, self._current_text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def _on_disabled_changed(self):
        self.is_hovered_state = False
        self.is_pressed_state = False
        self._update_visual_state()

    def _update_visual_state(self):
        if self.disabled:
            self._current_bg_color = self.colors["disabled"]
            self._current_text_color = self.text_color_disabled
        elif self.is_pressed_state:
            self._current_bg_color = self.colors["active"]
            self._current_text_color = self.text_color_normal # Or a specific active text color
        elif self.is_hovered_state:
            self._current_bg_color = self.colors["hover"]
            self._current_text_color = self.text_color_normal
        else:
            self._current_bg_color = self.colors["normal"]
            self._current_text_color = self.text_color_normal
        self._render_text_surface_internal() # Re-render text if color or text changed

    def handle_event(self, event, mouse_pos):
        if not self.visible or self.disabled:
            # If disabled, ensure hover/pressed states are false
            if self.is_hovered_state or self.is_pressed_state:
                self.is_hovered_state = False
                self.is_pressed_state = False
                self._update_visual_state() # Update to disabled appearance
            return False

        consumed = False
        # Manage hover state first, as it affects visual feedback
        current_hover = self.is_hovered(mouse_pos)
        if current_hover != self.is_hovered_state:
            self.is_hovered_state = current_hover
            if not self.is_pressed_state: # Only update visuals if not currently pressed
                self._update_visual_state()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered_state: # Use the updated hover state
                self.is_pressed_state = True
                self._update_visual_state() # Update to active appearance
                consumed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed_state:
                self.is_pressed_state = False
                # Check hover again on mouse up before firing callback
                if self.is_hovered(mouse_pos): 
                    if self.on_click_callback:
                        self.on_click_callback(*self.callback_args)
                self._update_visual_state() # Update to hover or normal appearance
                consumed = True
            # If mouse button released outside after pressing inside, reset pressed state and visuals
            elif event.button == 1 and not self.is_hovered(mouse_pos) and self.is_pressed_state:
                 self.is_pressed_state = False
                 self._update_visual_state() # Update to normal appearance
                 consumed = True # Consumed the mouse up that ended a press sequence


        return consumed

    def update(self, dt, mouse_pos):
        if self.disabled or not self.visible:
            if self.is_hovered_state or self.is_pressed_state:
                self.is_hovered_state = False
                self.is_pressed_state = False
                self._update_visual_state()
            return

        # Continuously update hover state if not pressed
        if not self.is_pressed_state:
            current_hover = self.is_hovered(mouse_pos)
            if current_hover != self.is_hovered_state:
                self.is_hovered_state = current_hover
                self._update_visual_state()

    def draw(self, surface):
        if not self.visible:
            return

        pygame.draw.rect(surface, self._current_bg_color, self.rect, border_radius=self.border_radius)
        
        if self.border_width > 0:
            border_color = tuple(max(0, c - 20) for c in self._current_bg_color[:3]) # Slightly darker border
            pygame.draw.rect(surface, border_color, self.rect, width=self.border_width, border_radius=self.border_radius)

        surface.blit(self.text_surface, self.text_rect)

    def set_text(self, new_text):
        if self.text != new_text:
            self.text = new_text
            self._update_visual_state() # Re-render text and potentially adjust rect if needed


class InputBox(UIElement):
    def __init__(self, x, y, w, h, initial_text='',
                 font_size=config.INPUT_BOX_FONT_SIZE,
                 max_len=10, allow_empty=True, validation_func=None,
                 text_color=config.INPUT_BOX_TEXT_COLOR,
                 bg_color=config.INPUT_BOX_BG_COLOR,
                 active_bg_color=config.INPUT_BOX_ACTIVE_BG_COLOR,
                 border_color=config.INPUT_BOX_BORDER_COLOR,
                 active_border_color=config.INPUT_BOX_ACTIVE_BORDER_COLOR,
                 invalid_bg_color=config.INPUT_BOX_INVALID_BG_COLOR,
                 invalid_border_color=config.INPUT_BOX_INVALID_BORDER_COLOR,
                 parent_surface=None, numeric_only=False, on_submit_callback=None): # Added on_submit_callback
        super().__init__(x, y, w, h, parent_surface)

        self.text = str(initial_text)
        self.font_size = font_size
        self.max_len = max_len
        self.allow_empty = allow_empty
        self.validation_func = validation_func # Should return True if valid
        self.numeric_only = numeric_only
        self.on_submit_callback = on_submit_callback # Called on Enter/Return

        self.colors = {
            "text": text_color,
            "bg_normal": bg_color,
            "bg_active": active_bg_color,
            "bg_invalid": invalid_bg_color,
            "border_normal": border_color,
            "border_active": active_border_color,
            "border_invalid": invalid_border_color,
        }

        self._font = pygame.font.Font(config.FONT_NAME, self.font_size)
        self.active = False # Is the input box focused?
        self.is_valid = True # Based on validation_func
        self._cursor_visible = False
        self._cursor_timer = 0
        self._cursor_blink_rate = 0.5 # seconds

        self._padding = 8 # Internal padding for text
        self._update_surface_and_validate(run_validation=True, initial_setup=True)


    def _update_surface_and_validate(self, run_validation=False, initial_setup=False):
        if run_validation or initial_setup: # Validate on initial setup as well
            if self.validation_func:
                self.is_valid = self.validation_func(self.text)
            elif not self.allow_empty and not self.text: # If empty not allowed and text is empty
                self.is_valid = False
            else: # Default to valid if no specific validation or if empty is allowed
                self.is_valid = True
        
        self.txt_surface = self._font.render(self.text, True, self.colors["text"])


    def handle_event(self, event, mouse_pos):
        if not self.visible: return False
        
        event_consumed = False
        prev_active_state = self.active
        text_changed = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(mouse_pos):
                    self.active = True
                    event_consumed = True
                else: # Clicked outside
                    if self.active: # Was active, now losing focus
                         self._update_surface_and_validate(run_validation=True) # Final validation on blur
                    self.active = False
        
        if self.active != prev_active_state: # Focus changed
            self._cursor_visible = self.active
            self._cursor_timer = 0


        if event.type == pygame.KEYDOWN and self.active:
            event_consumed = True
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.active = False # Lose focus
                self._update_surface_and_validate(run_validation=True) # Final validation
                if self.on_submit_callback and self.is_valid:
                    self.on_submit_callback(self.text)
            elif event.key == pygame.K_BACKSPACE:
                if self.text: # Only if text is not empty
                    self.text = self.text[:-1]
                    text_changed = True
            elif event.key == pygame.K_ESCAPE:
                self.active = False # Lose focus
                # Optionally revert text to initial or last valid state (not implemented here)
                self._update_surface_and_validate(run_validation=True) # Validate current text
            else:
                if len(self.text) < self.max_len:
                    char = event.unicode
                    can_add_char = False
                    if self.numeric_only:
                        if char.isdigit(): can_add_char = True
                    elif char.isprintable(): # Basic check for printable chars
                        can_add_char = True
                    
                    if can_add_char:
                        self.text += char
                        text_changed = True
            
            if text_changed: # If text was modified by backspace or char input
                self._update_surface_and_validate(run_validation=True) # Validate as user types

        return event_consumed

    def update(self, dt, mouse_pos):
        if self.active:
            self._cursor_timer += dt
            if self._cursor_timer >= self._cursor_blink_rate:
                self._cursor_timer = 0
                self._cursor_visible = not self._cursor_visible
        elif self._cursor_visible: # Ensure cursor is hidden when not active
            self._cursor_visible = False


    def draw(self, surface):
        if not self.visible: return

        current_bg_color = self.colors["bg_normal"]
        current_border_color = self.colors["border_normal"]

        if not self.is_valid:
            current_bg_color = self.colors["bg_invalid"]
            current_border_color = self.colors["border_invalid"]
        elif self.active:
            current_bg_color = self.colors["bg_active"]
            current_border_color = self.colors["border_active"]
        
        pygame.draw.rect(surface, current_bg_color, self.rect, border_radius=config.BUTTON_BORDER_RADIUS // 2)
        pygame.draw.rect(surface, current_border_color, self.rect, width=1, border_radius=config.BUTTON_BORDER_RADIUS // 2)

        text_render_x = self.rect.x + self._padding
        text_render_y = self.rect.centery - self.txt_surface.get_height() // 2
        
        # Clipping text if too long for the box (basic version)
        available_width_for_text = self.rect.width - 2 * self._padding
        if self.txt_surface.get_width() > available_width_for_text:
            # Render only the part of the text that fits, or scroll (more complex)
            # For now, just blit it; it might overflow visually.
            # A proper solution would involve a text_offset or rendering to a subsurface.
            surface.blit(self.txt_surface, (text_render_x, text_render_y), 
                         area=pygame.Rect(0,0, available_width_for_text, self.txt_surface.get_height()))

        else:
            surface.blit(self.txt_surface, (text_render_x, text_render_y))


        if self.active and self._cursor_visible:
            # Position cursor after the visible part of the text
            cursor_x_offset = self.txt_surface.get_width()
            if cursor_x_offset > available_width_for_text:
                cursor_x_offset = available_width_for_text
            
            cursor_x = text_render_x + cursor_x_offset + 1
            cursor_y_start = self.rect.y + self._padding // 2
            cursor_y_end = self.rect.bottom - self._padding // 2
            pygame.draw.line(surface, self.colors["text"], (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 1)

    def get_value(self):
        return self.text
    
    def set_value(self, value, trigger_validation=True):
        self.text = str(value)
        if len(self.text) > self.max_len:
            self.text = self.text[:self.max_len]
        self._update_surface_and_validate(run_validation=trigger_validation)


class Slider(UIElement):
    def __init__(self, x, y, w, h, min_val, max_val, initial_val,
                 on_value_change_callback=None, callback_args=None,
                 show_value_text=True,
                 track_color=config.SLIDER_TRACK_COLOR,
                 handle_color=config.SLIDER_HANDLE_COLOR,
                 handle_hover_color=config.SLIDER_HANDLE_HOVER_COLOR,
                 value_text_color=config.SLIDER_VALUE_TEXT_COLOR,
                 parent_surface=None, discrete_steps=None): # Added discrete_steps
        super().__init__(x, y, w, h, parent_surface)
        
        self.min_val = min_val
        self.max_val = max_val
        self._value = float(initial_val) # Internal value is float for smooth dragging
        self.on_value_change_callback = on_value_change_callback
        self.callback_args = callback_args if callback_args is not None else []
        self.discrete_steps = discrete_steps # If not None, number of steps including min/max

        self.show_value_text = show_value_text
        self.track_color = track_color
        self.handle_colors = {"normal": handle_color, "hover": handle_hover_color}
        self.value_text_color = value_text_color

        self.track_height = max(2, int(h * config.SLIDER_TRACK_HEIGHT_RATIO)) # Min height 2
        self.track_rect = pygame.Rect(x, y + (h - self.track_height) // 2, w, self.track_height)
        
        self.handle_radius = max(3, int((h / 2) * config.SLIDER_HANDLE_RADIUS_FACTOR))
        
        self.dragging = False
        self.is_hovered_state = False # Hovering over the handle specifically
        self._current_handle_color = self.handle_colors["normal"]

        self._font = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_SMALL)
        
        self._snap_value_to_discrete_step() # Snap initial value if discrete
        self._update_handle_pos_from_value()
        self._update_value_text_surface()

    def _snap_value_to_discrete_step(self):
        if self.discrete_steps and self.discrete_steps > 1:
            val_range = self.max_val - self.min_val
            step_size = val_range / float(self.discrete_steps - 1)
            
            # Find the closest step
            num_steps_from_min = round((self._value - self.min_val) / step_size)
            self._value = self.min_val + num_steps_from_min * step_size
            self._value = max(self.min_val, min(self._value, self.max_val)) # Clamp


    def _update_handle_pos_from_value(self):
        """Calculates handle_x based on current _value."""
        val_range = self.max_val - self.min_val
        ratio = (self._value - self.min_val) / val_range if val_range != 0 else 0
        self.handle_x = self.track_rect.x + int(ratio * self.track_rect.width)
        self.handle_x = max(self.track_rect.left, min(self.handle_x, self.track_rect.right))
        self.handle_y = self.rect.centery

    def _update_value_from_handle_pos(self, mouse_x_abs):
        """Calculates _value based on mouse_x relative to the track's start."""
        relative_x = mouse_x_abs - self.track_rect.x
        ratio = relative_x / float(self.track_rect.width) if self.track_rect.width != 0 else 0
        ratio = max(0.0, min(1.0, ratio))
        
        self._value = self.min_val + ratio * (self.max_val - self.min_val)
        self._snap_value_to_discrete_step() # Snap if discrete
        self._value = max(self.min_val, min(self._value, self.max_val)) # Clamp

    def _update_value_text_surface(self):
        if self.show_value_text:
            display_val_str = f"{self.get_value()}" # get_value() returns int or rounded
            self.value_text_surface = self._font.render(display_val_str, True, self.value_text_color)
            # Position text to the right of the slider's main rect
            self.value_text_rect = self.value_text_surface.get_rect(
                midleft=(self.rect.right + 10, self.rect.centery)
            )
        else:
            self.value_text_surface = None
            self.value_text_rect = None


    def _get_handle_hitbox(self): # Make hitbox slightly larger than visual handle
        return pygame.Rect(
            self.handle_x - self.handle_radius -2, # Extra padding for easier click
            self.handle_y - self.handle_radius -2,
            (self.handle_radius+2) * 2,
            (self.handle_radius+2) * 2
        )

    def handle_event(self, event, mouse_pos):
        if not self.visible or self.disabled: return False
        
        value_changed_in_event = False
        consumed = False

        # Hover check uses a slightly larger rect for easier interaction
        handle_hitbox = self._get_handle_hitbox()
        is_mouse_over_handle_area = handle_hitbox.collidepoint(mouse_pos)
        is_mouse_over_track_area = self.track_rect.collidepoint(mouse_pos)


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Allow clicking on track or handle to start drag/set value
                if is_mouse_over_handle_area or is_mouse_over_track_area:
                    self.dragging = True
                    self._update_value_from_handle_pos(mouse_pos[0]) # Set value based on click
                    self._update_handle_pos_from_value() # Sync handle to new value
                    value_changed_in_event = True
                    consumed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.dragging:
                    self.dragging = False
                    # Value might have already changed during drag, callback triggered below if so
                    consumed = True # Consumed the mouse up that ended a drag
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value_from_handle_pos(mouse_pos[0])
                self._update_handle_pos_from_value()
                value_changed_in_event = True
                consumed = True # Mouse motion during drag is consumed
        
        # Update hover state for visual feedback (handle color)
        if not self.dragging: # Don't change handle color if dragging
            if is_mouse_over_handle_area != self.is_hovered_state:
                self.is_hovered_state = is_mouse_over_handle_area
                self._current_handle_color = self.handle_colors["hover"] if self.is_hovered_state else self.handle_colors["normal"]
        elif self.dragging : # Ensure handle stays in 'active' or 'normal' color while dragging
             self._current_handle_color = self.handle_colors["normal"] # Or an "active" handle color if defined

        if value_changed_in_event:
            self._update_value_text_surface()
            if self.on_value_change_callback:
                self.on_value_change_callback(self.get_value(), *self.callback_args)
        
        return consumed

    def update(self, dt, mouse_pos): # dt not used, mouse_pos for hover if not dragging
        if self.disabled or not self.visible:
            if self.is_hovered_state or self.dragging:
                self.is_hovered_state = False
                self.dragging = False
                self._current_handle_color = self.handle_colors["normal"]
            return

        if not self.dragging:
            is_mouse_over_handle_area = self._get_handle_hitbox().collidepoint(mouse_pos)
            if is_mouse_over_handle_area != self.is_hovered_state:
                self.is_hovered_state = is_mouse_over_handle_area
                self._current_handle_color = self.handle_colors["hover"] if self.is_hovered_state else self.handle_colors["normal"]


    def draw(self, surface):
        if not self.visible: return

        pygame.draw.rect(surface, self.track_color, self.track_rect, border_radius=self.track_rect.height // 2)
        pygame.draw.circle(surface, self._current_handle_color, (self.handle_x, self.handle_y), self.handle_radius)
        
        if self.show_value_text and self.value_text_surface and self.value_text_rect:
            surface.blit(self.value_text_surface, self.value_text_rect)

    def get_value(self):
        # Return integer representation, or float if steps are float-based
        if self.discrete_steps and self.discrete_steps > 1:
            # If discrete steps, _value should already be snapped.
            # Return as int if steps are likely whole numbers, or round if _value is float.
             return int(round(self._value)) if (self.max_val - self.min_val) / (self.discrete_steps -1) >=1 else round(self._value,2)
        return int(round(self._value)) # Default to int

    def set_value(self, new_value, trigger_callback=True): # Changed default for trigger_callback
        prev_internal_val = self._value
        self._value = float(max(self.min_val, min(new_value, self.max_val)))
        self._snap_value_to_discrete_step() # Snap if discrete
        
        if self._value != prev_internal_val: # Only update/callback if value actually changed
            self._update_handle_pos_from_value()
            self._update_value_text_surface()
            if trigger_callback and self.on_value_change_callback:
                self.on_value_change_callback(self.get_value(), *self.callback_args)


class Panel(UIElement):
    """A simple container panel that can hold other UI elements."""
    def __init__(self, x, y, w, h, bg_color, border_color=None, border_width=0, border_radius=0, parent_surface=None):
        super().__init__(x, y, w, h, parent_surface)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.children = [] # List of UIElement objects, added with absolute coords or manage own relative

    def add_child(self, element): # Not used by current SettingsWindow structure (elements added to a flat list)
        self.children.append(element)

    def handle_event(self, event, mouse_pos): # Not used if children are handled externally
        if not self.visible: return False
        consumed = False
        for child in reversed(self.children):
            if child.handle_event(event, mouse_pos):
                consumed = True; break
        return consumed

    def update(self, dt, mouse_pos): # Not used if children are handled externally
        if not self.visible: return
        for child in self.children:
            child.update(dt, mouse_pos)

    def draw(self, surface):
        if not self.visible: return

        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, width=self.border_width, border_radius=self.border_radius)

        for child in self.children: # Not used if children are drawn externally
            child.draw(surface)