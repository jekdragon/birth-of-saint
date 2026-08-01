"""
Рождение святого - Stage Select Scene
Выбор карты перед игрой.
"""
import pygame
from scene_manager import Scene
from config import WIDTH, HEIGHT, WHITE, GOLD, DARK_BG, GREEN

# Font cache (PERF-1)
_font_cache = {}

def _get_fonts():
    if not _font_cache:
        _font_cache['font'] = pygame.font.Font(None, 24)
        _font_cache['big'] = pygame.font.Font(None, 48)
        _font_cache['small'] = pygame.font.Font(None, 18)
    return _font_cache['font'], _font_cache['big'], _font_cache['small']


# Карты (пока одна, расширяемая)
STAGES = [
    {
        "id": "cathedral",
        "name": "Собор",
        "desc": "Проклятый собор. Волны нечисти.",
        "difficulty": 1,
        "color": (100, 80, 60),
        "unlocked": True,
    },
    {
        "id": "catacombs",
        "name": "Катакомбы",
        "desc": "Подземелья под собором. Темнота и ужас.",
        "difficulty": 3,
        "color": (60, 40, 80),
        "unlocked": False,
    },
    {
        "id": "hellgate",
        "name": "Врата Ада",
        "desc": "Портал в преисподнюю. Финальное испытание.",
        "difficulty": 5,
        "color": (120, 30, 30),
        "unlocked": False,
    },
]


class StageSelectScene(Scene):
    """Сцена выбора карты."""
    
    def __init__(self):
        super().__init__()
        self.meta = None
        self.selected = 0
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.meta = kwargs.get("meta")
        self.selected = 0
    
    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            
            if event.key == pygame.K_ESCAPE:
                return "char_select"
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(STAGES)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(STAGES)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                stage = STAGES[self.selected]
                if stage["unlocked"]:
                    return "game"
        
        return None
    
    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        
        screen.fill(DARK_BG)
        cx = WIDTH // 2
        
        # Title
        title = big_font.render("ВЫБОР КАРТЫ", True, GOLD)
        screen.blit(title, (cx - title.get_width() // 2, 20))
        
        # Hint
        hint = small_font.render("Enter - играть  |  ESC - назад", True, (100, 100, 100))
        screen.blit(hint, (cx - hint.get_width() // 2, HEIGHT - 25))
        
        # Stage cards
        card_w, card_h = 400, 100
        gap = 16
        y_start = 100
        
        for i, stage in enumerate(STAGES):
            x = cx - card_w // 2
            y = y_start + i * (card_h + gap)
            is_selected = (i == self.selected)
            is_unlocked = stage["unlocked"]
            
            # Card
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if not is_unlocked:
                card.fill((30, 30, 30, 160))
                pygame.draw.rect(card, (60, 60, 60), (0, 0, card_w, card_h), 1, border_radius=8)
                lock = font.render("ЗАБЛОКИРОВАНО", True, (80, 80, 80))
                card.blit(lock, (card_w // 2 - lock.get_width() // 2, card_h // 2 - 8))
            else:
                fill = (50, 40, 70, 200) if is_selected else (35, 28, 50, 160)
                card.fill(fill)
                border = GOLD if is_selected else (100, 100, 100)
                bw = 3 if is_selected else 1
                pygame.draw.rect(card, border, (0, 0, card_w, card_h), bw, border_radius=8)
                
                # Name
                name = font.render(stage["name"], True, WHITE)
                card.blit(name, (20, 15))
                
                # Description
                desc = small_font.render(stage["desc"], True, (180, 180, 180))
                card.blit(desc, (20, 45))
                
                # Difficulty
                stars = "\u2605" * stage["difficulty"] + "\u2606" * (5 - stage["difficulty"])
                diff = small_font.render(f"Сложность: {stars}", True, (200, 180, 100))
                card.blit(diff, (20, 70))
            
            screen.blit(card, (x, y))
