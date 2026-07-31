"""
Рождение святого - Sprites
Процедурные пиксельные спрайты вместо кружков.
Генерируются на лету из массивов пикселей.
"""
import pygame
import math
import os

# 16x16 пиксельные паттерны (0=пусто, 1=основной цвет, 2=тёмный, 3=светлый)
PLAYER_SPRITES = {
    "warrior": [
        "......111.......",
        ".....13331......",
        ".....13331......",
        "......111.......",
        "....1111111.....",
        "...122222221....",
        "...122222221....",
        "...122222221....",
        "....1111111.....",
        ".....11111......",
        "....1222221.....",
        "....1222221.....",
        "....1222221.....",
        ".....1..1.......",
        "....11..11......",
        "...111..111.....",
    ],
    "paladin": [
        "......333.......",
        ".....31113......",
        ".....31113......",
        "......333.......",
        "....1111111.....",
        "...122222221....",
        "...122222221....",
        "...122222221....",
        "....1111111.....",
        ".....11111......",
        "....1222221.....",
        "....1222221.....",
        "....1222221.....",
        ".....1..1.......",
        "....11..11......",
        "...111..111.....",
    ],
    "inquisitor": [
        "......111.......",
        ".....13331......",
        ".....13331......",
        "......111.......",
        "....1111111.....",
        "...122222221....",
        "...122222221....",
        "...122222221....",
        "....1111111.....",
        ".....11111......",
        "....1222221.....",
        "....1222221.....",
        "....1222221.....",
        ".....1..1.......",
        "....11..11......",
        "...111..111.....",
    ],
    "pilgrim": [
        "......111.......",
        ".....13331......",
        ".....13331......",
        "......111.......",
        "....1111111.....",
        "...122222221....",
        "...122222221....",
        "...122222221....",
        "....1111111.....",
        ".....11111......",
        "....1222221.....",
        "....1222221.....",
        "....1222221.....",
        ".....1..1.......",
        "....11..11......",
        "...111..111.....",
    ],
    "monk": [
        "......333.......",
        ".....31113......",
        ".....31113......",
        "......333.......",
        "....1111111.....",
        "...122222221....",
        "...122222221....",
        "...122222221....",
        "....1111111.....",
        ".....11111......",
        "....1222221.....",
        "....1222221.....",
        "....1222221.....",
        ".....1..1.......",
        "....11..11......",
        "...111..111.....",
    ],
}

ENEMY_SPRITES = {
    "neophyte": [
        "................",
        "......222.......",
        ".....22222......",
        ".....21112......",
        ".....21112......",
        "......222.......",
        "....1111111.....",
        "...122222221....",
        "...122222221....",
        "....1111111.....",
        ".....11111......",
        "....1222221.....",
        "....1222221.....",
        ".....1..1.......",
        "....11..11......",
        "................",
    ],
    "acolyte": [
        "................",
        "......111.......",
        ".....11111......",
        ".....12221......",
        ".....12221......",
        "......111.......",
        "....1111111.....",
        "...122222221....",
        "...122222221....",
        "....1111111.....",
        ".....11111......",
        "....1222221.....",
        "....1222221.....",
        ".....1..1.......",
        "....11..11......",
        "................",
    ],
    "antichrist": [
        ".....11111......",
        "....1222221.....",
        "...122222221....",
        "..12222222221...",
        "..12221122221...",
        "..12221122221...",
        "..12222222221...",
        "..12222222221...",
        "...122222221....",
        "....1222221.....",
        ".....11111......",
        "....1222221.....",
        "...122222221....",
        "..12222222221...",
        "..12222222221...",
        "..11111111111...",
    ],
    "ghost": [
        "................",
        ".....1111.......",
        "....133331......",
        "...13333331.....",
        "...13313331.....",
        "...13333331.....",
        "....133331......",
        "....1111111.....",
        "...122222221....",
        "...1.2222.21....",
        "...1..22..21....",
        "....1.22.1......",
        "....1.22.1......",
        ".....1..1.......",
        "................",
        "................",
    ],
    "gargoyle": [
        "................",
        "..11......11....",
        "..131....131....",
        "..1331..1331....",
        "...13311331.....",
        "...13333331.....",
        "....133331......",
        "....122221......",
        "...12222221.....",
        "..1222222221....",
        "..1222222221....",
        "..1222222221....",
        "...12222221.....",
        "....1..1..1.....",
        "...11..1..11....",
        "................",
    ],
    "pope": [
        "......333.......",
        ".....31113......",
        "....3111113.....",
        "....3111113.....",
        ".....31113......",
        ".....11111......",
        "....1222221.....",
        "...122222221....",
        "..12222222221...",
        "..12222222221...",
        "..12222222221...",
        "...122222221....",
        "....1222221.....",
        "...122222221....",
        "..12222222221...",
        "..11111111111...",
    ],
}

