"""
Рождение святого — UI Theme (Design System)
Единая точка правды для всех цветов, шрифтов, размеров и палитры.
Все UI-компоненты берут значения отсюда.
"""
import pygame


# ============================================================
# SCREEN CONSTANTS
# ============================================================
SCREEN_W = 1024
SCREEN_H = 768


# ============================================================
# COLOR SYSTEM
# ============================================================

# Background
BG_NEAR_BLACK = (10, 14, 20)        # #0a0e14 — основной фон
BG_DARK = (16, 18, 24)              # чуть светлее для карточек

# Stone palette (Title, panels)
STONE_BASE = (28, 24, 32)           # #1c1820
STONE_LIGHT = (42, 38, 48)          # #2a2630
STONE_DARK = (16, 12, 20)           # #100c14
STONE_MORTAR = (20, 16, 24)         # линии между блоками

# Blood palette
BLOOD_DARK = (100, 15, 15)          # тёмная кровь
BLOOD = (140, 20, 20)               # #8c1414
BLOOD_DRIP = (160, 25, 30)          # стекающие капли
BLOOD_BRIGHT = (200, 40, 40)        # яркие акценты

# Gold palette
GOLD_LEAF = (255, 215, 0)           # #ffd700 — заголовки, акценты
GOLD_IDLE = (180, 150, 0)           # #b49600 — неактивные
GOLD_GLOW = (255, 235, 100)         # свечение
GOLD_DARK = (120, 100, 0)           # тёмное золото
GOLD_MUTED = (140, 120, 40)         # приглушённое

# Sacred / Divine
SACRED_CYAN = (0, 191, 255)         # #00bfff
SACRED_BLUE = (80, 120, 255)        # синий
SACRED_WHITE = (240, 240, 255)      # бело-голубой

# Danger
DANGER_RED = (220, 38, 38)          # #dc2626
DANGER_ORANGE = (255, 120, 0)       # оранжевый
WARNING_YELLOW = (255, 200, 0)      # жёлтый

# XP
XP_GREEN = (68, 255, 68)            # #44ff44
XP_GOLD = (255, 215, 0)             # #ffd700 (high level)

# HP
HP_RED = (255, 51, 51)              # #ff3333
HP_LOW = (255, 0, 0)                # критический
HP_GREEN = (80, 200, 80)            # здоровый

# Text
TEXT_PRIMARY = (255, 255, 255)      # #ffffff
TEXT_SECONDARY = (180, 180, 180)    # #b4b4b4
TEXT_DIM = (80, 80, 80)             # #505050
TEXT_GOLD = (255, 215, 0)           # заголовки
TEXT_GREY = (150, 150, 150)         # подсказки

# Rarity
RARITY_COLORS = {
    'common':    (120, 120, 120),   # grey
    'uncommon':  (80, 200, 80),     # green
    'rare':      (80, 120, 255),    # blue
    'epic':      (180, 80, 255),    # purple
    'legendary': (255, 180, 50),    # gold
}

# Iron palette (confessional, borders)
IRON = (80, 80, 85)
IRON_LIGHT = (120, 120, 125)
IRON_DARK = (50, 50, 55)

# Wood palette (confessional booth)
WOOD_DARK = (38, 28, 18)
WOOD_LIGHT = (55, 40, 28)
WOOD_BASE = (45, 33, 22)

# Parchment palette (illuminated manuscript)
PARCH_DARK = (18, 14, 8)
PARCH_MID = (32, 26, 18)
PARCH_BASE = (48, 40, 30)
PARCH_LIGHT = (58, 50, 38)
PARCH_INK = (200, 190, 160)
PARCH_INK_DIM = (140, 130, 110)

# Confessional palette
CONFESS_DARK = (18, 12, 8)
CONFESS_WOOD = (38, 28, 18)
CONFESS_WOOD_LIGHT = (55, 40, 28)
CONFESS_STONE = (60, 55, 50)
CONFESS_STONE_LIGHT = (85, 78, 70)
CONFESS_STONE_DARK = (35, 30, 25)
CONFESS_GOLD = (200, 170, 80)


# ============================================================
# PARTICLE COLORS
# ============================================================
PARTICLE_COLORS = {
    'gold':   [(200, 180, 100), (255, 215, 0), (255, 235, 100)],
    'white':  [(255, 255, 255), (240, 240, 255)],
    'blood':  [(160, 25, 30), (140, 20, 20), (200, 40, 40)],
    'fire':   [(255, 180, 50), (255, 120, 0), (255, 80, 0)],
    'ice':    [(150, 200, 255), (100, 150, 255), (200, 230, 255)],
    'holy':   [(255, 255, 200), (255, 240, 150), (240, 240, 255)],
    'shadow': [(80, 60, 100), (60, 40, 80), (100, 80, 120)],
}


