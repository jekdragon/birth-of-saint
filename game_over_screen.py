"""
Рождение святого - Game Over Screen
Полноценный экран поражения с анимациями и статистикой.
B4: Catechism of Ruin — Quill-scratch reveal on title.
"""
import pygame
import math
from config import WIDTH, HEIGHT, WHITE, GOLD, RED
from weapons import PASSIVE_DEFS


# Rarity colors (дублируем из hud.py для незавимости)
RARITY_COLORS = {
    'common': (120, 120, 120),
    'uncommon': (80, 200, 80),
    'rare': (80, 120, 255),
    'epic': (180, 80, 255),
    'legendary': (255, 180, 50),
}

# B4: Module-level QuillReveal for title animation (defined after class below)


class GameOverAnimator:
    """Аниматор для Game Over экрана."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.timer = 0.0
        # Play death sound
        try:
            import sound_manager
            sound_manager.play("game_over")
        except Exception:
            pass
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
        """Возвращает alpha (0-255) для фазы. Поддерживает динамические фазы с offset."""
        start = self.phases.get(phase, -1)
        if start < 0:
            # Динамическая фаза: "stats_0", "stats_1" и т.д.
            # Берём базовую фазу "stats" + offset из суффикса
            if phase.startswith("stats_"):
                try:
                    idx = int(phase.split("_")[1])
                    start = self.phases["stats"] + idx * 0.2
                except (ValueError, IndexError):
                    return 0
            else:
                return 0
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


class QuillReveal:
    """Quill-scratch letter-by-letter reveal for illuminated manuscript text.

    Each letter appears with a configurable delay, simulating a quill pen
    writing across parchment. Ink drops (small particles) trail each letter.
    """
    CHAR_DELAY = 0.05  # seconds per character

    def __init__(self):
        self.timer = 0.0
        self._ink_drops = []  # (x, y, alpha, size) tuples

    def reset(self):
        self.timer = 0.0
        self._ink_drops = []

    def update(self, dt: float):
        self.timer += dt
        # Decay ink drops
        new_drops = []
        for (x, y, a, s) in self._ink_drops:
            a -= 300 * dt
            if a > 0:
                new_drops.append((x, y, a, s))
        self._ink_drops = new_drops

    def get_visible_count(self) -> int:
        """How many characters are visible."""
        return min(int(self.timer / self.CHAR_DELAY), 100)

    def add_ink_drop(self, x: int, y: int):
        """Add a small ink splatter at quill position."""
        import random as _rng
        self._ink_drops.append((x + _rng.randint(-3, 3), y + _rng.randint(-2, 2),
                                _rng.randint(160, 240), _rng.randint(1, 3)))

    def draw_text_revealed(self, surface, text: str, font, color, x: int, y: int):
        """Draw text character-by-character with quill reveal effect."""
        visible = self.get_visible_count()
        if visible <= 0:
            return
        revealed = text[:visible]
        # Render each character individually for precise positioning
        char_x = x
        for ch in revealed:
            ch_surf = font.render(ch, True, color)
            # Slight vertical jitter for handwritten feel
            jitter_y = int(math.sin(ord(ch) * 0.7 + self.timer * 2.0) * 1.5)
            surface.blit(ch_surf, (char_x, y + jitter_y))
            # Add ink drop at quill tip
            if ch != ' ':
                self.add_ink_drop(char_x + ch_surf.get_width(), y + ch_surf.get_height() // 2)
            char_x += ch_surf.get_width()

        # Draw ink drops
        for (dx, dy, da, ds) in self._ink_drops:
            da_i = max(0, min(255, int(da)))
            if da_i > 0 and ds > 0:
                drop_surf = pygame.Surface((ds * 2, ds * 2), pygame.SRCALPHA)
                pygame.draw.circle(drop_surf, (40, 30, 20, da_i), (ds, ds), ds)
                surface.blit(drop_surf, (int(dx) - ds, int(dy) - ds))

# B4: Module-level QuillReveal instance for game over title
_quill = QuillReveal()


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
            wname = w.name
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
    # Guard: animator must exist
    if animator is None:
        from game_over_screen import GameOverAnimator
        animator = GameOverAnimator()
        animator.timer = 5.0

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

    # === Title: "ПАЛ В БОЮ" — B4: Quill-scratch reveal ===
    title_alpha = animator.get_alpha('title', 0.4)
    title_scale = animator.get_scale('title', 0.5)
    if title_alpha > 0:
        # Update quill timer
        _quill.update(1 / 60)
        # Reset quill when title phase just started
        if animator.timer < animator.phases.get('title', 0) + 0.05:
            _quill.reset()

        if _quill.get_visible_count() >= len("ПАЛ В БОЮ"):
            # Fully revealed — draw with scale punch
            title_surf = big_font.render("ПАЛ В БОЮ", True, RED)
            if title_scale != 1.0:
                w = int(title_surf.get_width() * title_scale)
                h = int(title_surf.get_height() * title_scale)
                title_surf = pygame.transform.smoothscale(title_surf, (w, h))
            title_surf.set_alpha(title_alpha)
            screen.blit(title_surf, (cx - title_surf.get_width() // 2, 50))
        else:
            # Quill reveal in progress — draw character by character
            title_text = "ПАЛ В БОЮ"
            # Measure total width for centering
            total_w = big_font.size(title_text)[0]
            start_x = cx - total_w // 2
            _quill.draw_text_revealed(screen, title_text, big_font, RED, start_x, 50)

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
        pulse = (math.sin(animator.timer * 2.5) + 1.0) / 2.0  # ~400ms period
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
