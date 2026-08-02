"""
Рождение святого - Lobby
Табированный экран лобби: Герои / Арканы / Магазин / Рекорды.
"""
import pygame
from config import (
    WIDTH, HEIGHT, WHITE, GOLD, DARK_BG, RED, GREEN,
    POWERUP_DEFS, ACHIEVEMENTS, POWERUP_COSTS, MAX_BANNED_ITEMS,
    ALTAR_DEFS, WEAPON_ARCHIVE_DEFS, FACTION_DEFS, OBELISK_DEFS
)
from arcana import ARCANA_DEFS
from player import CHARACTERS
from save_system import save_progress
from weapons import WEAPON_DEFS
import sound_manager


# Табы (v2: 6 tabs, added Кодекс)
TABS = ["Герои", "Арканы", "Магазин", "Кодекс", "Рекорды", "Прогресс"]
TAB_COLORS = {
    "Герои": (180, 180, 255),
    "Арканы": (255, 180, 100),
    "Магазин": (100, 255, 100),
    "Кодекс": (255, 100, 100),
    "Рекорды": (255, 215, 0),
    "Прогресс": (180, 100, 255),
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
        self.banned_items = set()  # item ids banned from level-up pool
        self.ban_tokens = 0  # available ban slots (earned via achievements)
        self.enemy_kills = {}  # {enemy_type_id: count} per-type kill tracking
        # C4: Multi-Vector Meta-Progression
        self.altar_level = {"might_altar": 0, "regen_altar": 0, "magnet_altar": 0, "luck_altar": 0}
        self.weapon_archive = set()  # unlocked variant ids
        self.faction_rep = {"angels": 0, "demons": 0, "humans": 0}
        self.obelisks = set()  # completed obelisk ids

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

    def can_ban(self) -> bool:
        """Есть ли свободные токены бана."""
        return len(self.banned_items) < self.ban_tokens and len(self.banned_items) < MAX_BANNED_ITEMS

    def toggle_ban(self, item_id: str) -> str:
        """Toggle ban on item. Returns 'banned', 'unbanned', or 'no_tokens'."""
        if item_id in self.banned_items:
            self.banned_items.discard(item_id)
            return "unbanned"
        if not self.can_ban():
            return "no_tokens"
        self.banned_items.add(item_id)
        return "banned"

    def check_achievements(self, elapsed, wave, kills, gold_total,
                           boss_killed=False, reaper_killed=False):
        new_unlocks = []
        if elapsed >= 300 and "survive_5" not in self.achievements_done:
            self.achievements_done.add("survive_5")
            new_unlocks.append(("survive_5", "inquisitor"))
            self.unlocked_chars.add("inquisitor")
            self.ban_tokens += 2
        if boss_killed and "first_boss" not in self.achievements_done:
            self.achievements_done.add("first_boss")
            new_unlocks.append(("first_boss", "weapon_lightning"))
            self.unlocked_weapons.add("lightning")
            self.ban_tokens += 2
        if elapsed >= 600 and "survive_10" not in self.achievements_done:
            self.achievements_done.add("survive_10")
            new_unlocks.append(("survive_10", "weapon_prayer"))
            self.unlocked_weapons.add("prayer")
            self.ban_tokens += 2
        if gold_total >= 10000 and "gold_10000" not in self.achievements_done:
            self.achievements_done.add("gold_10000")
            new_unlocks.append(("gold_10000", "powerup_revive"))
            self.ban_tokens += 2
        if reaper_killed and "kill_reaper" not in self.achievements_done:
            self.achievements_done.add("kill_reaper")
            new_unlocks.append(("kill_reaper", "char_secret"))
            self.ban_tokens += 2
        self.ban_tokens = min(self.ban_tokens, MAX_BANNED_ITEMS)
        return new_unlocks

    # --- C4: Altar ---
    def can_buy_altar(self, altar_id: str) -> bool:
        level = self.altar_level.get(altar_id, 0)
        adef = ALTAR_DEFS.get(altar_id)
        if not adef or level >= adef["max"]:
            return False
        return self.gold >= adef["costs"][level]

    def buy_altar(self, altar_id: str) -> bool:
        if not self.can_buy_altar(altar_id):
            return False
        level = self.altar_level[altar_id]
        cost = ALTAR_DEFS[altar_id]["costs"][level]
        self.gold -= cost
        self.altar_level[altar_id] += 1
        return True

    def get_altar_bonus(self, altar_id: str) -> float:
        """Returns total bonus multiplier (1.0 = no bonus)."""
        level = self.altar_level.get(altar_id, 0)
        adef = ALTAR_DEFS.get(altar_id)
        if not adef:
            return 1.0
        return 1.0 + adef["bonus_per_lvl"] * level

    def get_altar_regen_bonus(self) -> float:
        """Returns flat HP/sec bonus from regen altar."""
        level = self.altar_level.get("regen_altar", 0)
        adef = ALTAR_DEFS.get("regen_altar")
        if not adef:
            return 0.0
        return adef["bonus_per_lvl"] * level

    # --- C4: Weapon Archive ---
    def check_weapon_archive(self) -> list:
        """Check if total_kills unlocks new weapon variants. Returns list of newly unlocked ids."""
        newly = []
        for vid, vdef in WEAPON_ARCHIVE_DEFS.items():
            if vid not in self.weapon_archive and self.total_kills >= vdef["unlock_kills"]:
                self.weapon_archive.add(vid)
                newly.append(vid)
        return newly

    # --- C4: Faction Reputation ---
    def add_faction_rep(self, faction: str, amount: int):
        if faction in self.faction_rep:
            self.faction_rep[faction] += amount

    def get_faction_rewards(self, faction: str) -> list:
        """Returns list of (threshold, name, desc) for rewards earned."""
        rep = self.faction_rep.get(faction, 0)
        fdef = FACTION_DEFS.get(faction, {})
        rewards = []
        for thr, (name, desc) in sorted(fdef.get("rewards", {}).items()):
            if rep >= thr:
                rewards.append((thr, name, desc))
        return rewards

    # --- C4: Obelisks ---
    def complete_obelisk(self, obelisk_id: str) -> bool:
        """Mark an obelisk as completed and grant gold reward."""
        if obelisk_id in self.obelisks:
            return False
        odef = OBELISK_DEFS.get(obelisk_id)
        if not odef:
            return False
        self.obelisks.add(obelisk_id)
        self.gold += odef["reward_gold"]
        return True


class LobbyScreen:
    """Табированный экран лобби."""
    def __init__(self):
        self.active = False
        self.meta = None
        self.menu = None  # MainMenu (для selected_char)
        self.tab_index = 0
        self.selected = 0  # индекс внутри таба
        self.notification = ""
        self.notify_timer = 0.0
        self.leaderboard_entries = []
        self.ban_mode = False  # True = ban sub-menu in shop
        self.ban_scroll = 0    # scroll offset for ban list
        self.progress_lane = 0  # 0=Altar, 1=Weapon Archive, 2=Faction Rep, 3=Obelisks

    def activate(self, meta: MetaProgress, menu=None):
        self.active = True
        self.meta = meta
        self.menu = menu
        self.ban_mode = False
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
                self.ban_mode = False
                sound_manager.play("ui_hover")
                return None
            if event.key == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.tab_index = (self.tab_index - 1) % len(TABS)
                self.selected = 0
                self.ban_mode = False
                return None

            # ESC = назад в меню (или выход из подменю)
            if event.key == pygame.K_ESCAPE:
                if self.ban_mode:
                    self.ban_mode = False
                    self.selected = 0
                    sound_manager.play("ui_back")
                    return None
                self.active = False
                sound_manager.play("ui_back")
                return "back"

            # Бестиарий (B) — только если НЕ в магазине
            if event.key == pygame.K_b and self.current_tab != "Магазин":
                return "bestiary"

            # Кодекс (C)
            if event.key == pygame.K_c:
                return "codex"

            # Настройки (O)
            if event.key == pygame.K_o:
                return ("settings", {"return_to": "lobby"})

            # Навигация внутри таба
            # Если ban_mode активен, все события идут в _handle_ban
            if self.ban_mode:
                return self._handle_ban(event)
            if self.current_tab == "Герои":
                return self._handle_heroes(event)
            elif self.current_tab == "Арканы":
                return self._handle_arcanas(event)
            elif self.current_tab == "Магазин":
                return self._handle_shop(event)
            elif self.current_tab == "Рекорды":
                return self._handle_records(event)
            elif self.current_tab == "Прогресс":
                return self._handle_progress(event)
            elif self.current_tab == "Кодекс":
                return self._handle_codex(event)

        return None

    def _handle_heroes(self, event):
        chars = list(CHARACTERS.keys())
        if not chars:
            return None
        cols = min(3, len(chars))
        if event.key == pygame.K_UP:
            self.selected = (self.selected - cols) % len(chars)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + cols) % len(chars)
        elif event.key == pygame.K_LEFT:
            self.selected = (self.selected - 1) % len(chars)
        elif event.key == pygame.K_RIGHT:
            self.selected = (self.selected + 1) % len(chars)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            cid = chars[self.selected]
            if cid in self.meta.unlocked_chars:
                if self.menu:
                    # Если персонаж уже выбран — начинаем забег
                    if self.menu.selected_char == cid:
                        sound_manager.play("ui_confirm")
                        return "play"
                    self.menu.selected_char = cid
                    sound_manager.play("ui_select")
            else:
                sound_manager.play("ui_back")
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
                sound_manager.play("ui_back")
            else:
                self.meta.selected_arcana = aid
                self.notification = f"Аркана: {ARCANA_DEFS[aid]['name']}"
                sound_manager.play("ui_select")
            self.notify_timer = 2.0
            save_progress(self.meta)
        return None

    def _handle_shop(self, event):
        # Toggle ban mode with B key
        if event.key == pygame.K_b:
            self.ban_mode = not self.ban_mode
            self.selected = 0
            self.ban_scroll = 0
            sound_manager.play("ui_hover")
            return None

        if self.ban_mode:
            return self._handle_ban(event)
        return self._handle_powerups(event)

    def _get_ban_items(self):
        """Список всех предметов для бана: оружие + пассивки."""
        items = []
        from weapons import WEAPON_DEFS, PASSIVE_DEFS
        for wid, wdef in WEAPON_DEFS.items():
            items.append({"type": "weapon", "id": wid, "name": wdef["name"], "color": wdef["color"]})
        for pid, pdef in PASSIVE_DEFS.items():
            items.append({"type": "passive", "id": pid, "name": pdef["name"], "color": pdef["color"]})
        return items

    def _handle_ban(self, event):
        """Навигация по бан-листу."""
        items = self._get_ban_items()
        # B toggles ban_mode off
        if event.key == pygame.K_b:
            self.ban_mode = False
            self.selected = 0
            sound_manager.play("ui_back")
            return None
        max_visible = 8
        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(items)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(items)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            item = items[self.selected]
            item_id = item["id"]
            result = self.meta.toggle_ban(item_id)
            if result == "banned":
                self.notification = f"Забанено: {item['name']}"
                self.notify_timer = 2.0
                save_progress(self.meta)
                sound_manager.play("ui_confirm")
            elif result == "unbanned":
                self.notification = f"Разбанено: {item['name']}"
                self.notify_timer = 2.0
                save_progress(self.meta)
                sound_manager.play("ui_back")
            else:
                self.notification = "Нет токенов бана!"
                self.notify_timer = 1.5
                sound_manager.play("ui_back")
        # Scroll
        if self.selected >= self.ban_scroll + max_visible:
            self.ban_scroll = self.selected - max_visible + 1
        elif self.selected < self.ban_scroll:
            self.ban_scroll = self.selected
        return None

    def _handle_powerups(self, event):
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
                sound_manager.play("ui_confirm")
            else:
                self.notification = "Недостаточно золота!"
                self.notify_timer = 1.5
                sound_manager.play("ui_back")
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
        nav = small_font.render("Enter - играть  |  TAB - табы  |  B - бестиарий  |  C - кодекс  |  O - настройки  |  ESC - меню", True, (80, 80, 80))
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
        elif self.current_tab == "Прогресс":
            self._draw_progress(surface, font, big_font, small_font, content_y)
        elif self.current_tab == "Кодекс":
            self._draw_codex(surface, font, big_font, small_font, content_y)

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
                if self.menu and self.menu.selected_char == cid:
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
        """Таб Магазин: PowerUps + достижения + Бан."""
        if self.ban_mode:
            self._draw_ban_list(surface, font, big_font, small_font, y_start)
            return

        # Статистика
        stats = [
            f"Ранов: {self.meta.total_runs}",
            f"Лучшая волна: {self.meta.best_wave}",
            f"Убийств: {self.meta.total_kills}",
        ]
        for i, s in enumerate(stats):
            t = small_font.render(s, True, (140, 140, 140))
            surface.blit(t, (40, y_start + i * 20))

        # Бан-статус
        ban_info = font.render(
            f"[B] Бан: {len(self.meta.banned_items)}/{self.meta.ban_tokens} токенов",
            True, (200, 100, 100) if self.meta.banned_items else (100, 200, 100)
        )
        surface.blit(ban_info, (WIDTH - ban_info.get_width() - 20, y_start))

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

    def _draw_ban_list(self, surface, font, big_font, small_font, y_start):
        """Рисует бан-лист: все оружие + пассивки с toggle."""
        items = self._get_ban_items()
        max_visible = 8
        card_h = 44
        card_w = WIDTH - 80
        x = 40

        # Заголовок
        title = big_font.render("БАН ПРЕДМЕТОВ", True, (220, 80, 80))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, y_start))

        # Статус токенов
        status = font.render(
            f"Токенов: {self.meta.ban_tokens}  |  Забанено: {len(self.meta.banned_items)}/{MAX_BANNED_ITEMS}  |  ESC/B - назад",
            True, (180, 180, 180)
        )
        surface.blit(status, (WIDTH // 2 - status.get_width() // 2, y_start + 35))

        y = y_start + 70
        visible_items = items[self.ban_scroll:self.ban_scroll + max_visible]
        for i, item in enumerate(visible_items):
            idx = self.ban_scroll + i
            is_selected = (idx == self.selected)
            is_banned = item["id"] in self.meta.banned_items

            # Фон карточки
            fill = (60, 30, 30) if is_banned else ((50, 40, 70) if is_selected else (35, 28, 50))
            pygame.draw.rect(surface, fill, (x, y, card_w, card_h), border_radius=6)

            # Рамка
            if is_banned:
                border = (220, 60, 60)
                bw = 2
            elif is_selected:
                border = GOLD
                bw = 2
            else:
                border = (60, 55, 75)
                bw = 1
            pygame.draw.rect(surface, border, (x, y, card_w, card_h), bw, border_radius=6)

            # Тип-иконка
            type_label = "[W]" if item["type"] == "weapon" else "[P]"
            type_color = (180, 120, 120) if item["type"] == "weapon" else (120, 180, 120)
            tl = small_font.render(type_label, True, type_color)
            surface.blit(tl, (x + 10, y + card_h // 2 - tl.get_height() // 2))

            # Название
            name_color = (255, 100, 100) if is_banned else item["color"]
            name = font.render(item["name"], True, name_color)
            surface.blit(name, (x + 50, y + card_h // 2 - name.get_height() // 2))

            # Статус бана
            if is_banned:
                ban_tag = font.render("ЗАБАНЕНО", True, (255, 60, 60))
                surface.blit(ban_tag, (x + card_w - ban_tag.get_width() - 10, y + card_h // 2 - ban_tag.get_height() // 2))
            elif self.meta.can_ban():
                tag = small_font.render("ENTER - бан", True, (120, 120, 120))
                surface.blit(tag, (x + card_w - tag.get_width() - 10, y + card_h // 2 - tag.get_height() // 2))

            y += card_h + 4

        # Скролл-индикатор
        if len(items) > max_visible:
            scroll_text = small_font.render(f"{self.ban_scroll + 1}-{min(self.ban_scroll + max_visible, len(items))} из {len(items)}", True, (100, 100, 100))
            surface.blit(scroll_text, (WIDTH // 2 - scroll_text.get_width() // 2, y + 10))

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

    def _handle_progress(self, event):
        """Handle Progress tab: 4 lanes (Altar/Archive/Factions/Obelisks)."""
        LANES = ["altar", "archive", "factions", "obelisks"]
        if event.key == pygame.K_LEFT:
            self.progress_lane = (self.progress_lane - 1) % len(LANES)
            self.selected = 0
            sound_manager.play("ui_hover")
        elif event.key == pygame.K_RIGHT:
            self.progress_lane = (self.progress_lane + 1) % len(LANES)
            self.selected = 0
            sound_manager.play("ui_hover")
        elif event.key == pygame.K_UP:
            self.selected = max(0, self.selected - 1)
        elif event.key == pygame.K_DOWN:
            lane = LANES[self.progress_lane]
            max_items = self._progress_max_items(lane)
            self.selected = min(max_items - 1, self.selected + 1)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            lane = LANES[self.progress_lane]
            self._progress_action(lane)
        return None

    def _progress_max_items(self, lane: str) -> int:
        if lane == "altar":
            return len(ALTAR_DEFS)
        elif lane == "archive":
            return len(WEAPON_ARCHIVE_DEFS)
        elif lane == "factions":
            return len(FACTION_DEFS)
        elif lane == "obelisks":
            return len(OBELISK_DEFS)
        return 1

    def _progress_action(self, lane: str):
        """Execute action on selected item in the given lane."""
        if lane == "altar":
            altar_ids = list(ALTAR_DEFS.keys())
            if self.selected < len(altar_ids):
                aid = altar_ids[self.selected]
                if self.meta.buy_altar(aid):
                    self.notification = f"Алтарь: {ALTAR_DEFS[aid]['name']} улучшен!"
                    self.notify_timer = 2.0
                    save_progress(self.meta)
                    sound_manager.play("ui_confirm")
                else:
                    self.notification = "Недостаточно золота или максимум!"
                    self.notify_timer = 1.5
                    sound_manager.play("ui_back")
        elif lane == "archive":
            # Archive is display-only (unlock by kills)
            sound_manager.play("ui_back")
        elif lane == "factions":
            # Factions are display-only (rep gained from gameplay)
            sound_manager.play("ui_back")
        elif lane == "obelisks":
            obelisk_ids = list(OBELISK_DEFS.keys())
            if self.selected < len(obelisk_ids):
                oid = obelisk_ids[self.selected]
                if oid in self.meta.obelisks:
                    self.notification = "Столп уже покорён!"
                    self.notify_timer = 1.5
                    sound_manager.play("ui_back")
                else:
                    # Can only complete during gameplay, not from lobby
                    self.notification = "Столпы покоряются во время игры!"
                    self.notify_timer = 2.0
                    sound_manager.play("ui_back")

    def _draw_progress(self, surface, font, big_font, small_font, y_start):
        """Draw Progress tab with 4 lanes."""
        LANES = [
            ("altar", "Алтарь жертвоприношений", (220, 100, 100)),
            ("archive", "Архив оружия", (100, 200, 255)),
            ("factions", "Репутация фракций", (200, 200, 140)),
            ("obelisks", "Столпы испытаний", (180, 120, 220)),
        ]

        # Lane selector (horizontal tabs)
        lane_x = 40
        for i, (lane_id, lane_name, lane_color) in enumerate(LANES):
            is_active = (i == self.progress_lane)
            color = lane_color if is_active else (80, 80, 80)
            label = f"[{lane_name}]" if is_active else lane_name
            t = small_font.render(label, True, color)
            surface.blit(t, (lane_x, y_start))
            if is_active:
                pygame.draw.line(surface, color, (lane_x, y_start + 18),
                                (lane_x + t.get_width(), y_start + 18), 2)
            lane_x += t.get_width() + 16

        content_y = y_start + 30
        lane_id = LANES[self.progress_lane][0]

        if lane_id == "altar":
            self._draw_progress_altar(surface, font, small_font, content_y)
        elif lane_id == "archive":
            self._draw_progress_archive(surface, font, small_font, content_y)
        elif lane_id == "factions":
            self._draw_progress_factions(surface, font, small_font, content_y)
        elif lane_id == "obelisks":
            self._draw_progress_obelisks(surface, font, small_font, content_y)

    def _draw_progress_altar(self, surface, font, small_font, y_start):
        """Draw altar progression sub-tab."""
        altar_ids = list(ALTAR_DEFS.keys())
        card_h = 52
        card_w = WIDTH - 80
        x = 40

        for i, aid in enumerate(altar_ids):
            adef = ALTAR_DEFS[aid]
            level = self.meta.altar_level.get(aid, 0)
            cost = adef["costs"][level] if level < adef["max"] else "MAX"
            is_focused = (i == self.selected)

            y = y_start + i * (card_h + 6)
            fill = (50, 35, 60) if is_focused else (30, 22, 42)
            pygame.draw.rect(surface, fill, (x, y, card_w, card_h), border_radius=6)

            border = adef["color"] if is_focused else (50, 45, 65)
            bw = 2 if is_focused else 1
            pygame.draw.rect(surface, border, (x, y, card_w, card_h), bw, border_radius=6)

            # Color swatch
            pygame.draw.rect(surface, adef["color"], (x + 8, y + 10, 14, 14), border_radius=3)

            # Name + level
            name = font.render(f"{adef['name']} (Lv {level}/{adef['max']})", True, WHITE)
            surface.blit(name, (x + 30, y + 5))

            # Cost
            if cost != "MAX":
                can_buy = self.meta.can_buy_altar(aid)
                cost_color = GREEN if can_buy else (150, 150, 150)
                cost_t = small_font.render(f"{cost} G", True, cost_color)
            else:
                cost_t = small_font.render("МАКС", True, (100, 100, 100))
            surface.blit(cost_t, (x + card_w - cost_t.get_width() - 10, y + 5))

            # Desc
            desc = small_font.render(adef["desc"], True, (160, 160, 160))
            surface.blit(desc, (x + 30, y + 28))

            # Progress bar
            bar_x = x + card_w - 160
            bar_y = y + 30
            bar_w = 120
            bar_h = 8
            pygame.draw.rect(surface, (40, 30, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            if adef["max"] > 0:
                fill_w = int(bar_w * level / adef["max"])
                if fill_w > 0:
                    pygame.draw.rect(surface, adef["color"], (bar_x, bar_y, fill_w, bar_h), border_radius=4)

    def _draw_progress_archive(self, surface, font, small_font, y_start):
        """Draw weapon archive sub-tab."""
        archive_ids = list(WEAPON_ARCHIVE_DEFS.keys())
        card_h = 48
        card_w = WIDTH - 80
        x = 40

        for i, vid in enumerate(archive_ids):
            vdef = WEAPON_ARCHIVE_DEFS[vid]
            is_unlocked = vid in self.meta.weapon_archive
            is_focused = (i == self.selected)

            y = y_start + i * (card_h + 4)

            if not is_unlocked:
                fill = (25, 25, 30) if is_focused else (20, 20, 25)
            else:
                fill = (45, 35, 60) if is_focused else (30, 25, 45)
            pygame.draw.rect(surface, fill, (x, y, card_w, card_h), border_radius=6)

            border = vdef["color"] if is_unlocked and is_focused else ((80, 80, 80) if not is_unlocked else (50, 45, 65))
            bw = 2 if is_focused else 1
            pygame.draw.rect(surface, border, (x, y, card_w, card_h), bw, border_radius=6)

            if is_unlocked:
                # Color swatch
                pygame.draw.rect(surface, vdef["color"], (x + 8, y + 10, 12, 12), border_radius=3)
                # Name
                name = font.render(vdef["name"], True, vdef["color"])
                surface.blit(name, (x + 28, y + 4))
                # Desc
                desc = small_font.render(vdef["desc"], True, (160, 160, 160))
                surface.blit(desc, (x + 28, y + 24))
                # Base weapon tag
                tag = small_font.render(f"({WEAPON_DEFS.get(vdef['base'], {}).get('name', vdef['base'])})", True, (100, 100, 120))
                surface.blit(tag, (x + card_w - tag.get_width() - 10, y + 8))
            else:
                lock = small_font.render(f"???  ({vdef['unlock_kills']} убийств)", True, (80, 80, 80))
                surface.blit(lock, (x + 28, y + 4))
                # Progress
                progress = min(1.0, self.meta.total_kills / max(1, vdef["unlock_kills"]))
                bar_x = x + 28
                bar_y = y + 30
                bar_w = card_w - 60
                bar_h = 6
                pygame.draw.rect(surface, (40, 30, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
                fill_w = int(bar_w * progress)
                if fill_w > 0:
                    pygame.draw.rect(surface, vdef["color"], (bar_x, bar_y, fill_w, bar_h), border_radius=3)

    def _draw_progress_factions(self, surface, font, small_font, y_start):
        """Draw faction reputation sub-tab."""
        faction_ids = list(FACTION_DEFS.keys())
        card_h = 90
        card_w = WIDTH - 80
        x = 40

        for i, fid in enumerate(faction_ids):
            fdef = FACTION_DEFS[fid]
            rep = self.meta.faction_rep.get(fid, 0)
            is_focused = (i == self.selected)

            y = y_start + i * (card_h + 6)

            fill = (45, 35, 55) if is_focused else (28, 22, 38)
            pygame.draw.rect(surface, fill, (x, y, card_w, card_h), border_radius=8)

            border = fdef["color"] if is_focused else (50, 45, 65)
            bw = 2 if is_focused else 1
            pygame.draw.rect(surface, border, (x, y, card_w, card_h), bw, border_radius=8)

            # Color swatch
            pygame.draw.rect(surface, fdef["color"], (x + 10, y + 10, 16, 16), border_radius=4)

            # Name + rep
            name = font.render(f"{fdef['name']}  ({rep} REP)", True, WHITE)
            surface.blit(name, (x + 34, y + 8))

            # Desc
            desc = small_font.render(fdef["desc"], True, (140, 140, 140))
            surface.blit(desc, (x + 34, y + 28))

            # Rewards
            rewards = self.meta.get_faction_rewards(fid)
            reward_y = y + 48
            for thr, rname, rdesc in rewards:
                rt = small_font.render(f"[{rname}] {rdesc}", True, GREEN)
                surface.blit(rt, (x + 34, reward_y))
                reward_y += 16

            # Next reward
            next_reward = None
            for thr, (rname, rdesc) in sorted(fdef["rewards"].items()):
                if rep < thr:
                    next_reward = (thr, rname, rdesc)
                    break
            if next_reward:
                thr, rname, rdesc = next_reward
                nr = small_font.render(f"Далее: [{rname}] {rdesc} ({thr} REP)", True, (120, 120, 100))
                surface.blit(nr, (x + 34, reward_y))

    def _draw_progress_obelisks(self, surface, font, small_font, y_start):
        """Draw obelisks sub-tab."""
        obelisk_ids = list(OBELISK_DEFS.keys())
        card_h = 52
        card_w = WIDTH - 80
        x = 40

        for i, oid in enumerate(obelisk_ids):
            odef = OBELISK_DEFS[oid]
            is_done = oid in self.meta.obelisks
            is_focused = (i == self.selected)

            y = y_start + i * (card_h + 4)

            fill = (35, 50, 35) if is_done else ((45, 35, 55) if is_focused else (28, 22, 38))
            pygame.draw.rect(surface, fill, (x, y, card_w, card_h), border_radius=6)

            if is_done:
                border = GREEN
            elif is_focused:
                border = odef["color"]
            else:
                border = (50, 45, 65)
            bw = 2 if (is_done or is_focused) else 1
            pygame.draw.rect(surface, border, (x, y, card_w, card_h), bw, border_radius=6)

            # Status icon
            status = "✓" if is_done else "?"
            status_color = GREEN if is_done else (100, 100, 100)
            st = font.render(status, True, status_color)
            surface.blit(st, (x + 8, y + 4))

            # Name
            name = font.render(odef["name"], True, odef["color"] if not is_done else GREEN)
            surface.blit(name, (x + 28, y + 4))

            # Desc + reward
            if is_done:
                desc = small_font.render("ПОКОРЕНО", True, GREEN)
            else:
                desc = small_font.render(f"{odef['desc']}  +{odef['reward_gold']}G", True, (160, 160, 140))
            surface.blit(desc, (x + 28, y + 28))

    # ============================================================
    # КОДЕКС TAB (v2: integrated from bestiary.py CodexScreen)
    # ============================================================

    def _handle_codex(self, event):
        """Handle events for Кодекс tab."""
        from enemies import ENEMY_TYPES
        from bestiary import ENEMY_ORDER, WEAPON_ORDER
        from weapons import WEAPON_DEFS

        # Sub-tabs: Враги / Оружие / Эволюции
        if not hasattr(self, '_codex_subtab'):
            self._codex_subtab = 0  # 0=Враги, 1=Оружие, 2=Эволюции
            self._codex_selected = 0

        sub_tabs = ["Враги", "Оружие", "Эволюции"]

        if event.key == pygame.K_LEFT:
            self._codex_subtab = (self._codex_subtab - 1) % len(sub_tabs)
            self._codex_selected = 0
            sound_manager.play("ui_hover")
            return None
        if event.key == pygame.K_RIGHT:
            self._codex_subtab = (self._codex_subtab + 1) % len(sub_tabs)
            self._codex_selected = 0
            sound_manager.play("ui_hover")
            return None

        if event.key == pygame.K_UP:
            self._codex_selected = max(0, self._codex_selected - 1)
            sound_manager.play("ui_hover")
        elif event.key == pygame.K_DOWN:
            max_items = self._get_codex_max_items()
            self._codex_selected = min(max_items - 1, self._codex_selected + 1)
            sound_manager.play("ui_hover")

        return None

    def _get_codex_max_items(self):
        """Get max items for current codex sub-tab."""
        from enemies import ENEMY_TYPES
        from bestiary import ENEMY_ORDER, WEAPON_ORDER
        from weapons import WEAPON_DEFS
        if self._codex_subtab == 0:
            return len(ENEMY_ORDER)
        elif self._codex_subtab == 1:
            return len(WEAPON_ORDER)
        else:
            from weapons import EVOLUTIONS
            return len(EVOLUTIONS)

    def _draw_codex(self, surface, font, big_font, small_font, y_start):
        """Таб Кодекс: враги / оружие / эволюции."""
        from enemies import ENEMY_TYPES
        from bestiary import ENEMY_ORDER, WEAPON_ORDER
        from weapons import WEAPON_DEFS

        if not hasattr(self, '_codex_subtab'):
            self._codex_subtab = 0
            self._codex_selected = 0

        sub_tabs = ["Враги", "Оружие", "Эволюции"]

        # Sub-tab bar
        sub_y = y_start
        sub_w = 120
        total_sub_w = len(sub_tabs) * sub_w + (len(sub_tabs) - 1) * 8
        sub_x = WIDTH // 2 - total_sub_w // 2
        for i, st_name in enumerate(sub_tabs):
            sx = sub_x + i * (sub_w + 8)
            is_active = (i == self._codex_subtab)
            fill = (50, 45, 65) if is_active else (30, 28, 40)
            border = GOLD if is_active else (80, 75, 90)
            pygame.draw.rect(surface, fill, (sx, sub_y, sub_w, 28), border_radius=6)
            pygame.draw.rect(surface, border, (sx, sub_y, sub_w, 28), 1 if is_active else 0, border_radius=6)
            st_text = small_font.render(st_name, True, GOLD if is_active else (120, 120, 120))
            surface.blit(st_text, (sx + sub_w // 2 - st_text.get_width() // 2, sub_y + 6))

        # Content
        content_y = sub_y + 40
        if self._codex_subtab == 0:
            self._draw_codex_enemies(surface, font, small_font, content_y)
        elif self._codex_subtab == 1:
            self._draw_codex_weapons(surface, font, small_font, content_y)
        else:
            self._draw_codex_evolutions(surface, font, small_font, content_y)

    def _draw_codex_enemies(self, surface, font, small_font, y_start):
        """Draw enemy codex entries."""
        from enemies import ENEMY_TYPES
        from bestiary import ENEMY_ORDER

        y = y_start
        for i, eid in enumerate(ENEMY_ORDER):
            etype = ENEMY_TYPES.get(eid, {})
            kills = self.meta.enemy_kills.get(eid, 0) if self.meta else 0
            unlocked = kills > 0

            is_focused = (i == self._codex_selected)
            fill = (40, 35, 55) if is_focused else (25, 22, 35)
            border = GOLD if is_focused else (60, 55, 75)
            pygame.draw.rect(surface, fill, (60, y, WIDTH - 120, 36), border_radius=4)
            pygame.draw.rect(surface, border, (60, y, WIDTH - 120, 36), 1 if is_focused else 0, border_radius=4)

            if unlocked:
                name = font.render(etype.get("name", eid), True, WHITE)
                kills_text = small_font.render(f"Убийств: {kills}", True, (150, 150, 150))
                surface.blit(name, (80, y + 8))
                surface.blit(kills_text, (WIDTH - 200, y + 10))
            else:
                name = font.render("???", True, (80, 80, 80))
                surface.blit(name, (80, y + 8))

            y += 40

    def _draw_codex_weapons(self, surface, font, small_font, y_start):
        """Draw weapon codex entries."""
        from bestiary import WEAPON_ORDER
        from weapons import WEAPON_DEFS

        y = y_start
        for i, wid in enumerate(WEAPON_ORDER):
            wdef = WEAPON_DEFS.get(wid, {})
            is_focused = (i == self._codex_selected)

            fill = (40, 35, 55) if is_focused else (25, 22, 35)
            border = GOLD if is_focused else (60, 55, 75)
            pygame.draw.rect(surface, fill, (60, y, WIDTH - 120, 36), border_radius=4)
            pygame.draw.rect(surface, border, (60, y, WIDTH - 120, 36), 1 if is_focused else 0, border_radius=4)

            name = font.render(wdef.get("name", wid), True, WHITE)
            wtype = small_font.render(wdef.get("type", "?"), True, (150, 150, 150))
            surface.blit(name, (80, y + 8))
            surface.blit(wtype, (WIDTH - 200, y + 10))

            y += 40

    def _draw_codex_evolutions(self, surface, font, small_font, y_start):
        """Draw evolution codex entries."""
        from weapons import EVOLUTIONS

        y = y_start
        evo_list = list(EVOLUTIONS.items())
        for i, (eid, edef) in enumerate(evo_list):
            is_focused = (i == self._codex_selected)

            fill = (40, 35, 55) if is_focused else (25, 22, 35)
            border = GOLD if is_focused else (60, 55, 75)
            pygame.draw.rect(surface, fill, (60, y, WIDTH - 120, 36), border_radius=4)
            pygame.draw.rect(surface, border, (60, y, WIDTH - 120, 36), 1 if is_focused else 0, border_radius=4)

            name = font.render(edef.get("name", eid), True, GOLD)
            req = small_font.render(f"{edef.get('base_weapon', '?')} + {edef.get('passive', '?')}", True, (150, 150, 150))
            surface.blit(name, (80, y + 8))
            surface.blit(req, (300, y + 10))

            y += 40