# Цвета для спрайтов (R, G, B)
SPRITE_COLORS = {
    "warrior":      {1: (200, 60, 60),   2: (140, 30, 30),   3: (255, 100, 100)},
    "paladin":      {1: (60, 120, 220),  2: (30, 80, 160),   3: (100, 160, 255)},
    "inquisitor":   {1: (220, 180, 50),  2: (160, 120, 20),  3: (255, 220, 100)},
    "pilgrim":      {1: (100, 180, 120), 2: (60, 120, 80),   3: (140, 220, 160)},
    "monk":         {1: (180, 160, 140), 2: (120, 100, 80),  3: (220, 200, 180)},
    "neophyte":     {1: (100, 100, 100), 2: (60, 60, 60),    3: (150, 150, 150)},
    "acolyte":      {1: (80, 120, 80),   2: (50, 80, 50),    3: (120, 180, 120)},
    "heretic":      {1: (120, 60, 60),   2: (80, 30, 30),    3: (180, 100, 100)},
    "demon":        {1: (180, 50, 50),   2: (120, 20, 20),   3: (255, 100, 100)},
    "fanatic":      {1: (60, 60, 120),   2: (30, 30, 80),    3: (100, 100, 180)},
    "antichrist":   {1: (100, 40, 140),  2: (60, 20, 100),   3: (160, 80, 200)},
    "ghost":        {1: (120, 200, 255), 2: (80, 150, 220),  3: (180, 230, 255)},
    "gargoyle":     {1: (100, 100, 120), 2: (60, 60, 80),    3: (150, 150, 170)},
    "shade":        {1: (60, 60, 80),    2: (30, 30, 50),    3: (100, 100, 130)},
    "cultist":      {1: (100, 50, 100),  2: (60, 30, 60),    3: (150, 80, 150)},
    "pope":         {1: (220, 200, 50),  2: (180, 160, 30),  3: (255, 240, 100)},
}

# Кэш сгенерированных спрайтов
_sprite_cache = {}


def generate_sprite(sprite_id: str, pattern: list, colors: dict, scale: int = 2) -> pygame.Surface:
    """Генерирует Surface из пиксельного паттерна."""
    key = (sprite_id, scale)
    if key in _sprite_cache:
        return _sprite_cache[key]

    size = len(pattern)
    surf = pygame.Surface((size * scale, size * scale), pygame.SRCALPHA)

    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            color = colors.get(int(ch), (255, 255, 255))
            pygame.draw.rect(surf, color, (x * scale, y * scale, scale, scale))

    _sprite_cache[key] = surf
    return surf


ENEMY_TO_TEMPLATE = {
    "neophyte": "skeleton",
    "acolyte": "mage",
    "heretic": "zombie",
    "demon": "bat",
    "fanatic": "goblin",
    "antichrist": "knight",
    "ghost": "slime",
    "gargoyle": "knight",
    "shade": "bat",
    "cultist": "archer",
    "pope": "mage",
}

PLAYER_TO_TEMPLATE = {
    "warrior": "knight",
    "paladin": "knight",
    "inquisitor": "archer",
    "pilgrim": "skeleton",
    "monk": "zombie",
}

_sprite_cache = {}

def load_sprite_frame(template: str, state: str, frame: int, scale: int = 2) -> pygame.Surface:
    """Загрузить один кадр спрайта из assets/sprites/{template}/{state}_{frame:02d}.png

    Args:
        template: knight, slime, skeleton, bat, zombie, archer, mage, goblin
        state: idle, walk_down, walk_up, walk_left, walk_right, attack_down, death
        frame: 0-3
        scale: масштаб (2 = 32x32)
    """
    key = (template, state, frame, scale)
    if key in _sprite_cache:
        return _sprite_cache[key]

    path = os.path.join(ASSETS_DIR, "sprites", template, f"{state}_{frame:02d}.png")
    if os.path.exists(path):
        surf = pygame.image.load(path).convert_alpha()
        surf = pygame.transform.scale(surf, (scale * 16, scale * 16))
        _sprite_cache[key] = surf
        return surf

    # Fallback — procedural sprite
    return None


