"""
Рождение святого — Weapons
6 типов оружия: whip, fire, halo, rosary, lightning, prayer.
"""
import math
import pygame
from config import calc_damage_mult, calc_cooldown_mult, calc_area_mult
from projectiles import Projectile, Pulse

WEAPON_DEFS = {
    "whip": {
        "name": "Святой кнут",
        "type": "melee",
        "damage_base": 12, "damage_per_lvl": 5,
        "cooldown_base": 1.3, "cd_reduction": 0.09, "cd_min": 0.55,
        "length_base": 115, "length_per_lvl": 18,
        "width": 20,
        "color": (220, 110, 110),
        "evolve_passive": "regen", "evolve_name": "Кровавый свет",
    },
    "fire": {
        "name": "Священный огонь",
        "type": "projectile",
        "damage_base": 10, "damage_per_lvl": 4,
        "cooldown_base": 1.0, "cd_reduction": 0.08, "cd_min": 0.32,
        "proj_speed": 9, "proj_radius": 7, "proj_lifetime": 2.0,
        "proj_per_2lvl": 1,
        "color": (255, 150, 200),
        "evolve_passive": "cooldown", "evolve_name": "Вечное пламя",
    },
    "halo": {
        "name": "Орбитальная аура",
        "type": "aura",
        "damage_base": 4, "damage_per_lvl": 2,
        "orbit_base": 2, "orbit_per_2lvl": 1,
        "radius_base": 74, "radius_per_lvl": 10,
        "rotation": 2.6, "hit_cd": 0.22,
        "color": (255, 200, 100),
        "evolve_passive": "cooldown", "evolve_name": "Вечный ореол",
    },
    "rosary": {
        "name": "Чётки",
        "type": "boomerang",
        "damage_base": 22, "damage_per_lvl": 8,
        "speed_base": 5.0, "speed_per_lvl": 0.5,
        "range_base": 250, "range_per_lvl": 30,
        "cooldown_base": 90, "cd_reduction": 8, "cd_min": 45,  # в тиках
        "color": (100, 220, 100),
        "evolve_passive": "speed", "evolve_name": "Кара небес",
    },
    "lightning": {
        "name": "Божественная молния",
        "type": "strike",
        "damage_base": 25, "damage_per_lvl": 8,
        "cooldown_base": 1.5, "cd_reduction": 0.15, "cd_min": 0.5,
        "aoe_base": 50, "aoe_per_lvl": 10,
        "color": (255, 255, 150),
    },
    "prayer": {
        "name": "Молитвенная волна",
        "type": "ring",
        "damage_base": 15, "damage_per_lvl": 6,
        "cooldown_base": 2.0, "cd_reduction": 0.2, "cd_min": 0.8,
        "radius_base": 150, "radius_per_lvl": 20,
        "color": (180, 180, 255),
    },
    # Новое оружие
    "incense": {
        "name": "Кадило",
        "type": "orbit",
        "damage_base": 8, "damage_per_lvl": 3,
        "cooldown_base": 0.0, "cd_reduction": 0, "cd_min": 0,
        "count_base": 1, "count_per_lvl": 0.5,
        "radius_base": 100, "radius_per_lvl": 15,
        "color": (200, 180, 140),
        "evolve_passive": "magnet", "evolve_name": "Кадило фимиама",
    },
    "cross": {
        "name": "Крест",
        "type": "directional",
        "damage_base": 20, "damage_per_lvl": 8,
        "cooldown_base": 1.8, "cd_reduction": 0.15, "cd_min": 0.6,
        "projectile_speed": 5.0, "projectile_size": 16,
        "color": (255, 220, 100),
        "evolve_passive": "armor", "evolve_name": "Крест искупления",
    },
    "bell": {
        "name": "Колокол",
        "type": "ring",
        "damage_base": 25, "damage_per_lvl": 10,
        "cooldown_base": 3.0, "cd_reduction": 0.25, "cd_min": 1.0,
        "radius_base": 200, "radius_per_lvl": 25,
        "color": (220, 200, 160),
        "evolve_passive": "luck", "evolve_name": "Колокол судного дня",
    },
}

