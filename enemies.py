"""
Рождение святого — Enemies
Типы врагов, спавн, AI, урон.
"""
import math
import pygame
from config import WHITE, RED, DARK_RED, YELLOW, PURPLE, ICE_BLUE

ENEMY_TYPES = {
    "neophyte": {
        "name": "Неофит",
        "unlock_wave": 1,
        "hp_base": 11, "hp_per_wave": 3,
        "speed_base": 1.5, "speed_per_wave": 0.10,
        "damage": 0.8, "xp": 4, "score": 10,
        "radius": 17, "color": RED, "blood_color": DARK_RED,
    },
    "acolyte": {
        "name": "Акролит",
        "unlock_wave": 3,
        "hp_base": 7, "hp_per_wave": 2,
        "speed_base": 2.9, "speed_per_wave": 0.08,
        "damage": 0.5, "xp": 3, "score": 12,
        "radius": 12, "color": (255, 130, 130), "blood_color": DARK_RED,
    },
    "heretic": {
        "name": "Еретик",
        "unlock_wave": 4,
        "hp_base": 38, "hp_per_wave": 7,
        "speed_base": 1.05, "speed_per_wave": 0.04,
        "damage": 1.3, "xp": 9, "score": 28,
        "radius": 26, "color": (140, 55, 55), "blood_color": (110, 35, 35),
    },
    "demon": {
        "name": "Демон",
        "unlock_wave": 5,
        "hp_base": 14, "hp_per_wave": 2.5,
        "speed_base": 1.7, "speed_per_wave": 0.05,
        "damage": 0.6, "xp": 6, "score": 15,
        "radius": 14, "color": (120, 80, 160), "blood_color": (120, 80, 160),
        "shoot_range": 300, "shoot_cd": 1.5,
    },
    "fanatic": {
        "name": "Фанатик",
        "unlock_wave": 5,
        "hp_base": 8, "hp_per_wave": 1.5,
        "speed_base": 2.4, "speed_per_wave": 0.07,
        "damage": 0, "xp": 7, "score": 18,
        "radius": 16, "color": YELLOW, "blood_color": (255, 120, 60),
        "explode_radius": 60, "explode_damage": 3.0,
    },
    "antichrist": {
        "name": "Антихрист",
        "unlock_wave": 3,
        "hp_base": 180, "hp_per_wave": 70,
        "speed_base": 1.3, "speed_per_wave": 0,
        "damage": 1.5, "xp": 25, "score": 250,
        "radius": 38, "color": PURPLE, "blood_color": (220, 80, 220),
        "is_boss": True,
    },
}


class Enemy:
    def __init__(self, type_id: str, x: float, y: float, wave: int):
        t = ENEMY_TYPES[type_id]
        self.type_id = type_id
        self.pos = pygame.Vector2(x, y)
        self.hp = t["hp_base"] + t["hp_per_wave"] * wave
        self.max_hp = self.hp
        self.speed = t["speed_base"] + t["speed_per_wave"] * wave
        self.damage = t["damage"]
        self.xp = t["xp"]
        self.score = t["score"]
        self.radius = t["radius"]
        self.color = t["color"]
        self.blood_color = t["blood_color"]
        self.is_boss = t.get("is_boss", False)

        # Demon ranged attack
        self.shoot_range = t.get("shoot_range", 0)
        self.shoot_cd = t.get("shoot_cd", 0)
        self.shoot_timer = 0.0

        # Fanatic explode
        self.explode_radius = t.get("explode_radius", 0)
        self.explode_damage = t.get("explode_damage", 0)

        self.alive = True
        self.hit_flash = 0.0

    def take_damage(self, amount: float) -> bool:
        """Возвращает True если враг умер."""
        self.hp -= amount
        self.hit_flash = 0.1
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def update(self, player_pos: pygame.Vector2, dt: float):
        if not self.alive:
            return

        # Движение к игроку
        d = player_pos - self.pos
        if d.length() > 0:
            d = d.normalize()
            self.pos += d * self.speed * 60 * dt

        # Hit flash
        if self.hit_flash > 0:
            self.hit_flash -= dt

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, font=None):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)

        if sx < -50 or sx > 1074 or sy < -50 or sy > 818:
            return

        # Цвет при ударе
        color = WHITE if self.hit_flash > 0 else self.color

        # Тело
        pygame.draw.circle(surface, color, (sx, sy), self.radius)
        pygame.draw.circle(surface, WHITE, (sx, sy), self.radius, 1)

        # HP-бар (для боссов и если урон получен)
        if self.is_boss or self.hp < self.max_hp:
            bar_w = self.radius * 2
            bar_h = 4
            bar_x = sx - bar_w // 2
            bar_y = sy - self.radius - 8
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(surface, (60, 20, 20), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, RED, (bar_x, bar_y, int(bar_w * ratio), bar_h))

        # Имя босса
        if self.is_boss and font:
            name_text = font.render(ENEMY_TYPES[self.type_id]["name"], True, PURPLE)
            surface.blit(name_text, (sx - name_text.get_width() // 2, sy - self.radius - 20))
