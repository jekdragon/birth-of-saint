"""
Рождение святого - Enemies
Типы врагов, спавн, AI, урон.
"""
import math
import pygame
from config import RED, DARK_RED, YELLOW, PURPLE, ICE_BLUE, GOLD, MAP_WIDTH, MAP_HEIGHT

ENEMY_TYPES = {
    "neophyte": {
        "name": "Неофит",
        "unlock_wave": 1,
        "hp_base": 11, "hp_per_wave": 3,
        "speed_base": 1.5, "speed_per_wave": 0.10,
        "damage": 0.8, "xp": 4, "score": 10,
        "radius": 17, "color": RED, "blood_color": DARK_RED,
    },
    "acolyte": {
        "name": "Акролит",
        "unlock_wave": 3,
        "hp_base": 7, "hp_per_wave": 2,
        "speed_base": 2.9, "speed_per_wave": 0.08,
        "damage": 0.5, "xp": 3, "score": 12,
        "radius": 12, "color": (255, 130, 130), "blood_color": DARK_RED,
    },
    "heretic": {
        "name": "Еретик",
        "unlock_wave": 4,
        "hp_base": 38, "hp_per_wave": 7,
        "speed_base": 1.05, "speed_per_wave": 0.04,
        "damage": 1.3, "xp": 9, "score": 28,
        "radius": 26, "color": (140, 55, 55), "blood_color": (110, 35, 35),
    },
    "demon": {
        "name": "Демон",
        "unlock_wave": 5,
        "hp_base": 14, "hp_per_wave": 2.5,
        "speed_base": 1.7, "speed_per_wave": 0.05,
        "damage": 0.6, "xp": 6, "score": 15,
        "radius": 14, "color": (120, 80, 160), "blood_color": (120, 80, 160),
        "shoot_range": 300, "shoot_cd": 1.5,
    },
    "fanatic": {
        "name": "Фанатик",
        "unlock_wave": 5,
        "hp_base": 8, "hp_per_wave": 1.5,
        "speed_base": 2.4, "speed_per_wave": 0.07,
        "damage": 0, "xp": 7, "score": 18,
        "radius": 16, "color": YELLOW, "blood_color": (255, 120, 60),
        "explode_radius": 60, "explode_damage": 3.0,
    },
    "antichrist": {
        "name": "Антихрист",
        "unlock_wave": 3,
        "hp_base": 180, "hp_per_wave": 70,
        "speed_base": 1.3, "speed_per_wave": 0,
        "damage": 1.5, "xp": 25, "score": 250,
        "radius": 38, "color": PURPLE, "blood_color": (220, 80, 220),
        "is_boss": True,
    },
    # === Новые враги (Собор) ===
    "ghost": {
        "name": "Призрак",
        "unlock_wave": 6,
        "hp_base": 10, "hp_per_wave": 2,
        "speed_base": 2.0, "speed_per_wave": 0.06,
        "damage": 0.7, "xp": 8, "score": 20,
        "radius": 14, "color": ICE_BLUE, "blood_color": (150, 200, 255),
        "phasing": True,  # проходит сквозь препятствия
        "is_undead": True,
    },
    "gargoyle": {
        "name": "Горгулья",
        "unlock_wave": 7,
        "hp_base": 55, "hp_per_wave": 10,
        "speed_base": 0.9, "speed_per_wave": 0.03,
        "damage": 2.0, "xp": 15, "score": 40,
        "radius": 22, "color": (100, 100, 120), "blood_color": (80, 80, 100),
    },
    "shade": {
        "name": "Тень",
        "unlock_wave": 8,
        "hp_base": 6, "hp_per_wave": 1,
        "speed_base": 3.5, "speed_per_wave": 0.1,
        "damage": 0.4, "xp": 5, "score": 14,
        "radius": 10, "color": (60, 60, 80), "blood_color": (40, 40, 60),
        "is_undead": True,
    },
    "cultist": {
        "name": "Культист",
        "unlock_wave": 4,
        "hp_base": 20, "hp_per_wave": 4,
        "speed_base": 1.3, "speed_per_wave": 0.05,
        "damage": 1.0, "xp": 7, "score": 22,
        "radius": 18, "color": (100, 50, 100), "blood_color": (80, 30, 80),
        "shoot_range": 250, "shoot_cd": 2.0,
    },
    "pope": {
        "name": "Лжепапа",
        "unlock_wave": 9,
        "hp_base": 400, "hp_per_wave": 120,
        "speed_base": 0.8, "speed_per_wave": 0,
        "damage": 2.5, "xp": 50, "score": 500,
        "radius": 42, "color": GOLD, "blood_color": (200, 180, 50),
        "is_boss": True,
    },
}


