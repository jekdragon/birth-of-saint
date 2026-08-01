"""Refactor PauseOverlay.draw() into helper methods with cached arch."""
import re

with open('scenes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the draw method in PauseOverlay
# We need to replace from "    def draw(self, screen):" to the next class definition
# But only the one inside PauseOverlay

# Strategy: find "class PauseOverlay" then find its draw method, replace it
pause_class_start = content.index('class PauseOverlay')
# Find the draw method after PauseOverlay
draw_start = content.index('    def draw(self, screen):', pause_class_start)
# Find the next class or end of file
next_class = content.find('\nclass ', draw_start + 1)
if next_class == -1:
    next_class = len(content)

old_draw = content[draw_start:next_class]

new_methods = '''    def _get_arch(self):
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
        title = big_font.render("\u041f\u0410\u0423\u0417\u0410", True, CONFESS_GOLD)
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
            ("\u0423\u0431\u0438\u0439\u0441\u0442\u0432\u0430", str(p.kills)),
            ("\u0423\u0440\u043e\u0432\u0435\u043d\u044c", str(p.level)),
            ("\u0417\u043e\u043b\u043e\u0442\u043e", str(p.gold)),
            ("\u0412\u043e\u043b\u043d\u0430", str(self.game.wave_mgr.wave)),
            ("\u0412\u0440\u0435\u043c\u044f", f"{int(self.game.elapsed) // 60}:{int(self.game.elapsed) % 60:02d}"),
        ]:
            text = small_font.render(f"{label}: {value}", True, PARCH_INK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 20
        y += 8
        bt = small_font.render("-- \u0411\u0418\u041b\u0414 --", True, CONFESS_GOLD)
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

'''

content = content[:draw_start] + new_methods + content[next_class:]

with open('scenes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("ARCH-7 + PERF-2: PauseOverlay refactored into 6 helpers + cached arch")
