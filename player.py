"""
Рождение святого - Player
Класс игрока: движение, HP, статы, инвентарь.
"""
import pygame
from config import (
    WIDTH, HEIGHT, PLAYER_BASE_SPEED, PLAYER_BASE_HP,
    PICKUP_RANGE_BASE, INVULN_AFTER_LEVELUP,
    calc_damage_mult, calc_cooldown_mult, calc_area_mult,
    calc_speed_mult, calc_pickup_range, calc_regen, calc_max_hp,
    WHITE, RED, GOLD
)


CHARACTERS = {
    "warrior": {
        "name": "Воин",
        "desc": "+10% урон каждые 10 уровней",
        "start_weapon": "whip",
        "hp": 120,
        "speed": 3.0,
        "passive_bonus": "damage_per_10_levels",
        "color": (200, 60, 60),
    },
    "paladin": {
        "name": "Паладин",
        "desc": "+25% pickup range",
        "start_weapon": "halo",
        "hp": 100,
        "speed": 3.5,
        "passive_bonus": "pickup_range",
        "color": (60, 120, 200),
    },
    "inquisitor": {
        "name": "Инквизитор",
        "desc": "+1 снаряд ко всему оружию",
        "start_weapon": "fire",
        "hp": 80,
        "speed": 4.0,
        "passive_bonus": "projectile_bonus",
        "color": (200, 180, 60),
    },
    "pilgrim": {
        "name": "Пилигрим",
        "desc": "+30% XP от гемов",
        "start_weapon": "rosary",
        "hp": 90,
        "speed": 3.2,
        "passive_bonus": "xp_bonus",
        "color": (100, 180, 120),
    },
    "monk": {
        "name": "Монах",
        "desc": "+1 HP/сек регенерация",
        "start_weapon": "prayer",
        "hp": 110,
        "speed": 2.8,
        "passive_bonus": "base_regen",
        "color": (180, 160, 140),
    },
}


