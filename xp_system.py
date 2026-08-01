"""
Рождение святого - XP System & Level Up Screen
XP-гемы, левелап, выбор предмета.
"""
import random
import pygame
from config import (
    PICKUP_RANGE_BASE, PICKUP_MAGNET_SPEED,
    calc_xp_for_level, MAX_WEAPONS, MAX_PASSIVES,
    MAX_WEAPON_LEVEL, MAX_PASSIVE_LEVEL,
    WHITE, GREEN, BLUE, RED, GOLD, DARK_BG,
    LEVELUP_CARD_WIDTH, LEVELUP_CARD_HEIGHT, LEVELUP_CARD_GAP, WIDTH, HEIGHT
)
from weapons import WEAPON_DEFS, PASSIVE_DEFS, create_weapon


class XPGem:
    """XP-гем на земле."""
    def __init__(self, x: float, y: float, value: int):
        self.pos = pygame.Vector2(x, y)
        self.value = value
        self.alive = True
        self.attracting = False

        # Цвет по ценности
        if value >= 10:
            self.color = RED
            self.radius = 5
        elif value >= 5:
            self.color = BLUE
            self.radius = 4
        else:
            self.color = GREEN
            self.radius = 3

    def update(self, player_pos: pygame.Vector2, pickup_range: float, dt: float):
        dist = (self.pos - player_pos).length()
        if dist < pickup_range:
            self.attracting = True

        if self.attracting:
            d = player_pos - self.pos
            if d.length() > 0:
                self.pos += d.normalize() * PICKUP_MAGNET_SPEED * 60 * dt
            if dist < 10:
                self.alive = False
                return self.value
        return 0

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)
        if -10 < sx < 1034 and -10 < sy < 778:
            # Glow
            glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            r, g, b = self.color
            pygame.draw.circle(glow, (r, g, b, 40), (self.radius * 2, self.radius * 2), self.radius * 2)
            surface.blit(glow, (sx - self.radius * 2, sy - self.radius * 2))
            pygame.draw.circle(surface, self.color, (sx, sy), self.radius)


