"""
Рождение святого — Wave Manager
Система волн: спавн врагов, нарастающая сложность, map events.
"""
import random
import math
import pygame
from config import WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT, SPAWN_DISTANCE, WAVE_DURATION, BOSS_EVERY_N_WAVES, MAX_ENEMIES, CENTER_X, CENTER_Y
from enemies import Enemy, ENEMY_TYPES


# Map events — привязаны к конкретным секундам внутри волны
MAP_EVENTS = [
    {"wave": 6,  "time": 10, "type": "swarm",    "count": 50, "desc": "Рой"},
    {"wave": 8,  "time": 5,  "type": "surround",  "count": 30, "desc": "Окружение"},
    {"wave": 10, "time": 15, "type": "elite",     "count": 1,  "desc": "Элита"},
    {"wave": 12, "time": 10, "type": "swarm",    "count": 80, "desc": "Большой рой"},
    {"wave": 15, "time": 5,  "type": "surround",  "count": 50, "desc": "Окружение"},
    {"wave": 18, "time": 10, "type": "elite",     "count": 3,  "desc": "Элиты"},
    {"wave": 20, "time": 5,  "type": "swarm",    "count": 100,"desc": "Орда"},
    {"wave": 25, "time": 5,  "type": "surround",  "count": 80, "desc": "Адское кольцо"},
]


class WaveManager:
    def __init__(self):
        self.wave = 1
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        self.min_enemies_per_wave = 5
        self.boss_alive = False
        self.next_boss_wave = BOSS_EVERY_N_WAVES
        self.triggered_events = set()  # (wave, time) уже сработавшие

    def get_unlocked_types(self):
        """Возвращает типы врагов, доступные на текущей волне."""
        return [tid for tid, t in ENEMY_TYPES.items()
                if t["unlock_wave"] <= self.wave and not t.get("is_boss")]

    def spawn_enemy(self, wave: int, cam_x: float, cam_y: float) -> Enemy:
        """Спавнит врага за экраном."""
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x = cam_x + random.randint(0, WIDTH)
            y = cam_y - SPAWN_DISTANCE
        elif side == "bottom":
            x = cam_x + random.randint(0, WIDTH)
            y = cam_y + HEIGHT + SPAWN_DISTANCE
        elif side == "left":
            x = cam_x - SPAWN_DISTANCE
            y = cam_y + random.randint(0, HEIGHT)
        else:
            x = cam_x + WIDTH + SPAWN_DISTANCE
            y = cam_y + random.randint(0, HEIGHT)

        # Ограничение карты
        x = max(0, min(MAP_WIDTH, x))
        y = max(0, min(MAP_HEIGHT, y))

        # Выбор типа врага
        types = self.get_unlocked_types()
        if not types:
            types = ["neophyte"]

        r = random.random()
        type_id = "neophyte"

        if self.wave >= 5 and r < 0.10:
            type_id = "fanatic"
        elif self.wave >= 5 and r < 0.25:
            type_id = "demon"
        elif self.wave >= 3 and r < 0.40:
            type_id = "acolyte"
        elif self.wave >= 4 and r < 0.55:
            type_id = "heretic"
        else:
            type_id = "neophyte"

        return Enemy(type_id, x, y, wave)

    def spawn_boss(self, cam_x: float, cam_y: float) -> Enemy:
        """Спавнит босса."""
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x = cam_x + WIDTH // 2
            y = cam_y - SPAWN_DISTANCE * 2
        elif side == "bottom":
            x = cam_x + WIDTH // 2
            y = cam_y + HEIGHT + SPAWN_DISTANCE * 2
        elif side == "left":
            x = cam_x - SPAWN_DISTANCE * 2
            y = cam_y + HEIGHT // 2
        else:
            x = cam_x + WIDTH + SPAWN_DISTANCE * 2
            y = cam_y + HEIGHT // 2

        self.boss_alive = True
        return Enemy("antichrist", x, y, self.wave)

    def spawn_event_swarm(self, count: int, cam_x: float, cam_y: float) -> list:
        """Рой — много врагов с одной стороны."""
        enemies = []
        side = random.choice(["top", "bottom", "left", "right"])
        for _ in range(count):
            if side == "top":
                x = cam_x + random.randint(0, WIDTH)
                y = cam_y - random.randint(10, 80)
            elif side == "bottom":
                x = cam_x + random.randint(0, WIDTH)
                y = cam_y + HEIGHT + random.randint(10, 80)
            elif side == "left":
                x = cam_x - random.randint(10, 80)
                y = cam_y + random.randint(0, HEIGHT)
            else:
                x = cam_x + WIDTH + random.randint(10, 80)
                y = cam_y + random.randint(0, HEIGHT)
            x = max(0, min(MAP_WIDTH, x))
            y = max(0, min(MAP_HEIGHT, y))
            enemies.append(Enemy("neophyte", x, y, self.wave))
        return enemies

    def spawn_event_surround(self, count: int, player_pos: pygame.Vector2) -> list:
        """Окружение — враги кольцом вокруг игрока."""
        enemies = []
        for i in range(count):
            angle = (2 * math.pi / count) * i
            r = 300 + random.randint(0, 100)
            x = player_pos.x + math.cos(angle) * r
            y = player_pos.y + math.sin(angle) * r
            x = max(0, min(MAP_WIDTH, x))
            y = max(0, min(MAP_HEIGHT, y))
            enemies.append(Enemy("neophyte", x, y, self.wave))
        return enemies

    def spawn_event_elite(self, count: int, cam_x: float, cam_y: float) -> list:
        """Элита — усиленные враги."""
        enemies = []
        for _ in range(count):
            e = self.spawn_enemy(self.wave, cam_x, cam_y)
            e.hp *= 3
            e.max_hp *= 3
            e.damage *= 2
            e.xp *= 5
            e.radius = int(e.radius * 1.3)
            e.color = (255, 215, 0)  # золотой — маркер элиты
            enemies.append(e)
        return enemies

    def update(self, dt: float, enemy_count: int, cam_x: float, cam_y: float,
               player_pos: pygame.Vector2 = None):
        """Обновляет волну. Возвращает список новых врагов."""
        new_enemies = []
        self.wave_timer += dt

        # Переход на следующую волну
        if self.wave_timer >= WAVE_DURATION:
            self.wave_timer = 0
            self.wave += 1
            self.min_enemies_per_wave = 5 + self.wave * 2
            self.spawn_interval = max(0.2, 1.0 - self.wave * 0.02)

        # Босс
        if (self.wave == self.next_boss_wave and not self.boss_alive and
                self.wave_timer < 1.0):
            new_enemies.append(self.spawn_boss(cam_x, cam_y))
            self.next_boss_wave += BOSS_EVERY_N_WAVES

        # Спавн обычных врагов
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            if enemy_count < MAX_ENEMIES:
                new_enemies.append(self.spawn_enemy(self.wave, cam_x, cam_y))

        # Map events
        for event in MAP_EVENTS:
            key = (event["wave"], event["time"])
            if (self.wave == event["wave"] and
                    int(self.wave_timer) == event["time"] and
                    key not in self.triggered_events):
                self.triggered_events.add(key)
                if event["type"] == "swarm":
                    new_enemies.extend(self.spawn_event_swarm(event["count"], cam_x, cam_y))
                elif event["type"] == "surround" and player_pos:
                    new_enemies.extend(self.spawn_event_surround(event["count"], player_pos))
                elif event["type"] == "elite":
                    new_enemies.extend(self.spawn_event_elite(event["count"], cam_x, cam_y))

        return new_enemies
