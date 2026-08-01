"""
Рождение святого - Map: Собор
Вторая карта: узкие коридоры, залы, колонны.
Отличается от Арены тем, что препятствия образуют структуру.
"""
import random
import math
import pygame
from config import CENTER_X, CENTER_Y


# Цвета Собора
CATHEDRAL_COLORS = {
    "bg": (15, 12, 20),
    "grid": (30, 25, 40),
    "wall": (50, 40, 60),
    "column": (70, 60, 85),
    "altar": (120, 90, 50),
    "pew": (60, 45, 35),
}

# Типы препятствий Собора
CATHEDRAL_OBSTACLES = {
    "wall_h":    {"w": 128, "h": 16, "color": "wall"},
    "wall_v":    {"w": 16, "h": 128, "color": "wall"},
    "column":    {"w": 24, "h": 24, "color": "column", "circle": True},
    "altar":     {"w": 64, "h": 32, "color": "altar"},
    "pew":       {"w": 48, "h": 16, "color": "pew"},
}


class CathedralObstacle:
    """Препятствие на карте Собора."""
    def __init__(self, x: float, y: float, type_id: str):
        self.pos = pygame.Vector2(x, y)
        t = CATHEDRAL_OBSTACLES[type_id]
        self.width = t["w"]
        self.height = t["h"]
        self.color = CATHEDRAL_COLORS[t["color"]]
        self.type_id = type_id
        self.is_circle = t.get("circle", False)
        self.radius = max(self.width, self.height) // 2

    def collides_with(self, pos: pygame.Vector2, obj_radius: float) -> bool:
        """Проверяет коллизию с объектом."""
        if self.is_circle:
            dx = self.pos.x - pos.x
            dy = self.pos.y - pos.y
            dist = math.sqrt(dx * dx + dy * dy)
            return dist < self.radius + obj_radius
        else:
            # AABB коллизия
            closest_x = max(self.pos.x - self.width/2, min(pos.x, self.pos.x + self.width/2))
            closest_y = max(self.pos.y - self.height/2, min(pos.y, self.pos.y + self.height/2))
            dx = pos.x - closest_x
            dy = pos.y - closest_y
            return (dx*dx + dy*dy) < (obj_radius * obj_radius)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)
        if sx < -200 or sx > 1224 or sy < -200 or sy > 968:
            return
        if self.is_circle:
            pygame.draw.circle(surface, self.color, (sx, sy), self.radius)
        else:
            rect = pygame.Rect(sx - self.width//2, sy - self.height//2, self.width, self.height)
            pygame.draw.rect(surface, self.color, rect)


def generate_cathedral() -> list:
    """Генерирует структуру Собора."""
    obstacles = []
    cx, cy = CENTER_X, CENTER_Y

    # Главный зал (центр) - 4 колонны по углам
    for dx, dy in [(-200, -200), (200, -200), (-200, 200), (200, 200)]:
        obstacles.append(CathedralObstacle(cx + dx, cy + dy, "column"))

    # Алтарь (северная стена)
    obstacles.append(CathedralObstacle(cx, cy - 300, "altar"))

    # Коридоры (4 направления)
    # Северный коридор
    for i in range(3):
        obstacles.append(CathedralObstacle(cx - 80, cy - 350 - i*100, "wall_v"))
        obstacles.append(CathedralObstacle(cx + 80, cy - 350 - i*100, "wall_v"))

    # Южный коридор
    for i in range(3):
        obstacles.append(CathedralObstacle(cx - 80, cy + 350 + i*100, "wall_v"))
        obstacles.append(CathedralObstacle(cx + 80, cy + 350 + i*100, "wall_v"))

    # Западный коридор
    for i in range(3):
        obstacles.append(CathedralObstacle(cx - 350 - i*100, cy - 80, "wall_h"))
        obstacles.append(CathedralObstacle(cx - 350 - i*100, cy + 80, "wall_h"))

    # Восточный коридор
    for i in range(3):
        obstacles.append(CathedralObstacle(cx + 350 + i*100, cy - 80, "wall_h"))
        obstacles.append(CathedralObstacle(cx + 350 + i*100, cy + 80, "wall_h"))

    # Боковые залы (боковые капеллы)
    for side_x in [-600, 600]:
        # Стены капелл
        obstacles.append(CathedralObstacle(cx + side_x, cy - 150, "wall_h"))
        obstacles.append(CathedralObstacle(cx + side_x, cy + 150, "wall_h"))
        obstacles.append(CathedralObstacle(cx + side_x - 100, cy, "wall_v"))
        obstacles.append(CathedralObstacle(cx + side_x + 100, cy, "wall_v"))
        # Колонна в центре капеллы
        obstacles.append(CathedralObstacle(cx + side_x, cy, "column"))

    # Скамьи (pews) в главном зале
    for i in range(4):
        y_off = -100 + i * 60
        obstacles.append(CathedralObstacle(cx - 60, cy + y_off, "pew"))
        obstacles.append(CathedralObstacle(cx + 60, cy + y_off, "pew"))

    return obstacles


def get_cathedral_biome(player_x: float, player_y: float) -> dict:
    """Биом Собора - единый стиль."""
    return {
        "name": "Собор",
        "bg": CATHEDRAL_COLORS["bg"],
        "grid": CATHEDRAL_COLORS["grid"],
    }
