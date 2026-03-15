import os
import random
import sys

import pygame


# --- Oyun Ayarları ---
MODES = [
    {"id": "kolay", "label": "Kolay", "cols": 9, "rows": 9, "mines": 10},
    {"id": "orta", "label": "Orta", "cols": 16, "rows": 16, "mines": 40},
    {"id": "zor", "label": "Zor", "cols": 30, "rows": 16, "mines": 99},
    {
        "id": "uzman",
        "label": "Uzman",
        "cols": 40,
        "rows": 20,
        "mines": 160,
        "time_limit": 300,
    },
]
CELL_SIZE = 30
TOP_BAR = 60

current_mode = "orta"
GRID_COLS = 16
GRID_ROWS = 16
MINES = 40

WIDTH = GRID_COLS * CELL_SIZE
HEIGHT = GRID_ROWS * CELL_SIZE + TOP_BAR
START_SCALE = 1.40
START_WIDTH_SCALE = 1.80
START_WIDTH = int(WIDTH * START_WIDTH_SCALE)
START_HEIGHT = int(HEIGHT * START_SCALE)
BOSNA_BG_FILES = ["bosna.png", "bosna.jpg", "bosna.jpeg"]
BOSNA_BG_ALPHA = 90

bosna_bg = None
bosna_bg_scaled = None
bosna_bg_scaled_size = None
BG_COLOR = (20, 24, 28)
TOP_BAR_COLOR = (28, 32, 36)
GRID_COLOR = (50, 55, 60)
CELL_COLOR = (34, 40, 46)
REVEALED_COLOR = (65, 70, 76)
FLAG_COLOR = (215, 70, 60)
MINE_COLOR = (200, 50, 50)
TEXT_COLOR = (230, 230, 230)
BUTTON_COLOR = (55, 60, 66)
BUTTON_HOVER = (70, 76, 84)
MODE_SELECTED = (85, 105, 125)
PANEL_COLOR = (30, 34, 38)
SLIDER_BG = (80, 86, 94)
SLIDER_FILL = (160, 170, 180)

LIGHT_COLORS = {
    "bg": (240, 242, 245),
    "top_bar": (220, 224, 230),
    "grid": (180, 185, 190),
    "cell": (230, 232, 235),
    "revealed": (210, 214, 220),
    "flag": (200, 80, 80),
    "mine": (180, 60, 60),
    "text": (30, 30, 30),
    "button": (200, 205, 210),
    "button_hover": (180, 185, 190),
    "mode_selected": (170, 200, 230),
    "panel": (225, 228, 232),
    "slider_bg": (180, 185, 190),
    "slider_fill": (90, 120, 160),
}


def get_colors(light_mode):
    if light_mode:
        return LIGHT_COLORS
    return {
        "bg": BG_COLOR,
        "top_bar": TOP_BAR_COLOR,
        "grid": GRID_COLOR,
        "cell": CELL_COLOR,
        "revealed": REVEALED_COLOR,
        "flag": FLAG_COLOR,
        "mine": MINE_COLOR,
        "text": TEXT_COLOR,
        "button": BUTTON_COLOR,
        "button_hover": BUTTON_HOVER,
        "mode_selected": MODE_SELECTED,
        "panel": PANEL_COLOR,
        "slider_bg": SLIDER_BG,
        "slider_fill": SLIDER_FILL,
    }


def get_number_color(number, light_mode):
    if light_mode:
        palette = {
            1: (30, 90, 170),
            2: (25, 140, 90),
            3: (200, 120, 40),
            4: (170, 40, 40),
        }
    else:
        palette = {
            1: (80, 150, 255),
            2: (90, 200, 120),
            3: (255, 170, 80),
            4: (255, 90, 90),
        }
    return palette.get(number)


def resource_path(relative_path):
    base_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_dir, relative_path)


