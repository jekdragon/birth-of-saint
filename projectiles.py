"""
Рождение святого - Projectiles & Particles
Снаряды, частицы, визуальные эффекты атак.
"""
import math
import pygame
from config import WHITE

class Projectile:
    """Летящий снаряд."""
    def __init__(self, x, y, vx, vy, damage, radius=6, lifetime=2.0,
                 pierce=0, color=(185, 130, 255), homing=False,
                 target=None, explosive=False, explode_dmg=0, explode_r=0,
                 from_enemy=False):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vx, vy)
        self.damage = damage
        self.radius = radius
        self.lifetime = lifetime
        self.pierce = pierce
        self.color = color
        self.homing = homing
        self.target = target
        self.explosive = explosive
        self.explode_dmg = explode_dmg
        self.explode_r = explode_r
        self.hit_set = set()
        self.alive = True
        self.from_enemy = from_enemy
        self.trail = []  # предыдущие позиции для шлейфа

    def update(self, dt: float):
        # Сохраняем позицию для шлейфа
        self.trail.append(self.pos.copy())
        if len(self.trail) > 5:
            self.trail.pop(0)

        if self.homing and self.target and self.target.get("alive", True):
            target_pos = self.target.get("pos")
            if target_pos:
                d = target_pos - self.pos
                if d.length() > 0:
                    d = d.normalize()
                    self.vel = d * self.vel.length()

        self.pos += self.vel * 60 * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        r, g, b = self.color

        # Шлейф
        for i, pos in enumerate(self.trail):
            tx = int(pos.x - cam_x)
            ty = int(pos.y - cam_y)
            if -20 < tx < 1044 and -20 < ty < 788:
                alpha = int(40 * (i + 1) / len(self.trail))
                trail_r = max(1, self.radius // 2)
                trail_surf = pygame.Surface((trail_r * 2, trail_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (r, g, b, alpha), (trail_r, trail_r), trail_r)
                surface.blit(trail_surf, (tx - trail_r, ty - trail_r))

        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)
        if -20 < sx < 1044 and -20 < sy < 788:
            # Glow
            glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (r, g, b, 60),
                               (self.radius * 2, self.radius * 2), self.radius * 2)
            surface.blit(glow, (sx - self.radius * 2, sy - self.radius * 2))
            # Core
            pygame.draw.circle(surface, self.color, (sx, sy), self.radius)
            pygame.draw.circle(surface, WHITE, (sx, sy), max(1, self.radius // 2))


class Particle:
    """Короткоживущая частица (спарк при попадании)."""
    def __init__(self, x, y, color, speed=2.0, lifetime=0.3):
        angle = math.radians(__import__('random').randint(0, 360))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True

    def update(self, dt: float):
        self.pos += self.vel * 60 * dt
        self.vel *= 0.95
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)
        alpha = max(0, min(255, int(255 * (self.lifetime / max(0.001, self.max_lifetime)))))
        size = max(1, int(3 * (self.lifetime / max(0.001, self.max_lifetime))))
        r, g, b = int(self.color[0]), int(self.color[1]), int(self.color[2])
        if 0 <= sx < 1044 and 0 <= sy < 788:
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (r, g, b, alpha), (size, size), size)
            surface.blit(s, (sx - size, sy - size))


def ease_out_cubic(t):
    """Easing для плавного замедления."""
    return 1 - (1 - min(1.0, t)) ** 3


class FloatingNumberManager:
    """Менеджер для floating damage/XP/heal numbers."""
    MAX_NUMBERS = 50  # Limit for performance

    def __init__(self):
        self.numbers = []

    def spawn_damage(self, x, y, damage, color=WHITE, is_crit=False):
        """Создать число урона."""
        if len(self.numbers) >= self.MAX_NUMBERS:
            self.numbers.pop(0)
        self.numbers.append(DamageNumber(x, y, int(damage), color, is_crit=is_crit))

    def spawn_heal(self, x, y, amount):
        """Создать число лечения (зелёное)."""
        if len(self.numbers) >= self.MAX_NUMBERS:
            self.numbers.pop(0)
        n = DamageNumber(x, y, int(amount), (80, 255, 80), is_crit=False)
        n.lifetime = 1.0
        self.numbers.append(n)

    def spawn_xp(self, x, y, amount):
        """Создать число XP (cyan)."""
        if len(self.numbers) >= self.MAX_NUMBERS:
            self.numbers.pop(0)
        n = DamageNumber(x, y, int(amount), (0, 200, 255), is_crit=False)
        n.lifetime = 0.8
        self.numbers.append(n)

    def update(self, dt):
        for n in self.numbers:
            n.update(dt)
        self.numbers = [n for n in self.numbers if n.alive]

    def draw(self, surface, cam_x, cam_y, font):
        for n in self.numbers:
            n.draw(surface, cam_x, cam_y, font)