class LevelUpScreen:
    """Экран выбора предмета при левелапе."""
    def __init__(self):
        self.active = False
        self.options = []  # list of {"type": "weapon"/"passive", "id": str, "level": int}
        self.selected = -1
        self.rerolls_left = 3
        self.bans_left = 3
        # Stagger animation
        self.anim_timer = 0.0
        self.card_alpha = [0, 0, 0]  # alpha для каждой карточки (0-255)
        self.STAGGER_DELAY = 0.12  # секунды между карточками

    def generate_options(self, player, banned_items=None) -> list:
        """Генерирует 3 варианта для выбора. banned_items — set id забаненных предметов."""
        if banned_items is None:
            banned_items = set()
        pool = []

        # Оружие
        owned_weapon_ids = [w.weapon_id for w in player.weapons]
        for wid in WEAPON_DEFS:
            if wid in banned_items:
                continue
            w = next((w for w in player.weapons if w.weapon_id == wid), None)
            if w and w.level < MAX_WEAPON_LEVEL:
                pool.append({"type": "weapon", "id": wid, "current_level": w.level})
            elif not w and len(player.weapons) < MAX_WEAPONS:
                pool.append({"type": "weapon", "id": wid, "current_level": 0})

        # Пассивки
        for pid in PASSIVE_DEFS:
            if pid in banned_items:
                continue
            current = player.passives.get(pid, 0)
            if current < MAX_PASSIVE_LEVEL:
                if current > 0 or len(player.passives) < MAX_PASSIVES:
                    pool.append({"type": "passive", "id": pid, "current_level": current})

        # Если пул пуст - золото/HP
        if not pool:
            return [{"type": "gold", "id": "gold", "amount": 50},
                    {"type": "heal", "id": "heal", "amount": 30},
                    {"type": "gold", "id": "gold", "amount": 100}]

        # Выбираем 3 случайных
        random.shuffle(pool)
        return pool[:3]

    def activate(self, player, banned_items=None):
        self.active = True
        self.banned_items_ref = banned_items or set()
        self.options = self.generate_options(player, self.banned_items_ref)
        self.selected = -1
        # Reset stagger animation
        self.anim_timer = 0.0
        self.card_alpha = [0, 0, 0]

    def handle_event(self, event, player) -> bool:
        """Обрабатывает выбор. Возвращает True когда выбор сделан."""
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.selected = 0
            elif event.key == pygame.K_2:
                self.selected = 1
            elif event.key == pygame.K_3:
                self.selected = 2
            elif event.key == pygame.K_r and self.rerolls_left > 0:
                self.rerolls_left -= 1
                self.options = self.generate_options(player, getattr(self, 'banned_items_ref', set()))
                return False
            else:
                return False

        if self.selected >= 0 and self.selected < len(self.options):
            self._apply_choice(player, self.options[self.selected])
            self.active = False
            player.invuln_timer = 0.5
            return True

        return False

    def _apply_choice(self, player, choice):
        if choice["type"] == "weapon":
            w = next((w for w in player.weapons if w.weapon_id == choice["id"]), None)
            if w:
                w.upgrade()
            else:
                player.weapons.append(create_weapon(choice["id"]))
        elif choice["type"] == "passive":
            pid = choice["id"]
            player.passives[pid] = player.passives.get(pid, 0) + 1
            player.update_stats()
        elif choice["type"] == "gold":
            player.gold += choice.get("amount", 50)
        elif choice["type"] == "heal":
            player.heal(choice.get("amount", 30))

    def draw(self, surface: pygame.Surface, font, small_font):
        if not self.active:
            return

        # Update stagger animation
        self.anim_timer += 1 / 60.0  # approximate dt
        for i in range(3):
            delay = i * self.STAGGER_DELAY
            if self.anim_timer > delay:
                progress = min(1.0, (self.anim_timer - delay) / 0.2)  # 0.2s fade-in
                self.card_alpha[i] = int(255 * progress)

        # Затемнение
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Заголовок
        title = font.render("ВЫБЕРИ ДАР", True, GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Подсказка
        hint = small_font.render("Нажми 1, 2 или 3  |  R - реролл ({})".format(self.rerolls_left), True, WHITE)
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 140))

        # Карточки
        total_w = LEVELUP_CARD_WIDTH * 3 + LEVELUP_CARD_GAP * 2
        start_x = WIDTH // 2 - total_w // 2
        start_y = 180

        for i, opt in enumerate(self.options):
            alpha = self.card_alpha[i]
            if alpha <= 0:
                continue  # ещё не появилась

            x = start_x + i * (LEVELUP_CARD_WIDTH + LEVELUP_CARD_GAP)
            y = start_y

            # Hover highlight
            is_hovered = (i == self.selected)

            # Stagger slide-in: сдвиг вверх при появлении
            slide_offset = int(20 * (1.0 - alpha / 255))
            y += slide_offset

            # Scale на hover: +4px в каждую сторону
            if is_hovered:
                card_rect = pygame.Rect(x - 4, y - 4, LEVELUP_CARD_WIDTH + 8, LEVELUP_CARD_HEIGHT + 8)
            else:
                card_rect = pygame.Rect(x, y, LEVELUP_CARD_WIDTH, LEVELUP_CARD_HEIGHT)

            # Карточка-поверхность с alpha
            card_surf = pygame.Surface((card_rect.w, card_rect.h), pygame.SRCALPHA)

            # Фон карточки
            bg_color = (55, 40, 80, alpha) if is_hovered else (40, 30, 60, alpha)
            pygame.draw.rect(card_surf, bg_color, (0, 0, card_rect.w, card_rect.h), border_radius=8)

            # Rarity border
            if opt["type"] == "weapon":
                rarity = WEAPON_DEFS[opt["id"]].get("rarity", "common")
            elif opt["type"] == "passive":
                rarity = "uncommon"
            else:
                rarity = "common"
            rarity_colors = {
                'common': (120, 120, 120), 'uncommon': (80, 200, 80),
                'rare': (80, 120, 255), 'epic': (180, 80, 255), 'legendary': (255, 180, 50)
            }
            border_color = rarity_colors.get(rarity, GOLD)
            border_width = 3 if is_hovered else 2
            pygame.draw.rect(card_surf, (*border_color, alpha), (0, 0, card_rect.w, card_rect.h), border_width, border_radius=8)

            # Номер
            num_text = font.render(str(i + 1), True, GOLD)
            num_text.set_alpha(alpha)
            card_surf.blit(num_text, (10, 10))

            # Название
            if opt["type"] == "weapon":
                name = WEAPON_DEFS[opt["id"]]["name"]
                color = WEAPON_DEFS[opt["id"]]["color"]
                level = opt["current_level"]
                level_text = f"Lv {level + 1}" if level > 0 else "НОВЫЙ"
            elif opt["type"] == "passive":
                name = PASSIVE_DEFS[opt["id"]]["name"]
                color = PASSIVE_DEFS[opt["id"]]["color"]
                level = opt["current_level"]
                level_text = f"Lv {level + 1}" if level > 0 else "НОВЫЙ"
            else:
                name = "Золото" if opt["type"] == "gold" else "Исцеление"
                color = GOLD if opt["type"] == "gold" else (100, 255, 100)
                level_text = f"+{opt.get('amount', 0)}"

            name_text = font.render(name, True, color)
            name_text.set_alpha(alpha)
            card_surf.blit(name_text, (card_rect.w // 2 - name_text.get_width() // 2, 50))

            lvl_text = small_font.render(level_text, True, WHITE)
            lvl_text.set_alpha(alpha)
            card_surf.blit(lvl_text, (card_rect.w // 2 - lvl_text.get_width() // 2, 80))

            # Описание
            if opt["type"] == "weapon":
                desc = WEAPON_DEFS[opt["id"]].get("type", "")
            elif opt["type"] == "passive":
                desc = PASSIVE_DEFS[opt["id"]].get("desc", "")
            else:
                desc = ""

            desc_text = small_font.render(desc, True, (180, 180, 180))
            desc_text.set_alpha(alpha)
            card_surf.blit(desc_text, (card_rect.w // 2 - desc_text.get_width() // 2, 120))

            # Blit card to surface
            surface.blit(card_surf, card_rect.topleft)