PASSIVE_DEFS = {
    "faith": {"name": "Святая вера", "desc": "+10% урон", "max_level": 5, "color": (255, 200, 100)},
    "speed": {"name": "Благодать", "desc": "+10% скорость", "max_level": 5, "color": (100, 200, 255)},
    "cooldown": {"name": "Усердие", "desc": "-8% кулдаун", "max_level": 5, "color": (110, 220, 255)},
    "area": {"name": "Покровительство", "desc": "+10% зона", "max_level": 5, "color": (100, 255, 150)},
    "regen": {"name": "Молитва", "desc": "+0.3 HP/sec", "max_level": 5, "color": (255, 150, 150)},
    "max_hp": {"name": "Благословение", "desc": "+10 max HP", "max_level": 5, "color": (200, 100, 255)},
    "projectile": {"name": "Ревность", "desc": "+1 снаряд", "max_level": 3, "color": (255, 255, 100)},
    # Новые пассивки
    "magnet": {"name": "Притяжение", "desc": "+20% pickup range", "max_level": 5, "color": (255, 180, 220)},
    "armor": {"name": "Броня веры", "desc": "-10% получаемый урон", "max_level": 5, "color": (180, 180, 200)},
    "luck": {"name": "Провидение", "desc": "+15% шанс крита", "max_level": 5, "color": (255, 255, 180)},
}

EVOLUTIONS = {
    "whip": {"required_passive": "regen", "required_passive_lvl": 3, "name": "Кровавый свет"},
    "fire": {"required_passive": "cooldown", "required_passive_lvl": 3, "name": "Вечное пламя"},
    "halo": {"required_passive": "cooldown", "required_passive_lvl": 3, "name": "Вечный ореол"},
    "rosary": {"required_passive": "speed", "required_passive_lvl": 3, "name": "Кара небес"},
    "incense": {"required_passive": "magnet", "required_passive_lvl": 3, "name": "Кадило фимиама"},
    "cross": {"required_passive": "armor", "required_passive_lvl": 3, "name": "Крест искупления"},
    "bell": {"required_passive": "luck", "required_passive_lvl": 3, "name": "Колокол судного дня"},
}


class Weapon:
    """Базовый класс оружия."""
    def __init__(self, weapon_id: str):
        self.weapon_id = weapon_id
        self.defn = WEAPON_DEFS[weapon_id]
        self.level = 1
        self.timer = 0.0
        self.evolved = False

    def calc_damage(self, player) -> tuple:
        """Возвращает (damage, is_crit)."""
        import random
        d = self.defn
        damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult
        is_crit = random.random() < player.crit_chance
        if is_crit:
            damage *= 2.0
        return damage, is_crit

    @property
    def name(self) -> str:
        return self.defn["evolve_name"] if self.evolved else self.defn["name"]

    def upgrade(self):
        if self.level < 8:
            self.level += 1

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        """Переопределяется в подклассах."""
        pass

    def can_evolve(self, player) -> bool:
        evo = EVOLUTIONS.get(self.weapon_id)
        if not evo or self.evolved:
            return False
        if self.level < 8:
            return False
        return player.get_passive_level(evo["required_passive"]) >= evo["required_passive_lvl"]

    def evolve(self):
        self.evolved = True


