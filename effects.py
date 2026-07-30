"""
Рождение святого — Visual Effects
Screen shake, flash, grid rendering.
"""
import pygame
import random
from config import WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, DARK_BG, GRID_COLOR


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


def draw_grid(surface: pygame.Surface, cam_x: float, cam_y: float):
    """Рисует фоновую сетку."""
    surface.fill(DARK_BG)

    # Видимые тайлы
    start_col = int(cam_x // TILE_SIZE)
    start_row = int(cam_y // TILE_SIZE)
    end_col = start_col + WIDTH // TILE_SIZE + 2
    end_row = start_row + HEIGHT // TILE_SIZE + 2

    for col in range(start_col, end_col + 1):
        x = int(col * TILE_SIZE - cam_x)
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))

    for row in range(start_row, end_row + 1):
        y = int(row * TILE_SIZE - cam_y)
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))