# ============================================================
# TYPOGRAPHY
# ============================================================
# Sizes (not fonts — fonts created lazily via get_font)
FONT_SIZE_LOGO = 56
FONT_SIZE_HEADING = 48
FONT_SIZE_BUTTON = 24
FONT_SIZE_TAB = 22
FONT_SIZE_BODY = 18
FONT_SIZE_SMALL = 14
FONT_SIZE_TINY = 12

# Font cache (initialized on first call to get_font)
_font_cache: dict = {}


def get_font(size: int) -> pygame.font.Font:
    """Get or create a cached font at the given size."""
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


def get_logo_font() -> pygame.font.Font:
    return get_font(FONT_SIZE_LOGO)

def get_heading_font() -> pygame.font.Font:
    return get_font(FONT_SIZE_HEADING)

def get_button_font() -> pygame.font.Font:
    return get_font(FONT_SIZE_BUTTON)

def get_tab_font() -> pygame.font.Font:
    return get_font(FONT_SIZE_TAB)

def get_body_font() -> pygame.font.Font:
    return get_font(FONT_SIZE_BODY)

def get_small_font() -> pygame.font.Font:
    return get_font(FONT_SIZE_SMALL)

def get_tiny_font() -> pygame.font.Font:
    return get_font(FONT_SIZE_TINY)


# ============================================================
# LAYOUT CONSTANTS
# ============================================================

# Button sizes
BTN_SMALL_W = 100
BTN_SMALL_H = 32
BTN_MEDIUM_W = 160
BTN_MEDIUM_H = 40
BTN_LARGE_W = 240
BTN_LARGE_H = 50
BTN_CUSTOM_W = 300
BTN_CUSTOM_H = 60

# Button gap
BTN_GAP = 12

# Panel
PANEL_PADDING = 16
PANEL_RADIUS = 12
PANEL_BORDER_W = 2

# Tab bar
TAB_H = 44
TAB_GAP = 4
TAB_RADIUS = 8

# Card
CARD_W = 200
CARD_H = 260
CARD_GAP = 16
CARD_RADIUS = 10

# Slider
SLIDER_W = 400
SLIDER_H = 8
SLIDER_HANDLE_R = 12
SLIDER_GAP = 60

# Progress bar
PROG_BAR_W = 200
PROG_BAR_H = 12
PROG_BAR_RADIUS = 6

# Toast
TOAST_W = 300
TOAST_H = 50
TOAST_GAP = 8
TOAST_DURATION = 2.0

# Tooltip
TOOLTIP_DELAY = 0.5  # seconds before showing
TOOLTIP_PADDING = 8

# Overlay
OVERLAY_ALPHA = 180

# Animation durations (seconds)
DUR_FAST = 0.12
DUR_NORMAL = 0.2
DUR_SLOW = 0.4
DUR_FADE = 0.3
DUR_FADE_LONG = 0.5
DUR_FADE_RED = 0.8

# Stagger delay between elements
STAGGER_DELAY = 0.08

# Particle defaults
PARTICLE_COUNT_BG = 60       # фоновые частицы
PARTICLE_COUNT_SPLASH = 80   # splash screen
PARTICLE_SIZE_MIN = 1
PARTICLE_SIZE_MAX = 4
PARTICLE_SPEED_MIN = 0.15
PARTICLE_SPEED_MAX = 0.5


# ============================================================
# HEARTBEAT (logo pulse)
# ============================================================
HEARTBEAT_PERIOD = 2.0  # seconds per lub-dub cycle


# ============================================================
# CONFIRM DIALOG
# ============================================================
CONFIRM_W = 400
CONFIRM_H = 180
CONFIRM_TITLE_SIZE = FONT_SIZE_BUTTON
CONFIRM_BODY_SIZE = FONT_SIZE_BODY


# ============================================================
# HELPER: color with alpha
# ============================================================
def color_alpha(color: tuple, alpha: int) -> tuple:
    """Return (r, g, b, a) tuple."""
    return (*color[:3], max(0, min(255, alpha)))


def color_lerp(c1: tuple, c2: tuple, t: float) -> tuple:
    """Linear interpolation between two RGB colors."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))


def color_brighten(color: tuple, amount: int) -> tuple:
    """Brighten a color by amount (additive)."""
    return tuple(min(255, c + amount) for c in color[:3])


def color_dim(color: tuple, factor: float) -> tuple:
    """Dim a color by factor (0.0 = black, 1.0 = unchanged)."""
    return tuple(int(c * factor) for c in color[:3])