class WhipWeapon(Weapon):
    def __init__(self):
        super().__init__("whip")
        self.hit_set = set()

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        self.timer += dt
        d = self.defn
        cd = max(d["cd_min"], d["cooldown_base"] - self.level * d["cd_reduction"]) * player.cooldown_mult

        if self.timer >= cd:
            self.timer = 0
            length = (d["length_base"] + self.level * d["length_per_lvl"]) * player.area_mult
            damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult
            if self.evolved:
                damage *= 1.5
                length *= 1.4

            f = player.facing if player.facing.length() > 0 else pygame.Vector2(1, 0)
            side = pygame.Vector2(1, 0) if f.x >= 0 else pygame.Vector2(-1, 0)

            self.hit_set.clear()
            for e in enemies:
                if not e.alive:
                    continue
                to_enemy = e.pos - player.pos
                dist = to_enemy.length()
                if dist > length + e.radius:
                    continue
                # Проверка что враг в секторе кнута (±90 градусов от направления)
                if dist > 0:
                    angle = math.atan2(to_enemy.y, to_enemy.x)
                    facing_angle = math.atan2(side.y, side.x)
                    diff = abs(angle - facing_angle)
                    if diff > math.pi:
                        diff = 2 * math.pi - diff
                    if diff < math.pi / 2:
                        killed = e.take_damage(damage)
                        damage_numbers.append(DamageNumber(e.pos.x, e.pos.y, damage, d["color"]))
                        for _ in range(4):
                            particles.append(Particle(e.pos.x, e.pos.y, d["color"]))
                        if killed and self.evolved:
                            player.heal(2)


class FireWeapon(Weapon):
    def __init__(self):
        super().__init__("fire")

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        self.timer += dt
        d = self.defn
        cd = max(d["cd_min"], d["cooldown_base"] - self.level * d["cd_reduction"]) * player.cooldown_mult

        if self.timer >= cd:
            self.timer = 0
            n = 1 + (self.level - 1) // 2 + player.projectiles_bonus
            damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult

            alive = [e for e in enemies if e.alive]
            if not alive:
                return

            targets = sorted(alive, key=lambda e: (e.pos - player.pos).length_squared())[:n]
            for t in targets:
                direction = t.pos - player.pos
                if direction.length() > 0:
                    direction = direction.normalize()
                vel = direction * d["proj_speed"]
                homing = self.evolved
                explosive = self.evolved
                projectiles.append(Projectile(
                    player.pos.x, player.pos.y, vel.x, vel.y,
                    damage=damage,
                    radius=d["proj_radius"],
                    lifetime=d["proj_lifetime"],
                    color=d["color"],
                    homing=homing,
                    target=t if homing else None,
                    explosive=explosive,
                    explode_dmg=damage * 0.5 if explosive else 0,
                    explode_r=65 * player.area_mult if explosive else 0,
                ))


class HaloWeapon(Weapon):
    def __init__(self):
        super().__init__("halo")
        self.angle = 0.0
        self.hit_cds = {}  # enemy_id -> timer

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        d = self.defn
        n = d["orbit_base"] + (self.level - 1) // 2 + player.projectiles_bonus
        radius = (d["radius_base"] + self.level * d["radius_per_lvl"]) * player.area_mult
        damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult
        rot = d["rotation"]
        hit_cd = d["hit_cd"]

        if self.evolved:
            n += 2
            damage *= 1.5
            rot *= 1.5

        self.angle += dt * rot
        self.timer += dt

        # Обновить кулдауны
        for eid in list(self.hit_cds.keys()):
            self.hit_cds[eid] -= dt
            if self.hit_cds[eid] <= 0:
                del self.hit_cds[eid]

        can_hit = self.timer >= hit_cd
        if can_hit:
            self.timer = 0

        for i in range(n):
            ang = self.angle + (6.2832 / n) * i
            orb_pos = player.pos + pygame.Vector2(math.cos(ang), math.sin(ang)) * radius

            if can_hit:
                for e in enemies:
                    if not e.alive:
                        continue
                    eid = id(e)
                    if eid in self.hit_cds:
                        continue
                    dx = e.pos.x - orb_pos.x
                    dy = e.pos.y - orb_pos.y
                    R = e.radius + 14
                    if dx * dx + dy * dy < R * R:
                        e.take_damage(damage)
                        self.hit_cds[eid] = hit_cd
                        damage_numbers.append(DamageNumber(e.pos.x, e.pos.y, damage, d["color"]))
                        if self.evolved and e.alive:
                            # Burn
                            pass


