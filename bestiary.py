"""
Рождение святого - Кодекс
Полный кодекс: Враги / Оружие / Эволюции.
Экран с тремя вкладками, kill tracking, описания, рецепты.
Stained-glass medallion grid (vitrazh style) for enemies.
"""
import math
import pygame
from config import WIDTH, HEIGHT, WHITE, GOLD, DARK_BG, RED, GREEN
from enemies import ENEMY_TYPES
from weapons import WEAPON_DEFS, PASSIVE_DEFS, EVOLUTIONS


# ============================================================
# Описания врагов
# ============================================================
ENEMY_DESCRIPTIONS = {
    "neophyte":  "Слуга тьмы, первый из проклятых. Слабый, но приходит толпами.",
    "acolyte":   "Ученик еретика, быстрый и жадный. Обходит с флангов.",
    "heretic":   "Толстокожий фанатик, не знает пощады. Тяжело убить.",
    "demon":     "Пламенный стрелок из глубин ада. Мечет огненные снаряды.",
    "fanatic":   "Самоубийца, взрывается рядом с врагом. Держись подальше!",
    "antichrist":"Предвестник Апокалипсиса, повелитель тьмы. Босс.",
    "ghost":     "Бесплотная тень, проходит сквозь стены и препятствия.",
    "gargoyle":  "Каменный страж, тяжёлый и неумолимый. Медленный, но сильный.",
    "shade":     "Невидимый охотник, бьёт из темноты. Очень быстрый.",
    "cultist":   "Тёмный жрец, мечет проклятия издалека. Опасен на расстоянии.",
    "pope":      "Повелитель культа, финальное испытание. Легион под командованием.",
}

# Порядок отображения (по сложности)
ENEMY_ORDER = [
    "neophyte", "acolyte", "heretic", "ghost", "fanatic",
    "shade", "cultist", "gargoyle", "demon", "antichrist", "pope",
]

# Иконки (цвета для простых прямоугольников)
ENEMY_COLORS = {
    "neophyte":   (120, 120, 150),
    "acolyte":    (150, 100, 100),
    "heretic":    (180, 120, 60),
    "demon":      (220, 60, 40),
    "fanatic":    (200, 150, 50),
    "antichrist": (180, 30, 30),
    "ghost":      (150, 150, 200),
    "gargoyle":   (100, 100, 120),
    "shade":      (80, 80, 120),
    "cultist":    (120, 60, 150),
    "pope":       (200, 180, 100),
}


# ============================================================
# Описания оружия
# ============================================================
WEAPON_DESCRIPTIONS = {
    "whip": {
        "desc": "Священный кнут, бьёт дугой перед владельцем. Эффективен против групп.",
        "type_label": "Ближний бой",
        "base_stats": "Урон: 12 | Кулдаун: 1.3с | Длина: 115",
    },
    "fire": {
        "desc": "Кары небесные в миниатюре. Снаряды летят к ближайшим врагам.",
        "type_label": "Снаряды",
        "base_stats": "Урон: 10 | Кулдаун: 1.0с | Снаряды: 1",
    },
    "halo": {
        "desc": "Светящиеся орбы кружат вокруг святого, сжигая всё прикосновение.",
        "type_label": "Аура",
        "base_stats": "Урон: 4 | Орбы: 2 | Радиус: 74",
    },
    "rosary": {
        "desc": "Чётки-бумеранг: летят вперёд и возвращаются, бьют дважды.",
        "type_label": "Бумеранг",
        "base_stats": "Урон: 22 | Скорость: 5.0 | Дальность: 250",
    },
    "lightning": {
        "desc": "Гнев небес обрушивается на случайного врага и поражает область.",
        "type_label": "Удар",
        "base_stats": "Урон: 25 | Кулдаун: 1.5с | AoE: 50",
    },
    "prayer": {
        "desc": "Волна святой энергии расходится от проповедника, отталкивая нечестивых.",
        "type_label": "Кольцо",
        "base_stats": "Урон: 15 | Кулдаун: 2.0с | Радиус: 150",
    },
    "incense": {
        "desc": "Кадило вращается вокруг владельца, окутывая врагов священным дымом.",
        "type_label": "Орбита",
        "base_stats": "Урон: 8 | Кадил: 1 | Радиус: 100",
    },
    "cross": {
        "desc": "Святой крест летит в направлении движения, пронзая врагов насквозь.",
        "type_label": "Направленный",
        "base_stats": "Урон: 20 | Кулдаун: 1.8с | Пробитие: 1",
    },
    "bell": {
        "desc": "Колокол гремит мощной AoE волной. Долгий кулдаун, но сокрушительный удар.",
        "type_label": "Кольцо",
        "base_stats": "Урон: 25 | Кулдаун: 3.0с | Радиус: 200",
    },
}

