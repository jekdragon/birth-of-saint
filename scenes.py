"""
Рождение святого - Scenes
Конкретные сцены, обёрнутые над существующими классами.
"""
import pygame
from scene_manager import Scene, OverlayScene
from config import WIDTH, HEIGHT, DARK_BG

# Общие шрифты (ленивая инициализация)
_font_cache = {}

def _get_fonts():
    if not _font_cache:
        _font_cache['font'] = pygame.font.Font(None, 24)
        _font_cache['big'] = pygame.font.Font(None, 56)
        _font_cache['small'] = pygame.font.Font(None, 18)
    return _font_cache['font'], _font_cache['big'], _font_cache['small']


class TitleScene(Scene):
    """Сцена главного меню. Обёртка над MainMenu."""
    
    def __init__(self, menu, meta, lobby):
        super().__init__()
        self.menu = menu
        self.meta = meta
        self.lobby = lobby
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.menu.state = "main"
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass
            result = self.menu.handle_event(event)
            if result == "start":
                return "game"
            elif result == "char_select":
                pass
            elif result == "map_select":
                pass
        return None
    
    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        self.menu.draw(screen, font, big_font, small_font)


class GameScene(Scene):
    """Сцена геймплея. Управляет всем игровым процессом."""
    
    def __init__(self, game):
        super().__init__()
        self.game = game
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        char_id = kwargs.get("char_id", self.game.menu.selected_char)
        self.game.start_game(char_id)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "__quit__"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "__pause__"
            
            # LevelUp обрабатывает ввод
            if self.game.state == "levelup":
                done = self.game.levelup_screen.handle_event(event, self.game.player)
                if done:
                    self.game.state = "playing"
        
        return None
    
    def update(self, dt):
        self.game.update(dt)
        
        # Проверяем game over
        if self.game.state == "gameover":
            self.done = True
            self.next_scene = "game_over"
    
    def draw(self, screen):
        self.game.render()


class PauseOverlay(OverlayScene):
    """Оверлей паузы. Рисуется поверх GameScene."""
    
    def __init__(self):
        super().__init__()
        self.selected = 0
        self.items = ["Продолжить", "Настройки", "Выход в меню"]
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.selected = 0
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    return "__overlay__"
                
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.items)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        return "__overlay__"
                    elif self.selected == 1:
                        return "settings"
                    elif self.selected == 2:
                        return "lobby"
        return None
    
    def draw(self, screen):
        self.draw_background(screen)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        font, big_font, small_font = _get_fonts()
        
        title = big_font.render("ПАУЗА", True, (255, 215, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
        
        y = 280
        for i, item in enumerate(self.items):
            if i == self.selected:
                text = font.render(f">> {item}", True, (255, 255, 255))
            else:
                text = font.render(f"   {item}", True, (150, 150, 150))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 45
        
        hint = small_font.render("Up/Down - navigate | Enter - select | ESC - resume", True, (100, 100, 100))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))


class GameOverScene(Scene):
    """Сцена Game Over."""
    
    def __init__(self, menu, meta, lobby):
        super().__init__()
        self.menu = menu
        self.meta = meta
        self.lobby = lobby
        self.stats = {}
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.stats = kwargs.get("stats", {})
        self.menu.state = "game_over"
        self.menu.final_stats = self.stats
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "game"
                if event.key == pygame.K_ESCAPE:
                    return "lobby"
            result = self.menu.handle_event(event)
            if result == "restart":
                return "game"
            elif result == "menu":
                return "lobby"
        return None
    
    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        self.menu.draw(screen, font, big_font, small_font)


class LobbyScene(Scene):
    """Сцена лобби."""
    
    def __init__(self, lobby, meta, menu):
        super().__init__()
        self.lobby = lobby
        self.meta = meta
        self.menu = menu
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.lobby.activate(self.meta)
    
    def handle_events(self, events):
        for event in events:
            result = self.lobby.handle_event(event)
            if result == "play":
                return "game"
        return None
    
    def update(self, dt):
        self.lobby.update(dt)
    
    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        self.lobby.draw(screen, font, big_font, small_font)


class SettingsScene(Scene):
    """Сцена настроек."""
    
    def __init__(self):
        super().__init__()
        self.selected = 0
        self.items = ["Volume: 5", "Fullscreen: No", "Show FPS: No", "Back"]
        self.volume = 5
        self.fullscreen = False
        self.show_fps = False
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.selected = 0
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "__back__"
                
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.items)
                elif event.key == pygame.K_LEFT:
                    if self.selected == 0:
                        self.volume = max(0, self.volume - 1)
                    elif self.selected == 1:
                        self.fullscreen = False
                    elif self.selected == 2:
                        self.show_fps = False
                elif event.key == pygame.K_RIGHT:
                    if self.selected == 0:
                        self.volume = min(10, self.volume + 1)
                    elif self.selected == 1:
                        self.fullscreen = True
                    elif self.selected == 2:
                        self.show_fps = True
                elif event.key == pygame.K_RETURN:
                    if self.selected == 3:
                        return "__back__"
        
        self.items[0] = f"Volume: {self.volume}"
        self.items[1] = f"Fullscreen: {'Yes' if self.fullscreen else 'No'}"
        self.items[2] = f"Show FPS: {'Yes' if self.show_fps else 'No'}"
        return None
    
    def draw(self, screen):
        from config import GOLD, WHITE
        screen.fill(DARK_BG)
        
        font, big_font, small_font = _get_fonts()
        
        title = font.render("SETTINGS", True, GOLD)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        
        y = 250
        for i, item in enumerate(self.items):
            if i == self.selected:
                text = font.render(f">> {item}", True, WHITE)
            else:
                text = font.render(f"   {item}", True, (150, 150, 150))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 45
        
        hint = small_font.render("Left/Right - change | ESC - back", True, (100, 100, 100))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))
