import pygame
import sys
import argparse
import config

from src.maze_generator import create_maze
from ui.maze_display import MazeDisplay
from ui.settings_window import SettingsWindow

from src.solvers.bfs_solver import solve_bfs_step_by_step
from src.solvers.dfs_solver import solve_dfs_step_by_step
from src.solvers.astar_solver import solve_astar_step_by_step

SOLVERS = {
    "BFS": solve_bfs_step_by_step,
    "DFS": solve_dfs_step_by_step,
    "A*": solve_astar_step_by_step,
}

def _update_layout_elements(screen, sw, sh, mrw, mrh, cs, is_fs, maze_display, buttons, button_defs, button_font):
    avail_h = sh - (0 if is_fs else config.CONTROL_PANEL_HEIGHT)
    offset_x = max(0, (sw - mrw) // 2)
    offset_y = max(0, (avail_h - mrh) // 2)

    if maze_display:
        maze_display.screen = screen
        maze_display.offset_x = offset_x
        maze_display.offset_y = offset_y
        maze_display.cell_size = cs

    max_text_w = 0
    for btn_def in button_defs:
        text_surface = button_font.render(btn_def["text"], True, config.BUTTON_TEXT_COLOR)
        max_text_w = max(max_text_w, text_surface.get_rect().width)

    btn_w = max_text_w + config.BUTTON_PADDING * 2
    btn_h = button_font.get_height() + config.BUTTON_PADDING * 2
    btn_spacing = config.BUTTON_PADDING * 2

    total_btn_w = (btn_w * len(button_defs)) + (btn_spacing * (len(button_defs) - 1))
    start_x = max(config.BUTTON_PADDING, (sw - total_btn_w) // 2)
    btn_y = sh - config.CONTROL_PANEL_HEIGHT + (config.CONTROL_PANEL_HEIGHT - btn_h) // 2

    for i, btn in enumerate(buttons):
        btn["rect"] = pygame.Rect(
            start_x + i * (btn_w + btn_spacing),
            btn_y,
            btn_w,
            btn_h
        )
        btn["text_surface"] = button_font.render(button_defs[i]["text"], True, config.BUTTON_TEXT_COLOR)
        btn["text_rect"] = btn["text_surface"].get_rect(center=btn["rect"].center)

    maze_w = mrw // cs if cs > 0 else 0
    maze_h = mrh // cs if cs > 0 else 0
    pygame.display.set_caption(f"Maze ({maze_w}x{maze_h}) - Cell: {cs}px - Solver: {config.DEFAULT_SOLVER}")

    return offset_x, offset_y

def main():
    parser = argparse.ArgumentParser(description="Generate and display a maze with AI solving.")
    parser.add_argument("--width", type=int, default=config.DEFAULT_WIDTH, help=f"Width of the maze in cells (1 < width <= {config.MAX_MAZE_WIDTH}).")
    parser.add_argument("--height", type=int, default=config.DEFAULT_HEIGHT, help=f"Height of the maze in cells (1 < height <= {config.MAX_MAZE_HEIGHT}).")
    parser.add_argument("--cell_size", type=int, default=config.DEFAULT_CELL_SIZE, help="Size of each cell in pixels. Default (<=0) fits to screen.")
    parser.add_argument("--fullscreen", action="store_true", help="Run in fullscreen mode.")
    args = parser.parse_args()

    mw = max(2, min(args.width, config.MAX_MAZE_WIDTH))
    mh = max(2, min(args.height, config.MAX_MAZE_HEIGHT))
    user_cs = args.cell_size

    pygame.init()
    pygame.font.init()
    button_font = pygame.font.Font(None, 30)
    settings_ui_font = pygame.font.Font(None, 32)

    try:
        display_info = pygame.display.Info()
        nsw = display_info.current_w
        nsh = display_info.current_h
        print(f"Detected screen resolution: {nsw}x{nsh}")
    except pygame.error as e:
        print(f"Warning: Could not get display info ({e}). Using fallback 800x600.")
        nsw, nsh = 800, 600

    maze_grid, start_node, end_node = create_maze(mw, mh)
    if not maze_grid:
        print("Error: Failed to generate maze. Exiting.")
        pygame.quit()
        sys.exit()

    grh = len(maze_grid)
    grw = len(maze_grid[0]) if grh > 0 else 0

    if user_cs <= 0:
        target_w = nsw
        target_h = nsh - (0 if args.fullscreen else config.CONTROL_PANEL_HEIGHT)
        padding = 1.0 if args.fullscreen else config.AUTO_SIZE_PADDING_FACTOR

        max_cs_w = (target_w * padding) // grw if grw > 0 else config.FALLBACK_CELL_SIZE
        max_cs_h = (target_h * padding) // grh if grh > 0 else config.FALLBACK_CELL_SIZE

        cs = max(config.MIN_CELL_SIZE, int(min(max_cs_w, max_cs_h)))
        print(f"Auto-calculated cell size: {cs}px")
    else:
        cs = max(config.MIN_CELL_SIZE, user_cs)

    mrw = grw * cs
    mrh = grh * cs

    if args.fullscreen:
        sw = nsw
        sh = nsh
        screen_flags = pygame.FULLSCREEN | pygame.SCALED
    else:
        sw = mrw
        sh = mrh + config.CONTROL_PANEL_HEIGHT
        screen_flags = pygame.RESIZABLE

    print(f"Setting display mode: {sw}x{sh} Flags: {screen_flags}")
    screen = pygame.display.set_mode((sw, sh), screen_flags)
    sw = screen.get_width()
    sh = screen.get_height()
    print(f"Actual screen surface size: {sw}x{sh}")

    maze_display = MazeDisplay(screen, maze_grid, cs, start_node, end_node, 0, 0)
    maze_display.set_ai_solve_delay(config.MAX_DELAY_MS // 2)

    button_defs = [
        {"text": "Regenerate (R)", "key": pygame.K_r, "action": "regenerate"},
        {"text": "Solve (S)", "key": pygame.K_s, "action": "solve"},
        {"text": "Settings (G)", "key": pygame.K_g, "action": "settings"},
        {"text": "Exit (ESC)", "key": pygame.K_ESCAPE, "action": "exit"}
    ]
    buttons = [{"rect": None, "text_surface": None, "text_rect": None, "action": b["action"]} for b in button_defs]

    offset_x, offset_y = _update_layout_elements(screen, sw, sh, mrw, mrh,
                                                 cs, args.fullscreen, maze_display, buttons, button_defs, button_font)

    current_solver_name = config.DEFAULT_SOLVER
    settings_window = None

    def handle_speed_change(new_delay_ms):
        if maze_display:
            maze_display.set_ai_solve_delay(new_delay_ms)

    running = True
    clock = pygame.time.Clock()

    while running:
        dt = clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        if settings_window:
            action_result = None
            for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                     running = False
                     break
                 action_result = settings_window.handle_event(event)
                 if action_result:
                     break
            if not running: break

            if action_result:
                action_type = action_result.get("action")
                if action_type == "save":
                    new_w = action_result["width"]
                    new_h = action_result["height"]
                    new_solver_name = action_result["solver"]
                    print(f"Applying Settings: W={new_w}, H={new_h}, Solver={new_solver_name}")

                    mw = new_w
                    mh = new_h
                    current_solver_name = new_solver_name

                    maze_grid, start_node, end_node = create_maze(mw, mh)
                    if not maze_grid:
                         print("Error generating maze with new dimensions. Keeping old maze.")
                    else:
                        grh = len(maze_grid)
                        grw = len(maze_grid[0])

                        if user_cs <= 0:
                            target_w = nsw
                            target_h = nsh - (0 if args.fullscreen else config.CONTROL_PANEL_HEIGHT)
                            padding = 1.0 if args.fullscreen else config.AUTO_SIZE_PADDING_FACTOR
                            max_cs_w = (target_w * padding) // grw if grw > 0 else config.FALLBACK_CELL_SIZE
                            max_cs_h = (target_h * padding) // grh if grh > 0 else config.FALLBACK_CELL_SIZE
                            cs = max(config.MIN_CELL_SIZE, int(min(max_cs_w, max_cs_h)))
                            print(f"Auto-recalculated cell size: {cs}px")

                        mrw = grw * cs
                        mrh = grh * cs

                        if not args.fullscreen:
                            new_sw = mrw
                            new_sh = mrh + config.CONTROL_PANEL_HEIGHT
                            if new_sw != sw or new_sh != sh:
                                sw = new_sw
                                sh = new_sh
                                screen = pygame.display.set_mode((sw, sh), screen_flags)
                                print(f"Resized window to: {sw}x{sh}")

                        maze_display.set_maze(maze_grid, start_node, end_node)

                        offset_x, offset_y = _update_layout_elements(
                            screen, sw, sh, mrw, mrh,
                            cs, args.fullscreen, maze_display, buttons, button_defs, button_font
                        )
                        pygame.display.set_caption(f"Maze ({mw}x{mh}) - Cell: {cs}px - Solver: {current_solver_name}")

                    settings_window = None

                elif action_type == "cancel":
                    handle_speed_change(settings_window.initial_delay_ms)
                    settings_window = None

            if settings_window:
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                settings_window.draw(screen)
                pygame.display.flip()
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == config.AI_SOLVE_STEP_EVENT:
                maze_display.handle_event(event)

            if event.type == pygame.VIDEORESIZE and not args.fullscreen:
                sw = event.w
                sh = event.h
                sw = max(sw, mrw)
                sh = max(sh, mrh + config.CONTROL_PANEL_HEIGHT)
                screen = pygame.display.set_mode((sw, sh), screen_flags)
                print(f"Window resized by user to: {sw}x{sh}")

                offset_x, offset_y = _update_layout_elements(
                     screen, sw, sh, mrw, mrh,
                     cs, args.fullscreen, maze_display, buttons, button_defs, button_font
                )

            if event.type == pygame.KEYDOWN:
                action = None
                for i, btn_def in enumerate(button_defs):
                    if event.key == btn_def["key"]:
                        action = btn_def["action"]
                        break
                if action == "exit": running = False
                elif action == "regenerate":
                    print("Regenerating maze (Key)...")
                    maze_grid, start_node, end_node = create_maze(mw, mh)
                    if maze_grid: maze_display.set_maze(maze_grid, start_node, end_node)
                elif action == "solve":
                    print(f"Starting AI solve ({current_solver_name}) (Key)...")
                    solver_func = SOLVERS.get(current_solver_name, solve_bfs_step_by_step)
                    maze_display.start_ai_solve(solver_function=solver_func)
                elif action == "settings":
                    print("Opening settings...")
                    settings_window = SettingsWindow(
                        sw, sh,
                        mw, mh,
                        maze_display.get_ai_solve_delay(),
                        handle_speed_change,
                        current_solver_name,
                        settings_ui_font
                    )

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    action = None
                    for btn in buttons:
                        if btn["rect"] and btn["rect"].collidepoint(mouse_pos):
                            action = btn["action"]
                            break
                    if action == "exit": running = False
                    elif action == "regenerate":
                        print("Regenerating maze (Button)...")
                        maze_grid, start_node, end_node = create_maze(mw, mh)
                        if maze_grid: maze_display.set_maze(maze_grid, start_node, end_node)
                    elif action == "solve":
                         print(f"Starting AI solve ({current_solver_name}) (Button)...")
                         solver_func = SOLVERS.get(current_solver_name, solve_bfs_step_by_step)
                         maze_display.start_ai_solve(solver_function=solver_func)
                    elif action == "settings":
                        print("Opening settings...")
                        settings_window = SettingsWindow(
                            sw, sh,
                            mw, mh,
                            maze_display.get_ai_solve_delay(),
                            handle_speed_change,
                            current_solver_name,
                            settings_ui_font
                        )

        screen.fill(config.BACKGROUND_COLOR)

        maze_display.draw()

        panel_rect = pygame.Rect(0, sh - config.CONTROL_PANEL_HEIGHT, sw, config.CONTROL_PANEL_HEIGHT)
        pygame.draw.rect(screen, config.BACKGROUND_COLOR, panel_rect)

        for i, btn in enumerate(buttons):
             if btn["rect"]:
                 is_hover = btn["rect"].collidepoint(mouse_pos)
                 btn_color = config.BUTTON_HOVER_COLOR if is_hover else config.BUTTON_COLOR
                 pygame.draw.rect(screen, btn_color, btn["rect"], border_radius=5)
                 if btn["text_surface"] and btn["text_rect"]:
                     screen.blit(btn["text_surface"], btn["text_rect"])

        pygame.display.flip()

    pygame.font.quit()
    pygame.quit()
    print("Exiting application.")
    sys.exit()

if __name__ == "__main__":
    main()
