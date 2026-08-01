"""
Рождение святого — Main Menu (v2)
Stone altarpiece, blood seep, heartbeat logo, 3 buttons.
Использует: ui_theme, animation, ui_components
"""
import pygame
import math
import random
from config import WIDTH, HEIGHT, MAP_DEFS, MAP_ORDER
from player import CHARACTERS
from ui_theme import (
    STONE_BASE, STONE_LIGHT, STONE_DARK,
    BLOOD_DRIP, GOLD_LEAF, GOLD_GLOW, GOLD_DARK,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM,
    IRON, IRON_LIGHT,
    get_font, get_logo_font, get_button_font, get_body_font, get_small_font,
    PARTICLE_COUNT_BG,
    color_alpha, color_brighten,
)
from animation import (
    heartbeat_value, Parallax, StaggerAnimator, generate_stone_texture, draw_vignette,
    ease_out_cubic,
)
from ui_components import UIButton, UIParticleSystem
import sound_manager

MAPS = MAP_DEFS

# ============================================================
# КНОПКИ (3 вместо 7)
# ============================================================

MENU_BUTTONS = [
    {"id": "start",    "label": "ИГРАТЬ",     "style": "primary"},
    {"id": "settings", "label": "НАСТРОЙКИ",  "style": "default"},
    {"id": "quit",     "label": "ВЫХОД",      "style": "danger"},
]

BUTTON_WIDTH = 280
BUTTON_HEIGHT = 50
BUTTON_GAP = 14
BUTTON_START_Y = 400

# Heartbeat period
HEARTBEAT_PERIOD = 2.0


# ============================================================
# BLOOD DRIP (оставляем — классный эффект)
# ============================================================

class BloodDrip:
    """Single blood drip particle."""
    __slots__ = ('x', 'y', 'speed', 'length', 'alpha', 'phase', 'alive')

    def __init__(self, x=None, y=None, from_top=True):
        self.respawn(x, y, from_top)

    def respawn(self, x=None, y=None, from_top=True):
        if from_top:
            self.x = x if x is not None else random.uniform(0, WIDTH)
            self.y = y if y is not None else random.uniform(-20, 0)
        else:
            side = random.choice([0, 1])
            self.x = 0 if side == 0 else WIDTH
            self.y = y if y is not None else random.uniform(HEIGHT * 0.2, HEIGHT * 0.8)
        self.speed = random.uniform(0.3, 1.2)
        self.length = random.uniform(8, 25)
        self.alpha = random.randint(120, 220)
        self.phase = random.uniform(0, math.pi * 2)
        self.alive = True

    def update(self, dt):
        self.y += self.speed * dt * 60
        self.x += math.sin(self.y * 0.02 + self.phase) * 0.15
        if self.y > HEIGHT + self.length:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        y_end = min(self.y + self.length, HEIGHT)
        drip_h = int(y_end - self.y)
        if drip_h <= 0:
            return
        drip_surf = pygame.Surface((3, drip_h), pygame.SRCALPHA)
        for py_i in range(drip_h):
            t = py_i / max(drip_h - 1, 1)
            a = int(self.alpha * (1.0 - t * 0.5))
            r = max(1, int(1.5 * (1.0 - t * 0.3)))
            color = (BLOOD_DRIP[0], BLOOD_DRIP[1], BLOOD_DRIP[2], a)
            pygame.draw.circle(drip_surf, color, (1, py_i), r)
        surface.blit(drip_surf, (int(self.x), int(self.y)))


class BloodSeepPool:
    """Manages blood drip particles at screen edges."""
    def __init__(self, count=25):
        self.drips = [BloodDrip(from_top=True) for _ in range(count)]
        for _ in range(8):
            self.drips.append(BloodDrip(from_top=False))
        self._timer = 0.0

    def update(self, dt):
        self._timer += dt
        for d in self.drips:
            d.update(dt)
            if not d.alive:
                d.respawn(from_top=random.random() < 0.8)

    def draw(self, surface):
        for d in self.drips:
            d.draw(surface)


# ============================================================
# MAIN MENU
# ============================================================

