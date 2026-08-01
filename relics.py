"""
Рождение святого - Relics System
Реликвии: пассивные бонусы, которые появляются на карте раз в 60 секунд.
Максимум 3 активных реликвий одновременно.
"""
import random
import math
import pygame
from config import MAP_WIDTH, MAP_HEIGHT, WHITE, GOLD, RED, BLUE, PURPLE, ICE_BLUE, YELLOW


# === ОПРЕДЕЛЕНИЯ РЕЛИКВИЙ ===

RELIC_DEFS = {
    "holy_grail": {
        "name": "Священный Грааль",
        "desc": "+20% к урону",
        "bonuses": {"damage": 0.20},
        "color": GOLD,
        "radius": 8,
        "glyph": "G",
    },
    "cross_fragment": {
        "name": "Фрагмент Креста",
        "desc": "+1 снаряд",
        "bonuses": {"projectile": 1},
        "color": (255, 255, 200),
        "radius": 8,
        "glyph": "✝",
    },
    "prayer_beads": {
        "name": "Чётки",
        "desc": "+0.5 HP/сек регенерация",
        "bonuses": {"regen": 0.5},
        "color": (180, 140, 255),
        "radius": 8,
        "glyph": "◯",
    },
    "sacred_shield": {
        "name": "Священный Щит",
        "desc": "+50 макс. HP",
        "bonuses": {"max_hp": 50},
        "color": ICE_BLUE,
        "radius": 8,
        "glyph": "⛨",
    },
    "golden_chalice": {
        "name": "Золотая Чаша",
        "desc": "+30% золота",
        "bonuses": {"gold": 0.30},
        "color": YELLOW,
        "radius": 8,
        "glyph": "U",
    },
    "angel_feather": {
        "name": "Перо Ангела",
        "desc": "+15% скорости",
        "bonuses": {"speed": 0.15},
        "color": (200, 230, 255),
        "radius": 8,
        "glyph": "↑",
    },
    "demon_horn": {
        "name": "Рог Демона",
        "desc": "+25% области",
        "bonuses": {"area": 0.25},
        "color": RED,
        "radius": 8,
        "glyph": "⦿",
    },
    "blessed_ring": {
        "name": "Благословенное Кольцо",
        "desc": "-20% кулдаун",
        "bonuses": {"cooldown": 0.20},
        "color": PURPLE,
        "radius": 8,
        "glyph": "◎",
    },
}

RELIC_IDS = list(RELIC_DEFS.keys())

# Константы
RELIC_SPAWN_INTERVAL = 60.0  # каждые 60 секунд
MAX_ACTIVE_RELICS = 3
RELIC_LIFETIME = 15.0  # исчезает через 15 секунд если не подобрали
RELIC_PICKUP_RANGE = 40.0  # дистанция подбора
RELIC_ATTRACT_SPEED = 5.0  # скорость притяжения к игроку


class Relic:
    """Реликвия на земле."""

    def __init__(self, relic_id: str, x: float, y: float):
        self.relic_id = relic_id
        self.defn = RELIC_DEFS[relic_id]
        self.pos = pygame.Vector2(x, y)
        self.alive = True
        self.collected = False
        self.lifetime = RELIC_LIFETIME
        self.age = 0.0
        self.attracting = False

        # Визуальные данные
        self.color = self.defn["color"]
        self.radius = self.defn["radius"]
        self.glyph = self.defn["glyph"]

        # Анимация мерцания
        self.pulse_phase = random.uniform(0, 2 * math.pi)

    def update(self, player_pos: pygame.Vector2, dt: float):
        if not self.alive:
            return

        self.age += dt
        self.pulse_phase += dt * 3.0  # пульсация

        # Истечение времени - реликвия исчезает
        if self.age >= self.lifetime:
            self.alive = False
            return

        # Притяжение когда игрок рядом
        dist = (self.pos - player_pos).length()
        if dist < RELIC_PICKUP_RANGE:
            self.attracting = True

        if self.attracting:
            d = player_pos - self.pos
            if d.length() > 0:
                self.pos += d.normalize() * RELIC_ATTRACT_SPEED * 60 * dt
            if dist < 8:
                self.collected = True
                self.alive = False

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        if not self.alive:
            return

        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)

        # Off-screen skip
        if sx < -30 or sx > 1054 or sy < -30 or sy > 798:
            return

        # Пульсация радиуса
        pulse = math.sin(self.pulse_phase) * 2
        r = self.radius + max(0, pulse)

        # Glow
        glow_r = int(r * 3)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        cr, cg, cb = self.color
        alpha = int(60 + 30 * math.sin(self.pulse_phase))
        pygame.draw.circle(glow, (cr, cg, cb, alpha), (glow_r, glow_r), glow_r)
        surface.blit(glow, (sx - glow_r, sy - glow_r))

        # Внешний круг (пульсирующий)
        pygame.draw.circle(surface, self.color, (sx, sy), int(r), 2)

        # Внутренняя заливка
        inner_r = max(3, int(r * 0.6))
        inner_color = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.circle(surface, inner_color, (sx, sy), inner_r)

        # Глиф
        try:
            font = pygame.font.Font(None, 18)
            glyph_surf = font.render(self.glyph, True, WHITE)
            surface.blit(glyph_surf, (sx - glyph_surf.get_width() // 2, sy - glyph_surf.get_height() // 2))
        except Exception:
            pass  # если шрифт недоступен


class RelicManager:
    """Управляет появлением и отслеживанием реликвий на карте."""

    def __init__(self):
        self.relics = []         # активные реликвии на земле
        self.spawn_timer = 0.0   # таймер до следующего спавна
        self.total_spawned = 0
        self.first_spawn_delay = 30.0  # первая реликвия через 30 сек
        self._spawned_first = False

    def reset(self):
        """Сброс при старте новой игры."""
        self.relics = []
        self.spawn_timer = 0.0
        self.total_spawned = 0
        self._spawned_first = False

    def spawn_relic(self, player_pos: pygame.Vector2):
        """Спавнит случайную реликвию на карте."""
        # Выбираем случайную ID
        rid = random.choice(RELIC_IDS)

        # Спавним на случайном расстоянии от игрока
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(200, 500)  # не слишком близко, не слишком далеко
        x = player_pos.x + math.cos(angle) * dist
        y = player_pos.y + math.sin(angle) * dist
        x = max(50, min(MAP_WIDTH - 50, x))
        y = max(50, min(MAP_HEIGHT - 50, y))

        relic = Relic(rid, x, y)
        self.relics.append(relic)
        self.total_spawned += 1
        return relic

    def update(self, dt: float, current_relic_count: int, player_pos: pygame.Vector2):
        """Обновляет таймер спавна реликвий. Возвращает новую реликвию или None."""
        # Не спавним если уже макс
        if current_relic_count >= MAX_ACTIVE_RELICS:
            self.spawn_timer = min(self.spawn_timer + dt, RELIC_SPAWN_INTERVAL)
            return None

        self.spawn_timer += dt
        threshold = self.first_spawn_delay if not self._spawned_first else RELIC_SPAWN_INTERVAL
        if self.spawn_timer >= threshold:
            self.spawn_timer = 0.0
            self._spawned_first = True
            return self.spawn_relic(player_pos)

        return None

    def get_active_count(self) -> int:
        """Количество живых реликвий на земле."""
        return len([r for r in self.relics if r.alive])

    def clean_up(self):
        """Удаляет мёртвые реликвии."""
        self.relics = [r for r in self.relics if r.alive]