import pygame
import config
import math

class InputBox:
    def __init__(self, x, y, w, h, initial_text='', font=None, max_len=4, allow_empty=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font if font else pygame.font.Font(None, 32)
        self.color = config.SETTINGS_INPUT_BOX_COLOR
        self.active_color = config.SETTINGS_INPUT_BOX_ACTIVE_COLOR
        self.inactive_color = config.SETTINGS_INPUT_BOX_COLOR
        self.invalid_color = config.SETTINGS_INVALID_INPUT_COLOR
        self.text_color = config.SETTINGS_INPUT_TEXT_COLOR
        self.text = str(initial_text)
        self.max_len = max_len
        self.allow_empty = allow_empty
        self.active = False
        self.is_valid = True
        self._update_surface()

    def _update_surface(self):
        display_color = self.text_color if self.is_valid else self.invalid_color
        self.txt_surface = self.font.render(self.text, True, display_color)

    def set_validity(self, is_valid):
        if self.is_valid != is_valid:
            self.is_valid = is_valid
            self._update_surface()

    def handle_event(self, event, validation_func=None):
        made_change = False
        enter_pressed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.active_color if self.active else self.inactive_color
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.active = False
                    self.color = self.inactive_color
                    enter_pressed = True
                    if validation_func:
                        self.set_validity(validation_func(self.text))
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    made_change = True
                elif event.unicode.isdigit() and len(self.text) < self.max_len:
                    self.text += event.unicode
                    made_change = True

                if made_change:
                    if validation_func:
                         self.set_validity(validation_func(self.text))
                    else:
                         self.set_validity(True)
                    self._update_surface()

        return enter_pressed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 0, border_radius=5)
        text_x = self.rect.x + 5
        text_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2
        screen.blit(self.txt_surface, (text_x, text_y))

    def get_value(self):
        try:
            val = int(self.text)
            return val
        except ValueError:
            return None


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self._value = float(initial_val)
        self.handle_color = config.SETTINGS_SLIDER_HANDLE_COLOR
        self.track_color = config.SETTINGS_SLIDER_TRACK_COLOR
        self.handle_radius = h // 2 + 3
        self.track_rect = pygame.Rect(x, y + h // 3, w, h // 3)
        self.dragging = False
        self._update_handle_pos()

    def _update_handle_pos(self):
        range_val = self.max_val - self.min_val
        ratio = (self._value - self.min_val) / range_val if range_val != 0 else 0
        self.handle_x = self.rect.x + int(ratio * self.rect.width)
        self.handle_y = self.rect.centery

    def handle_event(self, event):
        changed = False
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                handle_hitbox = pygame.Rect(self.handle_x - self.handle_radius, self.handle_y - self.handle_radius,
                                           self.handle_radius * 2, self.handle_radius * 2)
                if self.rect.collidepoint(mouse_pos):
                    self.dragging = True
                    new_x = max(self.rect.x, min(mouse_pos[0], self.rect.right))
                    ratio = (new_x - self.rect.x) / self.rect.width if self.rect.width != 0 else 0
                    range_val = self.max_val - self.min_val
                    self._value = self.min_val + ratio * range_val
                    self._value = max(self.min_val, min(self._value, self.max_val))
                    self._update_handle_pos()
                    changed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = max(self.rect.x, min(mouse_pos[0], self.rect.right))
                ratio = (new_x - self.rect.x) / self.rect.width if self.rect.width != 0 else 0
                range_val = self.max_val - self.min_val
                self._value = self.min_val + ratio * range_val
                self._value = max(self.min_val, min(self._value, self.max_val))
                self._update_handle_pos()
                changed = True
        return changed

    def get_value(self):
        return int(round(self._value))

    def set_value(self, value):
        self._value = float(max(self.min_val, min(value, self.max_val)))
        self._update_handle_pos()

    def draw(self, screen):
        pygame.draw.rect(screen, self.track_color, self.track_rect, border_radius=self.track_rect.height // 2)
        pygame.draw.circle(screen, self.handle_color, (self.handle_x, self.handle_y), self.handle_radius)


class SettingsWindow:
    def __init__(self, screen_width, screen_height, current_width, current_height,
                 initial_delay_ms, speed_change_callback, current_solver, font):
        self.font = font
        self.on_speed_change_callback = speed_change_callback
        self.selected_solver = current_solver
        self.initial_width = current_width
        self.initial_height = current_height
        self.initial_solver = current_solver
        self.initial_delay_ms = initial_delay_ms

        win_width = config.SETTINGS_PANEL_WIDTH
        win_height = config.SETTINGS_PANEL_HEIGHT
        win_x = (screen_width - win_width) // 2
        win_y = (screen_height - win_height) // 2
        self.window_rect = pygame.Rect(win_x, win_y, win_width, win_height)

        padding = 15
        label_width = 100
        input_w = 100
        input_h = 35
        element_y = self.window_rect.top + 60

        self.width_label = self.font.render("Width:", True, config.SETTINGS_LABEL_COLOR)
        width_input_x = self.window_rect.left + label_width + padding
        self.width_input = InputBox(width_input_x, element_y, input_w, input_h,
                                    current_width, self.font, max_len=3)
        self.width_input.set_validity(self._validate_dimension(current_width, config.MAX_MAZE_WIDTH))
        element_y += input_h + padding * 1.5

        self.height_label = self.font.render("Height:", True, config.SETTINGS_LABEL_COLOR)
        height_input_x = width_input_x
        self.height_input = InputBox(height_input_x, element_y, input_w, input_h,
                                     current_height, self.font, max_len=3)
        self.height_input.set_validity(self._validate_dimension(current_height, config.MAX_MAZE_HEIGHT))
        element_y += input_h + padding * 1.5

        self.solver_label = self.font.render("Solver:", True, config.SETTINGS_LABEL_COLOR)
        solver_button_w = 70
        solver_button_h = 30
        solver_button_padding = 8
        num_solvers = len(config.SOLVER_OPTIONS)
        total_solver_button_width = (solver_button_w * num_solvers) + (solver_button_padding * (num_solvers - 1))
        solver_buttons_start_x = self.window_rect.left + label_width + padding
        solver_buttons_y = element_y

        self.solver_buttons = []
        button_font = pygame.font.Font(None, 28)
        for i, solver_name in enumerate(config.SOLVER_OPTIONS):
            btn_rect = pygame.Rect(
                solver_buttons_start_x + i * (solver_button_w + solver_button_padding),
                solver_buttons_y + (input_h - solver_button_h) // 2,
                solver_button_w, solver_button_h
            )
            text_surface = button_font.render(solver_name, True, config.BUTTON_TEXT_COLOR)
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.solver_buttons.append({
                "name": solver_name, "rect": btn_rect,
                "text_surface": text_surface, "text_rect": text_rect
            })
        element_y += input_h + padding * 1.5

        self.speed_label = self.font.render("AI Speed:", True, config.SETTINGS_LABEL_COLOR)
        slider_w = win_width - label_width - padding * 3 - 40
        slider_h = 25
        slider_x = self.window_rect.left + label_width + padding
        slider_y = element_y
        initial_slider_val = self._map_delay_to_slider(initial_delay_ms)
        self.speed_slider = Slider(slider_x, slider_y, slider_w, slider_h,
                                   config.SLIDER_MIN_VAL, config.SLIDER_MAX_VAL,
                                   initial_slider_val)
        element_y += slider_h + padding * 2.5

        button_w = 100
        button_h = 40
        button_y = self.window_rect.bottom - button_h - padding * 1.5
        total_button_width = button_w * 2 + padding
        start_button_x = self.window_rect.centerx - total_button_width // 2

        self.save_button_rect = pygame.Rect(start_button_x, button_y, button_w, button_h)
        self.cancel_button_rect = pygame.Rect(start_button_x + button_w + padding, button_y, button_w, button_h)
        self.save_text = self.font.render("Save", True, config.BUTTON_TEXT_COLOR)
        self.cancel_text = self.font.render("Cancel", True, config.BUTTON_TEXT_COLOR)
        self.save_text_rect = self.save_text.get_rect(center=self.save_button_rect.center)
        self.cancel_text_rect = self.cancel_text.get_rect(center=self.cancel_button_rect.center)

        self.title_surface = self.font.render("Settings", True, config.TEXT_COLOR)
        self.title_rect = self.title_surface.get_rect(center=(self.window_rect.centerx, self.window_rect.top + 30))

    def _validate_dimension(self, text_value, max_value):
        try:
            val = int(text_value)
            return 1 < val <= max_value
        except ValueError:
            return False

    def _validate_width(self, text_value):
        return self._validate_dimension(text_value, config.MAX_MAZE_WIDTH)

    def _validate_height(self, text_value):
        return self._validate_dimension(text_value, config.MAX_MAZE_HEIGHT)

    def _map_slider_to_delay(self, slider_value):
        min_delay, max_delay = config.MIN_DELAY_MS, config.MAX_DELAY_MS
        min_slider, max_slider = config.SLIDER_MIN_VAL, config.SLIDER_MAX_VAL
        exponent = config.SLIDER_EXPONENT

        if max_slider == min_slider: return min_delay
        if max_delay == min_delay: return min_delay

        ratio = (slider_value - min_slider) / (max_slider - min_slider)
        mapped_ratio = (1.0 - ratio) ** exponent
        delay = min_delay + mapped_ratio * (max_delay - min_delay)

        return int(max(min_delay, min(delay, max_delay)))

    def _map_delay_to_slider(self, delay_ms):
        min_delay, max_delay = config.MIN_DELAY_MS, config.MAX_DELAY_MS
        min_slider, max_slider = config.SLIDER_MIN_VAL, config.SLIDER_MAX_VAL
        exponent = config.SLIDER_EXPONENT

        if max_delay == min_delay: return min_slider
        if delay_ms <= min_delay: return max_slider
        if delay_ms >= max_delay: return min_slider

        delay_ratio = (delay_ms - min_delay) / (max_delay - min_delay)
        inv_exponent = 1.0 / exponent
        ratio = 1.0 - (delay_ratio ** inv_exponent)

        slider_value = min_slider + ratio * (max_slider - min_slider)

        return int(max(min_slider, min(round(slider_value), max_slider)))

    def handle_event(self, event):
        action = None
        mouse_pos = pygame.mouse.get_pos()

        width_enter = self.width_input.handle_event(event, self._validate_width)
        height_enter = self.height_input.handle_event(event, self._validate_height)

        slider_changed = self.speed_slider.handle_event(event)
        if slider_changed and self.on_speed_change_callback:
            new_delay = self._map_slider_to_delay(self.speed_slider.get_value())
            self.on_speed_change_callback(new_delay)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.solver_buttons:
                if btn["rect"].collidepoint(mouse_pos):
                    self.selected_solver = btn["name"]
                    print(f"Selected solver: {self.selected_solver}")

            if self.save_button_rect.collidepoint(mouse_pos):
                width_val = self.width_input.get_value()
                height_val = self.height_input.get_value()
                is_w_valid = self._validate_width(str(width_val) if width_val is not None else "")
                is_h_valid = self._validate_height(str(height_val) if height_val is not None else "")
                self.width_input.set_validity(is_w_valid)
                self.height_input.set_validity(is_h_valid)

                if is_w_valid and is_h_valid:
                    print(f"Settings saved: W={width_val}, H={height_val}, Solver={self.selected_solver}")
                    action = {"action": "save", "width": width_val, "height": height_val, "solver": self.selected_solver}
                else:
                    print("Cannot save: Invalid dimensions.")

            elif self.cancel_button_rect.collidepoint(mouse_pos):
                print("Settings canceled.")
                action = {"action": "cancel"}

        if (width_enter or height_enter):
            width_val = self.width_input.get_value()
            height_val = self.height_input.get_value()
            is_w_valid = self._validate_width(str(width_val) if width_val is not None else "")
            is_h_valid = self._validate_height(str(height_val) if height_val is not None else "")
            self.width_input.set_validity(is_w_valid)
            self.height_input.set_validity(is_h_valid)
            if is_w_valid and is_h_valid:
                 print(f"Settings saved (Enter): W={width_val}, H={height_val}, Solver={self.selected_solver}")
                 action = {"action": "save", "width": width_val, "height": height_val, "solver": self.selected_solver}
            else:
                 print("Enter pressed but dimensions invalid.")

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("Settings canceled (Escape key).")
            action = {"action": "cancel"}

        return action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()

        pygame.draw.rect(screen, config.SETTINGS_PANEL_COLOR, self.window_rect, border_radius=10)
        pygame.draw.rect(screen, config.SETTINGS_BORDER_COLOR, self.window_rect, 2, border_radius=10)

        screen.blit(self.title_surface, self.title_rect)

        label_x = self.window_rect.left + 15
        screen.blit(self.width_label, (label_x, self.width_input.rect.centery - self.width_label.get_height() // 2))
        self.width_input.draw(screen)
        screen.blit(self.height_label, (label_x, self.height_input.rect.centery - self.height_label.get_height() // 2))
        self.height_input.draw(screen)
        screen.blit(self.solver_label, (label_x, self.solver_buttons[0]["rect"].centery - self.solver_label.get_height() // 2))

        for btn in self.solver_buttons:
            is_selected = btn["name"] == self.selected_solver
            is_hover = btn["rect"].collidepoint(mouse_pos)
            base_color = config.BUTTON_COLOR
            hover_color = config.BUTTON_HOVER_COLOR

            if is_selected:
                sel_base_col = tuple(min(255, c + 40) for c in base_color)
                sel_hover_col = tuple(min(255, c + 40) for c in hover_color)
                btn_color = sel_hover_col if is_hover else sel_base_col
                border_color = config.SETTINGS_BORDER_COLOR
                border_width = 2
            else:
                btn_color = hover_color if is_hover else base_color
                border_color = btn_color
                border_width = 0

            pygame.draw.rect(screen, btn_color, btn["rect"], border_radius=5)
            if border_width > 0:
                 pygame.draw.rect(screen, border_color, btn["rect"], border_width, border_radius=5)

            screen.blit(btn["text_surface"], btn["text_rect"])

        screen.blit(self.speed_label, (label_x, self.speed_slider.rect.centery - self.speed_label.get_height() // 2))
        self.speed_slider.draw(screen)
        slider_val_text = self.font.render(f"{self.speed_slider.get_value()}", True, config.TEXT_COLOR)
        val_rect = slider_val_text.get_rect(midleft=(self.speed_slider.rect.right + 10, self.speed_slider.rect.centery))
        screen.blit(slider_val_text, val_rect)

        save_hover = self.save_button_rect.collidepoint(mouse_pos)
        cancel_hover = self.cancel_button_rect.collidepoint(mouse_pos)

        save_enabled = self.width_input.is_valid and self.height_input.is_valid
        save_base_color = config.BUTTON_COLOR if save_enabled else (100, 100, 100)
        save_hover_color = config.BUTTON_HOVER_COLOR if save_enabled else (120, 120, 120)
        save_color = save_hover_color if save_hover and save_enabled else save_base_color

        cancel_color = config.BUTTON_HOVER_COLOR if cancel_hover else config.BUTTON_COLOR

        pygame.draw.rect(screen, save_color, self.save_button_rect, border_radius=5)
        pygame.draw.rect(screen, cancel_color, self.cancel_button_rect, border_radius=5)

        screen.blit(self.save_text, self.save_text_rect)
        screen.blit(self.cancel_text, self.cancel_text_rect)
