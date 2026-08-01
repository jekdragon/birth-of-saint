"""
Рождение святого - Scenes
Конкретные сцены, обёрнутые над существующими классами.
"""
import pygame
import math
import random
from scene_manager import Scene, OverlayScene
from config import WIDTH, HEIGHT, DARK_BG
from ui_theme import (
    TEXT_PRIMARY, GOLD_LEAF,
    CONFESS_DARK, CONFESS_WOOD, CONFESS_WOOD_LIGHT,
    CONFESS_STONE, CONFESS_STONE_LIGHT, CONFESS_STONE_DARK,
    CONFESS_GOLD, IRON, IRON_LIGHT,
)
import sound_manager

CONFESS_IRON = IRON
CONFESS_IRON_LIGHT = IRON_LIGHT

# Общие шрифты (ленивая инициализация)
_font_cache = {}

def _get_fonts():
    if not _font_cache:
        _font_cache['font'] = pygame.font.Font(None, 24)
        _font_cache['big'] = pygame.font.Font(None, 56)
        _font_cache['small'] = pygame.font.Font(None, 18)
    return _font_cache['font'], _font_cache['big'], _font_cache['small']


# ============================================================
# B5: The Confessional Pause Screen — Visual Helpers
# ============================================================
# Confessional palette (dark wood + stone + iron) — из ui_theme
CONFESS_CHAIN = (100, 95, 85)

_wood_slats_cache = {}


def generate_wood_slats(w, h, seed=77):
    """Procedural vertical dark wood slats background (cached)."""
    key = (w, h, seed)
    if key in _wood_slats_cache:
        return _wood_slats_cache[key]

    surf = pygame.Surface((w, h))
    rng = random.Random(seed)
    surf.fill(CONFESS_DARK)

    slat_w = 28
    for sx in range(0, w + slat_w, slat_w):
        base_r = rng.randint(22, 40)
        base_g = rng.randint(15, 28)
        base_b = rng.randint(8, 16)
        pygame.draw.rect(surf, (base_r, base_g, base_b), (sx, 0, slat_w, h))

        for gy in range(0, h, rng.randint(6, 14)):
            ga = rng.randint(-6, 6)
            col = tuple(max(0, min(255, c + ga)) for c in (base_r, base_g, base_b))
            pygame.draw.line(surf, col, (sx + 1, gy), (sx + slat_w - 2, gy))

        pygame.draw.line(surf,
            (max(0, base_r - 12), max(0, base_g - 12), max(0, base_b - 8)),
            (sx + slat_w - 1, 0), (sx + slat_w - 1, h))
        pygame.draw.line(surf,
            (min(255, base_r + 8), min(255, base_g + 6), min(255, base_b + 4)),
            (sx, 0), (sx, h))

        if rng.random() < 0.15:
            kx = sx + rng.randint(6, slat_w - 6)
            ky = rng.randint(50, h - 50)
            kr = rng.randint(3, 6)
            pygame.draw.circle(surf, (base_r - 8, base_g - 8, base_b - 5), (kx, ky), kr)
            pygame.draw.circle(surf, (base_r + 4, base_g + 4, base_b + 2), (kx, ky), kr, 1)

    # Horizontal frame beams
    beam_h = 24
    for rect_y in (0, h - beam_h):
        pygame.draw.rect(surf, (30, 22, 14), (0, rect_y, w, beam_h))
        for by in range(rect_y, rect_y + beam_h, 3):
            shade = rng.randint(-4, 4)
            pygame.draw.line(surf, (34 + shade, 26 + shade, 16 + shade), (0, by), (w, by))

    # Iron corner brackets with rivets
    bs = 18
    for bx, by in [(0, 0), (w - bs, 0), (0, h - bs), (w - bs, h - bs)]:
        pygame.draw.rect(surf, CONFESS_IRON, (bx, by, bs, bs))
        pygame.draw.rect(surf, CONFESS_IRON_LIGHT, (bx + 2, by + 2, bs - 4, bs - 4), 1)
        rx, ry = bx + bs // 2, by + bs // 2
        pygame.draw.circle(surf, CONFESS_IRON_LIGHT, (rx, ry), 3)
        pygame.draw.circle(surf, (140, 140, 145), (rx - 1, ry - 1), 1)

    _wood_slats_cache[key] = surf
    return surf