class Player:
    def __init__(self, char_id: str, x: float, y: float):
        char = CHARACTERS[char_id]
        self.char_id = char_id
        self.name = char["name"]
        self.color = char["color"]

        # Позиция
        self.pos = pygame.Vector2(x, y)
        self.facing = pygame.Vector2(1, 0)
        self.radius = 14

        # Базовые статы
        self.base_hp = char["hp"]
        self.base_speed = char["speed"]
        self.char_bonus = char["passive_bonus"]

        # Текущие статы
        self.hp = self.base_hp
        self.max_hp = self.base_hp
        self.speed = self.base_speed

        # Инвентарь
        self.weapons = []  # list of Weapon instances
        self.passives = {}  # {"faith": 2, "speed": 1, ...}
        # Реликвии
        self.relics = []  # list of relic_ids collected
        self.relic_bonuses = {
            "damage": 0.0,
            "projectile": 0,
            "regen": 0.0,
            "max_hp": 0,
            "gold": 0.0,
            "speed": 0.0,
            "area": 0.0,
            "cooldown": 0.0,
        }

        # Прогрессия
        self.level = 1
        self.xp = 0
        self.xp_to_next = 5
        self.gold = 0
        self.kills = 0

        # Аркана-модификаторы (устанавливаются из main при старте)
        self.arcana_damage_bonus = 1.0
        self.arcana_no_heal = False
        self.arcana_gold_mult = 1.0

        # Состояние
        self.invuln_timer = 0.0
        self.alive = True

        # Анимация
        self.anim_timer = 0.0
        from sprites import SpriteAnimator, PLAYER_TO_TEMPLATE
        self.animator = SpriteAnimator(PLAYER_TO_TEMPLATE.get(char_id, "knight"), scale=2)

    def get_passive_level(self, passive_id: str) -> int:
        return self.passives.get(passive_id, 0)

    @property
    def damage_mult(self) -> float:
        base = calc_damage_mult(self.get_passive_level("faith"))
        if self.char_bonus == "damage_per_10_levels":
            base += 0.1 * (self.level // 10)
        # Реликвия: Священный Грааль +20%
        base += self.relic_bonuses.get("damage", 0.0)
        # Аркана: Обет молчания +100%
        base *= self.arcana_damage_bonus
        return base

    @property
    def cooldown_mult(self) -> float:
        base = calc_cooldown_mult(self.get_passive_level("cooldown"))
        # Реликвия: Благословенное Кольцо -20%
        base *= max(0.1, 1.0 - self.relic_bonuses.get("cooldown", 0.0))
        return base

    @property
    def area_mult(self) -> float:
        base = calc_area_mult(self.get_passive_level("area"))
        # Реликвия: Рог Демона +25%
        base += self.relic_bonuses.get("area", 0.0)
        return base

    @property
    def speed_mult(self) -> float:
        base = calc_speed_mult(self.get_passive_level("speed"))
        # Реликвия: Перо Ангела +15%
        base += self.relic_bonuses.get("speed", 0.0)
        return base

    @property
    def crit_chance(self) -> float:
        """Шанс крита (0.0 - 1.0)."""
        luck_lvl = self.get_passive_level("luck")
        return 0.05 * luck_lvl  # 5% за уровень, макс 25%

    @property
    def projectiles_bonus(self) -> int:
        base = self.get_passive_level("projectile")
        if self.char_bonus == "projectile_bonus":
            base += 1
        # Реликвия: Фрагмент Креста +1
        base += self.relic_bonuses.get("projectile", 0)
        return base

    @property
    def pickup_range(self) -> float:
        base = calc_pickup_range(
            PICKUP_RANGE_BASE,
            self.char_bonus == "pickup_range"
        )
        # Пассивка Притяжение: +20% за уровень
        magnet_lvl = self.get_passive_level("magnet")
        if magnet_lvl > 0:
            base *= 1.0 + 0.2 * magnet_lvl
        return base

    @property
    def regen(self) -> float:
        base = calc_regen(self.get_passive_level("regen"))
        if self.char_bonus == "base_regen":
            base += 1.0  # +1 HP/сек
        # Реликвия: Чётки +0.5
        base += self.relic_bonuses.get("regen", 0.0)
        return base

    @property
    def gold_mult(self) -> float:
        """Множитель золота. 1.0 = 100%."""
        base = 1.0
        # Реликвия: Золотая Чаша +30%
        base += self.relic_bonuses.get("gold", 0.0)
        return base * self.arcana_gold_mult

    def update_stats(self):
        """Пересчитать max_hp после изменения пассивек и реликвий."""
        self.max_hp = calc_max_hp(
            self.base_hp,
            self.get_passive_level("max_hp"),
            0
        )
        # Реликвия: Священный Щит +50 макс HP
        self.max_hp += self.relic_bonuses.get("max_hp", 0)
        self.speed = self.base_speed * self.speed_mult

    def handle_input(self, dt: float):
        """Движение по WASD / стрелкам / тач."""
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # Тач-управление (виртуальный джойстик)
        if not hasattr(Player, '_touch_active'):
            Player._touch_active = False
            Player._touch_start = None
            Player._touch_dx = 0.0
            Player._touch_dy = 0.0

        for event in pygame.event.get([pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION]):
            if event.type == pygame.FINGERDOWN:
                Player._touch_active = True
                Player._touch_start = pygame.Vector2(event.x, event.y)
            elif event.type == pygame.FINGERUP:
                Player._touch_active = False
                Player._touch_dx = 0.0
                Player._touch_dy = 0.0
            elif event.type == pygame.FINGERMOTION and Player._touch_active:
                current = pygame.Vector2(event.x, event.y)
                delta = current - Player._touch_start
                if delta.length() > 0.02:  # мёртвая зона
                    Player._touch_dx = delta.x * 5
                    Player._touch_dy = delta.y * 5

        if Player._touch_active:
            dx += Player._touch_dx
            dy += Player._touch_dy

        if dx != 0 or dy != 0:
            move = pygame.Vector2(dx, dy)
            if move.length() > 0:
                move = move.normalize()
            self.pos += move * self.speed * 60 * dt
            self.facing = move

            # Walk animation — определяем направление
            if abs(dx) > abs(dy):
                self.animator.set_state("walk_right" if dx > 0 else "walk_left")
            else:
                self.animator.set_state("walk_down" if dy > 0 else "walk_up")
        else:
            self.animator.set_state("idle")

        # Аниматор
        self.animator.update(dt)

        # Ограничение карты из config
        from config import MAP_WIDTH, MAP_HEIGHT
        self.pos.x = max(0, min(MAP_WIDTH, self.pos.x))
        self.pos.y = max(0, min(MAP_HEIGHT, self.pos.y))

        # Регенерация (блокируется арканой Обет молчания)
        if self.regen > 0 and not self.arcana_no_heal:
            self.hp = min(self.max_hp, self.hp + self.regen * dt)

        # Неуязвимость
        if self.invuln_timer > 0:
            self.invuln_timer -= dt

    def take_damage(self, amount: float):
        if self.invuln_timer > 0 or not self.alive:
            return
        # Пассивка Броня веры: -10% урон за уровень
        armor_lvl = self.get_passive_level("armor")
        if armor_lvl > 0:
            amount *= 1.0 - 0.1 * armor_lvl
            amount = max(0.1, amount)  # минимум 0.1 урона
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def heal(self, amount: float):
        if not self.arcana_no_heal:
            self.hp = min(self.max_hp, self.hp + amount)

    def apply_relic(self, relic_id: str, bonuses: dict):
        """Применить бонусы реликвии к игроку."""
        if relic_id in self.relics:
            return  # уже есть
        self.relics.append(relic_id)

        # Применяем каждый бонус
        if "max_hp" in bonuses:
            old_max = self.max_hp
            self.relic_bonuses["max_hp"] += bonuses["max_hp"]
            self.update_stats()
            # Хилим на то же количество, что и прибавка к макс HP
            hp_gain = self.max_hp - old_max
            self.hp = min(self.max_hp, self.hp + hp_gain)
        if "damage" in bonuses:
            self.relic_bonuses["damage"] += bonuses["damage"]
        if "projectile" in bonuses:
            self.relic_bonuses["projectile"] += bonuses["projectile"]
        if "regen" in bonuses:
            self.relic_bonuses["regen"] += bonuses["regen"]
        if "gold" in bonuses:
            self.relic_bonuses["gold"] += bonuses["gold"]
        if "speed" in bonuses:
            self.relic_bonuses["speed"] += bonuses["speed"]
            self.update_stats()
        if "area" in bonuses:
            self.relic_bonuses["area"] += bonuses["area"]
        if "cooldown" in bonuses:
            self.relic_bonuses["cooldown"] += bonuses["cooldown"]

    def add_xp(self, amount: int):
        self.xp += amount

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)

        # Мигание при неуязвимости
        if self.invuln_timer > 0 and int(self.invuln_timer * 10) % 2 == 0:
            return

        # Спрайт — animator
        sprite = self.animator.get_surface()
        sprite_rect = sprite.get_rect(center=(sx, sy))
        surface.blit(sprite, sprite_rect)
