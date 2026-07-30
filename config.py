"""
Рождение святого — Configuration
Все константы, настройки экрана, формулы.
"""
import math

# === ЭКРАН ===
WIDTH = 1024
HEIGHT = 768
FPS = 60
TITLE = "Рождение святого"

# === КАРТА ===
MAP_WIDTH = 4000
MAP_HEIGHT = 4000
TILE_SIZE = 64

# === ИГРОК ===
PLAYER_BASE_SPEED = 3.0
PLAYER_BASE_HP = 100
PICKUP_RANGE_BASE = 60.0
PICKUP_MAGNET_SPEED = 8.0  # скорость притяжения гемов
INVULN_AFTER_LEVELUP = 0.5  # секунды неуязвимости после левелапа

# === ОРУЖИЕ ===
MAX_WEAPONS = 6
MAX_PASSIVES = 6
MAX_WEAPON_LEVEL = 8
MAX_PASSIVE_LEVEL = 5

# === ВРАГИ ===
MAX_ENEMIES = 300
SPAWN_DISTANCE = 40  # пикселей за экраном

# === ВОЛНЫ ===
WAVE_DURATION = 25.0  # секунд на волну
BOSS_EVERY_N_WAVES = 3
WAVE_30_BOSS = 30  # Жнец

# === XP ===
XP_BASE = 5  # XP для уровня 1→2
XP_INCREMENT_EARLY = 10  # +10 за уровень до 20
XP_INCREMENT_MID = 13  # +13 для уровней 21-40
XP_INCREMENT_LATE = 16  # +16 для уровней 41+
XP_BONUS_LEVEL20 = 600
XP_BONUS_LEVEL40 = 2400

# === ЦВЕТА ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
DARK_RED = (140, 30, 30)
GREEN = (50, 220, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 50)
PURPLE = (180, 80, 255)
ICE_BLUE = (120, 200, 255)
GOLD = (255, 215, 0)
DARK_BG = (15, 10, 25)
GRID_COLOR = (30, 20, 45)

# === UI ===
HUD_PADDING = 10
HP_BAR_WIDTH = 200
HP_BAR_HEIGHT = 16
XP_BAR_WIDTH = 400
XP_BAR_HEIGHT = 10
LEVELUP_CARD_WIDTH = 200
LEVELUP_CARD_HEIGHT = 260
LEVELUP_CARD_GAP = 20

# === ЗВУК ===
SAMPLE_RATE = 22050
SOUND_VOLUME = 0.3


def calc_damage_mult(faith_level: int) -> float:
    return 1.0 + 0.1 * faith_level


def calc_cooldown_mult(cooldown_level: int) -> float:
    return 1.0 * (1 - 0.08 * cooldown_level)


def calc_area_mult(area_level: int) -> float:
    return 1.0 + 0.1 * area_level


def calc_speed_mult(speed_level: int) -> float:
    return 1.0 + 0.1 * speed_level


def calc_pickup_range(base: float, paladin_bonus: bool) -> float:
    return base * (1.25 if paladin_bonus else 1.0)


def calc_regen(regen_level: int) -> float:
    return 0.3 * regen_level  # HP per second


def calc_max_hp(base: int, max_hp_level: int, char_bonus: int = 0) -> int:
    return base + 10 * max_hp_level + char_bonus


def calc_xp_for_level(level: int) -> int:
    """XP, необходимый для перехода на следующий уровень."""
    if level < 1:
        return XP_BASE
    if level <= 20:
        return XP_BASE + XP_INCREMENT_EARLY * (level - 1)
    elif level <= 40:
        return XP_BASE + XP_INCREMENT_EARLY * 19 + XP_INCREMENT_MID * (level - 20)
    else:
        return (XP_BASE + XP_INCREMENT_EARLY * 19 +
                XP_INCREMENT_MID * 20 + XP_INCREMENT_LATE * (level - 40))
