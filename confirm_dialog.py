"""
Рождение святого - Confirm Dialog
Диалог подтверждения действия (ДА/НЕТ).
"""
import pygame
import math
from config import WIDTH, HEIGHT, WHITE, GOLD


class ConfirmDialog:
    """Диалог подтверждения с анимацией."""

    def __init__(self, title="Вы уверены?", subtitle="", yes_text="ДА", no_text="НЕТ"):
        self.title = title
        self.subtitle = subtitle
        self.yes_text = yes_text
        self.no_text = no_text
        self.selected = 1  # 0=ДА, 1=НЕТ (по умолчанию НЕТ — безопаснее)
        self.result = None  # None, True (ДА), False (НЕТ)
        self.timer = 0.0
        self.active = False

    def show(self):
        self.active = True
        self.selected = 1
        self.result = None
        self.timer = 0.0

    def handle_event(self, event) -> bool | None:
        """Returns: True (ДА), False (НЕТ), None (еще открыт)"""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected = 0
                import sound_manager
                sound_manager.play("ui_hover")
            elif event.key == pygame.K_RIGHT:
                self.selected = 1
                import sound_manager
                sound_manager.play("ui_hover")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                import sound_manager
                if self.selected == 0:
                    sound_manager.play("ui_select")
                    self.result = True
                    self.active = False
                    return True
                else:
                    sound_manager.play("ui_back")
                    self.result = False
                    self.active = False
                    return False
            elif event.key == pygame.K_ESCAPE:
                import sound_manager
                sound_manager.play("ui_back")
                self.result = False
                self.active = False
                return False

        return None

    def update(self, dt):
        if self.active:
            self.timer += dt

    def draw(self, surface, font=None, small_font=None):
        if not self.active:
            return

        if font is None:
            font = pygame.font.Font(None, 24)
        if small_font is None:
            small_font = pygame.font.Font(None, 18)

        cx = WIDTH // 2
        cy = HEIGHT // 2

        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        # Панель
        panel_w, panel_h = 360, 160
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((40, 30, 60, 230))
        pygame.draw.rect(panel, (100, 80, 140), (0, 0, panel_w, panel_h), 2, border_radius=10)
        surface.blit(panel, (cx - panel_w // 2, cy - panel_h // 2))

        # Заголовок
        title_t = font.render(self.title, True, WHITE)
        surface.blit(title_t, (cx - title_t.get_width() // 2, cy - panel_h // 2 + 20))

        # Подзаголовок
        if self.subtitle:
            sub_t = small_font.render(self.subtitle, True, (180, 180, 180))
            surface.blit(sub_t, (cx - sub_t.get_width() // 2, cy - panel_h // 2 + 50))

        # Кнопки
        btn_y = cy + 20
        btn_w, btn_h = 120, 40

        for i, (text, color) in enumerate([(self.yes_text, (80, 200, 80)), (self.no_text, (200, 80, 80))]):
            x = cx - btn_w - 10 if i == 0 else cx + 10
            is_sel = (i == self.selected)

            btn = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            if is_sel:
                btn.fill((60, 50, 80, 200))
                pygame.draw.rect(btn, color, (0, 0, btn_w, btn_h), 2, border_radius=6)
            else:
                btn.fill((30, 25, 45, 160))
                pygame.draw.rect(btn, (80, 80, 100), (0, 0, btn_w, btn_h), 1, border_radius=6)
            surface.blit(btn, (x, btn_y))

            label = font.render(text, True, color if is_sel else (150, 150, 150))
            surface.blit(label, (x + btn_w // 2 - label.get_width() // 2, btn_y + 8))

        # Подсказка
        hint = small_font.render("Left/Right - выбор  |  Enter - подтвердить", True, (100, 100, 100))
        surface.blit(hint, (cx - hint.get_width() // 2, cy + panel_h // 2 - 25))
