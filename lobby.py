"""
Рождение святого — Lobby
Магазин PowerUp между ранами. Достижения. Мета-прогрессия.
"""
import pygame
from config import (
    WIDTH, HEIGHT, WHITE, GOLD, DARK_BG, RED, GREEN,
    POWERUP_DEFS, ACHIEVEMENTS, POWERUP_COSTS, LUCKY_COSTS, REVIVE_COSTS
)


class MetaProgress:
    """Глобальный прогресс между ранами."""
    def __init__(self):
        self.gold = 0
        self.total_runs = 0
        self.best_wave = 0
        self.best_time = 0
        self.total_kills = 0
        self.powerups = {pid: 0 for pid in POWERUP_DEFS}
        self.unlocked_chars = {"warrior", "paladin"}  # Инквизитор нужно разблокировать
        self.unlocked_weapons = {"whip", "fire", "halo", "rosary"}
        self.achievements_done = set()

    def get_powerup_bonus(self, powerup_id: str) -> float:
        """Возвращает бонус от powerup."""
        level = self.powerups.get(powerup_id, 0)
        if powerup_id == "might":
            return 1.0 + 0.05 * level
        elif powerup_id == "sturdiness":
            return 1.0 + 0.10 * level
        elif powerup_id == "swiftness":
            return 1.0 + 0.05 * level
        elif powerup_id == "greed":
            return 1.0 + 0.10 * level
        elif powerup_id == "luck":
            return 1.0 + 0.10 * level
        elif powerup_id == "revive":
            return level  # количество воскрешений
        return 1.0

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

    def check_achievements(self, elapsed: float, wave: int, kills: int, gold_total: int,
                           boss_killed: bool = False, reaper_killed: bool = False):
        """Проверяет и разблокирует достижения."""
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
    """Экран лобби с магазином PowerUp."""
    def __init__(self):
        self.active = False
        self.selected = 0
        self.meta = None
        self.notification = ""  # текст уведомления
        self.notify_timer = 0.0

    def activate(self, meta: MetaProgress):
        self.active = True
        self.meta = meta
        self.selected = 0

    def handle_event(self, event) -> str:
        """Возвращает: 'play', None"""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            powerup_ids = list(POWERUP_DEFS.keys())

            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(powerup_ids)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(powerup_ids)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                pid = powerup_ids[self.selected]
                if self.meta.buy(pid):
                    self.notification = f"Куплено: {POWERUP_DEFS[pid]['name']}!"
                    self.notify_timer = 2.0
                else:
                    self.notification = "Недостаточно золота!"
                    self.notify_timer = 1.5
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                return "play"

        return None

    def update(self, dt: float):
        if self.notify_timer > 0:
            self.notify_timer -= dt

    def draw(self, surface: pygame.Surface, font, big_font, small_font):
        if not self.active:
            return

        surface.fill(DARK_BG)

        # Заголовок
        title = big_font.render("ЛОББИ", True, GOLD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        # Золото
        gold_text = font.render(f"Золото: {self.meta.gold}", True, GOLD)
        surface.blit(gold_text, (WIDTH // 2 - gold_text.get_width() // 2, 90))

        # Статистика
        stats = [
            f"Ранов: {self.meta.total_runs}",
            f"Лучшая волна: {self.meta.best_wave}",
            f"Лучшее время: {self.meta.best_time // 60}:{self.meta.best_time % 60:02d}",
            f"Всего убийств: {self.meta.total_kills}",
        ]
        for i, s in enumerate(stats):
            t = small_font.render(s, True, (180, 180, 180))
            surface.blit(t, (20, 130 + i * 22))

        # PowerUp магазин
        shop_title = font.render("МАГАЗИН", True, WHITE)
        surface.blit(shop_title, (WIDTH // 2 - shop_title.get_width() // 2, 140))

        powerup_ids = list(POWERUP_DEFS.keys())
        y = 180
        for i, pid in enumerate(powerup_ids):
            pdef = POWERUP_DEFS[pid]
            level = self.meta.powerups[pid]
            cost = pdef["costs"][level] if level < pdef["max"] else "MAX"
            can_buy = self.meta.can_buy(pid)

            # Подсветка выбранного
            if i == self.selected:
                pygame.draw.rect(surface, (50, 40, 70), (WIDTH // 2 - 200, y - 5, 400, 35), border_radius=5)
                pygame.draw.rect(surface, GOLD, (WIDTH // 2 - 200, y - 5, 400, 35), 2, border_radius=5)

            # Название
            name_color = GREEN if can_buy else (150, 150, 150)
            name_text = font.render(f"{pdef['name']} (Lv {level}/{pdef['max']})", True, name_color)
            surface.blit(name_text, (WIDTH // 2 - 180, y))

            # Стоимость
            if cost != "MAX":
                cost_text = small_font.render(f"{cost} золота", True, GOLD)
            else:
                cost_text = small_font.render("МАКС", True, (100, 100, 100))
            surface.blit(cost_text, (WIDTH // 2 + 80, y + 3))

            # Описание
            desc_text = small_font.render(pdef["desc"], True, (150, 150, 150))
            surface.blit(desc_text, (WIDTH // 2 - 180, y + 18))

            y += 45

        # Достижения
        ach_title = font.render("ДОСТИЖЕНИЯ", True, WHITE)
        surface.blit(ach_title, (20, 480))

        y = 510
        for aid, adef in ACHIEVEMENTS.items():
            done = aid in self.meta.achievements_done
            color = GREEN if done else (100, 100, 100)
            prefix = "✓" if done else "✗"
            text = small_font.render(f"{prefix} {adef['name']} — {adef['desc']}", True, color)
            surface.blit(text, (20, y))
            y += 20

        # Уведомление
        if self.notify_timer > 0:
            notif = font.render(self.notification, True, GOLD)
            surface.blit(notif, (WIDTH // 2 - notif.get_width() // 2, HEIGHT - 60))

        # Подсказка
        hint = small_font.render("↑↓ — выбор  |  ENTER — купить  |  ESC — начать ран", True, (120, 120, 120))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))
