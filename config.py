"""
Рождение святого - Configuration
Все константы, настройки экрана, формулы.
"""

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

# === ЗОЛОТЫЕ МОНЕТЫ (REF-8) ===
COIN_DROP_CHANCE = 0.40       # 40% шанс дропа монеты с врага
COIN_MAGNET_RANGE = 150       # радиус притяжения монет к игроку
COIN_VALUE = 1                # базовая ценность монеты
COIN_LIFETIME = 12.0          # секунды до исчезновения

# === ОРУЖИЕ ===
MAX_WEAPONS = 6
MAX_PASSIVES = 6
MAX_BANNED_ITEMS = 8
MAX_WEAPON_LEVEL = 8
MAX_PASSIVE_LEVEL = 5

# === ВРАГИ ===
MAX_ENEMIES = 300
SPAWN_DISTANCE = 200  # пикселей за экраном (образец: margin=200)

# === ВОЛНЫ ===
WAVE_DURATION = 25.0  # секунд на волну
BOSS_EVERY_N_WAVES = 3
SESSION_DURATION = 15 * 60  # 15 минут в секундах
DESPAWN_DISTANCE = 1500  # деспавн врагов за этой дистанцией от игрока

# === БИОМЫ ===
CENTER_X = MAP_WIDTH // 2
CENTER_Y = MAP_HEIGHT // 2

# Единый источник правды о картах (ARCH-5)
MAP_DEFS = {
    "arena":     {"name": "Арена",     "desc": "Бесконечная равнина, 4 биома-кольца", "diff": 2, "bonus": "+10% скорость", "unlocked": True},
    "cathedral": {"name": "Собор",     "desc": "Узкие коридоры, залы, колонны",       "diff": 3, "bonus": "+15% золото",   "unlocked": True},
    "catacombs": {"name": "Катакомбы", "desc": "Подземелья под собором. Темнота и ужас.", "diff": 3, "bonus": "", "unlocked": False},
    "hellgate":  {"name": "Врата Ада", "desc": "Портал в преисподнюю. Финальное испытание.", "diff": 5, "bonus": "", "unlocked": False},
}
MAP_ORDER = ["arena", "cathedral", "catacombs", "hellgate"]

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


# === C4: MULTI-VECTOR META-PROGRESSION ===

# Altar: sacrifice gold for permanent buffs (5 tiers)
ALTAR_COSTS = [500, 1500, 3500, 7000, 12000]
ALTAR_DEFS = {
    "might_altar":   {"name": "Алтарь Мощи",     "desc": "+3% урон за уровень",       "max": 5, "costs": ALTAR_COSTS, "bonus_per_lvl": 0.03, "color": (220, 80, 80)},
    "regen_altar":   {"name": "Алтарь Жизни",     "desc": "+0.2 HP/сек за уровень",    "max": 5, "costs": ALTAR_COSTS, "bonus_per_lvl": 0.2, "color": (80, 220, 80)},
    "magnet_altar":  {"name": "Алтарь Сбора",     "desc": "+10% дальность сбора",      "max": 5, "costs": ALTAR_COSTS, "bonus_per_lvl": 0.10, "color": (100, 180, 255)},
    "luck_altar":    {"name": "Алтарь Фортуны",   "desc": "+5% удача",                 "max": 5, "costs": ALTAR_COSTS, "bonus_per_lvl": 0.05, "color": (255, 215, 0)},
}