class MainMenu:
    def __init__(self):
        self.selected_char = "warrior"
        self.selected_map = "arena"
        self.state = "main"
        self.final_stats = {}
        self.leaderboard_rank = None
        self.leaderboard_entries = []
        self._time = 0.0
        self._blood_pool = BloodSeepPool(count=25)
        self._stone_bg = None
        self._profile_selected = 0

        # Новые компоненты
        self._buttons = []
        self._stagger = StaggerAnimator(len(MENU_BUTTONS), delay=0.1, duration=0.4)
        self._particles = UIParticleSystem(
            count=PARTICLE_COUNT_BG,
            colors=[(200, 180, 100), (255, 215, 0)],
            speed_range=(-0.3, -0.1),
            size_range=(1, 3),
        )
        self._hover_index = -1
        self._selected_index = 0
        self._create_buttons()

    def _create_buttons(self):
        """Create UIButton instances for main menu."""
        self._buttons = []
        cx = WIDTH // 2
        for i, btn_def in enumerate(MENU_BUTTONS):
            x = cx - BUTTON_WIDTH // 2
            y = BUTTON_START_Y + i * (BUTTON_HEIGHT + BUTTON_GAP)
            btn = UIButton(x, y, BUTTON_WIDTH, BUTTON_HEIGHT,
                           btn_def["label"], btn_def["style"],
                           callback=lambda idx=i: self._activate_button(idx))
            self._buttons.append(btn)

    def _get_stone_bg(self):
        """Cached procedural stone background."""
        if self._stone_bg is None:
            self._stone_bg = generate_stone_texture(WIDTH, HEIGHT, seed=42)
        return self._stone_bg

    def handle_event(self, event) -> str | None:
        if self.state == "main":
            # Mouse
            if event.type == pygame.MOUSEMOTION:
                old = self._hover_index
                self._hover_index = -1
                for i, btn in enumerate(self._buttons):
                    btn.handle_event(event)
                    if btn.is_hovered:
                        self._hover_index = i
                        self._selected_index = i
                        if old != i:
                            sound_manager.play("ui_hover")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self._buttons:
                    if btn.handle_event(event):
                        return None  # callback handles it

            # Keyboard
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._selected_index = (self._selected_index - 1) % len(self._buttons)
                    self._update_focus()
                    sound_manager.play("ui_hover")
                elif event.key == pygame.K_DOWN:
                    self._selected_index = (self._selected_index + 1) % len(self._buttons)
                    self._update_focus()
                    sound_manager.play("ui_hover")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_manager.play("ui_select")
                    return self._activate_button(self._selected_index)

        elif self.state == "char_select":
            if event.type == pygame.KEYDOWN:
                chars = list(CHARACTERS.keys())
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"
                elif event.key == pygame.K_RETURN:
                    self.state = "main"
                elif event.key == pygame.K_LEFT:
                    idx = chars.index(self.selected_char) if self.selected_char in chars else 0
                    self.selected_char = chars[(idx - 1) % len(chars)]
                elif event.key == pygame.K_RIGHT:
                    idx = chars.index(self.selected_char) if self.selected_char in chars else 0
                    self.selected_char = chars[(idx + 1) % len(chars)]

        elif self.state == "map_select":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"
                elif event.key == pygame.K_RETURN:
                    self.state = "main"
                elif event.key == pygame.K_LEFT:
                    idx = MAP_ORDER.index(self.selected_map) if self.selected_map in MAP_ORDER else 0
                    self.selected_map = MAP_ORDER[(idx - 1) % len(MAP_ORDER)]
                elif event.key == pygame.K_RIGHT:
                    idx = MAP_ORDER.index(self.selected_map) if self.selected_map in MAP_ORDER else 0
                    self.selected_map = MAP_ORDER[(idx + 1) % len(MAP_ORDER)]

        elif self.state == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"
                    return "menu"

        elif self.state == "records":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"

        elif self.state == "profiles":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"
                elif event.key == pygame.K_UP:
                    self._profile_selected = (self._profile_selected - 1) % 3
                    sound_manager.play("ui_hover")
                elif event.key == pygame.K_DOWN:
                    self._profile_selected = (self._profile_selected + 1) % 3
                    sound_manager.play("ui_hover")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_manager.play("ui_confirm")
                    return ("profile_select", {"profile_id": self._profile_selected + 1})

        return None

    def _update_focus(self):
        """Update keyboard focus on buttons."""
        for i, btn in enumerate(self._buttons):
            btn.is_focused = (i == self._selected_index)

    def _activate_button(self, index):
        """Activate button by index. Returns scene transition string."""
        btn_id = MENU_BUTTONS[index]["id"]
        if btn_id == "start":
            return "start"
        elif btn_id == "settings":
            return "settings"
        elif btn_id == "quit":
            return "quit"
        return None

    def draw(self, surface: pygame.Surface, font=None, big_font=None, small_font=None):
        if self.state == "main":
            self.draw_main(surface)
        elif self.state == "char_select":
            self.draw_char_select(surface, font, big_font, small_font)
        elif self.state == "map_select":
            self.draw_map_select(surface, font, big_font, small_font)
        elif self.state == "records":
            self.draw_records(surface, font, big_font, small_font)
        elif self.state == "profiles":
            self.draw_profiles(surface, font, big_font, small_font)
        elif self.state == "game_over":
            from game_over_screen import draw_game_over, GameOverAnimator
            anim = GameOverAnimator()
            anim.timer = 5.0
            draw_game_over(surface, self.final_stats, anim, menu=self,
                           font=font, big_font=big_font, small_font=small_font)

    def draw_main(self, surface):
        dt = 1.0 / 60.0
        self._time += dt
        self._blood_pool.update(dt)
        self._stagger.update(dt)
        self._particles.update(dt)

        # === Каменный фон ===
        stone = self._get_stone_bg()
        surface.blit(stone, (0, 0))

        # === Частицы ===
        self._particles.draw(surface)

        # === Кровь ===
        self._blood_pool.draw(surface)

        # === Виньетка ===
        draw_vignette(surface, margin_top=100, margin_bottom=100, margin_left=80, margin_right=80)

        cx = WIDTH // 2

        # === LOGO с heartbeat ===
        hb = heartbeat_value(self._time, period=HEARTBEAT_PERIOD)
        logo_font = get_logo_font()
        logo_text = logo_font.render("РОЖДЕНИЕ СВЯТОГО", True, GOLD_LEAF)

        # Pulsating gold aura
        if hb > 0.01:
            aura_size = int(20 + 40 * hb)
            aura = pygame.Surface((logo_text.get_width() + aura_size * 2,
                                   logo_text.get_height() + aura_size * 2), pygame.SRCALPHA)
            aura_alpha = int(50 * hb)
            pygame.draw.ellipse(aura, (255, 215, 0, aura_alpha), aura.get_rect())
            surface.blit(aura, (cx - aura.get_width() // 2, 180 - aura.get_height() // 2))

        # Logo text
        surface.blit(logo_text, (cx - logo_text.get_width() // 2, 180 - logo_text.get_height() // 2))

        # Subtitle
        sub_font = get_font(22)
        sub_text = sub_font.render("Гнев Небес", True, TEXT_DIM)
        surface.blit(sub_text, (cx - sub_text.get_width() // 2,
                                180 + logo_text.get_height() // 2 + 10))

        # === КНОПКИ (stagger-появление) ===
        for i, btn in enumerate(self._buttons):
            state = self._stagger.get(i)
            if state['alpha'] < 0.01:
                continue
            # Offset for stagger
            orig_y = BUTTON_START_Y + i * (BUTTON_HEIGHT + BUTTON_GAP)
            btn.rect.y = orig_y + int(state['offset_y'])
            btn.alpha = int(state['alpha'] * 255)
            btn.draw(surface)

        # === Версия ===
        ver_font = get_small_font()
        ver = ver_font.render("v0.7.0", True, TEXT_DIM)
        surface.blit(ver, (WIDTH - ver.get_width() - 10, HEIGHT - ver.get_height() - 10))

    # ============================================================
    # Остальные экраны (char_select, map_select, records, profiles)
    # Сохранены для обратной совместимости. В Phase 3 переедут в лобби.
    # ============================================================

    def draw_char_select(self, surface, font, big_font, small_font):
        """Экран выбора персонажа (временный, будет в лобби)."""
        surface.fill(STONE_DARK)
        if font is None:
            font = get_button_font()
        if big_font is None:
            big_font = get_font(48)
        if small_font is None:
            small_font = get_small_font()

        title = big_font.render("ВЫБОР ПЕРСОНАЖА", True, GOLD_LEAF)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        chars = list(CHARACTERS.keys())
        card_w = 180
        total_w = len(chars) * card_w + (len(chars) - 1) * 20
        start_x = (WIDTH - total_w) // 2

        for i, char_id in enumerate(chars):
            char_data = CHARACTERS[char_id]
            x = start_x + i * (card_w + 20)
            y = 180
            selected = (char_id == self.selected_char)

            # Card background
            fill = STONE_LIGHT if selected else STONE_BASE
            border = GOLD_LEAF if selected else IRON
            pygame.draw.rect(surface, fill, (x, y, card_w, 320), border_radius=10)
            pygame.draw.rect(surface, border, (x, y, card_w, 320), 2 if selected else 1, border_radius=10)

            # Name
            name = font.render(char_data.get("name", char_id), True, TEXT_PRIMARY)
            surface.blit(name, (x + card_w // 2 - name.get_width() // 2, y + 20))

            # Stats
            hp_text = small_font.render(f"HP: {char_data.get('max_hp', 100)}", True, TEXT_SECONDARY)
            surface.blit(hp_text, (x + 15, y + 70))
            spd_text = small_font.render(f"SPD: {char_data.get('speed', 3.0)}", True, TEXT_SECONDARY)
            surface.blit(spd_text, (x + 15, y + 95))

            # Weapon
            weapon = char_data.get("start_weapon", "?")
            wpn_text = small_font.render(f"Оружие: {weapon}", True, GOLD_DARK)
            surface.blit(wpn_text, (x + 15, y + 130))

            # Number hint
            num_text = small_font.render(f"[{i + 1}]", True, TEXT_DIM)
            surface.blit(num_text, (x + card_w // 2 - num_text.get_width() // 2, y + 290))

        # Instructions
        hint = small_font.render("← → выбрать | ENTER подтвердить | ESC назад", True, TEXT_DIM)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

    def draw_map_select(self, surface, font, big_font, small_font):
        """Экран выбора карты (временный, будет в лобби)."""
        surface.fill(STONE_DARK)
        if font is None:
            font = get_button_font()
        if big_font is None:
            big_font = get_font(48)
        if small_font is None:
            small_font = get_small_font()

        title = big_font.render("ВЫБОР КАРТЫ", True, GOLD_LEAF)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        for i, map_id in enumerate(MAP_ORDER):
            map_data = MAPS.get(map_id, {})
            selected = (map_id == self.selected_map)
            x = WIDTH // 2 - 200
            y = 200 + i * 80
            w, h = 400, 60

            fill = STONE_LIGHT if selected else STONE_BASE
            border = GOLD_LEAF if selected else IRON
            pygame.draw.rect(surface, fill, (x, y, w, h), border_radius=8)
            pygame.draw.rect(surface, border, (x, y, w, h), 2 if selected else 1, border_radius=8)

            name = font.render(map_data.get("name", map_id), True, TEXT_PRIMARY)
            surface.blit(name, (x + 20, y + h // 2 - name.get_height() // 2))

        hint = small_font.render("← → выбрать | ENTER подтвердить | ESC назад", True, TEXT_DIM)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

    def draw_records(self, surface, font, big_font, small_font):
        """Экран рекордов."""
        surface.fill(STONE_DARK)
        if font is None:
            font = get_button_font()
        if big_font is None:
            big_font = get_font(48)
        if small_font is None:
            small_font = get_small_font()

        title = big_font.render("РЕКОРДЫ", True, GOLD_LEAF)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        if self.leaderboard_entries:
            for i, entry in enumerate(self.leaderboard_entries[:10]):
                y = 150 + i * 36
                rank = small_font.render(f"{i + 1}.", True, GOLD_DARK)
                surface.blit(rank, (WIDTH // 2 - 150, y))
                name = font.render(entry.get("name", "---"), True, TEXT_PRIMARY)
                surface.blit(name, (WIDTH // 2 - 100, y))
                score = font.render(str(entry.get("score", 0)), True, GOLD_LEAF)
                surface.blit(score, (WIDTH // 2 + 100, y))
        else:
            empty = font.render("Пока нет записей", True, TEXT_DIM)
            surface.blit(empty, (WIDTH // 2 - empty.get_width() // 2, 300))

        hint = small_font.render("ESC назад", True, TEXT_DIM)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

    def draw_profiles(self, surface, font, big_font, small_font):
        """Экран выбора профиля."""
        surface.fill(STONE_DARK)
        if font is None:
            font = get_button_font()
        if big_font is None:
            big_font = get_font(48)
        if small_font is None:
            small_font = get_small_font()

        title = big_font.render("ПРОФИЛИ", True, GOLD_LEAF)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        from save_system import list_profiles
        profiles = list_profiles()

        for i, prof in enumerate(profiles):
            y = 180 + i * 120
            selected = (i == self._profile_selected)
            w, h = 400, 100
            x = WIDTH // 2 - w // 2

            fill = STONE_LIGHT if selected else STONE_BASE
            border = GOLD_LEAF if selected else IRON
            pygame.draw.rect(surface, fill, (x, y, w, h), border_radius=10)
            pygame.draw.rect(surface, border, (x, y, w, h), 2 if selected else 1, border_radius=10)

            name = font.render(f"Профиль {i + 1}", True, TEXT_PRIMARY)
            surface.blit(name, (x + 20, y + 15))

            stats = prof.get("stats", {})
            kills = stats.get("total_kills", 0)
            gold = stats.get("total_gold", 0)
            runs = stats.get("total_runs", 0)

            info = small_font.render(f"Убийства: {kills} | Золото: {gold} | Ранов: {runs}", True, TEXT_SECONDARY)
            surface.blit(info, (x + 20, y + 50))

        hint = small_font.render("↑↓ выбрать | ENTER подтвердить | ESC назад", True, TEXT_DIM)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))