def draw_stone_tablet(surface, x, y, w, h, text, selected, font):
    """Draw a stone tablet with chain links and iron rivets."""
    chain_y = y - 16
    chain_links = max(3, w // 30)
    link_spacing = w // (chain_links + 1)
    for ci in range(1, chain_links + 1):
        lx = x + ci * link_spacing
        pygame.draw.ellipse(surface, CONFESS_CHAIN, (lx - 3, chain_y - 2, 6, 8), 1)
        if ci < chain_links:
            nx = x + (ci + 1) * link_spacing
            pygame.draw.line(surface, CONFESS_CHAIN, (lx + 3, chain_y + 2), (nx - 3, chain_y + 2), 1)

    mid_x = x + w // 2
    pygame.draw.line(surface, CONFESS_IRON, (mid_x, chain_y + 6), (mid_x, y), 2)

    # Shadow
    shadow = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 60))
    surface.blit(shadow, (x + 2, y + 2))

    # Selected glow
    if selected:
        glow = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
        glow.fill((180, 150, 60, 30))
        surface.blit(glow, (x - 6, y - 6))

    # Stone gradient fill
    for row in range(h):
        frac = row / max(1, h - 1)
        wave = 0.5 + 0.5 * math.sin(frac * 3.14)
        r = int(CONFESS_STONE_DARK[0] + (CONFESS_STONE_LIGHT[0] - CONFESS_STONE_DARK[0]) * wave)
        g = int(CONFESS_STONE_DARK[1] + (CONFESS_STONE_LIGHT[1] - CONFESS_STONE_DARK[1]) * wave)
        b = int(CONFESS_STONE_DARK[2] + (CONFESS_STONE_LIGHT[2] - CONFESS_STONE_DARK[2]) * wave)
        pygame.draw.line(surface, (r, g, b), (x, y + row), (x + w - 1, y + row))

    # Edge bevel
    pygame.draw.line(surface, CONFESS_STONE_LIGHT, (x, y), (x + w - 1, y))
    pygame.draw.line(surface, CONFESS_STONE_LIGHT, (x, y), (x, y + h - 1))
    pygame.draw.line(surface, CONFESS_STONE_DARK, (x + w - 1, y), (x + w - 1, y + h - 1))
    pygame.draw.line(surface, CONFESS_STONE_DARK, (x, y + h - 1), (x + w - 1, y + h - 1))

    # Iron rivets at corners
    for rx, ry in [(x + 8, y + 8), (x + w - 8, y + 8), (x + 8, y + h - 8), (x + w - 8, y + h - 8)]:
        pygame.draw.circle(surface, CONFESS_IRON, (rx, ry), 4)
        pygame.draw.circle(surface, CONFESS_IRON_LIGHT, (rx - 1, ry - 1), 2)

    # Selected border
    if selected:
        pygame.draw.rect(surface, CONFESS_GOLD, (x - 2, y - 2, w + 4, h + 4), 2)

    # Carved text
    text_color = CONFESS_GOLD if selected else (160, 150, 130)
    text_surf = font.render(text, True, text_color)
    surface.blit(text_surf, (x + w // 2 - text_surf.get_width() // 2, y + h // 2 - text_surf.get_height() // 2))


class ConfessionalCandle:
    """Ambient candle flicker particle for the confessional booth."""
    __slots__ = ('x', 'y', 'vy', 'vx', 'alpha', 'size', 'life', 'max_life', 'color')

    def __init__(self, x, y):
        self.x = x + random.uniform(-8, 8)
        self.y = y
        self.vy = random.uniform(-40, -15)
        self.vx = random.uniform(-6, 6)
        self.alpha = random.randint(180, 255)
        self.size = random.randint(2, 4)
        self.life = 0.0
        self.max_life = random.uniform(1.5, 3.0)
        r = random.randint(200, 255)
        g = random.randint(140, 200)
        b = random.randint(30, 80)
        self.color = (r, g, b)

    def update(self, dt):
        self.life += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        ratio = max(0.0, 1.0 - self.life / self.max_life)
        self.alpha = max(0, int(255 * ratio * ratio))
        if random.random() < 0.3:
            self.size = max(1, min(5, self.size + random.choice([-1, 1])))

    @property
    def alive(self):
        return self.life < self.max_life and self.alpha > 0


class SplashScene(Scene):
    """Сцена сплеш-экрана с параллаксом и частицами."""
    
    def __init__(self):
        super().__init__()
        self.splash = None
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        from splash import SplashScreen
        self.splash = SplashScreen()
    
    def exit(self):
        if self.splash:
            self.splash.stop_sound()
    
    def handle_events(self, events):
        if self.splash:
            self.splash.handle_events(events)
        return None
    
    def update(self, dt):
        if self.splash:
            self.splash.update(dt)
            if self.splash.done:
                self.done = True
                self.next_scene = "title"
        return None
    
    def draw(self, screen):
        if self.splash:
            self.splash.draw(screen)


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
        # Загружаем рекорды
        try:
            from leaderboard import get_entries
            self.menu.leaderboard_entries = get_entries()[:10]
        except Exception:
            self.menu.leaderboard_entries = []
    
    def handle_events(self, events):
        for event in events:
            result = self.menu.handle_event(event)
            if result == "start":
                return "lobby"  # v2: идём сразу в лобби (char_select внутри лобби)
            elif result == "char_select":
                return "char_select"
            elif result == "map_select":
                return "stage_select"
            elif result == "settings":
                return "settings"
            elif result == "records":
                pass  # рекорды рисуются в menu.draw_records
            elif result == "quit":
                return "__quit__"
            elif isinstance(result, tuple) and len(result) == 2:
                # C5: profile_select — загружаем профиль и идём в лобби
                name, kwargs = result
                if name == "profile_select":
                    from save_system import set_active_profile, load_progress
                    pid = kwargs.get("profile_id", 1)
                    set_active_profile(pid)
                    load_progress(self.meta)
                    return "lobby"
                return result
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
        # Пробрасываем screen в глобальную переменную main.py
        import main
        main.screen = screen
        self.game.render()


class PauseOverlay(OverlayScene):
    """B5: Confessional Pause Screen.
    
    Dark wood slat background with an arched confessional frame.
    Menu items = stone tablets hanging from chains with iron rivets.
    Ambient candle flicker particles.
    Preserves all existing functionality: ConfirmDialog, stats, build display.
    """

    # Tablet layout
    TABLET_W = 360
    TABLET_H = 52
    TABLET_GAP = 16

    def __init__(self):
        super().__init__()
        self.selected = 0
        self.items = ["Продолжить", "Настройки", "Выход в меню"]
        self.game = None
        self.confirm = None
        self._candles = []
        self._timer = 0.0
        self._spawn_timer = 0.0
        self._arch_cache = None  # PERF-2: cached arch surface

    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.selected = 0
        self.game = kwargs.get("game")
        self.confirm = None
        self._candles = []
        self._timer = 0.0
        self._spawn_timer = 0.0

    def update(self, dt):
        self._timer += dt
        self._spawn_timer += dt

        # Spawn candle particles from bottom-left and bottom-right
        if self._spawn_timer > 0.12:
            self._spawn_timer = 0.0
            if len(self._candles) < 40:
                # Left candle cluster
                self._candles.append(ConfessionalCandle(
                    random.randint(80, 200), HEIGHT - 60))
                # Right candle cluster
                self._candles.append(ConfessionalCandle(
                    random.randint(WIDTH - 200, WIDTH - 80), HEIGHT - 60))

        # Update particles
        for c in self._candles:
            c.update(dt)
        self._candles = [c for c in self._candles if c.alive]

        if self.confirm:
            self.confirm.update(dt)

    def handle_events(self, events):
        for event in events:
            if self.confirm and self.confirm.active:
                result = self.confirm.handle_event(event)
                if result == True:
                    return "lobby"
                elif result == False:
                    self.confirm = None
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    return "__overlay__"

                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.items)
                    sound_manager.play("ui_hover")
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.items)
                    sound_manager.play("ui_hover")
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:
                        return "__overlay__"
                    elif self.selected == 1:
                        return ("settings", {"return_to": "__pause__"})
                    elif self.selected == 2:
                        from confirm_dialog import ConfirmDialog
                        self.confirm = ConfirmDialog(
                            title="Вы уверены?",
                            subtitle="Прогресс этой сессии будет потерян",
                            yes_text="ДА", no_text="НЕТ"
                        )
                        self.confirm.show()
                        sound_manager.play("ui_select")
        return None

    def _get_arch(self):
        """PERF-2: Cached arch surface."""
        if self._arch_cache is None:
            arch_w, arch_h = 600, 640
            arch_surf = pygame.Surface((arch_w, arch_h), pygame.SRCALPHA)
            arch_surf.fill((12, 8, 5, 220))
            inner_margin = 12
            inner = pygame.Surface((arch_w - inner_margin * 2, arch_h - inner_margin * 2), pygame.SRCALPHA)
            inner.fill((25, 18, 12, 200))
            arch_surf.blit(inner, (inner_margin, inner_margin))
            pygame.draw.rect(arch_surf, CONFESS_IRON, (0, 0, arch_w, arch_h), 3)
            pygame.draw.rect(arch_surf, CONFESS_IRON_LIGHT, (4, 4, arch_w - 8, arch_h - 8), 1)
            for cx_, cy_ in [(10, 10), (arch_w - 10, 10), (10, arch_h - 10), (arch_w - 10, arch_h - 10)]:
                pygame.draw.circle(arch_surf, CONFESS_IRON_LIGHT, (cx_, cy_), 5)
                pygame.draw.circle(arch_surf, (150, 150, 155), (cx_ - 1, cy_ - 1), 2)
            self._arch_cache = arch_surf
        return self._arch_cache

    def _draw_bg(self, screen):
        """Dark overlay + wood slats + arch."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))
        wood = generate_wood_slats(WIDTH, HEIGHT)
        wood_alpha = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        wood_alpha.blit(wood, (0, 0))
        wood_alpha.set_alpha(200)
        screen.blit(wood_alpha, (0, 0))
        screen.blit(self._get_arch(), ((WIDTH - 600) // 2, 30))

    def _draw_title(self, screen, big_font):
        """Title plaque with gold text."""
        plaque_w, plaque_h = 300, 50
        plaque_x = (WIDTH - plaque_w) // 2
        plaque_y = 50
        pygame.draw.rect(screen, (45, 32, 20), (plaque_x, plaque_y, plaque_w, plaque_h), border_radius=6)
        pygame.draw.rect(screen, (65, 48, 32), (plaque_x + 2, plaque_y + 2, plaque_w - 4, plaque_h - 4), 1, border_radius=5)
        pygame.draw.rect(screen, CONFESS_GOLD, (plaque_x, plaque_y, plaque_w, plaque_h), 2, border_radius=6)
        for ox, oy in [(plaque_x + 6, plaque_y + 6), (plaque_x + plaque_w - 6, plaque_y + 6),
                        (plaque_x + 6, plaque_y + plaque_h - 6), (plaque_x + plaque_w - 6, plaque_y + plaque_h - 6)]:
            pygame.draw.circle(screen, CONFESS_IRON_LIGHT, (ox, oy), 3)
        title = big_font.render("ПАУЗА", True, CONFESS_GOLD)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, plaque_y + plaque_h // 2 - title.get_height() // 2))

    def _draw_stats(self, screen, small_font):
        """Stats panel on parchment."""
        if not (self.game and self.game.player):
            return
        p = self.game.player
        from hud import generate_parchment, PARCH_INK, PARCH_INK_DIM
        stats_w, stats_h = 340, 180
        stats_x = (WIDTH - stats_w) // 2
        stats_y = 115
        parch = generate_parchment(stats_w, stats_h, seed=101)
        screen.blit(parch, (stats_x, stats_y))
        y = stats_y + 12
        for label, value in [
            ("Убийства", str(p.kills)),
            ("Уровень", str(p.level)),
            ("Золото", str(p.gold)),
            ("Волна", str(self.game.wave_mgr.wave)),
            ("Время", f"{int(self.game.elapsed) // 60}:{int(self.game.elapsed) % 60:02d}"),
        ]:
            text = small_font.render(f"{label}: {value}", True, PARCH_INK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 20
        y += 8
        bt = small_font.render("-- БИЛД --", True, CONFESS_GOLD)
        screen.blit(bt, (WIDTH // 2 - bt.get_width() // 2, y))
        y += 20
        for w in p.weapons:
            evolved = " [MAX]" if w.evolved else ""
            t = small_font.render(f"{w.name} Lv{w.level}{evolved}", True, PARCH_INK)
            screen.blit(t, (stats_x + 16, y))
            y += 18
        from xp_system import PASSIVE_DEFS
        for pid, lvl in p.passives.items():
            pname = PASSIVE_DEFS.get(pid, {}).get("name", pid)
            t = small_font.render(f"{pname} Lv{lvl}", True, PARCH_INK_DIM)
            screen.blit(t, (stats_x + 16, y))
            y += 18

    def _draw_tablets(self, screen, font):
        """Stone tablet menu items."""
        tablet_x = (WIDTH - self.TABLET_W) // 2
        arch_h = 640
        tablet_start_y = 30 + arch_h - self.TABLET_H * len(self.items) - self.TABLET_GAP * (len(self.items) - 1) - 50
        for i, item in enumerate(self.items):
            ty = tablet_start_y + i * (self.TABLET_H + self.TABLET_GAP)
            draw_stone_tablet(screen, tablet_x, ty, self.TABLET_W, self.TABLET_H, item, i == self.selected, font)

    def _draw_candles(self, screen):
        """Candle particles and glow spots."""
        for c in self._candles:
            if c.alpha > 0:
                ps = pygame.Surface((c.size * 2, c.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(ps, (c.color[0], c.color[1], c.color[2], c.alpha), (c.size, c.size), c.size)
                screen.blit(ps, (int(c.x) - c.size, int(c.y) - c.size))
        glow_phase = math.sin(self._timer * 2.0) * 0.15 + 0.85
        glow_alpha = int(40 * glow_phase)
        for gx, gy in [(130, HEIGHT - 90), (WIDTH - 130, HEIGHT - 90)]:
            gs = pygame.Surface((60, 60), pygame.SRCALPHA)
            gs.fill((255, 200, 80, glow_alpha))
            screen.blit(gs, (gx - 30, gy - 30))
            fh = int(10 * glow_phase)
            pygame.draw.ellipse(screen, (255, 200, 80), (gx - 3, gy - fh, 6, fh + 4))
            pygame.draw.ellipse(screen, (255, 240, 180), (gx - 2, gy - fh + 2, 4, fh))

    def draw(self, screen):
        """ARCH-7: Refactored draw — delegates to 6 helper methods."""
        self.draw_background(screen)
        font, big_font, small_font = _get_fonts()
        self._draw_bg(screen)
        self._draw_title(screen, big_font)
        self._draw_stats(screen, small_font)
        self._draw_tablets(screen, font)
        self._draw_candles(screen)
        hint = small_font.render("Up/Down | Enter | ESC", True, (100, 90, 70))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))
        if self.confirm and self.confirm.active:
            self.confirm.draw(screen, font, small_font)


class GameOverScene(Scene):
    """Сцена Game Over с анимациями и полной статистикой."""
    
    def __init__(self, menu, meta, lobby, game=None):
        super().__init__()
        self.menu = menu
        self.meta = meta
        self.lobby = lobby
        self.game = game  # ссылка на Game для доступа к player
        self.stats = {}
        self.animator = None
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.stats = kwargs.get("stats", {})
        self.menu.state = "game_over"
        self.menu.final_stats = self.stats
        # Сбрасываем аниматор
        from game_over_screen import GameOverAnimator
        self.animator = GameOverAnimator()
    
    def update(self, dt):
        if self.animator:
            self.animator.update(dt)
    
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
        from game_over_screen import draw_game_over, GameOverAnimator
        font, big_font, small_font = _get_fonts()
        # Guard: animator мог не инициализироваться
        if self.animator is None:
            self.animator = GameOverAnimator()
            self.animator.timer = 5.0  # skip animations
        # player берём из game (если есть)
        player = None
        if self.game and hasattr(self.game, 'player'):
            player = self.game.player
        draw_game_over(screen, self.stats, self.animator,
                       player=player, menu=self.menu,
                       font=font, big_font=big_font, small_font=small_font)


class LobbyScene(Scene):
    """Сцена лобби."""
    
    def __init__(self, lobby, meta, menu):
        super().__init__()
        self.lobby = lobby
        self.meta = meta
        self.menu = menu
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.lobby.activate(self.meta, menu=self.menu)
        # Загружаем рекорды
        try:
            from leaderboard import get_entries
            self.lobby.leaderboard_entries = get_entries()[:10]
        except Exception:
            self.lobby.leaderboard_entries = []
    
    def handle_events(self, events):
        for event in events:
            result = self.lobby.handle_event(event)
            if result == "play":
                return "run_prep"
            elif result == "bestiary":
                return "bestiary"
            elif result == "codex":
                return "codex"
            elif isinstance(result, tuple) and result[0] == "settings":
                return result  # pass (name, kwargs) to SceneManager
        return None
    
    def update(self, dt):
        self.lobby.update(dt)
    
    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        self.lobby.draw(screen, font, big_font, small_font)


class BestiaryScene(Scene):
    """Сцена бестиария (обратная совместимость)."""
    
    def __init__(self, meta, lobby):
        super().__init__()
        self.meta = meta
        self.lobby = lobby
        self.bestiary = None
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        from bestiary import BestiaryScreen
        self.bestiary = BestiaryScreen()
        self.bestiary.activate(self.meta)
    
    def handle_events(self, events):
        for event in events:
            if self.bestiary:
                result = self.bestiary.handle_event(event)
                if result == "back":
                    return "lobby"
        return None
    
    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        if self.bestiary:
            self.bestiary.draw(screen, font, big_font, small_font)


class CodexScene(Scene):
    """Сцена кодекса: Враги / Оружие / Эволюции."""
    
    def __init__(self, meta, lobby):
        super().__init__()
        self.meta = meta
        self.lobby = lobby
        self.codex = None
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        from bestiary import CodexScreen
        self.codex = CodexScreen()
        self.codex.activate(self.meta)
    
    def handle_events(self, events):
        for event in events:
            if self.codex:
                result = self.codex.handle_event(event)
                if result == "back":
                    return "lobby"
        return None
    
    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        if self.codex:
            self.codex.draw(screen, font, big_font, small_font)


class SettingsScene(Scene):
    """Экран настроек (v2): UISlider для громкости, UIButton для "Назад"."""
    
    def __init__(self):
        super().__init__()
        self.selected = 0
        self.volume = 7
        self.fullscreen = False
        self.show_fps = False
        self.show_controls = False
        self.items_count = 4
        self.return_to = "title"
        
        # UI компоненты (v2)
        from ui_components import UISlider, UIButton, UIPanel
        from ui_theme import GOLD_LEAF
        
        self._panel = None
        self._slider = None
        self._btn_back = None
        self._init_components()
    
    def _init_components(self):
        """Create UI components."""
        from ui_components import UISlider, UIButton, UIPanel
        cx = WIDTH // 2
        # Panel
        self._panel = UIPanel(cx - 280, 120, 560, 440, title="НАСТРОЙКИ")
        # Volume slider
        self._slider = UISlider(cx - 220, 220, 400, "Громкость", self.volume / 10.0,
                                 on_change=self._on_volume_change)
        # Back button
        from ui_components import UIButton
        self._btn_back = UIButton(cx - 100, 520, 200, 44, "НАЗАД", "ghost",
                                   callback=self._on_back)
    
    def _on_volume_change(self, value):
        self.volume = int(value * 10)
        self._apply()
    
    def _on_back(self):
        pass  # ESC handles return
    
    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.selected = 0
        self.return_to = kwargs.get("return_to", "title")
        self._apply()
        # Sync slider with current volume
        if self._slider:
            self._slider.value = self.volume / 10.0
    
    def _apply(self):
        try:
            import sound_manager
            sound_manager.set_volume(self.volume / 10.0)
        except Exception:
            pass
    
    def handle_events(self, events):
        for event in events:
            # Slider handles its own events
            if self._slider and self._slider.handle_event(event):
                return None
            # Back button
            if self._btn_back:
                self._btn_back.handle_event(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return self.return_to
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % self.items_count
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % self.items_count
                elif event.key == pygame.K_LEFT:
                    if self.selected == 0:
                        self.volume = max(0, self.volume - 1)
                        if self._slider:
                            self._slider.value = self.volume / 10.0
                        self._apply()
                    elif self.selected == 1:
                        self.fullscreen = False
                    elif self.selected == 2:
                        self.show_fps = False
                elif event.key == pygame.K_RIGHT:
                    if self.selected == 0:
                        self.volume = min(10, self.volume + 1)
                        if self._slider:
                            self._slider.value = self.volume / 10.0
                        self._apply()
                    elif self.selected == 1:
                        self.fullscreen = True
                    elif self.selected == 2:
                        self.show_fps = True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if self.selected == 1:
                        self.fullscreen = not self.fullscreen
                    elif self.selected == 2:
                        self.show_fps = not self.show_fps
                    elif self.selected == 3:
                        self.show_controls = not self.show_controls
        return None
    
    def draw(self, screen):
        from ui_theme import GOLD_LEAF, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM, STONE_LIGHT, STONE_BASE, IRON
        screen.fill(STONE_BASE)
        cx = WIDTH // 2
        
        # Panel
        if self._panel:
            self._panel.draw(screen)
        
        # Volume slider
        if self._slider:
            self._slider.is_focused = (self.selected == 0)
            self._slider.draw(screen)
        
        # Toggle settings
        font, big_font, small_font = _get_fonts()
        toggles = [
            ("Fullscreen", self.fullscreen, 1),
            ("Показ FPS", self.show_fps, 2),
            ("Управление", self.show_controls, 3),
        ]
        y = 310
        for label, val, idx in toggles:
            is_sel = (self.selected == idx)
            fill = STONE_LIGHT if is_sel else STONE_BASE
            border = GOLD_LEAF if is_sel else IRON
            pygame.draw.rect(screen, fill, (cx - 220, y, 440, 40), border_radius=6)
            pygame.draw.rect(screen, border, (cx - 220, y, 440, 40), 1 if not is_sel else 2, border_radius=6)
            
            name_color = TEXT_PRIMARY if is_sel else TEXT_SECONDARY
            name = font.render(label, True, name_color)
            screen.blit(name, (cx - 200, y + 10))
            
            toggle_color = (80, 200, 80) if val else TEXT_DIM
            toggle_text = "ДА" if val else "НЕТ"
            t = font.render(toggle_text, True, toggle_color)
            screen.blit(t, (cx + 160, y + 10))
            y += 50
        
        # Controls help
        if self.show_controls:
            ctrl_y = y + 20
            pygame.draw.rect(screen, (30, 25, 45), (cx - 200, ctrl_y, 400, 140), border_radius=8)
            pygame.draw.rect(screen, IRON, (cx - 200, ctrl_y, 400, 140), 1, border_radius=8)
            ctrl_title = font.render("УПРАВЛЕНИЕ", True, TEXT_PRIMARY)
            screen.blit(ctrl_title, (cx - ctrl_title.get_width() // 2, ctrl_y + 10))
            controls = [
                "WASD - движение", "1/2/3 - выбор при левелапе",
                "ESC/P - пауза", "R - заново (Game Over)", "TAB - сменить таб (лобби)",
            ]
            for j, c in enumerate(controls):
                t = small_font.render(c, True, TEXT_SECONDARY)
                screen.blit(t, (cx - 170, ctrl_y + 36 + j * 20))
        
        # Back button
        if self._btn_back:
            self._btn_back.is_focused = (self.selected == self.items_count - 1)
            self._btn_back.draw(screen)
        
        # Hint
        hint = small_font.render("↑↓ навигация  |  ← → изменить  |  ESC назад", True, TEXT_DIM)
        screen.blit(hint, (cx - hint.get_width() // 2, HEIGHT - 40))


class RunPrepScene(Scene):
    """Экран подготовки к забегу (C5).
    Показывает выбранного персонажа, карту, аркану, бан-лист.
    Enter - начать забег, ESC - назад в лобби.
    """

    def __init__(self):
        super().__init__()
        self.menu = None
        self.meta = None

    def enter(self, **kwargs):
        super().enter(**kwargs)
        self.menu = kwargs.get("menu")
        self.meta = kwargs.get("meta")

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "lobby"
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_manager.play("ui_confirm")
                    return "game"
        return None

    def draw(self, screen):
        font, big_font, small_font = _get_fonts()
        screen.fill(DARK_BG)
        cx = WIDTH // 2

        # Заголовок
        title = big_font.render("ПОДГОТОВКА К ЗАБЕГУ", True, GOLD_LEAF)
        screen.blit(title, (cx - title.get_width() // 2, 30))

        y = 100

        # --- Персонаж ---
        if self.menu:
            from player import CHARACTERS
            cid = self.menu.selected_char
            c = CHARACTERS.get(cid, {})
            char_label = font.render("ПЕРСОНАЖ", True, (150, 150, 200))
            screen.blit(char_label, (60, y))
            y += 28

            char_name = font.render(c.get("name", cid), True, c.get("color", TEXT_PRIMARY))
            screen.blit(char_name, (80, y))
            y += 24

            hp_text = small_font.render(f"HP: {c.get('hp', 100)}  SPD: {c.get('speed', 3.0):.1f}", True, (80, 200, 80))
            screen.blit(hp_text, (80, y))
            y += 20

            wep_text = small_font.render(f"Оружие: {c.get('start_weapon', '?')}", True, (150, 150, 200))
            screen.blit(wep_text, (80, y))
            y += 20

            desc_text = small_font.render(c.get("desc", ""), True, (180, 180, 160))
            screen.blit(desc_text, (80, y))
            y += 40

        # --- Карта ---
        if self.menu:
            from menu import MAPS
            mid = self.menu.selected_map
            m = MAPS.get(mid, {})
            map_label = font.render("КАРТА", True, (150, 150, 200))
            screen.blit(map_label, (60, y))
            y += 28

            map_name = font.render(m.get("name", mid), True, TEXT_PRIMARY)
            screen.blit(map_name, (80, y))
            y += 24

            map_desc = small_font.render(m.get("desc", ""), True, (180, 180, 180))
            screen.blit(map_desc, (80, y))
            y += 20

            diff = m.get("diff", 1)
            stars = "\u2605" * diff + "\u2606" * (5 - diff)
            diff_text = small_font.render(f"Сложность: {stars}", True, (200, 180, 100))
            screen.blit(diff_text, (80, y))
            y += 20

            bonus_text = small_font.render(m.get("bonus", ""), True, (100, 200, 100))
            screen.blit(bonus_text, (80, y))
            y += 40

        # --- Аркана ---
        from arcana import ARCANA_DEFS
        arcana_label = font.render("АРКАНА", True, (150, 150, 200))
        screen.blit(arcana_label, (60, y))
        y += 28

        if self.meta and self.meta.selected_arcana:
            adef = ARCANA_DEFS.get(self.meta.selected_arcana, {})
            arcana_name = font.render(adef.get("name", "?"), True, adef.get("color", TEXT_PRIMARY))
            screen.blit(arcana_name, (80, y))
            y += 24
            arcana_desc = small_font.render(adef.get("desc", ""), True, (180, 180, 160))
            screen.blit(arcana_desc, (80, y))
            y += 20
        else:
            none_text = small_font.render("Не выбрана", True, (100, 100, 100))
            screen.blit(none_text, (80, y))
            y += 20
        y += 20

        # --- Бан-лист ---
        ban_label = font.render("ЗАБАНЕННЫЕ ПРЕДМЕТЫ", True, (150, 150, 200))
        screen.blit(ban_label, (60, y))
        y += 28

        if self.meta and self.meta.banned_items:
            from weapons import WEAPON_DEFS
            from xp_system import PASSIVE_DEFS
            for bid in self.meta.banned_items:
                if bid in WEAPON_DEFS:
                    wdef = WEAPON_DEFS[bid]
                    t = small_font.render(f"[W] {wdef['name']}", True, wdef.get("color", (200, 80, 80)))
                elif bid in PASSIVE_DEFS:
                    pdef = PASSIVE_DEFS[bid]
                    t = small_font.render(f"[P] {pdef['name']}", True, pdef.get("color", (80, 200, 80)))
                else:
                    t = small_font.render(f"  {bid}", True, (150, 150, 150))
                screen.blit(t, (80, y))
                y += 20
        else:
            none_text = small_font.render("Нет забаненных", True, (100, 100, 100))
            screen.blit(none_text, (80, y))

        # Подсказка
        hint = small_font.render("Enter - начать забег  |  ESC - назад", True, (100, 100, 100))
        screen.blit(hint, (cx - hint.get_width() // 2, HEIGHT - 30))
