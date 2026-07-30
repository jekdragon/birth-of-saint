"""
Рождение святого - Camera
Камера следит за игроком, скроллит карту.
"""
from config import WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, target_x: float, target_y: float):
        """Следит за целевой позицией (игрок)."""
        self.x = target_x - WIDTH // 2
        self.y = target_y - HEIGHT // 2

        # Ограничение картой
        self.x = max(0, min(MAP_WIDTH - WIDTH, self.x))
        self.y = max(0, min(MAP_HEIGHT - HEIGHT, self.y))

    @property
    def cam_x(self) -> float:
        return self.x

    @property
    def cam_y(self) -> float:
        return self.y
