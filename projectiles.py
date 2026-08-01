"""
Рождение святого - Projectiles & Particles
Снаряды, частицы, визуальные эффекты атак.
"""
import math
import random
import pygame
from config import WHITE


# ============================================================
# A3: 4-tier particle burst presets
# ============================================================
PARTICLE_PRESETS = {
    "light": {"count": (3, 5), "speed": (2.0, 3.0), "lifetime": (0.15, 0.25), "size": 2},
    "medium": {"count": (8, 12), "speed": (3.0, 4.5), "lifetime": (0.25, 0.4), "size": 2},
    "heavy": {"count": (16, 24), "speed": (4.0, 6.0), "lifetime": (0.3, 0.5), "size": 3},
    "crit": {"count": (30, 45), "speed": (5.0, 8.0), "lifetime": (0.35, 0.6), "size": 3},
}

# Kill ring burst parameters
_RING_BURST = {"radius": 45, "duration": 0.25}

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
    def __init__(self, x, y, color, speed=2.0, lifetime=0.3,
                 hit_dir=None, spread_deg=360):
        """hit_dir: pygame.Vector2 normalized direction. If given, particles
        burst in that direction within ±spread_deg/2 instead of full 360."""
        if hit_dir is not None:
            base_angle = math.atan2(hit_dir.y, hit_dir.x)
            half = math.radians(spread_deg / 2)
            angle = base_angle + random.uniform(-half, half)
        else:
            angle = random.uniform(0, math.tau)
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


# ============================================================
# A3: Hit Particle Pool — pre-allocate 200, recycle dead
# ============================================================
class HitParticlePool:
    """Pre-allocated particle pool to avoid per-frame allocation.

    Particles are recycled: when one dies, its slot is reused by emit_hit_burst.
    The pool is transparent — use pool.particles in place of game.particles.
    """
    def __init__(self, capacity=200):
        self.capacity = capacity
        self.particles = []

    def _acquire(self, x, y, color, speed, lifetime, hit_dir, spread_deg):
        """Return a live Particle, reusing a dead slot if possible."""
        # Try to recycle a dead particle
        for p in self.particles:
            if not p.alive:
                p.__init__(x, y, color, speed=speed, lifetime=lifetime,
                           hit_dir=hit_dir, spread_deg=spread_deg)
                return p
        # If under capacity, create new
        if len(self.particles) < self.capacity:
            p = Particle(x, y, color, speed=speed, lifetime=lifetime,
                         hit_dir=hit_dir, spread_deg=spread_deg)
            self.particles.append(p)
            return p
        # At capacity: recycle oldest alive (wrap-around)
        oldest = self.particles[0]
        oldest.__init__(x, y, color, speed=speed, lifetime=lifetime,
                        hit_dir=hit_dir, spread_deg=spread_deg)
        self.particles.append(self.particles.pop(0))
        return oldest

    def update(self, dt):
        for p in self.particles:
            if p.alive:
                p.update(dt)

    def draw(self, surface, cam_x, cam_y):
        for p in self.particles:
            if p.alive:
                p.draw(surface, cam_x, cam_y)


# Global pool instance (shared across Game instances)
_hit_pool = HitParticlePool(200)


def emit_hit_burst(particles, x, y, tier, color, hit_dir=None):
    """Emit a tiered hit particle burst.

    Args:
        particles: list to append to (game.particles or pool.particles)
        x, y: world position
        tier: "light", "medium", "heavy", or "crit"
        color: RGB tuple
        hit_dir: optional pygame.Vector2 normalized direction for directional burst
    """
    preset = PARTICLE_PRESETS.get(tier, PARTICLE_PRESETS["light"])
    count = random.randint(*preset["count"])
    # When hit_dir given, use 120° cone; otherwise full 360°
    spread = 120 if hit_dir is not None else 360
    for _ in range(count):
        speed = random.uniform(*preset["speed"])
        life = random.uniform(*preset["lifetime"])
        particles.append(Particle(x, y, color, speed=speed, lifetime=life,
                                  hit_dir=hit_dir, spread_deg=spread))