# Глобальный экземпляр
floating_numbers = FloatingNumberManager()


class DamageNumber:
    """Всплывающее число урона с easing."""
    def __init__(self, x, y, damage, color=WHITE, is_crit=False):
        self.pos = pygame.Vector2(x, y)
        self.damage = int(damage)
        self.color = color
        self.is_crit = is_crit
        self.max_lifetime = 1.0 if is_crit else 0.8
        self.lifetime = self.max_lifetime
        self.alive = True
        self.offset_y = 0
        self.start_y = 0
        self.scale = 1.3 if is_crit else 1.0

    def update(self, dt: float):
        self.lifetime -= dt
        t = 1.0 - (self.lifetime / self.max_lifetime)
        # Easing: быстро вверх, потом замедляется
        target_offset = -60 if self.is_crit else -45
        self.offset_y = self.start_y + target_offset * ease_out_cubic(t)
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, font):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y + self.offset_y)
        t = 1.0 - (self.lifetime / self.max_lifetime)
        alpha = int(255 * max(0, 1.0 - t * 1.2))  # Fade out near end

        if self.is_crit:
            crit_color = (255, 255, 100)
            text = font.render(str(self.damage), True, crit_color)
            if self.scale != 1.0:
                w = int(text.get_width() * self.scale)
                h = int(text.get_height() * self.scale)
                text = pygame.transform.scale(text, (w, h))
            text.set_alpha(alpha)
            # Glow
            glow = text.copy()
            glow.fill((255, 255, 200, alpha // 3), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(glow, (sx - glow.get_width() // 2 - 1, sy - 1))
            surface.blit(text, (sx - text.get_width() // 2, sy))
        else:
            text = font.render(str(self.damage), True, self.color)
            text.set_alpha(alpha)
            surface.blit(text, (sx - text.get_width() // 2, sy))


def make_damage_number(x, y, damage, color, player=None):
    """Создать DamageNumber с учётом крита."""
    import random
    is_crit = False
    if player and hasattr(player, 'crit_chance'):
        is_crit = random.random() < player.crit_chance
        if is_crit:
            damage *= 2.0
    return DamageNumber(x, y, damage, color, is_crit=is_crit)


class Pulse:
    """Расширяющийся круг (для AoE атак)."""
    def __init__(self, x, y, max_radius, color, duration=0.22):
        self.pos = pygame.Vector2(x, y)
        self.max_radius = max_radius
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.alive = True

    def update(self, dt: float):
        self.duration -= dt
        if self.duration <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        progress = 1.0 - (self.duration / self.max_duration)
        radius = int(self.max_radius * progress)
        alpha = int(120 * (1 - progress))
        if radius > 0 and alpha > 0:
            sx = int(self.pos.x - cam_x)
            sy = int(self.pos.y - cam_y)
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            r, g, b = self.color
            pygame.draw.circle(s, (r, g, b, alpha), (radius, radius), radius, 3)
            surface.blit(s, (sx - radius, sy - radius))


class LightningBolt:
    """Эффект молнии (зигзаг)."""
    def __init__(self, x, y, aoe, color):
        self.pos = pygame.Vector2(x, y)
        self.aoe = aoe
        self.color = color
        self.duration = 0.3
        self.max_duration = 0.3
        self.alive = True
        # Генерируем зигзаг
        import random
        self.segments = []
        cx, cy = int(x), int(y)
        prev_x, prev_y = cx, cy - int(aoe)
        for i in range(6):
            next_y = prev_y + int(aoe * 2 / 6)
            next_x = cx + random.randint(-int(aoe * 0.3), int(aoe * 0.3))
            self.segments.append((prev_x, prev_y, next_x, next_y))
            prev_x, prev_y = next_x, next_y

    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0:
            self.alive = False

    def draw(self, surface, cam_x, cam_y):
        progress = 1.0 - (self.duration / self.max_duration)
        alpha = int(255 * (1 - progress))
        if alpha <= 0:
            return
        r, g, b = self.color
        # Glow
        for x1, y1, x2, y2 in self.segments:
            sx1, sy1 = int(x1 - cam_x), int(y1 - cam_y)
            sx2, sy2 = int(x2 - cam_x), int(y2 - cam_y)
            pygame.draw.line(surface, (r, g, b, alpha // 3), (sx1, sy1), (sx2, sy2), 4)
            pygame.draw.line(surface, (r, g, b, alpha), (sx1, sy1), (sx2, sy2), 2)
            pygame.draw.line(surface, (255, 255, 255, alpha), (sx1, sy1), (sx2, sy2), 1)
        # Impact flash
        if progress < 0.5:
            impact_a = int(alpha * 0.4)
            impact_r = int(self.aoe * 0.5 * (1 - progress * 2))
            if impact_r > 0:
                cx = int(self.pos.x - cam_x)
                cy = int(self.pos.y - cam_y)
                flash = pygame.Surface((impact_r * 2, impact_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(flash, (r, g, b, impact_a), (impact_r, impact_r), impact_r)
                surface.blit(flash, (cx - impact_r, cy - impact_r))


class WhipSweep:
    """Эффект удара кнутом (дуга)."""
    def __init__(self, x, y, direction, color, length=115):
        self.pos = pygame.Vector2(x, y)
        self.direction = direction  # 1 = right, -1 = left
        self.color = color
        self.length = length
        self.duration = 0.2
        self.max_duration = 0.2
        self.alive = True

    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0:
            self.alive = False

    def draw(self, surface, cam_x, cam_y):
        import math
        progress = 1.0 - (self.duration / self.max_duration)
        alpha = int(255 * (1 - progress * 0.8))
        if alpha <= 0:
            return
        cx = int(self.pos.x - cam_x)
        cy = int(self.pos.y - cam_y)
        r, g, b = self.color

        # Рисуем дугу
        start_angle = -60 + int(progress * 40)
        end_angle = start_angle + 120 - int(progress * 30)
        arc_r = int(self.length * 0.5 * (0.5 + progress * 0.5))

        points = []
        for deg in range(start_angle, end_angle, 5):
            rad = math.radians(deg)
            x = cx + int(math.cos(rad) * arc_r * self.direction)
            y = cy + int(math.sin(rad) * arc_r)
            points.append((x, y))

        if len(points) >= 2:
            # Glow
            pygame.draw.lines(surface, (r, g, b, alpha // 3), False, points, 4)
            # Core
            pygame.draw.lines(surface, (r, g, b, alpha), False, points, 2)
            # Bright
            pygame.draw.lines(surface, (255, 240, 200, alpha), False, points, 1)


class RingWave:
    """Расширяющееся кольцо (для Prayer/Bell)."""
    def __init__(self, x, y, max_radius, color, duration=0.3):
        self.pos = pygame.Vector2(x, y)
        self.max_radius = max_radius
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.alive = True

    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0:
            self.alive = False

    def draw(self, surface, cam_x, cam_y):
        progress = 1.0 - (self.duration / self.max_duration)
        alpha = int(200 * (1 - progress))
        if alpha <= 0:
            return
        cx = int(self.pos.x - cam_x)
        cy = int(self.pos.y - cam_y)
        r, g, b = self.color

        # 3 кольца с задержкой
        for ring_idx in range(3):
            ring_progress = max(0, progress - ring_idx * 0.15)
            ring_r = int(self.max_radius * ring_progress)
            ring_a = int(alpha * (1 - ring_idx * 0.25))
            if ring_r > 0 and ring_a > 0:
                s = pygame.Surface((ring_r * 2, ring_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (r, g, b, ring_a), (ring_r, ring_r), ring_r, 2)
                surface.blit(s, (cx - ring_r, cy - ring_r))
