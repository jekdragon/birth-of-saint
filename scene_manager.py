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
        self.fade = None  # FadeManager (опционально)
    
    def register(self, name: str, scene: Scene):
        """Регистрирует сцену."""
        self.scenes[name] = scene
    
    def switch(self, name: str, **kwargs):
        """Переключает на сцену. kwargs передаются в enter()."""
        self._transition_queue.append(name)
        self._transition_kwargs = kwargs
    
    def push_overlay(self, overlay: OverlayScene, **kwargs):
        """Показывает оверлей поверх текущей сцены."""
        if self.current:
            overlay.set_background(self.scenes[self.current])
        self.overlay = overlay
        overlay.enter(**kwargs)
    
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
        
        # Special: "__pause__" = открыть паузу после settings
        if name == "__pause__":
            from scenes import PauseOverlay
            pause = PauseOverlay()
            current_scene = self.scenes.get(self.current)
            game = getattr(current_scene, 'game', None) if current_scene else None
            self.push_overlay(pause, game=game)
            self._transition_kwargs = {}
            return
        
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
            if result == "__overlay__":
                self.pop_overlay()
            elif result:
                self.pop_overlay()
                self.switch(result)
            return True
        
        # Основная сцена (ARCH-4: адаптер для handle_event/handle_events)
        if self.current:
            scene = self.scenes[self.current]
            if hasattr(scene, 'handle_events'):
                result = scene.handle_events(events)
            else:
                # Адаптер: вызываем handle_event для каждого события
                result = None
                for event in events:
                    result = scene.handle_event(event)
                    if result:
                        break
            if result == "__quit__":
                return False
            elif result == "__pause__":
                # Создаём и показываем оверлей паузы
                from scenes import PauseOverlay
                pause = PauseOverlay()
                # Передаём game из GameScene
                current_scene = self.scenes[self.current]
                game = getattr(current_scene, 'game', None)
                self.push_overlay(pause, game=game)
            elif isinstance(result, tuple) and len(result) == 2:
                # (scene_name, kwargs) — передаём параметры в switch
                name, kwargs = result
                self.switch(name, **kwargs)
            elif result:
                self.switch(result)
        
        return True
    
    def update(self, dt: float):
        """Обновляет текущую сцену (и оверлей)."""
        if self.fade:
            self.fade.update(dt)
        self._do_transition()
        
        if self.overlay:
            self.overlay.update(dt)
        elif self.current:
            self.scenes[self.current].update(dt)
    
    def draw(self, screen: pygame.Surface):
        """Рисует текущую сцену (и оверлей)."""
        if self.overlay:
            self.overlay.draw(screen)
        elif self.current:
            self.scenes[self.current].draw(screen)
        
        # Fade overlay поверх всего
        if self.fade:
            self.fade.draw(screen)