class RingBurst:
    """Expanding ring that spawns on kill. Quick outward wave."""
    def __init__(self, x, y, radius=45, color=(255, 220, 100), duration=0.25):
        self.pos = pygame.Vector2(x, y)
        self.max_radius = radius
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.alive = True

    def update(self, dt):
        self.duration -= dt
        if self.duration <= 0:
            self.alive = False

    def draw(self, surface, cam_x, cam_y):
        progress = 1.0 - (self.duration / max(0.001, self.max_duration))
        radius = int(self.max_radius * progress)
        alpha = int(180 * (1 - progress))
        if radius <= 0 or alpha <= 0:
            return
        cx = int(self.pos.x - cam_x)
        cy = int(self.pos.y - cam_y)
        r, g, b = self.color
        # Two concentric rings for thickness
        for ring_r, ring_w in [(radius, 3), (int(radius * 0.7), 2)]:
            if ring_r > 0:
                s = pygame.Surface((ring_r * 2, ring_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (r, g, b, alpha), (ring_r, ring_r), ring_r, ring_w)
                surface.blit(s, (cx - ring_r, cy - ring_r))


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
    """REF-10: Молния с телеграфом (сжимающееся кольцо) перед ударом."""
    TELEGRAPH_TIME = 0.3    # ~18 frames at 60fps - shrinking ring warning
    STRIKE_FLASH_TIME = 0.25  # bolt visual after strike

    def __init__(self, x, y, aoe, color, on_strike=None):
        self.pos = pygame.Vector2(x, y)
        self.tx, self.ty = float(x), float(y)
        self.aoe = aoe
        self.color = color
        self.on_strike = on_strike  # callback for delayed damage
        self.alive = True
        # Phase: telegraph -> strike -> dead
        self.phase = "telegraph"
        self.telegraph_timer = self.TELEGRAPH_TIME
        self.strike_timer = 0.0
        self.segments = []

    def _generate_segments(self):
        """Сгенерировать зигзаг-сегменты для визуала молнии."""
        cx, cy = int(self.tx), int(self.ty)
        prev_x, prev_y = cx, cy - int(self.aoe)
        self.segments = []
        for i in range(6):
            next_y = prev_y + int(self.aoe * 2 / 6)
            next_x = cx + random.randint(-int(self.aoe * 0.3), int(self.aoe * 0.3))
            self.segments.append((prev_x, prev_y, next_x, next_y))
            prev_x, prev_y = next_x, next_y

    def update(self, dt):
        if self.phase == "telegraph":
            self.telegraph_timer -= dt
            if self.telegraph_timer <= 0:
                self.phase = "strike"
                self.strike_timer = self.STRIKE_FLASH_TIME
                self._generate_segments()
                if self.on_strike:
                    self.on_strike()
        elif self.phase == "strike":
            self.strike_timer -= dt
            if self.strike_timer <= 0:
                self.alive = False

    def draw(self, surface, cam_x, cam_y):
        sx = int(self.tx - cam_x)
        sy = int(self.ty - cam_y)
        if self.phase == "telegraph":
            # Сжимающееся кольцо-предупреждение (reference pattern)
            t = self.telegraph_timer / self.TELEGRAPH_TIME  # 1.0 -> 0.0
            r = max(4, int(self.aoe * (0.55 + 0.45 * t)))
            warn_alpha = int(80 + 100 * (1 - t))
            ring = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            rc, gc, bc = self.color
            pygame.draw.circle(ring, (rc, gc, bc, warn_alpha), (r + 2, r + 2), r, 3)
            surface.blit(ring, (sx - r - 2, sy - r - 2))
        elif self.phase == "strike":
            t = self.strike_timer / self.STRIKE_FLASH_TIME  # 1.0 -> 0.0
            alpha = int(220 * t)
            if alpha <= 0:
                return
            r, g, b = self.color
            # Зигзаг-молния
            for x1, y1, x2, y2 in self.segments:
                sx1, sy1 = int(x1 - cam_x), int(y1 - cam_y)
                sx2, sy2 = int(x2 - cam_x), int(y2 - cam_y)
                pygame.draw.line(surface, (r, g, b, alpha // 3), (sx1, sy1), (sx2, sy2), 4)
                pygame.draw.line(surface, (r, g, b, alpha), (sx1, sy1), (sx2, sy2), 2)
                pygame.draw.line(surface, (255, 255, 255, alpha), (sx1, sy1), (sx2, sy2), 1)
            # Impact flash
            if t > 0.3:
                impact_a = int(90 * t)
                flash = pygame.Surface((self.aoe * 2, self.aoe * 2), pygame.SRCALPHA)
                pygame.draw.circle(flash, (r, g, b, impact_a),
                                   (self.aoe, self.aoe), self.aoe)
                surface.blit(flash, (sx - self.aoe, sy - self.aoe))
            # Белый центр
            pygame.draw.circle(surface, WHITE, (sx, sy), max(2, int(6 * t)))


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


class GoldCoin:
    """Золотая монета, выпадающая из врагов. Притягивается к игроку."""
    def __init__(self, x, y, value=1):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(
            random.uniform(-2.0, 2.0),
            random.uniform(-3.0, -1.0)
        )
        self.value = value
        self.alive = True
        self.bob = random.uniform(0, math.tau)
        self.lifetime = 12.0
        self.attracting = False

    def update(self, player_pos, pickup_range, dt):
        """Update coin physics. Returns value if collected, 0 otherwise."""
        self.bob += dt * 5.0
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return 0

        dist = (self.pos - player_pos).length()
        if dist < pickup_range:
            self.attracting = True
        if self.attracting:
            d = player_pos - self.pos
            if d.length() > 0:
                speed = 8.0 + max(0, (pickup_range - dist) / pickup_range) * 6.0
                self.pos += d.normalize() * speed * 60 * dt
            if dist < 15:
                self.alive = False
                return self.value
        else:
            self.vel.y += 0.08
            self.pos += self.vel * 60 * dt
            self.vel.x *= 0.97

        return 0

    def draw(self, surface, cam_x, cam_y):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y + math.sin(self.bob) * 3)
        if -12 < sx < 1036 and -12 < sy < 780:
            pygame.draw.circle(surface, (200, 160, 0), (sx, sy), 7)
            pygame.draw.circle(surface, (255, 215, 0), (sx, sy), 5)
            pygame.draw.circle(surface, (255, 255, 180), (sx - 2, sy - 2), 2)
            if self.attracting:
                glow = pygame.Surface((24, 24), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 215, 0, 50), (12, 12), 12)
                surface.blit(glow, (sx - 12, sy - 12))


class EvolutionGlow:
    """Пульсирующая аура при эволюции оружия. Следует за игроком."""
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.duration = 1.8
        self.max_duration = 1.8
        self.alive = True
        self.phase = 0.0

    def update(self, dt: float, player_pos=None):
        self.duration -= dt
        self.phase += dt * 6.0  # пульсация
        if player_pos:
            self.pos = pygame.Vector2(player_pos)
        if self.duration <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        import math
        progress = 1.0 - (self.duration / self.max_duration)
        alpha = int(180 * (1 - progress * 0.7))
        if alpha <= 0:
            return
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)
        # Пульсирующий радиус
        pulse = math.sin(self.phase) * 0.15 + 1.0
        base_r = int(50 * pulse)
        # 3 кольца с разной прозрачностью
        for i in range(3):
            r = base_r + i * 12
            a = max(0, alpha - i * 50)
            if r > 0 and a > 0:
                s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                # Золотое свечение
                pygame.draw.circle(s, (255, 220, 80, a), (r, r), r, 3)
                surface.blit(s, (sx - r, sy - r))
        # Центральная вспышка
        if progress < 0.3:
            flash_a = int(200 * (1 - progress / 0.3))
            flash_r = int(30 * (1 + progress))
            s = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 200, flash_a), (flash_r, flash_r), flash_r)
            surface.blit(s, (sx - flash_r, sy - flash_r))
