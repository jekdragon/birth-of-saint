"""
Рождение святого - Fade Transition
Плавные fade-in/fade-out переходы между экранами.
"""
import pygame
from config import WIDTH, HEIGHT


class FadeManager:
    """Управляет fade-переходами между экранами."""
    
    def __init__(self):
        self.active = False
        self.timer = 0.0
        self.duration = 0.3  # секунд
        self.phase = "none"  # "none", "out", "in"
        self.alpha = 0
        self.color = (0, 0, 0)
        self._callback = None
    
    def fade_out(self, duration=0.3, color=(0, 0, 0), callback=None):
        """Начинает fade-out. callback вызывается после завершения."""
        self.active = True
        self.timer = 0.0
        self.duration = duration
        self.phase = "out"
        self.alpha = 0
        self.color = color
        self._callback = callback
    
    def fade_in(self, duration=0.3, color=(0, 0, 0)):
        """Начинает fade-in (от чёрного к прозрачному)."""
        self.active = True
        self.timer = 0.0
        self.duration = duration
        self.phase = "in"
        self.alpha = 255
        self.color = color
        self._callback = None
    
    def update(self, dt):
        if not self.active:
            return
        
        self.timer += dt
        t = min(1.0, self.timer / self.duration)
        
        if self.phase == "out":
            self.alpha = int(255 * t)
            if t >= 1.0:
                self.alpha = 255
                if self._callback:
                    self._callback()
                    self._callback = None
                # Автоматически начинаем fade-in
                self.phase = "in"
                self.timer = 0.0
        elif self.phase == "in":
            self.alpha = int(255 * (1.0 - t))
            if t >= 1.0:
                self.alpha = 0
                self.active = False
                self.phase = "none"
    
    def draw(self, surface):
        if not self.active or self.alpha <= 0:
            return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*self.color, self.alpha))
        surface.blit(overlay, (0, 0))
    
    @property
    def is_fading(self):
        return self.active