class Enemy:
    def __init__(self, type_id: str, x: float, y: float, wave: int):
        t = ENEMY_TYPES[type_id]
        self.type_id = type_id
        self.pos = pygame.Vector2(x, y)
        self.hp = t["hp_base"] + t["hp_per_wave"] * wave
        self.max_hp = self.hp
        self.speed = t["speed_base"] + t["speed_per_wave"] * wave
        self.damage = t["damage"]
        self.xp = t["xp"]
        self.score = t["score"]
        self.radius = t["radius"]
        self.color = t["color"]
        self.blood_color = t["blood_color"]
        self.is_boss = t.get("is_boss", False)
        self.is_undead = t.get("is_undead", False)

        # Animator
        from sprites import SpriteAnimator, ENEMY_TO_TEMPLATE
        self.animator = SpriteAnimator(ENEMY_TO_TEMPLATE.get(type_id, "skeleton"), scale=2)

        # Demon ranged attack
        self.shoot_range = t.get("shoot_range", 0)
        self.shoot_cd = t.get("shoot_cd", 0)
        self.shoot_timer = 0.0

        # Fanatic explode
        self.explode_radius = t.get("explode_radius", 0)
        self.explode_damage = t.get("explode_damage", 0)

        self.alive = True
        self.hit_flash = 0.0
        self.stun_timer = 0.0
        self.death_fade = 0.0  # > 0 = fading out
        self.freeze_frames = 0  # Hitstop: directional freeze on attacker+target
        self.knockback_x = 0.0  # Knockback velocity
        self.knockback_y = 0.0
        # C3: Rune status effects
        self.burn_timer = 0.0    # remaining burn duration (seconds)
        self.burn_dps = 0.0      # burn damage per second
        self.slow_timer = 0.0    # remaining slow duration
        self.slow_factor = 1.0   # speed multiplier (1.0 = no slow)
        self.frozen_timer = 0.0  # remaining freeze duration

    def take_damage(self, amount: float, knockback_dir=None) -> bool:
        """Возвращает True если враг умер. knockback_dir = (dx, dy) normalized."""
        self.hp -= amount
        self.hit_flash = 0.1
        # Knockback (образец: kbx/kby)
        if knockback_dir:
            kb_strength = min(8.0, 3.0 + amount * 0.1)
            self.knockback_x = knockback_dir[0] * kb_strength
            self.knockback_y = knockback_dir[1] * kb_strength
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def apply_slow(self, factor: float, duration: float) -> None:
        """Замедление: factor=0.5 = половина скорости. Стакается по минимуму."""
        self.slow_timer = max(self.slow_timer, duration)
        self.slow_factor = min(self.slow_factor, factor)

    def apply_freeze(self, duration: float) -> None:
        """Заморозка: полная остановка движения."""
        self.frozen_timer = max(self.frozen_timer, duration)

    def update(self, player_pos: pygame.Vector2, dt: float):
        if not self.alive:
            return None

        # Hitstop freeze — skip movement/animation, keep drawing
        if self.freeze_frames > 0:
            self.freeze_frames -= 1
            if self.hit_flash > 0:
                self.hit_flash -= dt
            return None

        # Стан - пропускаем движение
        if self.stun_timer > 0:
            self.stun_timer -= dt
            return None

        # Status effects: tick down timers
        if self.frozen_timer > 0:
            self.frozen_timer -= dt
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0
        # C3: Burn DOT — deal damage per second
        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.hp -= self.burn_dps * dt
            if self.hp <= 0:
                self.alive = False
                return None
            if self.burn_timer <= 0:
                self.burn_dps = 0.0

        # Frozen: skip all movement & attacks
        if self.frozen_timer > 0:
            if self.hit_flash > 0:
                self.hit_flash -= dt
            return None

        # Рендж-атака (demon, cultist)
        if self.shoot_range > 0:
            dist = (player_pos - self.pos).length()
            if dist <= self.shoot_range:
                self.shoot_timer += dt
                if self.shoot_timer >= self.shoot_cd:
                    self.shoot_timer = 0.0
                    d = player_pos - self.pos
                    if d.length() > 0:
                        d = d.normalize()
                    else:
                        d = pygame.Vector2(1, 0)
                    speed = 4.0
                    shot = {
                        "x": self.pos.x, "y": self.pos.y,
                        "vx": d.x * speed, "vy": d.y * speed,
                        "damage": self.damage * 0.5,
                        "color": self.color,
                    }
                    if self.hit_flash > 0:
                        self.hit_flash -= dt
                    return shot
                # В пределах дистанции - стоим и ждём кулдаун
                if self.hit_flash > 0:
                    self.hit_flash -= dt
                return None

        # Движение к игроку
        d = player_pos - self.pos
        if d.length() > 0:
            d = d.normalize()
            effective_speed = self.speed * self.slow_factor
            self.pos += d * effective_speed * 60 * dt

            # Walk animation
            if abs(d.x) > abs(d.y):
                self.animator.set_state("walk_right" if d.x > 0 else "walk_left")
            else:
                self.animator.set_state("walk_down" if d.y > 0 else "walk_up")
        else:
            self.animator.set_state("idle")
        
        # Knockback (образец: decayed per frame)
        if self.knockback_x != 0 or self.knockback_y != 0:
            self.pos.x += self.knockback_x
            self.pos.y += self.knockback_y
            self.knockback_x *= 0.85  # decay
            self.knockback_y *= 0.85
            if abs(self.knockback_x) < 0.1 and abs(self.knockback_y) < 0.1:
                self.knockback_x = 0
                self.knockback_y = 0

        # Clamp to map bounds
        self.pos.x = max(0, min(self.pos.x, MAP_WIDTH))
        self.pos.y = max(0, min(self.pos.y, MAP_HEIGHT))

        self.animator.update(dt)

        # Hit flash
        if self.hit_flash > 0:
            self.hit_flash -= dt
        return None

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, font=None):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)

        if sx < -50 or sx > 1074 or sy < -50 or sy > 818:
            return

        # Death state — animator
        if self.death_fade > 0:
            self.animator.set_state("death")

        # Спрайт — animator
        sprite = self.animator.get_surface()

        # Death fade alpha
        if self.death_fade > 0:
            alpha = int(255 * (self.death_fade / 0.4))
            sprite = sprite.copy()
            sprite.set_alpha(alpha)
            fade_progress = 1.0 - (self.death_fade / 0.4)
            shrink = max(1, int(32 * (1 - fade_progress * 0.3)))
            sprite = pygame.transform.scale(sprite, (shrink, shrink))

        if self.hit_flash > 0:
            # Белая вспышка при ударе
            sprite = sprite.copy()
            sprite.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
        elif self.freeze_frames > 0:
            # Голубой оттенок во время hitstop
            sprite = sprite.copy()
            sprite.fill((80, 140, 255), special_flags=pygame.BLEND_ADD)
        elif self.frozen_timer > 0:
            # Ярко-голубой при заморозке
            sprite = sprite.copy()
            sprite.fill((60, 120, 255), special_flags=pygame.BLEND_ADD)
        elif self.slow_timer > 0:
            # Тускло-голубой при замедлении
            sprite = sprite.copy()
            sprite.fill((40, 80, 160), special_flags=pygame.BLEND_ADD)
        elif self.burn_timer > 0:
            # Оранжевый оттенок при горении
            sprite = sprite.copy()
            sprite.fill((80, 30, 0), special_flags=pygame.BLEND_ADD)
        sprite_rect = sprite.get_rect(center=(sx, sy))
        surface.blit(sprite, sprite_rect)

        # Stun visual — вращающиеся звёздочки над головой
        if self.stun_timer > 0:
            import math
            t = pygame.time.get_ticks() / 1000.0
            for i in range(3):
                angle = t * 3.0 + i * 2.094  # 2π/3
                star_x = sx + int(math.cos(angle) * 12)
                star_y = sy - self.radius - 10 + int(math.sin(angle) * 4)
                pygame.draw.circle(surface, (255, 255, 100), (star_x, star_y), 2)

        # HP-бар (для боссов и если урон получен)
        if self.is_boss or self.hp < self.max_hp:
            bar_w = self.radius * 2
            bar_h = 4
            bar_x = sx - bar_w // 2
            bar_y = sy - self.radius - 8
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(surface, (60, 20, 20), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(surface, RED, (bar_x, bar_y, int(bar_w * ratio), bar_h))

        # Имя босса
        if self.is_boss and font:
            name_text = font.render(ENEMY_TYPES[self.type_id]["name"], True, PURPLE)
            surface.blit(name_text, (sx - name_text.get_width() // 2, sy - self.radius - 20))
