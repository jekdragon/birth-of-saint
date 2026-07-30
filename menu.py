"""
Рождение святого — Menu
Главное меню, выбор персонажа, Game Over.
"""
import pygame
from config import WIDTH, HEIGHT, WHITE, GOLD, DARK_BG, RED
from player import CHARACTERS


MAPS = {
    "arena":     {"name": "Арена",     "desc": "Бесконечная равнина, 4 биома-кольца"},
    "cathedral": {"name": "Собор",     "desc": "Узкие коридоры, залы, колонны"},
}
MAP_ORDER = ["arena", "cathedral"]


class MainMenu:
    def __init__(self):
        self.selected_char = "warrior"
        self.selected_map = "arena"
        self.state = "main"  # "main", "char_select", "map_select", "game_over"
        self.final_stats = {}

    def handle_event(self, event) -> str:
        """Возвращает: 'start', 'char_select', None"""
        if self.state == "main":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "start"
                if event.key == pygame.K_c:
                    self.state = "char_select"
                    return "char_select"
                if event.key == pygame.K_m:
                    self.state = "map_select"
                    return "map_select"

        elif self.state == "char_select":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_char = "warrior"
                    self.state = "main"
                elif event.key == pygame.K_2:
                    self.selected_char = "paladin"
                    self.state = "main"
                elif event.key == pygame.K_3:
                    self.selected_char = "inquisitor"
                    self.state = "main"
                elif event.key == pygame.K_4:
                    self.selected_char = "pilgrim"
                    self.state = "main"
                elif event.key == pygame.K_5:
                    self.selected_char = "monk"
                    self.state = "main"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "main"

        elif self.state == "map_select":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_map = "arena"
                    self.state = "main"
                elif event.key == pygame.K_2:
                    self.selected_map = "cathedral"
                    self.state = "main"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "main"

        elif self.state == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"
                    return "menu"

        return None

    def draw_main(self, surface: pygame.Surface, font, big_font, small_font):
        surface.fill(DARK_BG)

        # Название
        title = big_font.render("РОЖДЕНИЕ СВЯТОГО", True, GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        # Подзаголовок
        sub = font.render("Survivors-like Roguelike", True, WHITE)
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 210))

        # Персонаж
        char = CHARACTERS[self.selected_char]
        char_text = font.render(f"Персонаж: {char['name']}", True, char["color"])
        surface.blit(char_text, (WIDTH // 2 - char_text.get_width() // 2, 320))

        char_desc = small_font.render(char["desc"], True, (180, 180, 180))
        surface.blit(char_desc, (WIDTH // 2 - char_desc.get_width() // 2, 350))

        # Управление
        start_text = font.render("[ENTER] — Начать", True, WHITE)
        surface.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 440))

        char_sel = small_font.render("[C] — Выбор персонажа", True, (150, 150, 150))
        surface.blit(char_sel, (WIDTH // 2 - char_sel.get_width() // 2, 480))

        # Управление в игре
        controls = small_font.render("WASD — движение | 1/2/3 — выбор при левелапе", True, (100, 100, 100))
        surface.blit(controls, (WIDTH // 2 - controls.get_width() // 2, 560))

    def draw_char_select(self, surface: pygame.Surface, font, small_font):
        surface.fill(DARK_BG)

        title = font.render("ВЫБОР ПЕРСОНАЖА", True, GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        y = 160
        for i, (cid, char) in enumerate(CHARACTERS.items()):
            num = str(i + 1)
            prefix = "▶ " if cid == self.selected_char else "  "

            name_text = font.render(f"{prefix}[{num}] {char['name']}", True, char["color"])
            surface.blit(name_text, (WIDTH // 2 - 150, y))

            desc_text = small_font.render(char["desc"], True, (180, 180, 180))
            surface.blit(desc_text, (WIDTH // 2 - 150, y + 30))

            weapon_text = small_font.render(f"Оружие: {char['start_weapon']}", True, (150, 150, 150))
            surface.blit(weapon_text, (WIDTH // 2 - 150, y + 50))

            hp_text = small_font.render(f"HP: {char['hp']}  Скорость: {char['speed']}", True, (150, 150, 150))
            surface.blit(hp_text, (WIDTH // 2 - 150, y + 70))

            y += 110

        hint = small_font.render("[ESC] — назад", True, (100, 100, 100))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, y + 20))

    def draw_game_over(self, surface: pygame.Surface, font, big_font, small_font):
        surface.fill(DARK_BG)

        title = big_font.render("ПАЛ В БОЮ", True, RED)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        stats = self.final_stats
        y = 280

        for label, value in [
            ("Волна", stats.get("wave", 0)),
            ("Время", f"{stats.get('time', 0) // 60}:{stats.get('time', 0) % 60:02d}"),
            ("Убийства", stats.get("kills", 0)),
            ("Уровень", stats.get("level", 1)),
            ("Золото", stats.get("gold", 0)),
        ]:
            text = font.render(f"{label}: {value}", True, WHITE)
            surface.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 35

        restart_text = font.render("[R] — Заново", True, WHITE)
        surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, y + 40))

        menu_text = small_font.render("[ESC] — В меню", True, (150, 150, 150))
        surface.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, y + 80))

    def draw_map_select(self, surface: pygame.Surface, font, small_font):
        surface.fill(DARK_BG)
        title = font.render("ВЫБОР КАРТЫ", True, GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        for i, mid in enumerate(MAP_ORDER):
            m = MAPS[mid]
            prefix = "▶ " if mid == self.selected_map else "  "
            y = 200 + i * 60
            name = font.render(f"{prefix}{i+1}. {m['name']}", True, WHITE)
            surface.blit(name, (WIDTH // 2 - 100, y))
            desc = small_font.render(m['desc'], True, (150, 150, 150))
            surface.blit(desc, (WIDTH // 2 - 100, y + 25))

        hint = small_font.render("1/2 — выбор  |  ESC — назад", True, (120, 120, 120))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

    def draw(self, surface, font, big_font, small_font):
        if self.state == "main":
            self.draw_main(surface, font, big_font, small_font)
        elif self.state == "char_select":
            self.draw_char_select(surface, font, small_font)
        elif self.state == "map_select":
            self.draw_map_select(surface, font, small_font)
        elif self.state == "game_over":
            self.draw_game_over(surface, font, big_font, small_font)
