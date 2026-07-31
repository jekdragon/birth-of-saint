"""
Рождение святого - Visual Effects
Screen shake, flash, grid rendering.
"""
import pygame
import random
import math
from config import WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, BIOMES, CENTER_X, CENTER_Y


class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.timer = 0.0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, intensity: int, duration: float = 0.2):
        self.intensity = intensity
        self.timer = duration

    def update(self, dt: float):
        if self.timer > 0:
            self.timer -= dt
            self.offset_x = random.randint(-self.intensity, self.intensity)
            self.offset_y = random.randint(-self.intensity, self.intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0
            self.intensity = 0


class ScreenFlash:
    def __init__(self):
        self.timer = 0.0
        self.color = (255, 0, 0)

    def trigger(self, color=(255, 0, 0), duration=0.15):
        self.color = color
        self.timer = duration

    def update(self, dt: float):
        if self.timer > 0:
            self.timer -= dt

    def draw(self, surface: pygame.Surface):
        if self.timer > 0:
            alpha = int(80 * (self.timer / 0.15))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((*self.color, alpha))
            surface.blit(overlay, (0, 0))


def get_biome(player_x: float, player_y: float) -> dict:
    """Определяет биом по расстоянию от центра карты."""
    dx = player_x - CENTER_X
    dy = player_y - CENTER_Y
    dist = math.sqrt(dx * dx + dy * dy)
    for biome in BIOMES:
        if dist < biome["radius"]:
            return biome
    return BIOMES[-1]  # Пустошь (крайний)


def draw_grid(surface: pygame.Surface, cam_x: float, cam_y: float,
              player_x: float = None, player_y: float = None):
    """Рисует фоновую сетку с учётом биома."""
    # Определяем биом
    if player_x is not None and player_y is not None:
        biome = get_biome(player_x, player_y)
    else:
        biome = BIOMES[0]

    bg_color = biome["bg"]
    grid_color = biome["grid"]

    surface.fill(bg_color)

    # Видимые тайлы
    start_col = int(cam_x // TILE_SIZE)
    start_row = int(cam_y // TILE_SIZE)
    end_col = start_col + WIDTH // TILE_SIZE + 2
    end_row = start_row + HEIGHT // TILE_SIZE + 2

    for col in range(start_col, end_col + 1):
        x = int(col * TILE_SIZE - cam_x)
        pygame.draw.line(surface, grid_color, (x, 0), (x, HEIGHT))

    for row in range(start_row, end_row + 1):
        y = int(row * TILE_SIZE - cam_y)
        pygame.draw.line(surface, grid_color, (0, y), (WIDTH, y))


class LowHPVignette:
    """Красная пульсирующая vignette при низком HP."""
    def __init__(self):
        self.active = False
        self.intensity = 0.0

    def update(self, hp_ratio: float, dt: float):
        """hp_ratio = hp / max_hp (0.0 - 1.0)."""
        if hp_ratio < 0.25:
            self.active = True
            # Пульсация
            import math
            t = pygame.time.get_ticks() / 1000.0
            pulse = (math.sin(t * 4.0) + 1.0) * 0.5  # 0..1
            self.intensity = (1.0 - hp_ratio / 0.25) * (0.3 + pulse * 0.2)
        else:
            self.active = False
            self.intensity = 0.0

    def draw(self, surface: pygame.Surface):
        if not self.active or self.intensity <= 0:
            return
        alpha = int(80 * self.intensity)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((200, 0, 0, alpha))
        surface.blit(overlay, (0, 0))
