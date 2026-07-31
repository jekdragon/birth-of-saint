"""
Рождение святого - Obstacles
Препятствия на карте: руины, надгробия, деревья, кости.
Блокируют движение и снаряды.
"""
import random
import math
import pygame
import os
from config import MAP_WIDTH, MAP_HEIGHT, BIOMES, CENTER_X, CENTER_Y, TILE_SIZE


OBSTACLE_TYPES = {
    "column":   {"radius": 30, "color": (60, 55, 80),  "biome": 0},  # Руины
    "wall":     {"radius": 35, "color": (70, 65, 90),  "biome": 0},
    "gravestone":{"radius": 25, "color": (50, 50, 50), "biome": 1},  # Кладбище
    "cross":    {"radius": 22, "color": (60, 60, 60),  "biome": 1},
    "tree":     {"radius": 35, "color": (40, 25, 25),  "biome": 2},  # Адский лес
    "root":     {"radius": 18, "color": (50, 30, 30),  "biome": 2},
    "bone":     {"radius": 20, "color": (180, 170, 140),"biome": 3},  # Пустошь
    "skull":    {"radius": 24, "color": (160, 150, 130),"biome": 3},
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
            sprite = OBSTACLE_SPRITES.get(self.type_id)
            if sprite:
                rect = sprite.get_rect(center=(sx, sy))
                surface.blit(sprite, rect)
            else:
                pygame.draw.circle(surface, self.color, (sx, sy), self.radius)
                pygame.draw.circle(surface, (255, 255, 255), (sx, sy), self.radius, 1)


OBSTACLE_SPRITES = {}

def preload_obstacle_sprites():
    """Загрузить все спрайты препятствий при старте."""
    assets_dir = os.path.join(os.getcwd(), "assets", "obstacles")
    for tid in OBSTACLE_TYPES:
        radius = OBSTACLE_TYPES[tid]["radius"]
        size = radius * 2
        path = os.path.join(assets_dir, f"{tid}_{size}.png")
        if os.path.exists(path):
            OBSTACLE_SPRITES[tid] = pygame.image.load(path).convert_alpha()
        else:
            # Fallback на ближайший размер
            best_size = min([24, 28, 30, 32, 36, 40, 50, 60], key=lambda s: abs(s - size))
            path = os.path.join(assets_dir, f"{tid}_{best_size}.png")
            if os.path.exists(path):
                sprite = pygame.image.load(path).convert_alpha()
                OBSTACLE_SPRITES[tid] = pygame.transform.scale(sprite, (size, size))


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