class SpriteAnimator:
    """Per-entity аниматор: idle, walk, attack, death."""
    def __init__(self, template: str, scale: int = 2):
        self.template = template
        self.scale = scale
        self.state = "idle"
        self.frame = 0
        self.timer = 0.0
        self.frame_duration = 0.15  # секунд на кадр
        self.attack_timer = 0.0
        self.attack_duration = 0.3  # длительность attack анимации

    def set_state(self, state: str):
        if self.state == "death":
            return  # death не прерывается
        if state != self.state:
            self.state = state
            self.frame = 0
            self.timer = 0.0

    def start_attack(self):
        if self.state != "death":
            self.state = "attack_down"
            self.frame = 0
            self.timer = 0.0
            self.attack_timer = self.attack_duration

    def update(self, dt: float):
        if self.state == "death":
            # Death: проиграть 4 кадра и остановиться на последнем
            self.timer += dt
            if self.timer >= self.frame_duration and self.frame < 3:
                self.timer = 0.0
                self.frame = min(3, self.frame + 1)
            return

        # Attack возврат в idle
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.state = "idle"
                self.frame = 0
                self.timer = 0.0

        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0.0
            self.frame = (self.frame + 1) % 4

    def get_surface(self) -> pygame.Surface:
        surf = load_sprite_frame(self.template, self.state, self.frame, self.scale)
        if surf is None:
            # Fallback
            return generate_sprite(self.template,
                                   PLAYER_SPRITES.get(self.template, PLAYER_SPRITES.get("warrior", [])),
                                   SPRITE_COLORS.get(self.template, SPRITE_COLORS.get("warrior", {})),
                                   self.scale)
        return surf


def get_player_sprite(char_id: str, scale: int = 2) -> pygame.Surface:
    """Fallback: idle кадр из assets."""
    template = PLAYER_TO_TEMPLATE.get(char_id, "knight")
    surf = load_sprite_frame(template, "idle", 0, scale)
    if surf:
        return surf
    pattern = PLAYER_SPRITES.get(char_id, PLAYER_SPRITES["warrior"])
    colors = SPRITE_COLORS.get(char_id, SPRITE_COLORS["warrior"])
    return generate_sprite(char_id, pattern, colors, scale)


def get_enemy_sprite(enemy_type: str, scale: int = 2) -> pygame.Surface:
    """Fallback: idle кадр из assets."""
    template = ENEMY_TO_TEMPLATE.get(enemy_type, "skeleton")
    surf = load_sprite_frame(template, "idle", 0, scale)
    if surf:
        return surf
    pattern = ENEMY_SPRITES.get(enemy_type, ENEMY_SPRITES["neophyte"])
    colors = SPRITE_COLORS.get(enemy_type, SPRITE_COLORS["neophyte"])
    return generate_sprite(enemy_type, pattern, colors, scale)


# === VFX & Animation Loaders ===

_vfx_cache = {}
_anim_cache = {}

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def load_vfx_frames(vfx_type: str, size: int = 32) -> list:
    """Загрузить VFX кадры из assets/vfx/.

    Args:
        vfx_type: explosion, lightning, slash, trail, particle, crit_flash, evolution_glow, whip_sweep, ring_wave
        size: размер спрайта

    Returns:
        list[pygame.Surface] или пустой список если файлы не найдены
    """
    cache_key = (vfx_type, size)
    if cache_key in _vfx_cache:
        return _vfx_cache[cache_key]

    vfx_dir = os.path.join(ASSETS_DIR, "vfx")
    frames = []

    # Ищем файлы типа_XX.png
    i = 0
    while True:
        path = os.path.join(vfx_dir, f"{vfx_type}_{i:02d}.png")
        if not os.path.exists(path):
            break
        try:
            img = pygame.image.load(path).convert_alpha()
            if img.get_size() != (size, size):
                img = pygame.transform.scale(img, (size, size))
            frames.append(img)
        except Exception:
            pass
        i += 1

    # Fallback: генерируем процедурно если файлов нет
    if not frames:
        frames = _generate_vfx_fallback(vfx_type, size)

    _vfx_cache[cache_key] = frames
    return frames


