"""
Рождение святого - Configuration
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
SESSION_DURATION = 15 * 60  # 15 минут в секундах
DESPAWN_DISTANCE = 1500  # деспавн врагов за этой дистанцией от игрока

# === БИОМЫ ===
CENTER_X = MAP_WIDTH // 2
CENTER_Y = MAP_HEIGHT // 2

BIOMES = [
    {"name": "Руины",       "radius": 1000, "bg": (26, 26, 46),   "grid": (40, 35, 60)},
    {"name": "Кладбище",    "radius": 2000, "bg": (13, 13, 26),   "grid": (25, 25, 40)},
    {"name": "Адский лес",  "radius": 3000, "bg": (26, 13, 13),   "grid": (45, 25, 25)},
    {"name": "Пустошь",     "radius": 4000, "bg": (13, 13, 13),   "grid": (30, 30, 25)},
]

# === МЕТА-ПРОГРЕССИЯ ===
POWERUP_COSTS = [100, 200, 400, 800]  # 4 уровня
LUCKY_COSTS = [200, 400, 800, 1600]
REVIVE_COSTS = [500, 1000, 2000]  # 3 уровня

POWERUP_DEFS = {
    "might":     {"name": "Мощь",       "desc": "+5% базовый урон",   "max": 4, "costs": POWERUP_COSTS},
    "sturdiness":{"name": "Стойкость",  "desc": "+10% макс HP",       "max": 4, "costs": POWERUP_COSTS},
    "swiftness": {"name": "Проворство", "desc": "+5% скорость",       "max": 4, "costs": POWERUP_COSTS},
    "greed":     {"name": "Жадность",   "desc": "+10% золото",        "max": 4, "costs": POWERUP_COSTS},
    "luck":      {"name": "Удача",      "desc": "+10% шанс 4-го варианта", "max": 4, "costs": LUCKY_COSTS},
    "revive":    {"name": "Воскрешение","desc": "1 возрождение (30% HP)", "max": 3, "costs": REVIVE_COSTS},
}

# === ДОСТИЖЕНИЯ ===
ACHIEVEMENTS = {
    "survive_5":    {"name": "5 минут",       "desc": "Дожить до 5 минут",  "unlock": "inquisitor"},
    "first_boss":   {"name": "Первый босс",   "desc": "Убить первого босса", "unlock": "weapon_lightning"},
    "survive_10":   {"name": "10 минут",      "desc": "Дожить до 10 минут", "unlock": "weapon_prayer"},
    "gold_10000":   {"name": "Богач",         "desc": "Накопить 10000 золота","unlock": "powerup_revive"},
    "kill_reaper":  {"name": "Убийца Жнеца",  "desc": "Убить Жнеца",        "unlock": "char_secret"},
}

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
