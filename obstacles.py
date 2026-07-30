"""
Рождение святого - Obstacles
Препятствия на карте: руины, надгробия, деревья, кости.
Блокируют движение и снаряды.
"""
import random
import math
import pygame
from config import MAP_WIDTH, MAP_HEIGHT, BIOMES, CENTER_X, CENTER_Y, TILE_SIZE


OBSTACLE_TYPES = {
    "column":   {"radius": 20, "color": (60, 55, 80),  "biome": 0},  # Руины
    "wall":     {"radius": 30, "color": (70, 65, 90),  "biome": 0},
    "gravestone":{"radius": 18, "color": (50, 50, 50), "biome": 1},  # Кладбище
    "cross":    {"radius": 15, "color": (60, 60, 60),  "biome": 1},
    "tree":     {"radius": 25, "color": (40, 25, 25),  "biome": 2},  # Адский лес
    "root":     {"radius": 12, "color": (50, 30, 30),  "biome": 2},
    "bone":     {"radius": 14, "color": (180, 170, 140),"biome": 3},  # Пустошь
    "skull":    {"radius": 16, "color": (160, 150, 130),"biome": 3},
}


class Obstacle:
    def __init__(self, x: float, y: float, type_id: str):
        self.pos = pygame.Vector2(x, y)
        t = OBSTACLE_TYPES[type_id]
        self.radius = t["radius"]
        self.color = t["color"]
        self.type_id = type_id

    def collides_with(self, pos: pygame.Vector2, obj_radius: float) -> bool:
        """Проверяет коллизию с объектом."""
        dx = self.pos.x - pos.x
        dy = self.pos.y - pos.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < self.radius + obj_radius

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)
        if -50 < sx < 1074 and -50 < sy < 818:
            pygame.draw.circle(surface, self.color, (sx, sy), self.radius)
            pygame.draw.circle(surface, (255, 255, 255), (sx, sy), self.radius, 1)


def generate_obstacles(count_per_biome: int = 30) -> list:
    """Генерирует препятствия для всех биомов."""
    obstacles = []
    for biome_idx, biome in enumerate(BIOMES):
        types = [tid for tid, t in OBSTACLE_TYPES.items() if t["biome"] == biome_idx]
        inner = BIOMES[biome_idx - 1]["radius"] if biome_idx > 0 else 0
        outer = biome["radius"]

        for _ in range(count_per_biome):
            # Случайная позиция в кольце биома
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(inner + 50, outer - 50)
            x = CENTER_X + math.cos(angle) * r
            y = CENTER_Y + math.sin(angle) * r

            # Не слишком близко к центру (стартовая зона)
            if math.sqrt((x - CENTER_X)**2 + (y - CENTER_Y)**2) < 200:
                continue

            type_id = random.choice(types)
            obstacles.append(Obstacle(x, y, type_id))

    return obstacles
