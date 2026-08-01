"""
Рождение святого - Game Over Screen
Полноценный экран поражения с анимациями и статистикой.
"""
import pygame
import math
from config import WIDTH, HEIGHT, WHITE, GOLD, RED, DARK_BG
from weapons import WEAPON_DEFS, PASSIVE_DEFS


# Rarity colors (дублируем из hud.py для незавимости)
RARITY_COLORS = {
    'common': (120, 120, 120),
    'uncommon': (80, 200, 80),
    'rare': (80, 120, 255),
    'epic': (180, 80, 255),
    'legendary': (255, 180, 50),
}


class GameOverAnimator:
    """Аниматор для Game Over экрана."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.timer = 0.0
        # Каждый элемент появляется с задержкой
        # 0.0s — fade в красной виньетке
        # 0.3s — "ПАЛ В БОЮ" title (scale punch)
        # 0.6s — разделитель
        # 0.8s, 1.0s, 1.2s, 1.4s, 1.6s — строки статистики
        # 2.0s — разделитель билда
        # 2.2s+ — оружия
        # 3.0s+ — пассивки
        # 3.5s — лидерборд
        # 4.0s — кнопки
        self.phases = {
            'vignette': 0.0,
            'title': 0.3,
            'divider1': 0.6,
            'stats': 0.8,
            'divider2': 1.8,
            'build_title': 2.0,
            'weapons': 2.2,
            'passives': 3.0,
            'leaderboard': 3.5,
            'buttons': 4.0,
        }

    def get_alpha(self, phase: str, fade_duration: float = 0.3) -> int:
        """Возвращает alpha (0-255) для фазы."""
        start = self.phases.get(phase, 0)
        if self.timer < start:
            return 0
        elapsed = self.timer - start
        if elapsed >= fade_duration:
            return 255
        return int(255 * (elapsed / fade_duration))

    def get_scale(self, phase: str, punch_duration: float = 0.4) -> float:
        """Возвращает scale для punch-эффекта (1.0 → 1.15 → 1.0)."""
        start = self.phases.get(phase, 0)
        if self.timer < start:
            return 0.8
        elapsed = self.timer - start
        if elapsed >= punch_duration:
            return 1.0
        # ease_out_back: overshoot then settle
        t = elapsed / punch_duration
        # Простой bounce: 1.0 → 1.15 → 1.0
        if t < 0.5:
            return 1.0 + 0.15 * (t / 0.5)
        else:
            return 1.15 - 0.15 * ((t - 0.5) / 0.5)

    def update(self, dt: float):
        self.timer += dt


class GameOverBuildPanel:
    """Панель билда (оружия + пассивки)."""

    @staticmethod
    def draw_weapons(surface, weapons, x, y, font, small_font, alpha):
        """Рисует список оружий."""
        if alpha <= 0:
            return y

        title = font.render("ОРУЖИЕ", True, (180, 200, 255))
        title.set_alpha(alpha)
        surface.blit(title, (x, y))
        y += 28

        for w in weapons:
            rarity = getattr(w, 'rarity', 'common')
            color = RARITY_COLORS.get(rarity, (120, 120, 120))

            # Имя + уровень
            wname = w.display_name()
            evolved = " [MAX]" if w.evolved else ""
            text_str = f"{wname} Lv{w.level}{evolved}"

            text = small_font.render(text_str, True, color)
            text.set_alpha(alpha)
            surface.blit(text, (x + 10, y))

            # Rarity badge
            badge = small_font.render(f"[{rarity.upper()}]", True, color)
            badge.set_alpha(alpha)
            surface.blit(badge, (x + 250, y))

            y += 20
        return y

    @staticmethod
    def draw_passives(surface, passives_dict, x, y, font, small_font, alpha):
        """Рисует список пассивок."""
        if alpha <= 0:
            return y
        if not passives_dict:
            return y

        title = font.render("ПАССИВКИ", True, (180, 255, 180))
        title.set_alpha(alpha)
        surface.blit(title, (x, y))
        y += 28

        for pid, lvl in passives_dict.items():
            pname = PASSIVE_DEFS.get(pid, {}).get("name", pid)
            color = PASSIVE_DEFS.get(pid, {}).get("color", (150, 255, 150))

            text = small_font.render(f"{pname} Lv{lvl}", True, color)
            text.set_alpha(alpha)
            surface.blit(text, (x + 10, y))
            y += 20
        return y


def draw_game_over(screen, stats, animator, player=None, menu=None,
                   font=None, big_font=None, small_font=None):
    """
    Полная отрисовка Game Over экрана.

    Args:
        stats: dict с wave, time, kills, level, gold
        animator: GameOverAnimator (состояние анимаций)
        player: Player объект (для билда, может быть None)
        menu: MainMenu (для leaderboard_rank/entries)
    """
    if font is None:
        font = pygame.font.Font(None, 24)
    if big_font is None:
        big_font = pygame.font.Font(None, 56)
    if small_font is None:
        small_font = pygame.font.Font(None, 18)

    # === Фон: красная виньетка поверх тёмного фона ===
    screen.fill((8, 4, 4))

    vignette_alpha = animator.get_alpha('vignette', 0.5)
    if vignette_alpha > 0:
        # Радиальная виньетка: красный край
        vig = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        vig_alpha = int(vignette_alpha * 0.4)
        # Красный край
        pygame.draw.rect(vig, (80, 0, 0, vig_alpha), (0, 0, WIDTH, HEIGHT))
        # Затемнение центра
        center_alpha = int(vig_alpha * 0.3)
        pygame.draw.rect(vig, (0, 0, 0, center_alpha),
                        (WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2))
        screen.blit(vig, (0, 0))

    cx = WIDTH // 2  # центр по X

    # === Title: "ПАЛ В БОЮ" ===
    title_alpha = animator.get_alpha('title', 0.4)
    title_scale = animator.get_scale('title', 0.5)
    if title_alpha > 0:
        title_surf = big_font.render("ПАЛ В БОЮ", True, RED)
        # Scale punch
        if title_scale != 1.0:
            w = int(title_surf.get_width() * title_scale)
            h = int(title_surf.get_height() * title_scale)
            title_surf = pygame.transform.smoothscale(title_surf, (w, h))
        title_surf.set_alpha(title_alpha)
        screen.blit(title_surf, (cx - title_surf.get_width() // 2, 50))

    # === Разделитель 1 ===
    div1_alpha = animator.get_alpha('divider1', 0.2)
    if div1_alpha > 0:
        div_w = 200
        div_surf = pygame.Surface((div_w, 2), pygame.SRCALPHA)
        div_surf.fill((100, 80, 80, div1_alpha))
        screen.blit(div_surf, (cx - div_w // 2, 115))

    # === Статистика ===
    stats_y = 135
    stat_items = [
        ("Волна", str(stats.get("wave", 0)), (255, 200, 100)),
        ("Время", f"{stats.get('time', 0) // 60}:{stats.get('time', 0) % 60:02d}", WHITE),
        ("Убийства", str(stats.get("kills", 0)), (255, 120, 120)),
        ("Уровень", str(stats.get("level", 1)), (120, 200, 255)),
        ("Золото", str(stats.get("gold", 0)), GOLD),
    ]

    for i, (label, value, color) in enumerate(stat_items):
        phase_delay = 0.8 + i * 0.2  # stagger: 0.8, 1.0, 1.2, 1.4, 1.6
        alpha = animator.get_alpha(f'stats_{i}', 0.3)
        if alpha <= 0:
            # Вычисляем alpha из общей фазы stats + offset
            base_start = animator.phases['stats'] + i * 0.2
            if animator.timer < base_start:
                stats_y += 28
                continue
            elapsed = animator.timer - base_start
            alpha = min(255, int(255 * (elapsed / 0.3)))

        if alpha <= 0:
            stats_y += 28
            continue

        # Label (серый)
        label_surf = small_font.render(f"{label}:", True, (180, 180, 180))
        label_surf.set_alpha(alpha)
        screen.blit(label_surf, (cx - 120, stats_y))

        # Value (цветной, с punch)
        punch_start = animator.phases['stats'] + i * 0.2
        if animator.timer > punch_start:
            elapsed = animator.timer - punch_start
            scale = 1.0
            if elapsed < 0.3:
                t = elapsed / 0.3
                scale = 1.0 + 0.08 * math.sin(t * math.pi)
            value_surf = font.render(value, True, color)
            if scale != 1.0:
                w = int(value_surf.get_width() * scale)
                h = int(value_surf.get_height() * scale)
                value_surf = pygame.transform.smoothscale(value_surf, (w, h))
        else:
            value_surf = font.render(value, True, color)
        value_surf.set_alpha(alpha)
        screen.blit(value_surf, (cx + 20, stats_y - 2))

        stats_y += 28

    # === Разделитель 2 ===
    div2_alpha = animator.get_alpha('divider2', 0.2)
    if div2_alpha > 0:
        div_surf = pygame.Surface((160, 2), pygame.SRCALPHA)
        div_surf.fill((80, 80, 100, div2_alpha))
        screen.blit(div_surf, (cx - 80, stats_y + 5))
        stats_y += 15

    # === Билд ===
    build_title_alpha = animator.get_alpha('build_title', 0.3)
    build_y = stats_y + 5

    if build_title_alpha > 0 and player:
        build_title = font.render("-- БИЛД СЕССИИ --", True, GOLD)
        build_title.set_alpha(build_title_alpha)
        screen.blit(build_title, (cx - build_title.get_width() // 2, build_y))
        build_y += 30

        # Оружия
        weapons_alpha = animator.get_alpha('weapons', 0.3)
        if weapons_alpha > 0:
            build_y = GameOverBuildPanel.draw_weapons(
                screen, player.weapons, cx - 140, build_y, font, small_font, weapons_alpha)

            # Пассивки
            passives_alpha = animator.get_alpha('passives', 0.3)
            if passives_alpha > 0 and player.passives:
                build_y += 10
                build_y = GameOverBuildPanel.draw_passives(
                    screen, player.passives, cx - 140, build_y, font, small_font, passives_alpha)

    # === Лидерборд ===
    lb_alpha = animator.get_alpha('leaderboard', 0.3)
    if lb_alpha > 0 and menu:
        rank = getattr(menu, 'leaderboard_rank', None)
        entries = getattr(menu, 'leaderboard_entries', [])

        lb_y = max(build_y + 20, HEIGHT // 2 + 20)

        if rank:
            rank_text = font.render(f"Место в таблице: #{rank}", True, GOLD)
            rank_text.set_alpha(lb_alpha)
            screen.blit(rank_text, (cx - rank_text.get_width() // 2, lb_y))
            lb_y += 30

        if entries:
            lb_title = small_font.render("--- ТАБЛИЦА РЕКОРДОВ ---", True, (180, 160, 100))
            lb_title.set_alpha(lb_alpha)
            screen.blit(lb_title, (cx - lb_title.get_width() // 2, lb_y))
            lb_y += 22

            for i, e in enumerate(entries[:5]):
                is_current = (i + 1 == rank) if rank else False
                color = GOLD if is_current else (200, 200, 200)

                survived = e.get('survived', 0)
                line = f"{i+1}. {e.get('character', '?')} - Волна {e.get('wave', 0)} | {e.get('kills', 0)} kills | {survived}c"
                text = small_font.render(line, True, color)
                text.set_alpha(lb_alpha)
                screen.blit(text, (cx - text.get_width() // 2, lb_y))
                lb_y += 18

    # === Кнопки ===
    btn_alpha = animator.get_alpha('buttons', 0.3)
    if btn_alpha > 0:
        # Пульсация кнопок
        pulse = (math.sin(pygame.time.get_ticks() / 400.0) + 1.0) / 2.0
        btn_color = (
            int(200 + 55 * pulse),
            int(200 + 55 * pulse),
            int(200 + 55 * pulse)
        )

        restart_text = font.render("[R] Заново", True, btn_color)
        restart_text.set_alpha(btn_alpha)
        screen.blit(restart_text, (cx - restart_text.get_width() // 2, HEIGHT - 70))

        menu_text = small_font.render("[ESC] В лобби", True, (150, 150, 150))
        menu_text.set_alpha(btn_alpha)
        screen.blit(menu_text, (cx - menu_text.get_width() // 2, HEIGHT - 42))