def _generate_vfx_fallback(vfx_type: str, size: int) -> list:
    """Процедурный fallback если VFX файлы не найдены."""
    frames = []
    cx, cy = size // 2, size // 2

    if vfx_type == "explosion":
        for fi in range(6):
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            t = fi / 5.0
            r = int(size * 0.3 * (1 - t * 0.5))
            a = int(200 * (1 - t))
            pygame.draw.circle(surf, (255, 200, 50, a), (cx, cy), r)
            pygame.draw.circle(surf, (255, 255, 200, a), (cx, cy), max(1, r // 2))
            frames.append(surf)

    elif vfx_type == "lightning":
        for fi in range(4):
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            a = int(255 * (1 - fi / 4.0))
            pygame.draw.line(surf, (200, 220, 255, a), (cx, 0), (cx + (fi % 2) * 4 - 2, size - 1), 2)
            frames.append(surf)

    elif vfx_type in ("slash", "whip_sweep"):
        for fi in range(4):
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            t = fi / 3.0
            a = int(255 * (1 - t * 0.7))
            r = int(size * 0.35)
            start_deg = -30 + int(t * 40)
            end_deg = start_deg + 120 - int(t * 30)
            points = []
            for deg in range(start_deg, end_deg, 5):
                rad = math.radians(deg) if 'math' in dir() else deg * 3.14159 / 180
                x = int(cx + __import__('math').cos(rad) * r)
                y = int(cy + __import__('math').sin(rad) * r)
                points.append((x, y))
            if len(points) >= 2:
                pygame.draw.lines(surf, (255, 240, 200, a), False, points, 2)
            frames.append(surf)

    elif vfx_type == "ring_wave":
        for fi in range(5):
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            t = fi / 4.0
            r = int(size * 0.4 * t)
            a = int(200 * (1 - t))
            if r > 0:
                pygame.draw.circle(surf, (180, 180, 255, a), (cx, cy), r, 2)
            frames.append(surf)

    else:
        # Универсальный fallback: затухающий круг
        for fi in range(4):
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            t = fi / 3.0
            r = max(2, int(size * 0.3 * (1 - t * 0.5)))
            a = int(200 * (1 - t))
            pygame.draw.circle(surf, (255, 255, 255, a), (cx, cy), r)
            frames.append(surf)

    return frames


def get_attack_frames(template_id: str, size: int = 32) -> list:
    """Загрузить attack animation кадры.

    Args:
        template_id: knight, slime, skeleton, bat, zombie, archer, mage, goblin
        size: размер спрайта

    Returns:
        list[pygame.Surface] или пустой список
    """
    cache_key = ("attack", template_id, size)
    if cache_key in _anim_cache:
        return _anim_cache[cache_key]

    anim_dir = os.path.join(ASSETS_DIR, "sprites", template_id)
    frames = _load_animation_frames(anim_dir, "attack_down", size)

    _anim_cache[cache_key] = frames
    return frames


def get_death_frames(template_id: str, size: int = 32) -> list:
    """Загрузить death animation кадры.

    Args:
        template_id: knight, slime, skeleton, bat, zombie, archer, mage, goblin
        size: размер спрайта

    Returns:
        list[pygame.Surface] или пустой список
    """
    cache_key = ("death", template_id, size)
    if cache_key in _anim_cache:
        return _anim_cache[cache_key]

    anim_dir = os.path.join(ASSETS_DIR, "sprites", template_id)
    frames = _load_animation_frames(anim_dir, "death", size)

    _anim_cache[cache_key] = frames
    return frames


def _load_animation_frames(anim_dir: str, state: str, size: int) -> list:
    """Загрузить кадры анимации из директории."""
    frames = []
    for i in range(4):
        path = os.path.join(anim_dir, f"{state}_{i:02d}.png")
        if not os.path.exists(path):
            continue
        try:
            img = pygame.image.load(path).convert_alpha()
            if img.get_size() != (size, size):
                img = pygame.transform.scale(img, (size, size))
            frames.append(img)
        except Exception:
            pass
    return frames
