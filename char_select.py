"""
Рождение святого - Character Select Scene
Полноэкранный выбор персонажа перед игрой.
"""
import pygame
from scene_manager import Scene
from config import WIDTH, HEIGHT, WHITE, GOLD, DARK_BG, GREEN
from player import CHARACTERS

# Font cache (PERF-1)
_font_cache = {}

def _get_fonts():
    if not _font_cache:
        _font_cache['font'] = pygame.font.Font(None, 24)
        _font_cache['big'] = pygame.font.Font(None, 48)
        _font_cache['small'] = pygame.font.Font(None, 18)
    return _font_cache['font'], _font_cache['big'], _font_cache['small']


class CharSelectScene(Scene):
    """Сцена выбора персонажа."""
    
    def __init__(self):
        super().__init__()
        self.meta = None
        self.menu = None
        self.selected = 0
        self.confirmed = False
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.meta = kwargs.get("meta")
        self.menu = kwargs.get("menu")
        self.confirmed = False
        # Start on currently selected char
        if self.menu and self.menu.selected_char:
            chars = list(CHARACTERS.keys())
            if self.menu.selected_char in chars:
                self.selected = chars.index(self.menu.selected_char)
    
    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            
            chars = list(CHARACTERS.keys())
            cols = min(3, len(chars))
            
            if event.key == pygame.K_ESCAPE:
                return "lobby"
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - cols) % len(chars)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + cols) % len(chars)
            elif event.key == pygame.K_LEFT:
                self.selected = (self.selected - 1) % len(chars)
            elif event.key == pygame.K_RIGHT:
                self.selected = (self.selected + 1) % len(chars)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                cid = chars[self.selected]
                if cid in self.meta.unlocked_chars:
                    self.menu.selected_char = cid
                    self.confirmed = True
                    return "stage_select"
        
        return None
    
    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        
        screen.fill(DARK_BG)
        cx = WIDTH // 2
        
        # Title
        title = big_font.render("ВЫБОР ПЕРСОНАЖА", True, GOLD)
        screen.blit(title, (cx - title.get_width() // 2, 20))
        
        # Hint
        hint = small_font.render("Enter - выбрать  |  ESC - назад", True, (100, 100, 100))
        screen.blit(hint, (cx - hint.get_width() // 2, HEIGHT - 25))
        
        chars = list(CHARACTERS.keys())
        card_w, card_h = 200, 160
        gap = 20
        cols = min(3, len(chars))
        grid_w = cols * card_w + (cols - 1) * gap
        start_x = cx - grid_w // 2
        y_start = 80
        
        for i, cid in enumerate(chars):
            c = CHARACTERS[cid]
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + gap)
            y = y_start + row * (card_h + gap)
            
            is_unlocked = cid in self.meta.unlocked_chars
            is_selected = (i == self.selected)
            is_current = (self.menu and self.menu.selected_char == cid)
            
            # Card background
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if not is_unlocked:
                card.fill((30, 30, 30, 160))
                pygame.draw.rect(card, (60, 60, 60), (0, 0, card_w, card_h), 1, border_radius=8)
                lock = small_font.render("???", True, (80, 80, 80))
                card.blit(lock, (card_w // 2 - lock.get_width() // 2, card_h // 2 - 8))
            else:
                fill = (60, 45, 80, 200) if is_selected else (40, 30, 60, 160)
                card.fill(fill)
                border = GOLD if is_selected else (120, 120, 120)
                bw = 3 if is_selected else 1
                pygame.draw.rect(card, border, (0, 0, card_w, card_h), bw, border_radius=8)
                
                # Name
                name = font.render(c["name"], True, WHITE)
                card.blit(name, (card_w // 2 - name.get_width() // 2, 12))
                
                # Stats
                hp_text = small_font.render(f"HP: {c['hp']}", True, (80, 200, 80))
                card.blit(hp_text, (12, 45))
                spd_text = small_font.render(f"SPD: {c['speed']:.1f}", True, (180, 180, 180))
                card.blit(spd_text, (12, 65))
                wep_text = small_font.render(f"Оружие: {c.get('start_weapon', '?')}", True, (150, 150, 200))
                card.blit(wep_text, (12, 85))
                desc_text = small_font.render(c.get("desc", ""), True, (200, 200, 150))
                card.blit(desc_text, (12, 110))
                
                # Current marker
                if is_current:
                    sel = small_font.render("ВЫБРАН", True, GREEN)
                    card.blit(sel, (card_w - sel.get_width() - 8, 8))
            
            screen.blit(card, (x, y))
        
        # Big preview of selected char
        if self.selected < len(chars):
            cid = chars[self.selected]
            if cid in self.meta.unlocked_chars:
                c = CHARACTERS[cid]
                preview_y = y_start + 2 * (card_h + gap) + 20
                desc = font.render(c.get("desc", ""), True, (220, 220, 200))
                screen.blit(desc, (cx - desc.get_width() // 2, preview_y))
