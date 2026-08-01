"""
Рождение святого - Lobby
Табированный экран лобби: Герои / Арканы / Магазин / Рекорды.
"""
import pygame
from config import (
    WIDTH, HEIGHT, WHITE, GOLD, DARK_BG, RED, GREEN,
    POWERUP_DEFS, ACHIEVEMENTS, POWERUP_COSTS
)
from arcana import ARCANA_DEFS
from player import CHARACTERS
from save_system import save_progress


# Табы
TABS = ["Герои", "Арканы", "Магазин", "Рекорды"]
TAB_COLORS = {
    "Герои": (180, 180, 255),
    "Арканы": (255, 180, 100),
    "Магазин": (100, 255, 100),
    "Рекорды": (255, 215, 0),
}


class MetaProgress:
    """Глобальный прогресс между ранами."""
    def __init__(self):
        self.gold = 0
        self.total_runs = 0
        self.best_wave = 0
        self.best_time = 0
        self.total_kills = 0
        self.powerups = {pid: 0 for pid in POWERUP_DEFS}
        self.unlocked_chars = {"warrior", "paladin"}
        self.unlocked_weapons = {"whip", "fire", "halo", "rosary"}
        self.achievements_done = set()
        self.selected_arcana = None

    def get_powerup_bonus(self, powerup_id: str) -> float:
        level = self.powerups.get(powerup_id, 0)
        bonuses = {
            "might": 1.0 + 0.05 * level,
            "sturdiness": 1.0 + 0.10 * level,
            "swiftness": 1.0 + 0.05 * level,
            "greed": 1.0 + 0.10 * level,
            "luck": 1.0 + 0.10 * level,
            "revive": level,
        }
        return bonuses.get(powerup_id, 1.0)

    def can_buy(self, powerup_id: str) -> bool:
        level = self.powerups.get(powerup_id, 0)
        pdef = POWERUP_DEFS[powerup_id]
        if level >= pdef["max"]:
            return False
        cost = pdef["costs"][level]
        return self.gold >= cost

    def buy(self, powerup_id: str) -> bool:
        if not self.can_buy(powerup_id):
            return False
        level = self.powerups[powerup_id]
        cost = POWERUP_DEFS[powerup_id]["costs"][level]
        self.gold -= cost
        self.powerups[powerup_id] += 1
        return True

    def check_achievements(self, elapsed, wave, kills, gold_total,
                           boss_killed=False, reaper_killed=False):
        new_unlocks = []
        if elapsed >= 300 and "survive_5" not in self.achievements_done:
            self.achievements_done.add("survive_5")
            new_unlocks.append(("survive_5", "inquisitor"))
            self.unlocked_chars.add("inquisitor")
        if boss_killed and "first_boss" not in self.achievements_done:
            self.achievements_done.add("first_boss")
            new_unlocks.append(("first_boss", "weapon_lightning"))
            self.unlocked_weapons.add("lightning")
        if elapsed >= 600 and "survive_10" not in self.achievements_done:
            self.achievements_done.add("survive_10")
            new_unlocks.append(("survive_10", "weapon_prayer"))
            self.unlocked_weapons.add("prayer")
        if gold_total >= 10000 and "gold_10000" not in self.achievements_done:
            self.achievements_done.add("gold_10000")
            new_unlocks.append(("gold_10000", "powerup_revive"))
        if reaper_killed and "kill_reaper" not in self.achievements_done:
            self.achievements_done.add("kill_reaper")
            new_unlocks.append(("kill_reaper", "char_secret"))
        return new_unlocks