# Порядок оружия для кодекса
WEAPON_ORDER = [
    "whip", "fire", "halo", "rosary", "lightning", "prayer",
    "incense", "cross", "bell",
]

# ============================================================
# Табы кодекса
# ============================================================
CODEX_TABS = ["Враги", "Оружие", "Эволюции"]
CODEX_TAB_COLORS = {
    "Враги": (200, 80, 80),
    "Оружие": (80, 160, 255),
    "Эволюции": (255, 215, 0),
}

# ============================================================
# Stained-glass medallion (vitrazh) constants
# ============================================================
MEDALLION_RADIUS = 38
MEDALLION_GAP = 18
GRID_COLS = 4
GRID_X = 25
GRID_Y = 148

# Parchment palette
PARCH_DARK = (18, 14, 8)
PARCH_MID = (32, 26, 18)
PARCH_BASE = (48, 40, 30)
PARCH_LIGHT = (58, 50, 38)
PARCH_INK = (200, 190, 160)
PARCH_INK_DIM = (140, 130, 110)


class CodexScreen:
    """Полный кодекс: Враги / Оружие / Эволюции."""

    def __init__(self):
        self.tab_index = 0
        self.selected = 0
        self.scroll = 0
        self.meta = None

    def activate(self, meta):
        self.meta = meta
        self.selected = 0
        self.scroll = 0

    def handle_event(self, event) -> str | None:
        """Returns: 'back', None"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"

            # Смена таба
            if event.key == pygame.K_TAB:
                self.tab_index = (self.tab_index + 1) % len(CODEX_TABS)
                self.selected = 0
                self.scroll = 0
                return None

            # Навигация
            if event.key == pygame.K_UP:
                self.selected = max(0, self.selected - 1)
                self._auto_scroll_up()
            elif event.key == pygame.K_DOWN:
                max_idx = self._max_index()
                self.selected = min(max_idx, self.selected + 1)
                self._auto_scroll_down()

            # Листание деталей (Left/Right для врагов)
            if event.key == pygame.K_LEFT:
                if self.tab_index == 0:
                    self.tab_index = (self.tab_index - 1) % len(CODEX_TABS)
                    self.selected = 0
                    self.scroll = 0
            elif event.key == pygame.K_RIGHT:
                if self.tab_index == 0:
                    self.tab_index = (self.tab_index + 1) % len(CODEX_TABS)
                    self.selected = 0
                    self.scroll = 0

        return None

    def _max_index(self):
        if self.tab_index == 0:
            return len(ENEMY_ORDER) - 1
        elif self.tab_index == 1:
            return len(WEAPON_ORDER) - 1
        else:
            return len(EVOLUTIONS) - 1

    def _auto_scroll_up(self):
        max_visible = self._max_visible()
        if self.selected < self.scroll:
            self.scroll = self.selected

    def _auto_scroll_down(self):
        max_visible = self._max_visible()
        if self.selected >= self.scroll + max_visible:
            self.scroll = self.selected - max_visible + 1

    def _max_visible(self):
        if self.tab_index == 0:
            return 10  # врагов на экране
        elif self.tab_index == 1:
            return 7
        else:
            return 6

    def draw(self, surface, font, big_font, small_font):
        surface.fill(DARK_BG)
        cx = WIDTH // 2

        # Заголовок
        title = big_font.render("КОДЕКС", True, GOLD)
        surface.blit(title, (cx - title.get_width() // 2, 15))

        # Табы
        tab_y = 70
        tab_x = 40
        for i, tab_name in enumerate(CODEX_TABS):
            is_active = (i == self.tab_index)
            color = CODEX_TAB_COLORS[tab_name] if is_active else (100, 100, 100)
            label = f"[{tab_name}]" if is_active else tab_name
            t = font.render(label, True, color)
            surface.blit(t, (tab_x, tab_y))
            if is_active:
                pygame.draw.line(surface, color, (tab_x, tab_y + 22),
                                (tab_x + t.get_width(), tab_y + 22), 2)
            tab_x += t.get_width() + 24

        content_y = tab_y + 35

        if self.tab_index == 0:
            self._draw_enemies(surface, font, big_font, small_font, content_y)
        elif self.tab_index == 1:
            self._draw_weapons(surface, font, big_font, small_font, content_y)
        elif self.tab_index == 2:
            self._draw_evolutions(surface, font, big_font, small_font, content_y)

        # Подсказка
        hint = small_font.render("TAB - вкладка  |  Up/Down - выбор  |  ESC - назад", True, (80, 80, 80))
        surface.blit(hint, (cx - hint.get_width() // 2, HEIGHT - 25))

    # ============================================================
    # Вкладка ВРАГИ — Stained-glass medallion grid (vitrazh)
    # ============================================================
    def _draw_enemies(self, surface, font, big_font, small_font, y_start):
        cx = WIDTH // 2

        # Прогресс
        unlocked = self._count_unlocked()
        total = len(ENEMY_ORDER)
        progress_text = font.render(f"{unlocked}/{total} врагов открыто", True, (180, 180, 180))
        surface.blit(progress_text, (cx - progress_text.get_width() // 2, y_start))

        # Полоска прогресса
        bar_x, bar_y = cx - 100, y_start + 25
        bar_w, bar_h = 200, 8
        pygame.draw.rect(surface, (40, 40, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * unlocked / total) if total > 0 else 0
        pygame.draw.rect(surface, (80, 200, 80), (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        # --- Grid of stained-glass medallions ---
        for i, eid in enumerate(ENEMY_ORDER):
            row = i // GRID_COLS
            col = i % GRID_COLS
            mcx = GRID_X + col * (MEDALLION_RADIUS * 2 + MEDALLION_GAP) + MEDALLION_RADIUS
            mcy = GRID_Y + row * (MEDALLION_RADIUS * 2 + MEDALLION_GAP) + MEDALLION_RADIUS

            is_sel = (i == self.selected)
            is_unlocked = self._is_enemy_unlocked(eid)

            self._draw_medallion(surface, eid, mcx, mcy, MEDALLION_RADIUS,
                               is_sel, is_unlocked, small_font)

        # --- Parchment details panel ---
        panel_x = GRID_X + GRID_COLS * (MEDALLION_RADIUS * 2 + MEDALLION_GAP) + 20
        panel_y = GRID_Y
        panel_w = WIDTH - panel_x - 20
        panel_h = HEIGHT - panel_y - 50

        self._draw_parchment_panel(surface, panel_x, panel_y, panel_w, panel_h)

        # Details content
        if self.selected < len(ENEMY_ORDER):
            eid = ENEMY_ORDER[self.selected]
            self._draw_enemy_details(surface, eid, panel_x, panel_y, panel_w, panel_h,
                                    font, big_font, small_font)

    # ============================================================
    # Stained-glass medallion renderer
    # ============================================================
    def _draw_medallion(self, surface, eid, cx, cy, radius, is_sel, is_unlocked, font):
        """Draw a single stained-glass medallion (vitrazh)."""
        if is_unlocked:
            color = ENEMY_COLORS.get(eid, (120, 120, 120))
            r, g, b = color

            # Lead came (dark outer frame)
            pygame.draw.circle(surface, (18, 15, 12), (cx, cy), radius + 4)
            # Main glass fill
            pygame.draw.circle(surface, color, (cx, cy), radius)

            # Inner glow (lighter tone, shifted up-left for directional light)
            glow_r = min(255, r + 55)
            glow_g = min(255, g + 55)
            glow_b = min(255, b + 55)
            glow_rad = int(radius * 0.55)
            pygame.draw.circle(surface, (glow_r, glow_g, glow_b),
                             (cx - radius // 5, cy - radius // 5), glow_rad)

            # Specular highlight (bright spot, top-left)
            spec_r = min(255, r + 130)
            spec_g = min(255, g + 130)
            spec_b = min(255, b + 130)
            spec_rad = max(3, int(radius * 0.2))
            pygame.draw.circle(surface, (spec_r, spec_g, spec_b),
                             (cx - radius // 3, cy - radius // 3), spec_rad)

            # White glint on specular
            pygame.draw.circle(surface, (255, 255, 255),
                             (cx - radius // 3, cy - radius // 3), max(1, spec_rad // 2))

            # Lead came cross pattern
            lead = (25, 20, 15)
            pygame.draw.line(surface, lead,
                           (cx - radius + 10, cy), (cx + radius - 10, cy), 2)
            pygame.draw.line(surface, lead,
                           (cx, cy - radius + 10), (cx, cy + radius - 10), 2)

            # First letter of enemy name as portrait symbol
            etype = ENEMY_TYPES.get(eid, {})
            name = etype.get("name", eid)
            first = name[0].upper() if name else "?"
            char_t = font.render(first, True, (220, 215, 200))
            surface.blit(char_t, (cx - char_t.get_width() // 2,
                                  cy - char_t.get_height() // 2))

            # Kill count below medallion
            kills = self._get_kills(eid)
            kt = font.render(f"x{kills}", True, (160, 155, 140))
            surface.blit(kt, (cx - kt.get_width() // 2, cy + radius + 5))

            # Name label
            short = name if len(name) <= 10 else name[:9] + ".."
            nt = font.render(short, True, (130, 125, 110))
            surface.blit(nt, (cx - nt.get_width() // 2, cy + radius + 21))

        else:
            # --- Dark fractured glass (locked) ---
            pygame.draw.circle(surface, (12, 10, 8), (cx, cy), radius + 4)
            pygame.draw.circle(surface, (30, 28, 38), (cx, cy), radius)

            # Crack lines (deterministic from eid hash)
            seed = sum(ord(c) for c in eid) * 137
            crack_col = (22, 20, 30)
            for ci in range(5):
                angle = math.radians((seed + ci * 73) % 360)
                length = radius * (0.4 + ((seed + ci * 31) % 40) / 100.0)
                ex = cx + int(math.cos(angle) * length)
                ey = cy + int(math.sin(angle) * length)
                pygame.draw.line(surface, crack_col, (cx, cy), (ex, ey), 1)
                # Branch crack
                ba = angle + math.radians(25 + (ci * 17) % 30)
                bl = length * 0.5
                bx = ex + int(math.cos(ba) * bl)
                by = ey + int(math.sin(ba) * bl)
                pygame.draw.line(surface, crack_col, (ex, ey), (bx, by), 1)

            # Dim "?" symbol
            qt = font.render("?", True, (55, 50, 62))
            surface.blit(qt, (cx - qt.get_width() // 2, cy - qt.get_height() // 2))

        # --- Selection glow ---
        if is_sel:
            pygame.draw.circle(surface, GOLD, (cx, cy), radius + 6, 3)
            glow_dim = (GOLD[0] // 3, GOLD[1] // 3, GOLD[2] // 3)
            pygame.draw.circle(surface, glow_dim, (cx, cy), radius + 10, 2)

    # ============================================================
    # Parchment panel with singed edges
    # ============================================================
    def _draw_parchment_panel(self, surface, x, y, w, h):
        """Draw parchment background with singed/burned edges."""
        # Layer 1: outer charred edge
        pygame.draw.rect(surface, PARCH_DARK, (x, y, w, h), border_radius=8)
        # Layer 2: smoke-stained ring
        pygame.draw.rect(surface, PARCH_MID, (x + 4, y + 4, w - 8, h - 8), border_radius=6)
        # Layer 3: parchment base
        pygame.draw.rect(surface, PARCH_BASE, (x + 10, y + 10, w - 20, h - 20), border_radius=5)
        # Layer 4: lighter inner area
        pygame.draw.rect(surface, PARCH_LIGHT, (x + 14, y + 14, w - 28, h - 28), border_radius=4)

        # Corner burns (darker patches)
        bsz = 22
        corners = [
            (x + 12, y + 12),
            (x + w - 12 - bsz, y + 12),
            (x + 12, y + h - 12 - bsz),
            (x + w - 12 - bsz, y + h - 12 - bsz),
        ]
        for cx_, cy_ in corners:
            pygame.draw.rect(surface, PARCH_MID, (cx_, cy_, bsz, bsz), border_radius=5)

        # Decorative top border line (ink)
        pygame.draw.line(surface, (80, 70, 50), (x + 18, y + 16), (x + w - 18, y + 16), 1)

    # ============================================================
    # Enemy details on parchment
    # ============================================================
    def _draw_enemy_details(self, surface, eid, px, py, pw, ph,
                           font, big_font, small_font):
        """Draw enemy details inside parchment panel."""
        etype = ENEMY_TYPES.get(eid, {})
        is_unlocked = self._is_enemy_unlocked(eid)

        ink = PARCH_INK
        ink_dim = PARCH_INK_DIM
        ink_red = (180, 60, 40)
        ink_green = (50, 140, 50)
        ink_blue = (60, 100, 180)
        ink_gold = (200, 170, 50)

        ix = px + 22
        iy = py + 24

        if is_unlocked:
            # --- Enemy icon (stained glass medallion, larger) ---
            icon_color = ENEMY_COLORS.get(eid, (120, 120, 120))
            ir = 24
            icx = ix + ir + 4
            icy = iy + ir + 4

            pygame.draw.circle(surface, (18, 15, 12), (icx, icy), ir + 3)
            pygame.draw.circle(surface, icon_color, (icx, icy), ir)
            # Highlight
            hr = min(255, icon_color[0] + 80)
            hg = min(255, icon_color[1] + 80)
            hb = min(255, icon_color[2] + 80)
            pygame.draw.circle(surface, (hr, hg, hb),
                             (icx - ir // 3, icy - ir // 3), ir // 3)
            # Glint
            pygame.draw.circle(surface, (255, 255, 255),
                             (icx - ir // 3, icy - ir // 3), max(1, ir // 5))

            # --- Name ---
            name = etype.get("name", eid)
            name_t = big_font.render(name, True, ink)
            surface.blit(name_t, (ix + ir * 2 + 16, iy))

            # Boss tag
            if etype.get("is_boss"):
                boss_t = small_font.render("БОСС", True, ink_red)
                surface.blit(boss_t, (ix + ir * 2 + 16, iy + 38))

            # --- Stats ---
            sy = iy + ir * 2 + 16
            hp = etype.get("hp_base", 0)
            dmg = etype.get("damage", 0)
            spd = etype.get("speed_base", 0)
            xp = etype.get("xp", 0)
            score = etype.get("score", 0)

            stats = [
                (f"HP: {hp}  (+{etype.get('hp_per_wave', 0)}/волна)", ink_green),
                (f"Урон: {dmg}", ink_red),
                (f"Скорость: {spd:.1f}", ink),
                (f"XP: {xp}  |  Очки: {score}", ink_gold),
            ]

            if etype.get("shoot_range"):
                stats.append((f"Дальность: {etype['shoot_range']}px", (150, 120, 200)))
            if etype.get("explode_radius"):
                stats.append((f"Взрыв: {etype['explode_radius']}px / "
                             f"{etype['explode_damage']} урона", ink_gold))
            if etype.get("phasing"):
                stats.append(("Проходит сквозь препятствия", ink_blue))

            for j, (stat, color) in enumerate(stats):
                t = small_font.render(stat, True, color)
                surface.blit(t, (ix, sy + j * 22))

            # --- Description ---
            dy = sy + len(stats) * 22 + 10
            desc = ENEMY_DESCRIPTIONS.get(eid, "")
            if desc:
                self._draw_wrapped(surface, small_font, desc, ix, dy,
                                  pw - 44, ink_dim)

            # --- Kills (bold, gold) ---
            kills = self._get_kills(eid)
            kills_t = font.render(f"Убито: {kills}", True, ink_gold)
            surface.blit(kills_t, (ix, py + ph - 65))

            # Unlock wave
            wave = etype.get("unlock_wave", 1)
            wave_t = small_font.render(f"Появляется с волны {wave}", True, ink_dim)
            surface.blit(wave_t, (ix, py + ph - 40))

        else:
            # Locked state
            lock_t = font.render("??? - убей хотя бы одного", True, ink_dim)
            surface.blit(lock_t, (px + pw // 2 - lock_t.get_width() // 2,
                                  py + ph // 2 - 10))

    # ============================================================
    # Вкладка ОРУЖИЕ
    # ============================================================
    def _draw_weapons(self, surface, font, big_font, small_font, y_start):
        cx = WIDTH // 2

        # Левая панель: список оружия
        list_x = 30
        list_y = y_start + 5
        list_w = 240
        row_h = 38

        max_visible = self._max_visible()
        visible = WEAPON_ORDER[self.scroll:self.scroll + max_visible]

        for i, wid in enumerate(visible):
            idx = self.scroll + i
            y = list_y + i * row_h
            is_sel = (idx == self.selected)
            wdef = WEAPON_DEFS.get(wid, {})
            name = wdef.get("name", wid)
            color = wdef.get("color", (150, 150, 150))

            if is_sel:
                pygame.draw.rect(surface, (40, 45, 65), (list_x, y, list_w, row_h - 4))
                pygame.draw.rect(surface, (80, 160, 255), (list_x, y, 3, row_h - 4))

            # Иконка (цветной квадрат)
            pygame.draw.rect(surface, color, (list_x + 8, y + 7, 18, 18), border_radius=3)

            name_color = WHITE if is_sel else (180, 180, 180)
            name_t = font.render(name, True, name_color)
            surface.blit(name_t, (list_x + 34, y + 7))

            # Тип
            wdesc = WEAPON_DESCRIPTIONS.get(wid, {})
            type_label = wdesc.get("type_label", "")
            if type_label:
                tt = small_font.render(type_label, True, (120, 120, 140))
                surface.blit(tt, (list_x + 34, y + 22))

        # Скролл
        if len(WEAPON_ORDER) > max_visible:
            si = small_font.render(f"{self.scroll+1}-{min(self.scroll+max_visible, len(WEAPON_ORDER))}/{len(WEAPON_ORDER)}", True, (60, 60, 60))
            surface.blit(si, (list_x + list_w - si.get_width() - 5, list_y + max_visible * row_h + 2))

        # Правая панель: детали
        det_x = 290
        det_y = y_start + 5

        if self.selected < len(WEAPON_ORDER):
            wid = WEAPON_ORDER[self.selected]
            wdef = WEAPON_DEFS.get(wid, {})
            wdesc = WEAPON_DESCRIPTIONS.get(wid, {})
            color = wdef.get("color", (150, 150, 150))

            # Иконка
            pygame.draw.rect(surface, color, (det_x, det_y, 56, 56), border_radius=6)

            # Имя
            name = wdef.get("name", wid)
            name_t = big_font.render(name, True, WHITE)
            surface.blit(name_t, (det_x + 70, det_y))

            # Тип оружия
            type_label = wdesc.get("type_label", wdef.get("type", ""))
            type_t = font.render(type_label, True, color)
            surface.blit(type_t, (det_x + 70, det_y + 36))

            # Описание
            desc_y = det_y + 70
            desc = wdesc.get("desc", "")
            if desc:
                self._draw_wrapped(surface, small_font, desc, det_x, desc_y, 480, (200, 200, 200))
                desc_y += 40

            # Базовые статы
            stats_title = font.render("СТАТЫ (уровень 1)", True, (160, 160, 200))
            surface.blit(stats_title, (det_x, desc_y))
            desc_y += 25

            base_stats = wdesc.get("base_stats", "")
            if base_stats:
                st = small_font.render(base_stats, True, (180, 180, 180))
                surface.blit(st, (det_x, desc_y))
                desc_y += 20

            # Макс. уровень
            max_lvl = 8
            ml = small_font.render(f"Макс. уровень: {max_lvl}", True, (140, 140, 140))
            surface.blit(ml, (det_x, desc_y))
            desc_y += 25

            # Урон за уровень
            dmg_base = wdef.get("damage_base", 0)
            dmg_plvl = wdef.get("damage_per_lvl", 0)
            dmg_line = f"Урон: {dmg_base} (+{dmg_plvl}/уровень)"
            dl = small_font.render(dmg_line, True, (220, 120, 120))
            surface.blit(dl, (det_x, desc_y))
            desc_y += 20

            # Кулдаун
            cd_base = wdef.get("cooldown_base", 0)
            cd_min = wdef.get("cd_min", 0)
            cd_line = f"Кулдаун: {cd_base}с (мин: {cd_min}с)"
            cl = small_font.render(cd_line, True, (120, 180, 255))
            surface.blit(cl, (det_x, desc_y))
            desc_y += 25

            # Эволюция (если есть)
            evo = EVOLUTIONS.get(wid)
            if evo:
                evo_title = font.render("ЭВОЛЮЦИЯ", True, GOLD)
                surface.blit(evo_title, (det_x, desc_y))
                desc_y += 22

                req_passive = evo.get("required_passive", "")
                req_lvl = evo.get("required_passive_lvl", 0)
                pdef = PASSIVE_DEFS.get(req_passive, {})
                p_name = pdef.get("name", req_passive)

                evo_text = f"{name} (уровень 8) + {p_name} (уровень {req_lvl})"
                et = small_font.render(evo_text, True, (200, 200, 150))
                surface.blit(et, (det_x, desc_y))
                desc_y += 20

                evo_result = f"= {evo.get('name', '???')}"
                er = font.render(evo_result, True, (255, 215, 0))
                surface.blit(er, (det_x, desc_y))
            else:
                no_evo = small_font.render("Нет эволюции", True, (100, 100, 100))
                surface.blit(no_evo, (det_x, desc_y))

    # ============================================================
    # Вкладка ЭВОЛЮЦИИ
    # ============================================================
    def _draw_evolutions(self, surface, font, big_font, small_font, y_start):
        cx = WIDTH // 2

        evo_list = list(EVOLUTIONS.items())
        max_visible = self._max_visible()

        # Заголовок
        title = font.render("Рецепты эволюций: оружие Lv.8 + пассивка Lv.3", True, (160, 160, 200))
        surface.blit(title, (cx - title.get_width() // 2, y_start))
        y = y_start + 30

        visible = evo_list[self.scroll:self.scroll + max_visible]

        for i, (weapon_id, evo) in enumerate(visible):
            idx = self.scroll + i
            card_y = y + i * 60
            is_sel = (idx == self.selected)

            wdef = WEAPON_DEFS.get(weapon_id, {})
            w_name = wdef.get("name", weapon_id)
            w_color = wdef.get("color", (150, 150, 150))

            req_pid = evo.get("required_passive", "")
            req_lvl = evo.get("required_passive_lvl", 0)
            pdef = PASSIVE_DEFS.get(req_pid, {})
            p_name = pdef.get("name", req_pid)
            p_color = pdef.get("color", (150, 150, 150))

            evo_name = evo.get("name", "???")

            # Карточка
            card_w = WIDTH - 80
            card_h = 52
            card_x = 40

            fill = (50, 40, 70) if is_sel else (30, 25, 45)
            pygame.draw.rect(surface, fill, (card_x, card_y, card_w, card_h), border_radius=6)
            border = GOLD if is_sel else (60, 55, 75)
            bw = 2 if is_sel else 1
            pygame.draw.rect(surface, border, (card_x, card_y, card_w, card_h), bw, border_radius=6)

            # Иконка оружия
            pygame.draw.rect(surface, w_color, (card_x + 10, card_y + 8, 16, 16), border_radius=3)
            # Имя оружия
            w_label = font.render(f"{w_name} Lv.8", True, WHITE)
            surface.blit(w_label, (card_x + 32, card_y + 5))

            # Плюс
            plus = font.render("+", True, (180, 180, 180))
            surface.blit(plus, (card_x + 200, card_y + 5))

            # Иконка пассивки
            pygame.draw.rect(surface, p_color, (card_x + 220, card_y + 8, 16, 16), border_radius=3)
            # Имя пассивки
            p_label = font.render(f"{p_name} Lv.{req_lvl}", True, (200, 200, 200))
            surface.blit(p_label, (card_x + 242, card_y + 5))

            # Стрелка и результат
            arrow = font.render("=", True, (255, 215, 0))
            surface.blit(arrow, (card_x + 410, card_y + 5))

            evo_label = font.render(evo_name, True, GOLD)
            surface.blit(evo_label, (card_x + 435, card_y + 5))

            # Описание результата (мелким шрифтом)
            if is_sel:
                desc_y = card_y + 28
                desc_t = small_font.render(f"Эволюция {w_name} в {evo_name} при наличии {p_name} Lv.{req_lvl}+", True, (160, 160, 160))
                surface.blit(desc_t, (card_x + 12, desc_y))

        # Скролл-индикатор
        if len(evo_list) > max_visible:
            si = small_font.render(f"{self.scroll+1}-{min(self.scroll+max_visible, len(evo_list))}/{len(evo_list)}", True, (60, 60, 60))
            surface.blit(si, (cx - si.get_width() // 2, y + max_visible * 60 + 10))

    # ============================================================
    # Утилиты
    # ============================================================
    def _is_enemy_unlocked(self, eid):
        if not self.meta:
            return False
        return self._get_kills(eid) > 0

    def _get_kills(self, eid):
        if not self.meta:
            return 0
        return self.meta.enemy_kills.get(eid, 0)

    def _draw_wrapped(self, surface, font, text, x, y, max_w, color):
        """Рисует текст с переносом по словам."""
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            tw, _ = font.size(test)
            if tw > max_w and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
        for i, line in enumerate(lines):
            t = font.render(line, True, color)
            surface.blit(t, (x, y + i * 18))

    def _count_unlocked(self):
        return sum(1 for eid in ENEMY_ORDER if self._is_enemy_unlocked(eid))


# Совместимость со старым BestiaryScreen (alias)
BestiaryScreen = CodexScreen
