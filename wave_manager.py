"""
Рождение святого — Wave Manager
Система волн: спавн врагов, нарастающая сложность.
"""
import random
import pygame
from config import WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT, SPAWN_DISTANCE, WAVE_DURATION, BOSS_EVERY_N_WAVES, MAX_ENEMIES
from enemies import Enemy, ENEMY_TYPES


class WaveManager:
    def __init__(self):
        self.wave = 1
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0  # секунды между спавнами
        self.min_enemies_per_wave = 5
        self.boss_alive = False
        self.next_boss_wave = BOSS_EVERY_N_WAVES

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

    def update(self, dt: float, enemy_count: int, cam_x: float, cam_y: float):
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

        return new_enemies