class RosaryWeapon(Weapon):
    def __init__(self):
        super().__init__("rosary")
        self.boomerangs = []

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        d = self.defn
        speed = d["speed_base"] + self.level * d["speed_per_lvl"]
        max_range = d["range_base"] + self.level * d["range_per_lvl"]
        damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult

        # Обновить бумеранги
        for b in self.boomerangs:
            b["pos"] += b["vel"] * 60 * dt
            if b["returning"]:
                to_player = player.pos - b["pos"]
                if to_player.length() > 0:
                    b["vel"] = to_player.normalize() * speed
                if to_player.length() < 15:
                    b["alive"] = False
            else:
                b["traveled"] += speed * 60 * dt
                if b["traveled"] >= max_range:
                    b["returning"] = True
                    b["hit_set"].clear()

            # Коллизия
            if b["alive"]:
                for e in enemies:
                    if not e.alive or id(e) in b["hit_set"]:
                        continue
                    dx = e.pos.x - b["pos"].x
                    dy = e.pos.y - b["pos"].y
                    if dx * dx + dy * dy < (16 + e.radius) ** 2:
                        e.take_damage(damage)
                        b["hit_set"].add(id(e))
                        dmg_mult = 2.0 if (self.evolved and b["returning"]) else 1.0
                        damage_numbers.append(DamageNumber(e.pos.x, e.pos.y, damage * dmg_mult, d["color"]))

        self.boomerangs = [b for b in self.boomerangs if b["alive"]]

        # Спавн нового бумеранга
        self.timer += dt
        cd_ticks = max(d["cd_min"], d["cooldown_base"] - self.level * d["cd_reduction"]) / 60.0
        if self.timer >= cd_ticks:
            self.timer = 0
            alive = [e for e in enemies if e.alive]
            if alive:
                closest = min(alive, key=lambda e: (e.pos - player.pos).length_squared())
                direction = closest.pos - player.pos
                if direction.length() > 0:
                    direction = direction.normalize()
                self.boomerangs.append({
                    "pos": player.pos.copy(),
                    "vel": direction * speed,
                    "traveled": 0,
                    "returning": False,
                    "hit_set": set(),
                    "alive": True,
                })


class LightningWeapon(Weapon):
    def __init__(self):
        super().__init__("lightning")

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        self.timer += dt
        d = self.defn
        cd = max(d["cd_min"], d["cooldown_base"] - self.level * d["cd_reduction"]) * player.cooldown_mult
        aoe = (d["aoe_base"] + self.level * d["aoe_per_lvl"]) * player.area_mult
        damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult

        if self.timer >= cd:
            self.timer = 0
            alive = [e for e in enemies if e.alive]
            if not alive:
                return
            # Бьём по случайному врагу в радиусе
            import random
            target = random.choice(alive)
            # AoE вокруг цели
            for e in enemies:
                if not e.alive:
                    continue
                dx = e.pos.x - target.pos.x
                dy = e.pos.y - target.pos.y
                if dx * dx + dy * dy < (aoe + e.radius) ** 2:
                    e.take_damage(damage)
                    damage_numbers.append(DamageNumber(e.pos.x, e.pos.y, damage, d["color"]))

            # Визуал: пульс
            pulses.append(Pulse(target.pos.x, target.pos.y, aoe, d["color"]))


class PrayerWeapon(Weapon):
    def __init__(self):
        super().__init__("prayer")

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        self.timer += dt
        d = self.defn
        cd = max(d["cd_min"], d["cooldown_base"] - self.level * d["cd_reduction"]) * player.cooldown_mult
        radius = (d["radius_base"] + self.level * d["radius_per_lvl"]) * player.area_mult
        damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult

        if self.timer >= cd:
            self.timer = 0
            for e in enemies:
                if not e.alive:
                    continue
                dx = e.pos.x - player.pos.x
                dy = e.pos.y - player.pos.y
                if dx * dx + dy * dy < (radius + e.radius) ** 2:
                    e.take_damage(damage)
                    damage_numbers.append(DamageNumber(e.pos.x, e.pos.y, damage, d["color"]))

            pulses.append(Pulse(player.pos.x, player.pos.y, radius, d["color"], duration=0.3))