class LobbyScreen:
    """Табированный экран лобби."""
    def __init__(self):
        self.active = False
        self.meta = None
        self.tab_index = 0
        self.selected = 0  # индекс внутри таба
        self.notification = ""
        self.notify_timer = 0.0
        self.leaderboard_entries = []

    def activate(self, meta: MetaProgress):
        self.active = True
        self.meta = meta
        self.selected = 0

    @property
    def current_tab(self):
        return TABS[self.tab_index]

    def handle_event(self, event) -> str | None:
        """Возвращает: 'play', 'back', None"""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            # Переключение табов
            if event.key == pygame.K_TAB:
                self.tab_index = (self.tab_index + 1) % len(TABS)
                self.selected = 0
                return None
            if event.key == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.tab_index = (self.tab_index - 1) % len(TABS)
                self.selected = 0
                return None

            # ESC = играть (или выход из подменю)
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return "play"

            # Навигация внутри таба
            if self.current_tab == "Герои":
                return self._handle_heroes(event)
            elif self.current_tab == "Арканы":
                return self._handle_arcanas(event)
            elif self.current_tab == "Магазин":
                return self._handle_shop(event)
            elif self.current_tab == "Рекорды":
                return self._handle_records(event)

        return None

    def _handle_heroes(self, event):
        chars = [cid for cid in CHARACTERS if cid in self.meta.unlocked_chars]
        if not chars:
            return None
        if event.key == pygame.K_UP:
            self.selected = (self.selected - 3) % len(chars)  # 3 колонки
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 3) % len(chars)
        elif event.key == pygame.K_LEFT:
            self.selected = (self.selected - 1) % len(chars)
        elif event.key == pygame.K_RIGHT:
            self.selected = (self.selected + 1) % len(chars)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.selected < len(chars):
                self.meta._selected_char = chars[self.selected]
        return None

    def _handle_arcanas(self, event):
        arcana_ids = list(ARCANA_DEFS.keys())
        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(arcana_ids)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(arcana_ids)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_TAB):
            aid = arcana_ids[self.selected]
            if self.meta.selected_arcana == aid:
                self.meta.selected_arcana = None
                self.notification = "Аркана снята"
            else:
                self.meta.selected_arcana = aid
                self.notification = f"Аркана: {ARCANA_DEFS[aid]['name']}"
            self.notify_timer = 2.0
            save_progress(self.meta)
        return None

    def _handle_shop(self, event):
        powerup_ids = list(POWERUP_DEFS.keys())
        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(powerup_ids)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(powerup_ids)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            pid = powerup_ids[self.selected]
            if self.meta.buy(pid):
                self.notification = f"Куплено: {POWERUP_DEFS[pid]['name']}!"
                self.notify_timer = 2.0
                save_progress(self.meta)
            else:
                self.notification = "Недостаточно золота!"
                self.notify_timer = 1.5
        return None

    def _handle_records(self, event):
        # Рекорды - только просмотр
        return None

    def update(self, dt: float):
        if self.notify_timer > 0:
            self.notify_timer -= dt

    def draw(self, surface, font, big_font, small_font):
        if not self.active:
            return

        self._draw_bg(surface)
        cx = WIDTH // 2

        # === Заголовок ===
        title = big_font.render("ЛОББИ", True, GOLD)
        surface.blit(title, (cx - title.get_width() // 2, 20))

        # Золото (верх право)
        gold_text = font.render(f"{self.meta.gold} G", True, GOLD)
        surface.blit(gold_text, (WIDTH - gold_text.get_width() - 20, 25))

        # === Табы ===
        tab_y = 80
        tab_x = 40
        for i, tab_name in enumerate(TABS):
            is_active = (i == self.tab_index)
            color = TAB_COLORS[tab_name] if is_active else (100, 100, 100)
            label = f"[{tab_name}]" if is_active else tab_name
            t = font.render(label, True, color)
            surface.blit(t, (tab_x, tab_y))
            if is_active:
                pygame.draw.line(surface, color, (tab_x, tab_y + 25),
                                (tab_x + t.get_width(), tab_y + 25), 2)
            tab_x += t.get_width() + 24

        # Подсказка навигации
        nav = small_font.render("TAB - сменить таб  |  ENTER - действие  |  ESC - играть", True, (80, 80, 80))
        surface.blit(nav, (cx - nav.get_width() // 2, HEIGHT - 25))

        # === Контент таба ===
        content_y = tab_y + 40
        if self.current_tab == "Герои":
            self._draw_heroes(surface, font, big_font, small_font, content_y)
        elif self.current_tab == "Арканы":
            self._draw_arcanas(surface, font, big_font, small_font, content_y)
        elif self.current_tab == "Магазин":
            self._draw_shop(surface, font, big_font, small_font, content_y)
        elif self.current_tab == "Рекорды":
            self._draw_records(surface, font, big_font, small_font, content_y)

        # Уведомление
        if self.notify_timer > 0:
            notif = font.render(self.notification, True, GOLD)
            surface.blit(notif, (cx - notif.get_width() // 2, HEIGHT - 55))

    def _draw_bg(self, surface):
        surface.fill(DARK_BG)

    def _draw_heroes(self, surface, font, big_font, small_font, y_start):
        """Таб Герои: сетка карточек персонажей."""
        chars = list(CHARACTERS.keys())
        card_w, card_h = 160, 120
        gap = 16
        cols = min(3, len(chars))
        cx = WIDTH // 2
        grid_w = cols * card_w + (cols - 1) * gap
        start_x = cx - grid_w // 2

        for i, cid in enumerate(chars):
            c = CHARACTERS[cid]
            col = i % cols
            row = i // cols
            x = start_x + col * (card_w + gap)
            y = y_start + row * (card_h + gap)

            is_unlocked = cid in self.meta.unlocked_chars
            is_selected = (i == self.selected)

            # Карточка
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if not is_unlocked:
                card.fill((30, 30, 30, 160))
                pygame.draw.rect(card, (60, 60, 60), (0, 0, card_w, card_h), 1)
                lock = small_font.render("???", True, (80, 80, 80))
                card.blit(lock, (card_w // 2 - lock.get_width() // 2, card_h // 2 - 8))
            else:
                fill = (60, 45, 80, 200) if is_selected else (40, 30, 60, 160)
                card.fill(fill)
                border = GOLD if is_selected else (120, 120, 120)
                bw = 3 if is_selected else 1
                pygame.draw.rect(card, border, (0, 0, card_w, card_h), bw)

                # Имя
                name = font.render(c["name"], True, WHITE)
                card.blit(name, (card_w // 2 - name.get_width() // 2, 10))

                # HP
                hp = small_font.render(f"HP: {c['hp']}", True, (80, 200, 80))
                card.blit(hp, (10, 40))

                # Скорость
                spd = small_font.render(f"SPD: {c['speed']:.1f}", True, (180, 180, 180))
                card.blit(spd, (10, 58))

                # Оружие
                wep = small_font.render(c.get("start_weapon", ""), True, (150, 150, 200))
                card.blit(wep, (10, 76))

                # Выбран
                if hasattr(self.meta, '_selected_char') and self.meta._selected_char == cid:
                    sel = small_font.render("ВЫБРАН", True, GREEN)
                    card.blit(sel, (card_w - sel.get_width() - 8, 8))

            surface.blit(card, (x, y))

        # Описание выбранного
        if self.selected < len(chars):
            cid = chars[self.selected]
            if cid in self.meta.unlocked_chars:
                c = CHARACTERS[cid]
                desc = small_font.render(c.get("desc", ""), True, (200, 200, 200))
                surface.blit(desc, (cx - desc.get_width() // 2, y_start + 2 * (card_h + gap) + 10))

    def _draw_arcanas(self, surface, font, big_font, small_font, y_start):
        """Таб Арканы: вертикальный список."""
        arcana_ids = list(ARCANA_DEFS.keys())
        card_h = 56
        card_w = WIDTH - 80
        x = 40

        for i, aid in enumerate(arcana_ids):
            adef = ARCANA_DEFS[aid]
            y = y_start + i * (card_h + 6)
            is_selected = (self.meta.selected_arcana == aid)
            is_focused = (i == self.selected)

            # Фон
            card_color = (50, 40, 70) if is_focused else (30, 25, 45)
            pygame.draw.rect(surface, card_color, (x, y, card_w, card_h), border_radius=6)

            # Рамка
            border = GOLD if is_selected else ((100, 140, 255) if is_focused else (50, 45, 65))
            bw = 2 if (is_selected or is_focused) else 1
            pygame.draw.rect(surface, border, (x, y, card_w, card_h), bw, border_radius=6)

            # Иконка
            pygame.draw.rect(surface, adef["color"], (x + 8, y + 10, 14, 14), border_radius=3)

            # Название
            name = font.render(adef["name"], True, adef["color"] if is_selected else WHITE)
            surface.blit(name, (x + 30, y + 6))

            # Описание
            desc = small_font.render(adef["desc"], True, (180, 180, 180))
            surface.blit(desc, (x + 30, y + 28))

            # Выбрана
            if is_selected:
                tag = small_font.render("ВЫБРАНА", True, GOLD)
                surface.blit(tag, (x + card_w - tag.get_width() - 10, y + 10))

    def _draw_shop(self, surface, font, big_font, small_font, y_start):
        """Таб Магазин: PowerUps + достижения."""
        # Статистика
        stats = [
            f"Ранов: {self.meta.total_runs}",
            f"Лучшая волна: {self.meta.best_wave}",
            f"Убийств: {self.meta.total_kills}",
        ]
        for i, s in enumerate(stats):
            t = small_font.render(s, True, (140, 140, 140))
            surface.blit(t, (40, y_start + i * 20))

        y = y_start + 70
        powerup_ids = list(POWERUP_DEFS.keys())
        for i, pid in enumerate(powerup_ids):
            pdef = POWERUP_DEFS[pid]
            level = self.meta.powerups[pid]
            cost = pdef["costs"][level] if level < pdef["max"] else "MAX"
            can_buy = self.meta.can_buy(pid)

            # Подсветка
            if i == self.selected:
                pygame.draw.rect(surface, (50, 40, 70), (WIDTH // 2 - 220, y - 5, 440, 40), border_radius=5)
                pygame.draw.rect(surface, GOLD, (WIDTH // 2 - 220, y - 5, 440, 40), 2, border_radius=5)

            # Название
            name_color = GREEN if can_buy else (150, 150, 150)
            name = font.render(f"{pdef['name']} (Lv {level}/{pdef['max']})", True, name_color)
            surface.blit(name, (WIDTH // 2 - 200, y))

            # Стоимость
            if cost != "MAX":
                cost_t = small_font.render(f"{cost} золота", True, GOLD)
            else:
                cost_t = small_font.render("МАКС", True, (100, 100, 100))
            surface.blit(cost_t, (WIDTH // 2 + 80, y + 3))

            # Описание
            desc = small_font.render(pdef["desc"], True, (130, 130, 130))
            surface.blit(desc, (WIDTH // 2 - 200, y + 20))

            y += 50

        # Достижения (нижняя часть)
        ach_y = HEIGHT - 180
        ach_title = font.render("ДОСТИЖЕНИЯ", True, WHITE)
        surface.blit(ach_title, (40, ach_y))
        ach_y += 28
        for aid, adef in ACHIEVEMENTS.items():
            done = aid in self.meta.achievements_done
            color = GREEN if done else (100, 100, 100)
            prefix = "✓" if done else "✗"
            t = small_font.render(f"{prefix} {adef['name']} - {adef['desc']}", True, color)
            surface.blit(t, (40, ach_y))
            ach_y += 20

    def _draw_records(self, surface, font, big_font, small_font, y_start):
        """Таб Рекорды: таблица лидеров."""
        entries = self.leaderboard_entries[:10]
        if not entries:
            no_data = font.render("Пока нет записей", True, (120, 120, 120))
            surface.blit(no_data, (WIDTH // 2 - no_data.get_width() // 2, y_start + 50))
            return

        # Заголовок таблицы
        headers = "Место  Персонаж    Волна  Убийства  Время"
        h = small_font.render(headers, True, (150, 150, 150))
        surface.blit(h, (60, y_start))
        y = y_start + 28

        for i, e in enumerate(entries):
            survived = e.get("survived", 0)
            line = f"  {i+1:>2}.   {e.get('character', '?'):<12} {e.get('wave', 0):>4}    {e.get('kills', 0):>5}    {survived:>4}c"
            color = GOLD if (i + 1 == getattr(self.meta, '_leaderboard_rank', None)) else WHITE
            t = small_font.render(line, True, color)
            surface.blit(t, (60, y))
            y += 24
