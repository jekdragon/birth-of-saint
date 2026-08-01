"""
Рождение святого - Scene Manager
Базовые классы для управления экранами.
"""
import pygame
from typing import Optional


class Scene:
    """Базовый класс для всех экранов."""
    
    def __init__(self):
        self.next_scene: Optional[str] = None  # имя следующей сцены
        self.done = False  # сцена завершена
    
    def enter(self, **kwargs):
        """Вызывается при входе в сцену. kwargs - данные от предыдущей сцены."""
        self.done = False
        self.next_scene = None
    
    def exit(self):
        """Вызывается при выходе из сцены."""
        pass
    
    def handle_events(self, events: list) -> Optional[str]:
        """Обработка ввода. Возвращает имя следующей сцены или None."""
        return None
    
    def update(self, dt: float):
        """Логика обновления."""
        pass
    
    def draw(self, screen: pygame.Surface):
        """Рендер."""
        pass


class OverlayScene(Scene):
    """Сцена-оверлей поверх другой сцены. Не заменяет предыдущую сцену."""
    
    def __init__(self):
        super().__init__()
        self.background_scene: Optional[Scene] = None
    
    def set_background(self, scene: Scene):
        """Устанавливает сцену на заднем плане."""
        self.background_scene = scene
    
    def draw_background(self, screen: pygame.Surface):
        """Рисует фоновую сцену."""
        if self.background_scene:
            self.background_scene.draw(screen)


class SceneManager:
    """Менеджер сцен. Управляет переходами между экранами."""
    
    def __init__(self):
        self.scenes: dict[str, Scene] = {}
        self.current: Optional[str] = None
        self.overlay: Optional[OverlayScene] = None
        self._transition_queue: list[str] = []
        self._transition_kwargs: dict = {}
    
    def register(self, name: str, scene: Scene):
        """Регистрирует сцену."""
        self.scenes[name] = scene
    
    def switch(self, name: str, **kwargs):
        """Переключает на сцену. kwargs передаются в enter()."""
        self._transition_queue.append(name)
        self._transition_kwargs = kwargs
    
    def push_overlay(self, overlay: OverlayScene):
        """Показывает оверлей поверх текущей сцены."""
        if self.current:
            overlay.set_background(self.scenes[self.current])
        self.overlay = overlay
        overlay.enter()
    
    def pop_overlay(self):
        """Закрывает оверлей."""
        if self.overlay:
            self.overlay.exit()
            self.overlay = None
    
    def _do_transition(self):
        """Выполняет отложенные переходы."""
        if not self._transition_queue:
            return
        
        name = self._transition_queue.pop(0)
        if name not in self.scenes:
            return
        
        # Закрываем оверлей при смене сцены
        if self.overlay:
            self.pop_overlay()
        
        # Выходим из текущей сцены
        if self.current and self.current in self.scenes:
            self.scenes[self.current].exit()
        
        # Входим в новую
        self.current = name
        self.scenes[self.current].enter(**self._transition_kwargs)
        self._transition_kwargs = {}
    
    def handle_events(self, events: list) -> bool:
        """
        Обрабатывает события. Возвращает False для выхода из игры.
        """
        for event in events:
            if event.type == pygame.QUIT:
                return False
        
        # Оверлей получает приоритет
        if self.overlay:
            result = self.overlay.handle_events(events)
            if result:
                self.pop_overlay()
                if result != "__overlay__":
                    self.switch(result)
            return True
        
        # Основная сцена
        if self.current:
            result = self.scenes[self.current].handle_events(events)
            if result:
                self.switch(result)
        
        return True
    
    def update(self, dt: float):
        """Обновляет текущую сцену (и оверлей)."""
        self._do_transition()
        
        if self.overlay:
            self.overlay.update(dt)
        elif self.current:
            self.scenes[self.current].update(dt)
    
    def draw(self, screen: pygame.Surface):
        """Рисует текущую сцену (и оверлей)."""
        if self.overlay:
            # Оверлей сам рисует фон
            self.overlay.draw(screen)
        elif self.current:
            self.scenes[self.current].draw(screen)