# Weapon Archive: unlock weapon variants (cosmetic + stat tweaks)
WEAPON_ARCHIVE_DEFS = {
    "whip_flame":    {"base": "whip",      "name": "Пламенный кнут",    "desc": "Урон +10%, скорость -5%",  "unlock_kills": 500, "color": (255, 100, 50)},
    "fire_ice":      {"base": "fire",      "name": "Ледяное пламя",     "desc": "Замедляет врагов на 15%",   "unlock_kills": 500, "color": (150, 200, 255)},
    "halo_shadow":   {"base": "halo",      "name": "Тёмный ореол",      "desc": "Урон +15%, радиус -10%",   "unlock_kills": 500, "color": (120, 80, 160)},
    "rosary_thunder": {"base": "rosary",   "name": "Громовые чётки",    "desc": "Скорость +20%, урон -5%",  "unlock_kills": 500, "color": (255, 255, 150)},
    "lightning_holy": {"base": "lightning", "name": "Священный гром",    "desc": "Цели +2, урон -10%",       "unlock_kills": 750, "color": (255, 255, 220)},
    "prayer_dark":    {"base": "prayer",   "name": "Молитва тьмы",      "desc": "Урон +20%, кулдаун +15%",  "unlock_kills": 750, "color": (160, 100, 200)},
}

# Faction Reputation: 3 factions, rep gained from kills/achievements
FACTION_DEFS = {
    "angels":  {"name": "Ангелы",   "desc": "Небесные силы света",           "color": (200, 200, 255),
                "rewards": {100: ("Благословение", "+3% урон"), 300: ("Аура защиты", "-5% получаемый урон"), 600: ("Крылья", "+8% скорость")}},
    "demons":  {"name": "Демоны",   "desc": "Силы бездны",                   "color": (255, 100, 100),
                "rewards": {100: ("Пламя", "+5% урон огнём"), 300: ("Кровопийство", "+15% вампиризм"), 600: ("Ярость", "+10% урон на <30% HP")}},
    "humans":  {"name": "Люди",     "desc": "Смертные, но упорные",          "color": (200, 180, 140),
                "rewards": {100: ("Стойкость", "+10% макс HP"), 300: ("Торговец", "-15% цены в магазине"), 600: ("Изобретатель", "+1 слот оружия")}},
}

# Obelisks: map-specific challenges
OBELISK_DEFS = {
    "ruins_survive":   {"name": "Столп Руин",      "desc": "Продержаться 5 мин в Руинах",     "biome": 0, "condition": "survive_300",  "reward_gold": 500, "color": (120, 120, 180)},
    "cemetery_kill":   {"name": "Столп Кладбища",   "desc": "Убить 200 врагов на Кладбище",    "biome": 1, "condition": "kill_200",     "reward_gold": 800, "color": (80, 80, 130)},
    "forest_streak":   {"name": "Столп Леса",       "desc": "Серия 50 убийств в Адском лесу",  "biome": 2, "condition": "streak_50",     "reward_gold": 1200, "color": (180, 80, 80)},
    "wasteland_gold":  {"name": "Столп Пустоши",    "desc": "Собрать 5000 золота в Пустоши",   "biome": 3, "condition": "gold_5000",     "reward_gold": 2000, "color": (130, 130, 100)},
    "global_level":    {"name": "Столп Славы",      "desc": "Достичь 30 уровня за один ран",   "biome": -1, "condition": "level_30",     "reward_gold": 1500, "color": (255, 215, 0)},
}


# === C3: RUNE SOCKETING ===
RUNE_DEFS = {
    "fire": {"name": "Руна огня", "desc": "Горение: 2% урона/сек на 3с", "color": (255, 100, 50), "type": "burn"},
    "ice": {"name": "Руна льда", "desc": "Замедление: -30% скорости на 2с", "color": (120, 200, 255), "type": "slow"},
    "lightning": {"name": "Руна молнии", "desc": "Цепь: урон по 2 доп. целям", "color": (255, 255, 100), "type": "chain"},
    "holy": {"name": "Святая руна", "desc": "+50% урон по нежити", "color": (255, 255, 200), "type": "holy"},
    "shadow": {"name": "Руна тени", "desc": "Вампиризм: 5% урона", "color": (150, 80, 200), "type": "lifesteal"},
}
RUNE_SLOT_LEVELS = [1, 5, 8]  # Weapon levels that unlock rune slots (3 slots per weapon)
RUNE_TYPES = list(RUNE_DEFS.keys())  # For random selection


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

