"""
Рождение святого — Player
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

        # Прогрессия
        self.level = 1
        self.xp = 0
        self.xp_to_next = 5
        self.gold = 0
        self.kills = 0

        # Состояние
        self.invuln_timer = 0.0
        self.alive = True

        # Анимация
        self.anim_timer = 0.0

    def get_passive_level(self, passive_id: str) -> int:
        return self.passives.get(passive_id, 0)

    @property
    def damage_mult(self) -> float:
        base = calc_damage_mult(self.get_passive_level("faith"))
        if self.char_bonus == "damage_per_10_levels":
            base += 0.1 * (self.level // 10)
        return base

    @property
    def cooldown_mult(self) -> float:
        return calc_cooldown_mult(self.get_passive_level("cooldown"))

    @property
    def area_mult(self) -> float:
        return calc_area_mult(self.get_passive_level("area"))

    @property
    def speed_mult(self) -> float:
        return calc_speed_mult(self.get_passive_level("speed"))

    @property
    def projectiles_bonus(self) -> int:
        base = self.get_passive_level("projectile")
        if self.char_bonus == "projectile_bonus":
            base += 1
        return base

    @property
    def pickup_range(self) -> float:
        return calc_pickup_range(
            PICKUP_RANGE_BASE,
            self.char_bonus == "pickup_range"
        )

    @property
    def regen(self) -> float:
        base = calc_regen(self.get_passive_level("regen"))
        if self.char_bonus == "base_regen":
            base += 1.0  # +1 HP/сек
        return base

    def update_stats(self):
        """Пересчитать max_hp после изменения пассивек."""
        self.max_hp = calc_max_hp(
            self.base_hp,
            self.get_passive_level("max_hp"),
            0
        )
        self.speed = self.base_speed * self.speed_mult

    def handle_input(self, dt: float):
        """Движение по WASD / стрелкам."""
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

        if dx != 0 or dy != 0:
            move = pygame.Vector2(dx, dy)
            if move.length() > 0:
                move = move.normalize()
            self.pos += move * self.speed * 60 * dt
            self.facing = move

        # Ограничение карты из config
        from config import MAP_WIDTH, MAP_HEIGHT
        self.pos.x = max(0, min(MAP_WIDTH, self.pos.x))
        self.pos.y = max(0, min(MAP_HEIGHT, self.pos.y))

        # Регенерация
        if self.regen > 0:
            self.hp = min(self.max_hp, self.hp + self.regen * dt)

        # Неуязвимость
        if self.invuln_timer > 0:
            self.invuln_timer -= dt

    def take_damage(self, amount: float):
        if self.invuln_timer > 0 or not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def heal(self, amount: float):
        self.hp = min(self.max_hp, self.hp + amount)

    def add_xp(self, amount: int):
        self.xp += amount

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)

        # Мигание при неуязвимости
        if self.invuln_timer > 0 and int(self.invuln_timer * 10) % 2 == 0:
            return

        # Спрайт
        from sprites import get_player_sprite
        sprite = get_player_sprite(self.char_id, scale=2)
        sprite_rect = sprite.get_rect(center=(sx, sy))
        surface.blit(sprite, sprite_rect)
