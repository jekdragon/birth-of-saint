"""
Рождение святого — Projectiles & Particles
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

    def update(self, dt: float):
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
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)
        if -20 < sx < 1044 and -20 < sy < 788:
            # Glow
            glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            r, g, b = self.color
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


class DamageNumber:
    """Всплывающее число урона."""
    def __init__(self, x, y, damage, color=WHITE):
        self.pos = pygame.Vector2(x, y)
        self.damage = int(damage)
        self.color = color
        self.lifetime = 0.6
        self.alive = True
        self.offset_y = 0

    def update(self, dt: float):
        self.offset_y -= 40 * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float, font):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y + self.offset_y)
        alpha = int(255 * (self.lifetime / 0.6))
        text = font.render(str(self.damage), True, self.color)
        text.set_alpha(alpha)
        surface.blit(text, (sx - text.get_width() // 2, sy))


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