def load_bosna_background():
    global bosna_bg
    bosna_bg = None
    for name in BOSNA_BG_FILES:
        path = resource_path(name)
        if os.path.exists(path):
            try:
                surface = pygame.image.load(path)
                if surface.get_alpha() is not None:
                    bosna_bg = surface.convert_alpha()
                else:
                    bosna_bg = surface.convert()
            except pygame.error:
                bosna_bg = None
            return


def get_bosna_background(grid_w, grid_h):
    global bosna_bg_scaled, bosna_bg_scaled_size
    if bosna_bg is None:
        return None
    size = (grid_w, grid_h)
    if bosna_bg_scaled is None or bosna_bg_scaled_size != size:
        bosna_bg_scaled = pygame.transform.smoothscale(bosna_bg, size)
        bosna_bg_scaled.set_alpha(BOSNA_BG_ALPHA)
        bosna_bg_scaled_size = size
    return bosna_bg_scaled

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent = 0


def make_grid():
    grid = [[Cell() for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    # Mayınları yerleştir
    positions = list(range(GRID_COLS * GRID_ROWS))
    random.shuffle(positions)
    for idx in positions[:MINES]:
        r = idx // GRID_COLS
        c = idx % GRID_COLS
        grid[r][c].is_mine = True
    # Komşu sayıları
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid[r][c].is_mine:
                continue
            count = 0
            for rr in range(max(0, r - 1), min(GRID_ROWS, r + 2)):
                for cc in range(max(0, c - 1), min(GRID_COLS, c + 2)):
                    if grid[rr][cc].is_mine:
                        count += 1
            grid[r][c].adjacent = count
    return grid


def flood_reveal(grid, r, c):
    stack = [(r, c)]
    while stack:
        cr, cc = stack.pop()
        cell = grid[cr][cc]
        if cell.is_revealed or cell.is_flagged:
            continue
        cell.is_revealed = True
        if cell.adjacent == 0 and not cell.is_mine:
            for rr in range(max(0, cr - 1), min(GRID_ROWS, cr + 2)):
                for cc2 in range(max(0, cc - 1), min(GRID_COLS, cc + 2)):
                    if not grid[rr][cc2].is_revealed:
                        stack.append((rr, cc2))


def all_safe_revealed(grid):
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cell = grid[r][c]
            if not cell.is_mine and not cell.is_revealed:
                return False
    return True


def apply_mode(mode_id):
    global current_mode, GRID_COLS, GRID_ROWS, MINES, WIDTH, HEIGHT
    mode = get_mode_config(mode_id)
    if not mode:
        return False
    current_mode = mode_id
    GRID_COLS = mode["cols"]
    GRID_ROWS = mode["rows"]
    MINES = mode["mines"]
    WIDTH = GRID_COLS * CELL_SIZE
    HEIGHT = GRID_ROWS * CELL_SIZE + TOP_BAR
    return True


def get_mode_config(mode_id):
    for mode in MODES:
        if mode["id"] == mode_id:
            return mode
    return None


def get_mode_buttons(font):
    buttons = []
    x = 16
    y = (TOP_BAR - 26) // 2
    for mode in MODES:
        label = mode["label"]
        text_w = font.size(label)[0]
        w = max(60, text_w + 20)
        rect = pygame.Rect(x, y, w, 26)
        buttons.append((mode["id"], label, rect))
        x += w + 8
    return buttons


def get_layout(screen_w, screen_h):
    avail_w = max(1, screen_w)
    avail_h = max(1, screen_h - TOP_BAR)
    cell_size = max(1, min(avail_w // GRID_COLS, avail_h // GRID_ROWS))
    grid_w = cell_size * GRID_COLS
    grid_h = cell_size * GRID_ROWS
    grid_x = max(0, (screen_w - grid_w) // 2)
    grid_y = TOP_BAR + max(0, (avail_h - grid_h) // 2)
    return cell_size, grid_x, grid_y, grid_w, grid_h


def get_top_buttons(screen_w):
    button_w = 110
    button_h = 30
    button_pad = 10
    gap = 8
    settings_btn = pygame.Rect(
        screen_w - button_w - button_pad,
        (TOP_BAR - button_h) // 2,
        button_w,
        button_h,
    )
    quit_btn = pygame.Rect(
        settings_btn.x - button_w - gap,
        (TOP_BAR - button_h) // 2,
        button_w,
        button_h,
    )
    restart_btn = pygame.Rect(
        quit_btn.x - button_w - gap,
        (TOP_BAR - button_h) // 2,
        button_w,
        button_h,
    )
    return restart_btn, quit_btn, settings_btn


def get_ui_rects(screen_w):
    restart_btn, quit_btn, settings_btn = get_top_buttons(screen_w)
    panel_w = 240
    panel_h = 240
    panel_x = max(10, screen_w - panel_w - 10)
    panel = pygame.Rect(panel_x, TOP_BAR + 10, panel_w, panel_h)
    toggle_btn = pygame.Rect(panel.x + 12, panel.y + 12, panel.w - 24, 30)
    fullscreen_btn = pygame.Rect(panel.x + 12, panel.y + 52, panel.w - 24, 30)
    light_btn = pygame.Rect(panel.x + 12, panel.y + 92, panel.w - 24, 30)
    bosna_btn = pygame.Rect(panel.x + 12, panel.y + 132, panel.w - 24, 30)
    slider = pygame.Rect(panel.x + 12, panel.y + 192, panel.w - 24, 10)
    return (
        restart_btn,
        quit_btn,
        settings_btn,
        panel,
        toggle_btn,
        fullscreen_btn,
        light_btn,
        bosna_btn,
        slider,
    )


def get_end_panel(screen_w, screen_h):
    panel_w = 320
    panel_h = 200
    panel = pygame.Rect(
        (screen_w - panel_w) // 2, (screen_h - panel_h) // 2, panel_w, panel_h
    )
    btn_w = panel_w - 40
    btn_h = 34
    gap = 10
    restart_btn = pygame.Rect(panel.x + 20, panel.y + 60, btn_w, btn_h)
    settings_btn = pygame.Rect(
        panel.x + 20, restart_btn.bottom + gap, btn_w, btn_h
    )
    quit_btn = pygame.Rect(panel.x + 20, settings_btn.bottom + gap, btn_w, btn_h)
    return panel, restart_btn, settings_btn, quit_btn


def draw_settings_panel(
    screen,
    colors,
    font,
    panel,
    toggle_btn,
    fullscreen_btn,
    light_btn,
    bosna_btn,
    slider,
    music_enabled,
    fullscreen_enabled,
    light_mode,
    bosna_enabled,
    volume,
    mx,
    my,
):
    pygame.draw.rect(screen, colors["panel"], panel, border_radius=8)
    toggle_color = (
        colors["button_hover"] if toggle_btn.collidepoint(mx, my) else colors["button"]
    )
    pygame.draw.rect(screen, toggle_color, toggle_btn, border_radius=6)
    toggle_label = "Müzik: Açık" if music_enabled else "Müzik: Kapalı"
    toggle_text = font.render(toggle_label, True, colors["text"])
    screen.blit(
        toggle_text,
        (
            toggle_btn.x + (toggle_btn.w - toggle_text.get_width()) // 2,
            toggle_btn.y + (toggle_btn.h - toggle_text.get_height()) // 2,
        ),
    )

    fullscreen_color = (
        colors["button_hover"]
        if fullscreen_btn.collidepoint(mx, my)
        else colors["button"]
    )
    pygame.draw.rect(screen, fullscreen_color, fullscreen_btn, border_radius=6)
    fullscreen_label = (
        "Tam Ekran: Açık" if fullscreen_enabled else "Tam Ekran: Kapalı"
    )
    fullscreen_text = font.render(fullscreen_label, True, colors["text"])
    screen.blit(
        fullscreen_text,
        (
            fullscreen_btn.x + (fullscreen_btn.w - fullscreen_text.get_width()) // 2,
            fullscreen_btn.y + (fullscreen_btn.h - fullscreen_text.get_height()) // 2,
        ),
    )

    light_color = (
        colors["button_hover"] if light_btn.collidepoint(mx, my) else colors["button"]
    )
    pygame.draw.rect(screen, light_color, light_btn, border_radius=6)
    light_label = "Açık Mod: Açık" if light_mode else "Açık Mod: Kapalı"
    light_text = font.render(light_label, True, colors["text"])
    screen.blit(
        light_text,
        (
            light_btn.x + (light_btn.w - light_text.get_width()) // 2,
            light_btn.y + (light_btn.h - light_text.get_height()) // 2,
        ),
    )

    bosna_color = (
        colors["button_hover"] if bosna_btn.collidepoint(mx, my) else colors["button"]
    )
    pygame.draw.rect(screen, bosna_color, bosna_btn, border_radius=6)
    bosna_label = "Bosna Modu: Açık" if bosna_enabled else "Bosna Modu: Kapalı"
    bosna_text = font.render(bosna_label, True, colors["text"])
    screen.blit(
        bosna_text,
        (
            bosna_btn.x + (bosna_btn.w - bosna_text.get_width()) // 2,
            bosna_btn.y + (bosna_btn.h - bosna_text.get_height()) // 2,
        ),
    )

    pygame.draw.rect(screen, colors["slider_bg"], slider, border_radius=4)
    fill_w = int(slider.w * volume)
    fill_rect = pygame.Rect(slider.x, slider.y, fill_w, slider.h)
    pygame.draw.rect(screen, colors["slider_fill"], fill_rect, border_radius=4)
    vol_text = font.render(f"Ses: {int(volume * 100)}", True, colors["text"])
    screen.blit(vol_text, (slider.x, slider.y - 24))


def draw(
    screen,
    grid,
    font,
    big_font,
    status_text,
    settings_open,
    music_enabled,
    volume,
    fullscreen_enabled,
    light_mode,
    bosna_enabled,
    time_text,
    show_end_panel,
    end_title,
):
    colors = get_colors(light_mode)
    screen_w, screen_h = screen.get_size()
    screen.fill(colors["bg"])
    # Üst bar
    pygame.draw.rect(screen, colors["top_bar"], (0, 0, screen_w, TOP_BAR))
    text = font.render(status_text, True, colors["text"])
    screen.blit(text, ((screen_w - text.get_width()) // 2, 18))
    if time_text:
        time_surface = font.render(time_text, True, colors["text"])
        screen.blit(time_surface, ((screen_w - time_surface.get_width()) // 2, 38))

    # Grid
    cell_size, grid_x, grid_y, grid_w, grid_h = get_layout(screen_w, screen_h)
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = grid_x + c * cell_size
            y = grid_y + r * cell_size
            cell = grid[r][c]

            rect = pygame.Rect(x, y, cell_size, cell_size)
            if cell.is_revealed:
                pygame.draw.rect(screen, colors["revealed"], rect)
                if cell.is_mine:
                    pygame.draw.circle(
                        screen,
                        colors["mine"],
                        rect.center,
                        max(2, cell_size // 3),
                    )
                elif cell.adjacent > 0:
                    num_color = get_number_color(cell.adjacent, light_mode) or colors[
                        "text"
                    ]
                    num = big_font.render(str(cell.adjacent), True, num_color)
                    num_rect = num.get_rect(center=rect.center)
                    screen.blit(num, num_rect)
            else:
                pygame.draw.rect(screen, colors["cell"], rect)
                if cell.is_flagged:
                    pygame.draw.polygon(
                        screen,
                        colors["flag"],
                        [
                            (x + cell_size // 3, y + cell_size // 4),
                            (x + cell_size // 3, y + cell_size * 3 // 4),
                            (x + cell_size * 3 // 4, y + cell_size // 2),
                        ],
                    )

            pygame.draw.rect(screen, colors["grid"], rect, 1)

    if bosna_enabled:
        bg = get_bosna_background(grid_w, grid_h)
        if bg is not None:
            screen.blit(bg, (grid_x, grid_y))

    mode_buttons = get_mode_buttons(font)
    mx, my = pygame.mouse.get_pos()
    for mode_id, label, rect in mode_buttons:
        is_selected = mode_id == current_mode
        is_hover = rect.collidepoint(mx, my)
        if is_selected:
            color = colors["mode_selected"]
        else:
            color = colors["button_hover"] if is_hover else colors["button"]
        pygame.draw.rect(screen, color, rect, border_radius=6)
        label_text = font.render(label, True, colors["text"])
        screen.blit(
            label_text,
            (
                rect.x + (rect.w - label_text.get_width()) // 2,
                rect.y + (rect.h - label_text.get_height()) // 2,
            ),
        )

    (
        restart_btn,
        quit_btn,
        settings_btn,
        panel,
        toggle_btn,
        fullscreen_btn,
        light_btn,
        bosna_btn,
        slider,
    ) = get_ui_rects(screen_w)
    restart_color = (
        colors["button_hover"] if restart_btn.collidepoint(mx, my) else colors["button"]
    )
    pygame.draw.rect(screen, restart_color, restart_btn, border_radius=6)
    restart_text = font.render("Yeniden", True, colors["text"])
    screen.blit(
        restart_text,
        (
            restart_btn.x + (restart_btn.w - restart_text.get_width()) // 2,
            restart_btn.y + (restart_btn.h - restart_text.get_height()) // 2,
        ),
    )

    quit_color = (
        colors["button_hover"] if quit_btn.collidepoint(mx, my) else colors["button"]
    )
    pygame.draw.rect(screen, quit_color, quit_btn, border_radius=6)
    quit_text = font.render("Çıkış", True, colors["text"])
    screen.blit(
        quit_text,
        (
            quit_btn.x + (quit_btn.w - quit_text.get_width()) // 2,
            quit_btn.y + (quit_btn.h - quit_text.get_height()) // 2,
        ),
    )

    btn_color = (
        colors["button_hover"] if settings_btn.collidepoint(mx, my) else colors["button"]
    )
    pygame.draw.rect(screen, btn_color, settings_btn, border_radius=6)
    btn_text = font.render("Ayarlar", True, colors["text"])
    screen.blit(
        btn_text,
        (
            settings_btn.x + (settings_btn.w - btn_text.get_width()) // 2,
            settings_btn.y + (settings_btn.h - btn_text.get_height()) // 2,
        ),
    )

    if settings_open:
        draw_settings_panel(
            screen,
            colors,
            font,
            panel,
            toggle_btn,
            fullscreen_btn,
            light_btn,
            bosna_btn,
            slider,
            music_enabled,
            fullscreen_enabled,
            light_mode,
            bosna_enabled,
            volume,
            mx,
            my,
        )

    if show_end_panel:
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        end_panel, end_restart, end_settings, end_quit = get_end_panel(
            screen_w, screen_h
        )
        pygame.draw.rect(screen, colors["panel"], end_panel, border_radius=10)
        if end_title:
            end_text = big_font.render(end_title, True, colors["text"])
            screen.blit(
                end_text,
                (
                    end_panel.x + (end_panel.w - end_text.get_width()) // 2,
                    end_panel.y + 18,
                ),
            )

        for rect, label in [
            (end_restart, "Yeniden"),
            (end_settings, "Ayarlar"),
            (end_quit, "Çıkış"),
        ]:
            is_hover = rect.collidepoint(mx, my)
            color = colors["button_hover"] if is_hover else colors["button"]
            pygame.draw.rect(screen, color, rect, border_radius=6)
            label_text = font.render(label, True, colors["text"])
            screen.blit(
                label_text,
                (
                    rect.x + (rect.w - label_text.get_width()) // 2,
                    rect.y + (rect.h - label_text.get_height()) // 2,
                ),
            )

        if settings_open:
            draw_settings_panel(
                screen,
                colors,
                font,
                panel,
                toggle_btn,
                fullscreen_btn,
                light_btn,
                bosna_btn,
                slider,
                music_enabled,
                fullscreen_enabled,
                light_mode,
                bosna_enabled,
                volume,
                mx,
                my,
            )

    pygame.display.flip()

def apply_music_state(music_loaded, music_enabled, volume, music_started):
    if not music_loaded:
        return music_started
    if music_enabled:
        if not music_started:
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            music_started = True
        pygame.mixer.music.unpause()
        pygame.mixer.music.set_volume(volume)
    else:
        if music_started:
            pygame.mixer.music.pause()
    return music_started


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((START_WIDTH, START_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Mayın Tarlası")
    font = pygame.font.SysFont("Consolas", 18)
    big_font = pygame.font.SysFont("Consolas", 20, bold=True)
    load_bosna_background()

    # Arka plan müziği (dosyayı aynı klasöre koy)
    # Örn: music.mp3
    music_loaded = False
    try:
        pygame.mixer.music.load(resource_path("music.mp3"))
        pygame.mixer.music.set_volume(0.5)
        music_loaded = True
    except pygame.error:
        pass
    music_enabled = False
    music_started = False
    volume = 0.5
    settings_open = False
    volume_dragging = False
    fullscreen_enabled = False
    light_mode = False
    bosna_enabled = False
    windowed_size = (START_WIDTH, START_HEIGHT)
    start_time = None
    time_up = False

    grid = make_grid()
    game_over = False
    win = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.VIDEORESIZE and not fullscreen_enabled:
                windowed_size = (event.w, event.h)
                screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                screen_w, screen_h = screen.get_size()
                (
                    restart_btn,
                    quit_btn,
                    settings_btn,
                    panel,
                    toggle_btn,
                    fullscreen_btn,
                    light_btn,
                    bosna_btn,
                    slider,
                ) = get_ui_rects(screen_w)
                mode_buttons = get_mode_buttons(font)
                mode_clicked = False
                cell_size, grid_x, grid_y, grid_w, grid_h = get_layout(
                    screen_w, screen_h
                )
                grid_rect = pygame.Rect(grid_x, grid_y, grid_w, grid_h)
                end_panel, end_restart, end_settings, end_quit = get_end_panel(
                    screen_w, screen_h
                )

                if event.button == 1:
                    if (game_over or win) and end_panel.collidepoint(mx, my):
                        if end_restart.collidepoint(mx, my):
                            grid = make_grid()
                            game_over = False
                            win = False
                            time_up = False
                            start_time = None
                            settings_open = False
                            volume_dragging = False
                            continue
                        if end_settings.collidepoint(mx, my):
                            settings_open = True
                            continue
                        if end_quit.collidepoint(mx, my):
                            pygame.quit()
                            sys.exit(0)
                    if restart_btn.collidepoint(mx, my):
                        grid = make_grid()
                        game_over = False
                        win = False
                        time_up = False
                        start_time = None
                        settings_open = False
                        volume_dragging = False
                        continue
                    if quit_btn.collidepoint(mx, my):
                        pygame.quit()
                        sys.exit(0)
                    if settings_btn.collidepoint(mx, my):
                        settings_open = not settings_open
                        volume_dragging = False
                        continue
                    for mode_id, _label, rect in mode_buttons:
                        if rect.collidepoint(mx, my):
                            if apply_mode(mode_id):
                                grid = make_grid()
                                game_over = False
                                win = False
                                time_up = False
                                start_time = None
                                settings_open = False
                                volume_dragging = False
                                if mode_id == "bosna":
                                    music_enabled = True
                                    apply_music_state(
                                        music_loaded, music_enabled, volume
                                    )
                            mode_clicked = True
                            break
                    if mode_clicked:
                        continue
                    if settings_open and panel.collidepoint(mx, my):
                        if toggle_btn.collidepoint(mx, my):
                            if bosna_enabled:
                                music_enabled = not music_enabled
                                music_started = apply_music_state(
                                    music_loaded, music_enabled, volume, music_started
                                )
                        elif fullscreen_btn.collidepoint(mx, my):
                            fullscreen_enabled = not fullscreen_enabled
                            volume_dragging = False
                            if fullscreen_enabled:
                                windowed_size = screen.get_size()
                                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            else:
                                screen = pygame.display.set_mode(
                                    windowed_size, pygame.RESIZABLE
                                )
                        elif light_btn.collidepoint(mx, my):
                            light_mode = not light_mode
                        elif bosna_btn.collidepoint(mx, my):
                            bosna_enabled = not bosna_enabled
                            music_enabled = bosna_enabled
                            music_started = apply_music_state(
                                music_loaded, music_enabled, volume, music_started
                            )
                        elif slider.collidepoint(mx, my):
                            volume = max(0.0, min(1.0, (mx - slider.x) / slider.w))
                            volume_dragging = True
                            music_started = apply_music_state(
                                music_loaded, music_enabled, volume, music_started
                            )
                        continue
                    if not grid_rect.collidepoint(mx, my):
                        continue

                if event.button == 3 and not grid_rect.collidepoint(mx, my):
                    continue

                if not game_over and not win:
                    c = (mx - grid_x) // cell_size
                    r = (my - grid_y) // cell_size
                    if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                        cell = grid[r][c]
                        if event.button == 1:  # Sol tık
                            if start_time is None:
                                start_time = pygame.time.get_ticks()
                            if cell.is_mine:
                                cell.is_revealed = True
                                game_over = True
                            else:
                                flood_reveal(grid, r, c)
                        elif event.button == 3:  # Sağ tık
                            if not cell.is_revealed:
                                cell.is_flagged = not cell.is_flagged

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    volume_dragging = False

            if event.type == pygame.MOUSEMOTION and volume_dragging:
                mx, my = pygame.mouse.get_pos()
                screen_w, _screen_h = screen.get_size()
                _, _, _, _, _, _, _, _, slider = get_ui_rects(screen_w)
                volume = max(0.0, min(1.0, (mx - slider.x) / slider.w))
                music_started = apply_music_state(
                    music_loaded, music_enabled, volume, music_started
                )

        if not game_over and not win and all_safe_revealed(grid):
            win = True

        mode_cfg = get_mode_config(current_mode)
        time_limit = mode_cfg.get("time_limit") if mode_cfg else None
        elapsed = 0
        if start_time is not None:
            elapsed = (pygame.time.get_ticks() - start_time) / 1000.0
        if time_limit:
            remaining = max(0, int(time_limit - elapsed))
            time_text = f"Süre: {remaining // 60}:{remaining % 60:02d}"
            if not game_over and not win and not time_up and elapsed >= time_limit:
                game_over = True
                time_up = True
        else:
            time_text = None

        status_text = "Mayın Tarlası"
        if game_over:
            if time_up:
                status_text = "Süre doldu! Yeniden başlamak için R"
            else:
                status_text = "Kaybettin! Yeniden başlamak için R"
        elif win:
            status_text = "Kazandın! Yeniden başlamak için R"

        end_title = None
        if game_over:
            end_title = "Süre doldu!" if time_up else "Kaybettin!"
        elif win:
            end_title = "Kazandın!"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            grid = make_grid()
            game_over = False
            win = False
            time_up = False
            start_time = None

        draw(
            screen,
            grid,
            font,
            big_font,
            status_text,
            settings_open,
            music_enabled,
            volume,
            fullscreen_enabled,
            light_mode,
            bosna_enabled,
            time_text,
            game_over or win,
            end_title,
        )
        clock.tick(60)


if __name__ == "__main__":
    main()