class IncenseWeapon(Weapon):
    """Кадило — орбитальное оружие вокруг игрока."""
    def __init__(self):
        super().__init__("incense")
        self.angle = 0.0

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        d = self.defn
        count = int(d["count_base"] + self.level * d["count_per_lvl"])
        radius = (d["radius_base"] + self.level * d["radius_per_lvl"]) * player.area_mult
        damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult

        if self.evolved:
            radius *= 2.0
            damage *= 1.5

        self.angle += dt * 2.0  # скорость вращения

        for i in range(count):
            a = self.angle + (2 * 3.14159 / count) * i
            ox = player.pos.x + math.cos(a) * radius
            oy = player.pos.y + math.sin(a) * radius
            for e in enemies:
                if not e.alive:
                    continue
                dx = e.pos.x - ox
                dy = e.pos.y - oy
                if dx * dx + dy * dy < (15 + e.radius) ** 2:
                    e.take_damage(damage * dt * 5)  # DPS
                    if int(self.angle * 10) % 5 == 0:
                        damage_numbers.append(DamageNumber(e.pos.x, e.pos.y, damage, d["color"]))


class CrossWeapon(Weapon):
    """Крест — стреляет крестами в направлении движения."""
    def __init__(self):
        super().__init__("cross")

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        self.timer += dt
        d = self.defn
        cd = max(d["cd_min"], d["cooldown_base"] - self.level * d["cd_reduction"]) * player.cooldown_mult
        damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult

        if self.evolved:
            damage *= 2.0

        if self.timer >= cd:
            self.timer = 0
            pierce = 3 if self.evolved else (1 + player.projectiles_bonus)
            projectiles.append(Projectile(
                player.pos.x, player.pos.y,
                player.facing.x * d["projectile_speed"],
                player.facing.y * d["projectile_speed"],
                damage, d["projectile_size"],
                color=d["color"],
                pierce=pierce
            ))


class BellWeapon(Weapon):
    """Колокол — мощная AoE волна с длинным кулдауном."""
    def __init__(self):
        super().__init__("bell")

    def update(self, player, enemies, projectiles, pulses, particles, damage_numbers, dt):
        self.timer += dt
        d = self.defn
        cd = max(d["cd_min"], d["cooldown_base"] - self.level * d["cd_reduction"]) * player.cooldown_mult
        radius = (d["radius_base"] + self.level * d["radius_per_lvl"]) * player.area_mult
        damage = (d["damage_base"] + self.level * d["damage_per_lvl"]) * player.damage_mult

        if self.evolved:
            damage *= 1.8

        if self.timer >= cd:
            self.timer = 0
            for e in enemies:
                if not e.alive:
                    continue
                dx = e.pos.x - player.pos.x
                dy = e.pos.y - player.pos.y
                if dx * dx + dy * dy < (radius + e.radius) ** 2:
                    e.take_damage(damage)
                    if self.evolved:
                        e.stun_timer = 1.0
                    damage_numbers.append(DamageNumber(e.pos.x, e.pos.y, damage, d["color"]))

            pulses.append(Pulse(player.pos.x, player.pos.y, radius, d["color"], duration=0.5))


WEAPON_CLASSES = {
    "whip": WhipWeapon,
    "fire": FireWeapon,
    "halo": HaloWeapon,
    "rosary": RosaryWeapon,
    "lightning": LightningWeapon,
    "prayer": PrayerWeapon,
    "incense": IncenseWeapon,
    "cross": CrossWeapon,
    "bell": BellWeapon,
}


def create_weapon(weapon_id: str) -> Weapon:
    cls = WEAPON_CLASSES.get(weapon_id)
    if cls:
        return cls()
    return Weapon(weapon_id)


# Нужен для DamageNumber и Particle
from projectiles import DamageNumber, Particle
