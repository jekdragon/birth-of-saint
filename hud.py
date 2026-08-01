"""
Рождение святого - HUD
Отрисовка интерфейса: HP, XP, таймер, оружие, пассивки.
Animated bars, weapon slots, passive slots, combo counter, boss HP bar.
"""
import pygame
import math
import random
from config import (
    WIDTH, HEIGHT, HUD_PADDING
)
from ui_theme import (
    GOLD_LEAF, TEXT_PRIMARY, RARITY_COLORS,
    PARCH_DARK, PARCH_MID, PARCH_BASE, PARCH_LIGHT, PARCH_INK, PARCH_INK_DIM,
)
from weapons import WEAPON_DEFS, PASSIVE_DEFS


def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * min(1.0, t)


# ============================================================
# B4: Catechism of Ruin — Illuminated Manuscript Parchment
# ============================================================
# Parchment palette (warm aged vellum) — из ui_theme
# (PARCH_DARK, PARCH_MID, PARCH_BASE, PARCH_LIGHT, PARCH_INK, PARCH_INK_DIM)

# Cache for procedural parchment textures (keyed by (w, h))
_parchment_cache: dict = {}


def generate_parchment(w: int, h: int, seed: int = 42) -> pygame.Surface:
    """Procedural torn-parchment background with singed edges and fiber noise."""
    key = (w, h, seed)
    if key in _parchment_cache:
        return _parchment_cache[key]

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(seed)

    # Layer 1: outer charred border
    pygame.draw.rect(surf, PARCH_DARK, (0, 0, w, h), border_radius=6)
    # Layer 2: smoke-stained ring
    pygame.draw.rect(surf, PARCH_MID, (3, 3, w - 6, h - 6), border_radius=5)
    # Layer 3: parchment base
    pygame.draw.rect(surf, PARCH_BASE, (8, 8, w - 16, h - 16), border_radius=4)
    # Layer 4: lighter inner area
    pygame.draw.rect(surf, PARCH_LIGHT, (12, 12, w - 24, h - 24), border_radius=3)

    # Fiber noise (subtle horizontal streaks like real vellum)
    for fy in range(14, h - 14, 3):
        streak_a = rng.randint(8, 25)
        streak_r = rng.randint(-8, 8)
        y_offset = rng.randint(-1, 1)
        pygame.draw.line(
            surf,
            (PARCH_BASE[0] + streak_r, PARCH_BASE[1] + streak_r, PARCH_BASE[2] + streak_r, streak_a),
            (14, fy + y_offset),
            (w - 14, fy + y_offset),
        )

    # Corner burns (singed/charred patches)
    bsz = max(12, min(20, w // 8))
    corners = [(12, 12), (w - 12 - bsz, 12), (12, h - 12 - bsz), (w - 12 - bsz, h - 12 - bsz)]
    for cx_, cy_ in corners:
        burn_surf = pygame.Surface((bsz, bsz), pygame.SRCALPHA)
        burn_surf.fill((PARCH_MID[0], PARCH_MID[1], PARCH_MID[2], rng.randint(80, 140)))
        surf.blit(burn_surf, (cx_, cy_))

    # Decorative top border line (ink)
    pygame.draw.line(surf, (80, 70, 50), (16, 14), (w - 16, 14), 1)

    # Edge tears (irregular edge pixels)
    for tx in range(0, w, 4):
        tear_a = rng.randint(0, 60)
        if tear_a > 30:
            tear_len = rng.randint(1, 3)
            for ty_offset in range(tear_len):
                surf.set_at((tx, ty_offset), (PARCH_DARK[0], PARCH_DARK[1], PARCH_DARK[2], tear_a))
                surf.set_at((tx, h - 1 - ty_offset), (PARCH_DARK[0], PARCH_DARK[1], PARCH_DARK[2], tear_a))

    _parchment_cache[key] = surf
    return surf


class WaxDrip:
    """Single wax drip particle falling from candle."""
    __slots__ = ('x', 'y', 'vy', 'alpha', 'size', 'alive')

    def __init__(self, x, y):
        self.x = x + random.uniform(-4, 4)
        self.y = y
        self.vy = random.uniform(30, 80)
        self.alpha = 255
        self.size = random.randint(2, 4)
        self.alive = True

    def update(self, dt):
        self.y += self.vy * dt
        self.vy += 120 * dt  # gravity
        self.alpha -= 180 * dt
        if self.alpha <= 0 or self.y > 120:
            self.alive = False


class AnimatedHealthBar:
    """Pyre of Grace — HP bar as a liturgical candle.

    Candle body (wax) depletes with HP. Flame on top has 5 intensity states:
      100-80% = strong golden flame
      80-60%  = moderate warm flame
      60-40%  = flickering amber flame
      40-20%  = weak dying flame
      <20%    = barely alive ember

    Wax drip particles fall when HP decreases. Glow aura around flame.
    """

    # Flame state thresholds (HP ratio)
    FLAME_STRONG = 0.80
    FLAME_MODERATE = 0.60
    FLAME_FLICKER = 0.40
    FLAME_WEAK = 0.20

    # Candle dimensions
    CANDLE_W = 14
    FLAME_BASE_H = 20  # max flame height at 100%

    # Colors per flame state: (core, outer, glow)
    FLAME_COLORS = {
        'strong':   ((255, 240, 180), (255, 180, 50),  (255, 200, 80)),
        'moderate': ((255, 210, 120), (240, 150, 40),  (255, 170, 60)),
        'flicker':  ((255, 170, 60),  (200, 100, 20),  (240, 130, 40)),
        'weak':     ((220, 100, 30),  (160, 60, 10),   (200, 80, 20)),
        'ember':    ((180, 60, 10),   (100, 30, 5),    (150, 40, 10)),
    }

    def __init__(self):
        self.display_hp = 0
        self.damage_bar = 0
        self.damage_timer = 0.0
        self._wax_drips = []
        self._prev_hp = 0
        self._frame_counter = 0

    def update(self, dt, current_hp, max_hp):
        old_hp = self.display_hp
        self.display_hp = current_hp

        # Wax drip on damage
        if current_hp < old_hp and old_hp > 0:
            drop = old_hp - current_hp
            n_drips = max(1, min(8, int(drop / max(1, max_hp) * 20)))
            for _ in range(n_drips):
                self._wax_drips.append(WaxDrip(0, 0))  # positions set in draw

        # Update wax drips
        for d in self._wax_drips:
            d.update(dt)
        self._wax_drips = [d for d in self._wax_drips if d.alive]
        if len(self._wax_drips) > 40:
            self._wax_drips = self._wax_drips[-40:]

        # Damage bar trailing
        if self.damage_bar > self.display_hp:
            if self.damage_timer <= 0:
                self.damage_timer = 0.5
            self.damage_timer -= dt
            if self.damage_timer <= 0:
                self.damage_bar = lerp(self.damage_bar, self.display_hp, 5.0 * dt)
        else:
            self.damage_bar = self.display_hp
            self.damage_timer = 0.0

        self._frame_counter += 1

    def _get_flame_state(self, hp_ratio):
        """Return flame state string from HP ratio."""
        if hp_ratio > self.FLAME_STRONG:
            return 'strong'
        elif hp_ratio > self.FLAME_MODERATE:
            return 'moderate'
        elif hp_ratio > self.FLAME_FLICKER:
            return 'flicker'
        elif hp_ratio > self.FLAME_WEAK:
            return 'weak'
        else:
            return 'ember'

    def _get_flicker_speed(self, state):
        """Flicker frequency per flame state."""
        return {'strong': 3.0, 'moderate': 5.0, 'flicker': 8.0, 'weak': 12.0, 'ember': 18.0}[state]

    def draw(self, surface, x, y, width, height, max_hp, font):
        """Draw candle HP bar.

        Args:
            x, y: top-left of the allocated HUD area
            width, height: allocated area dimensions (180, 18 default)
        """
        hp_ratio = max(0.0, min(1.0, self.display_hp / max(1, max_hp)))
        state = self._get_flame_state(hp_ratio)
        core_col, outer_col, glow_col = self.FLAME_COLORS[state]
        t = pygame.time.get_ticks() / 1000.0

        # --- Candle geometry ---
        candle_x = x + 6
        candle_bottom = y + height + 30  # extends below original bar area
        candle_h = max(8, int(42 * hp_ratio))  # wax body height scales with HP
        candle_top = candle_bottom - candle_h
        cw = self.CANDLE_W

        # --- Wax shadow (below candle) ---
        shadow_surf = pygame.Surface((cw + 10, 6), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 50))
        surface.blit(shadow_surf, (candle_x - 5, candle_bottom - 1))

        # --- Candle base (stand) ---
        base_w = cw + 8
        pygame.draw.rect(surface, (80, 60, 40), (candle_x - 4, candle_bottom - 3, base_w, 5))
        pygame.draw.rect(surface, (120, 90, 60), (candle_x - 4, candle_bottom - 3, base_w, 2))

        # --- Wax body ---
        # Trailing damage bar (darker wax behind)
        dmg_ratio = max(0, self.damage_bar / max(1, max_hp))
        dmg_h = max(0, int(42 * dmg_ratio))
        if dmg_h > 0:
            dmg_top = candle_bottom - dmg_h
            pygame.draw.rect(surface, (180, 160, 120), (candle_x, dmg_top, cw, dmg_h))

        # Current HP wax
        if candle_h > 0:
            # Wax gradient: warm cream at top, darker at bottom
            for row in range(candle_h):
                row_y = candle_top + row
                frac = row / max(1, candle_h - 1)  # 0=top, 1=bottom
                r = int(240 - 60 * frac)
                g = int(220 - 70 * frac)
                b = int(180 - 80 * frac)
                pygame.draw.line(surface, (r, g, b), (candle_x, row_y), (candle_x + cw - 1, row_y))

            # Wax edge highlights (left = bright, right = shadow)
            pygame.draw.line(surface, (255, 240, 220), (candle_x, candle_top), (candle_x, candle_bottom - 1))
            pygame.draw.line(surface, (160, 140, 100), (candle_x + cw - 1, candle_top), (candle_x + cw - 1, candle_bottom - 1))

            # Wax top rim
            pygame.draw.line(surface, (255, 250, 230), (candle_x, candle_top), (candle_x + cw - 1, candle_top))

        # --- Damage bar (trailing, darker wax) ---
        dmg_ratio = max(0, self.damage_bar / max(1, max_hp))
        dmg_h = max(0, int(42 * dmg_ratio))
        if dmg_h > candle_h:
            extra_h = dmg_h - candle_h
            extra_top = candle_bottom - dmg_h
            pygame.draw.rect(surface, (180, 160, 120), (candle_x, extra_top, cw, extra_h))

        # --- Wick ---
        wick_x = candle_x + cw // 2
        wick_top = candle_top - 3
        if candle_h > 2:
            pygame.draw.line(surface, (40, 30, 20), (wick_x, candle_top), (wick_x, wick_top))

        # --- Flame ---
        if hp_ratio > 0:
            flicker_speed = self._get_flicker_speed(state)
            # 5 flame lobes using sinusoidal motion
            flame_h = max(4, int(self.FLAME_BASE_H * hp_ratio))
            flame_cx = wick_x
            flame_base_y = wick_top

            # Outer glow
            glow_r = flame_h + 8
            glow_alpha = int(40 + 20 * hp_ratio + 15 * math.sin(t * flicker_speed))
            glow_alpha = max(0, min(255, glow_alpha))
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow_col, glow_alpha // 2), (glow_r, glow_r), glow_r)
            surface.blit(glow_surf, (flame_cx - glow_r, flame_base_y - glow_r + 2))

            # Flame body (3 overlapping ellipses for organic shape)
            sway = math.sin(t * flicker_speed * 0.7) * 2.0
            flicker_h = 1.0 + 0.15 * math.sin(t * flicker_speed)

            # Main flame (outer)
            fh_main = max(3, int(flame_h * flicker_h))
            fw_main = max(3, int(cw * 0.9))
            flame_rect_outer = pygame.Rect(
                int(flame_cx - fw_main // 2 + sway * 0.3),
                flame_base_y - fh_main,
                fw_main, fh_main
            )
            if fh_main > 2 and fw_main > 2:
                outer_surf = pygame.Surface((fw_main, fh_main), pygame.SRCALPHA)
                pygame.draw.ellipse(outer_surf, (*outer_col, 200), (0, 0, fw_main, fh_main))
                surface.blit(outer_surf, (flame_rect_outer.x, flame_rect_outer.y))

            # Inner flame (core) — smaller, brighter
            fh_core = max(2, int(flame_h * 0.55 * flicker_h))
            fw_core = max(2, int(cw * 0.5))
            sway_core = sway * 1.2
            flame_rect_core = pygame.Rect(
                int(flame_cx - fw_core // 2 + sway_core),
                flame_base_y - fh_core,
                fw_core, fh_core
            )
            if fh_core > 1 and fw_core > 1:
                core_surf = pygame.Surface((fw_core, fh_core), pygame.SRCALPHA)
                pygame.draw.ellipse(core_surf, (*core_col, 230), (0, 0, fw_core, fh_core))
                surface.blit(core_surf, (flame_rect_core.x, flame_rect_core.y))

            # Bright center dot (hot spot)
            dot_y = flame_base_y - fh_core // 3
            dot_r = max(1, int(2 * hp_ratio))
            pygame.draw.circle(surface, (255, 255, 220), (int(flame_cx + sway_core), int(dot_y)), dot_r)

            # Flickering spark particles (at low HP, more sparks)
            if state in ('flicker', 'weak', 'ember'):
                n_sparks = 2 if state == 'ember' else 1
                for _ in range(n_sparks):
                    # Use frame counter for deterministic but varied sparks
                    seed = self._frame_counter + random.randint(0, 50)
                    sx = flame_cx + math.sin(seed * 0.3) * 6
                    sy = flame_base_y - flame_h * 0.3 + math.cos(seed * 0.5) * flame_h * 0.4
                    spark_alpha = int(150 + 100 * math.sin(seed * 0.8))
                    spark_alpha = max(0, min(255, spark_alpha))
                    spark_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                    pygame.draw.circle(spark_surf, (*core_col, spark_alpha), (2, 2), 1)
                    surface.blit(spark_surf, (int(sx) - 2, int(sy) - 2))

        # --- Wax drip particles ---
        drip_cx = candle_x + cw // 2
        for d in self._wax_drips:
            # Offset from candle position
            dx = drip_cx + (d.x - 0)  # x was set relative to 0 in WaxDrip
            dy = candle_top + d.y
            da = max(0, min(255, int(d.alpha)))
            if da > 0:
                drip_surf = pygame.Surface((d.size, d.size + 1), pygame.SRCALPHA)
                drip_surf.fill((230, 210, 170, da))
                surface.blit(drip_surf, (int(dx), int(dy)))

        # --- HP text (right of candle) ---
        text_x = candle_x + cw + 6
        text_y = y + height // 2 - font.get_height() // 2 + 10

        # Color based on flame state
        if state == 'strong':
            text_col = (200, 230, 200)
        elif state == 'moderate':
            text_col = TEXT_PRIMARY
        elif state == 'flicker':
            text_col = (255, 200, 100)
        elif state == 'weak':
            text_col = (255, 140, 60)
        else:
            # Ember — pulsing red text
            pulse = (math.sin(t * 6.0) + 1.0) / 2.0
            r = int(180 + 75 * pulse)
            text_col = (r, 60, 20)

        hp_text = font.render(f"{int(self.display_hp)}/{max_hp}", True, text_col)
        surface.blit(hp_text, (text_x, text_y))

        # --- Low HP vignette pulse (drawn last, on top) ---
        if hp_ratio < 0.2 and hp_ratio > 0:
            pulse = (math.sin(t * 4.0) + 1.0) / 2.0
            vig_alpha = int(50 * pulse * (1.0 - hp_ratio / 0.2))
            if vig_alpha > 0:
                vig_surf = pygame.Surface((width, height + 40), pygame.SRCALPHA)
                vig_surf.fill((200, 30, 10, vig_alpha))
                surface.blit(vig_surf, (x, y))


class BrazierParticle:
    """Fire particle rising from brazier."""
    __slots__ = ('x', 'y', 'vy', 'alpha', 'size', 'color_idx', 'alive')

    def __init__(self, x, base_y, intensity):
        self.x = x + random.uniform(-8, 8)
        self.y = base_y
        self.vy = random.uniform(-40, -20) * (0.5 + intensity)
        self.alpha = random.randint(150, 255)
        self.size = random.randint(2, 4)
        self.color_idx = random.randint(0, 2)  # 0=yellow, 1=orange, 2=red
        self.alive = True

    def update(self, dt):
        self.y += self.vy * dt
        self.vy -= 10 * dt  # decelerate upward
        self.x += random.uniform(-1, 1)  # sway
        self.alpha -= 200 * dt
        if self.alpha <= 0:
            self.alive = False


class AnimatedXPBar:
    """Brazier with sacred fire — XP bar.

    Brazier base spans full width. Fire particles rise from the fill edge.
    Fire intensity = XP progress. Level badge sits above the brazier.
    """

    # Brazier dimensions
    BRAZIER_H = 14
    FIRE_COLORS = [
        (255, 220, 80),   # yellow core
        (255, 150, 40),   # orange mid
        (220, 80, 20),    # red outer
    ]

    def __init__(self):
        self.display_progress = 0.0
        self.target_progress = 0.0
        self._particles = []
        self._spawn_accum = 0.0

    def update(self, dt, xp, xp_to_next):
        self.target_progress = xp / max(1, xp_to_next)
        self.display_progress = lerp(self.display_progress, self.target_progress, 8.0 * dt)

        # Spawn fire particles from fill edge
        intensity = self.display_progress
        if intensity > 0.01:
            spawn_rate = 15.0 + 35.0 * intensity  # particles per second
            self._spawn_accum += spawn_rate * dt
            while self._spawn_accum >= 1.0:
                self._spawn_accum -= 1.0
                fill_x = int(WIDTH * self.display_progress)
                self._particles.append(BrazierParticle(
                    random.randint(0, max(1, fill_x)),
                    0,  # y offset set in draw
                    intensity
                ))

        # Update particles
        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if p.alive]
        if len(self._particles) > 100:
            self._particles = self._particles[-100:]

    def draw(self, surface, font):
        bar_y = 0
        bar_h = self.BRAZIER_H

        # === Brazier body (dark metal) ===
        # Outer rim
        pygame.draw.rect(surface, (50, 40, 30), (0, bar_y, WIDTH, bar_h))
        # Inner groove
        pygame.draw.rect(surface, (35, 25, 18), (0, bar_y + 2, WIDTH, bar_h - 4))

        # === Fill: glowing ember bed ===
        fill_w = int(WIDTH * self.display_progress)
        if fill_w > 0:
            # Base ember color (dark red-orange gradient)
            for col_x in range(fill_w):
                frac = col_x / max(1, WIDTH)
                r = int(180 + 75 * frac)
                g = int(60 + 90 * frac)
                b = int(10 + 30 * frac)
                pygame.draw.line(surface, (r, g, b), (col_x, bar_y + 3), (col_x, bar_y + bar_h - 4))

            # Glowing edge at fill point
            edge_glow_w = 8
            for gx in range(max(0, fill_w - edge_glow_w), fill_w):
                edge_frac = (gx - (fill_w - edge_glow_w)) / max(1, edge_glow_w)
                ga = int(180 * (1.0 - edge_frac))
                glow_surf = pygame.Surface((1, bar_h), pygame.SRCALPHA)
                glow_surf.fill((255, 180, 60, ga))
                surface.blit(glow_surf, (gx, bar_y))

            # Top flame strip (bright edge above fill)
            t = pygame.time.get_ticks() / 1000.0
            for fx in range(0, fill_w, 3):
                flicker = math.sin(t * 8.0 + fx * 0.15) * 2.0
                fh = max(1, int(4 * self.display_progress + flicker))
                flame_r = 255
                flame_g = int(180 + 40 * math.sin(t * 6.0 + fx * 0.1))
                pygame.draw.line(surface, (flame_r, max(0, min(255, flame_g)), 40),
                                 (fx, bar_y - fh), (fx, bar_y))

        # === Rising fire particles ===
        for p in self._particles:
            da = max(0, min(255, int(p.alpha)))
            fc = self.FIRE_COLORS[p.color_idx]
            if da > 0 and p.size > 0:
                ps = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(ps, (*fc, da), (p.size, p.size), p.size)
                surface.blit(ps, (int(p.x) - p.size, int(bar_y + p.y) - p.size))

        # === Rim highlights ===
        # Top bright edge
        pygame.draw.line(surface, (100, 80, 60), (0, bar_y), (WIDTH, bar_y))
        # Bottom shadow
        pygame.draw.line(surface, (20, 15, 10), (0, bar_y + bar_h - 1), (WIDTH, bar_y + bar_h - 1))

        # === Ornamental brackets every 25% ===
        for pct in [0.25, 0.50, 0.75]:
            bx = int(WIDTH * pct)
            pygame.draw.line(surface, (120, 100, 70), (bx, bar_y), (bx, bar_y + bar_h), 1)

        # Level badge on top-left (below XP bar)
        # We'll draw level separately in draw_hud


class Toast:
    """Notification toast."""
    ENTERING = 0
    VISIBLE = 1
    EXITING = 2

    def __init__(self, text, color, duration=2.0):
        self.text = text
        self.color = color
        self.state = self.ENTERING
        self.timer = 0.0
        self.duration = duration
        self.x_offset = 200
        self.alpha = 0

    def update(self, dt):
        self.timer += dt
        if self.state == self.ENTERING:
            self.x_offset = lerp(self.x_offset, 0, 8.0 * dt)
            self.alpha = min(255, self.alpha + 500 * dt)
            if self.x_offset < 5:
                self.state = self.VISIBLE
        elif self.state == self.VISIBLE:
            if self.timer > self.duration:
                self.state = self.EXITING
        elif self.state == self.EXITING:
            self.x_offset = lerp(self.x_offset, 200, 6.0 * dt)
            self.alpha = max(0, self.alpha - 400 * dt)

    @property
    def alive(self):
        return self.alpha > 0 or self.state != self.EXITING


class ToastManager:
    """Manages toast notifications."""
    MAX_VISIBLE = 3

    def __init__(self):
        self.toasts = []

    def spawn(self, text, color, duration=2.0):
        self.toasts.append(Toast(text, color, duration))
        if len(self.toasts) > self.MAX_VISIBLE:
            self.toasts[0].state = Toast.EXITING

    def update(self, dt):
        for t in self.toasts:
            t.update(dt)
        self.toasts = [t for t in self.toasts if t.alive]

    def draw(self, surface, font):
        y = HEIGHT - 80
        for t in reversed(self.toasts):
            text_surf = font.render(t.text, True, PARCH_INK)
            text_surf.set_alpha(int(t.alpha))
            tw, th = text_surf.get_size()
            bw, bh = tw + 24, th + 14
            x = WIDTH - tw - HUD_PADDING + int(t.x_offset)
            bg_x, bg_y = x - 12, y - 7
            # B4: Parchment background with torn edges
            parch = generate_parchment(bw, bh, seed=hash(t.text) & 0xFFFF)
            parch.set_alpha(int(t.alpha * 0.85))
            surface.blit(parch, (bg_x, bg_y))
            # Ink text on parchment
            surface.blit(text_surf, (x, y))
            y -= 34


# ============================================================
# REF-9: Achievement Toast — gold-bordered notification
# ============================================================
ACH_TOAST_GOLD = (220, 190, 60)
ACH_TOAST_GOLD_DIM = (160, 140, 40)
ACH_TOAST_BG = (18, 14, 35)
ACH_TOAST_W = 280
ACH_TOAST_H = 52


class AchievementToast:
    """Achievement notification: slide from right, gold border, icon, 3s hold, fade out."""
    ENTERING = 0
    VISIBLE = 1
    EXITING = 2

    def __init__(self, text, subtitle="", duration=3.0):
        self.text = text
        self.subtitle = subtitle
        self.state = self.ENTERING
        self.timer = 0.0
        self.duration = duration
        self.x_offset = 350
        self.alpha = 0

    def update(self, dt):
        self.timer += dt
        if self.state == self.ENTERING:
            self.x_offset = lerp(self.x_offset, 0, 5.0 * dt)
            self.alpha = min(255, self.alpha + 600 * dt)
            if self.x_offset < 3:
                self.x_offset = 0
                self.alpha = 255
                self.state = self.VISIBLE
        elif self.state == self.VISIBLE:
            if self.timer > self.duration:
                self.state = self.EXITING
        elif self.state == self.EXITING:
            self.x_offset = lerp(self.x_offset, 350, 4.0 * dt)
            self.alpha = max(0, self.alpha - 300 * dt)

    @property
    def alive(self):
        return self.alpha > 0 or self.state != self.EXITING

    def draw(self, surface, font, small_font, x_base, y_base):
        """Draw the achievement toast at (x_base + x_offset, y_base)."""
        a = int(self.alpha)
        if a <= 0:
            return
        tx = x_base + int(self.x_offset)
        ty = y_base

        # Dark background
        bg = pygame.Surface((ACH_TOAST_W, ACH_TOAST_H), pygame.SRCALPHA)
        bg.fill((ACH_TOAST_BG[0], ACH_TOAST_BG[1], ACH_TOAST_BG[2], int(220 * a / 255)))
        surface.blit(bg, (tx, ty))

        # Gold border
        border = pygame.Surface((ACH_TOAST_W, ACH_TOAST_H), pygame.SRCALPHA)
        border.set_alpha(a)
        pygame.draw.rect(border, ACH_TOAST_GOLD, (0, 0, ACH_TOAST_W, ACH_TOAST_H), 2, border_radius=6)
        surface.blit(border, (tx, ty))

        # Left gold accent strip
        strip = pygame.Surface((4, ACH_TOAST_H - 4), pygame.SRCALPHA)
        strip.fill((ACH_TOAST_GOLD[0], ACH_TOAST_GOLD[1], ACH_TOAST_GOLD[2], a))
        surface.blit(strip, (tx + 2, ty + 2))

        # Achievement star icon (drawn as a small diamond/star shape)
        icon_x, icon_y = tx + 16, ty + ACH_TOAST_H // 2
        star_pts = [
            (icon_x, icon_y - 8), (icon_x + 3, icon_y - 3),
            (icon_x + 8, icon_y - 2), (icon_x + 4, icon_y + 2),
            (icon_x + 6, icon_y + 8), (icon_x, icon_y + 4),
            (icon_x - 6, icon_y + 8), (icon_x - 4, icon_y + 2),
            (icon_x - 8, icon_y - 2), (icon_x - 3, icon_y - 3),
        ]
        star_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(star_surf, (255, 215, 0, a), [(p[0] - icon_x + 10, p[1] - icon_y + 10) for p in star_pts])
        surface.blit(star_surf, (icon_x - 10, icon_y - 10))

        # "ДОСТИЖЕНИЕ" label
        text_x = tx + 32
        label_s = small_font.render("ДОСТИЖЕНИЕ", True, ACH_TOAST_GOLD_DIM)
        label_s.set_alpha(a)
        surface.blit(label_s, (text_x, ty + 6))

        # Main title
        title_s = font.render(self.text, True, (240, 235, 220))
        title_s.set_alpha(a)
        surface.blit(title_s, (text_x, ty + 20))

        # Subtitle (unlock reward)
        if self.subtitle:
            desc_s = small_font.render(self.subtitle, True, (160, 150, 130))
            desc_s.set_alpha(a)
            surface.blit(desc_s, (text_x, ty + 36))


class AchievementToastManager:
    """Queue-based achievement toast display. One at a time, next queued."""
    def __init__(self):
        self._queue = []
        self._active = None

    def enqueue(self, text, subtitle="", duration=3.0):
        self._queue.append(AchievementToast(text, subtitle, duration))

    def update(self, dt):
        if self._active is not None:
            self._active.update(dt)
            if not self._active.alive:
                self._active = None
        if self._active is None and self._queue:
            self._active = self._queue.pop(0)

    def draw(self, surface, font, small_font):
        if self._active is None:
            return
        x_base = WIDTH - ACH_TOAST_W - HUD_PADDING
        y_base = HEIGHT - ACH_TOAST_H - 90  # above regular toasts
        self._active.draw(surface, font, small_font, x_base, y_base)

    @property
    def has_active(self):
        return self._active is not None or len(self._queue) > 0


# ============================================================
# A5: Boss HP Bar — Dark Souls style with death rattle
# ============================================================
class AnimatedBossHealthBar:
    """Boss health bar at top-center with trailing grey bar, cyan flash, death rattle.

    Features:
    - Delayed grey bar (0.7s lag behind actual HP)
    - Cyan flash on armor hits
    - Segmented death rattle at <25% HP (5 segments with random Y offset)
    - Shake effect at <25% HP
    - Boss name label above bar
    """

    BOSS_BAR_WIDTH = 400
    BOSS_BAR_HEIGHT = 22
    SEGMENTS = 5
    RATTLE_THRESHOLD = 0.25
    FLASH_DURATION = 0.3
    SHAKE_INTENSITY = 3
    TRAIL_DELAY = 0.7  # seconds before grey bar starts following

    def __init__(self):
        self.display_hp = 0.0
        self.delayed_hp = 0.0
        self.max_hp = 1
        self.flash_timer = 0.0
        self.flash_color = None
        self.trail_timer = 0.0
        self.active = False
        self.boss_name = ""
        self.boss_type_id = ""
        # Death rattle segment offsets (randomized once per boss encounter)
        self._rattle_offsets = [0.0] * self.SEGMENTS
        self._rattle_seed = 0
        self._rattle_frame_counter = 0

    def activate(self, boss_name: str, boss_type_id: str, current_hp: float, max_hp: float):
        """Start tracking a boss encounter."""
        if boss_type_id != self.boss_type_id:
            # New boss — reset everything
            self.boss_type_id = boss_type_id
            self.boss_name = boss_name
            self.display_hp = current_hp
            self.delayed_hp = current_hp
            self.max_hp = max(1, max_hp)
            self.flash_timer = 0.0
            self.flash_color = None
            self.trail_timer = 0.0
            self._rattle_seed = random.randint(0, 9999)
            self._generate_rattle_offsets()
        self.active = True

    def deactivate(self):
        """Boss encounter ended."""
        self.active = False
        self.boss_type_id = ""

    def trigger_flash(self, color=(0, 255, 255)):
        """Trigger cyan flash (armor hit)."""
        self.flash_color = color
        self.flash_timer = self.FLASH_DURATION

    def _generate_rattle_offsets(self):
        """Generate random Y offsets for death rattle segments."""
        intensity = self.SHAKE_INTENSITY
        self._rattle_offsets = [random.uniform(-intensity, intensity) for _ in range(self.SEGMENTS)]

    def update(self, dt, current_hp, max_hp):
        """Update bar state."""
        if not self.active:
            return

        self.display_hp = current_hp
        self.max_hp = max(1, max_hp)

        # Delayed grey bar — starts moving after TRAIL_DELAY
        if self.delayed_hp > self.display_hp:
            self.trail_timer += dt
            if self.trail_timer >= self.TRAIL_DELAY:
                self.delayed_hp = lerp(self.delayed_hp, self.display_hp, 4.0 * dt)
        else:
            self.delayed_hp = self.display_hp
            self.trail_timer = 0.0

        # Flash decay
        if self.flash_timer > 0:
            self.flash_timer = max(0, self.flash_timer - dt)

        # Re-randomize rattle offsets periodically at <25%
        hp_ratio = self.display_hp / self.max_hp
        if hp_ratio < self.RATTLE_THRESHOLD and hp_ratio > 0:
            self._rattle_frame_counter += 1
            if self._rattle_frame_counter % 10 == 0:  # every 10 frames
                self._generate_rattle_offsets()

    def draw(self, surface, font, small_font):
        """Draw boss HP bar at top-center of screen."""
        if not self.active or self.max_hp <= 0:
            return

        bar_w = self.BOSS_BAR_WIDTH
        bar_h = self.BOSS_BAR_HEIGHT
        bar_x = (WIDTH - bar_w) // 2
        bar_y = 20

        hp_ratio = max(0.0, min(1.0, self.display_hp / self.max_hp))
        delayed_ratio = max(0.0, min(1.0, self.delayed_hp / self.max_hp))

        # Check if in death rattle mode
        in_rattle = hp_ratio < self.RATTLE_THRESHOLD and hp_ratio > 0

        if in_rattle:
            self._draw_rattle(surface, bar_x, bar_y, bar_w, bar_h, hp_ratio, delayed_ratio)
        else:
            self._draw_normal(surface, bar_x, bar_y, bar_w, bar_h, hp_ratio, delayed_ratio)

        # Flash overlay (cyan armor hit)
        if self.flash_timer > 0 and self.flash_color:
            progress = self.flash_timer / self.FLASH_DURATION
            alpha = int(120 * progress)
            flash_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
            r, g, b = self.flash_color
            flash_surf.fill((r, g, b, alpha))
            surface.blit(flash_surf, (bar_x, bar_y))

        # Border
        pygame.draw.rect(surface, (180, 160, 120), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=3)

        # Boss name above bar
        name_surf = font.render(self.boss_name, True, (220, 50, 50))
        surface.blit(name_surf, (bar_x + bar_w // 2 - name_surf.get_width() // 2, bar_y - 20))

        # HP text inside bar
        hp_text = small_font.render(f"{int(self.display_hp)} / {self.max_hp}", True, TEXT_PRIMARY)
        text_x = bar_x + bar_w // 2 - hp_text.get_width() // 2
        text_y = bar_y + bar_h // 2 - hp_text.get_height() // 2
        surface.blit(hp_text, (text_x, text_y))

    def _draw_normal(self, surface, x, y, w, h, hp_ratio, delayed_ratio):
        """Draw normal (non-rattle) boss bar."""
        # Background
        pygame.draw.rect(surface, (40, 15, 15), (x, y, w, h), border_radius=3)

        # Grey trailing bar (delayed damage)
        delayed_w = int(w * delayed_ratio)
        if delayed_w > 0:
            pygame.draw.rect(surface, (100, 90, 80), (x, y, delayed_w, h), border_radius=3)

        # Main HP bar — crimson red gradient
        fill_w = int(w * hp_ratio)
        if fill_w > 0:
            # Base color: dark red
            pygame.draw.rect(surface, (180, 30, 30), (x, y, fill_w, h), border_radius=3)
            # Bright top edge
            pygame.draw.rect(surface, (220, 60, 60), (x, y, fill_w, 4))
            # Bottom shadow
            pygame.draw.rect(surface, (120, 15, 15), (x, y + h - 4, fill_w, 4))

        # Pulsing glow at low HP
        if hp_ratio < 0.3 and hp_ratio > 0:
            t = pygame.time.get_ticks() / 1000.0
            pulse = (math.sin(t * 4.0) + 1.0) / 2.0
            pulse_alpha = int(60 * pulse)
            pulse_surf = pygame.Surface((fill_w, h), pygame.SRCALPHA)
            pulse_surf.fill((255, 50, 50, pulse_alpha))
            surface.blit(pulse_surf, (x, y))

    def _draw_rattle(self, surface, x, y, w, h, hp_ratio, delayed_ratio):
        """Draw death rattle — 5 segments with random Y offsets, shaking."""
        seg_w = w // self.SEGMENTS
        t = pygame.time.get_ticks() / 1000.0

        # Background
        pygame.draw.rect(surface, (40, 15, 15), (x, y, w, h), border_radius=3)

        for i in range(self.SEGMENTS):
            sx = x + i * seg_w
            sw = seg_w - 1  # gap between segments

            # Random Y offset for death rattle
            offset_y = self._rattle_offsets[i]

            # Shake — adds sinusoidal wobble
            shake_y = math.sin(t * 12.0 + i * 1.7) * 2.0
            final_y = int(y + offset_y + shake_y)

            # Grey trailing bar segment
            delayed_start = i / self.SEGMENTS
            delayed_end = (i + 1) / self.SEGMENTS
            if delayed_ratio > delayed_start:
                seg_delayed = min(1.0, (delayed_ratio - delayed_start) * self.SEGMENTS)
                dw = int(sw * seg_delayed)
                if dw > 0:
                    pygame.draw.rect(surface, (100, 90, 80), (sx, final_y, dw, h), border_radius=2)

            # Main HP bar segment
            if hp_ratio > delayed_start:
                seg_hp = min(1.0, (hp_ratio - delayed_start) * self.SEGMENTS)
                fw = int(sw * seg_hp)
                if fw > 0:
                    # Pulsing red intensity based on how low HP is
                    intensity = 0.5 + 0.5 * math.sin(t * 8.0 + i * 0.5)
                    r = int(180 + 75 * intensity)
                    g = int(20 + 20 * (1 - intensity))
                    pygame.draw.rect(surface, (r, g, 20), (sx, final_y, fw, h), border_radius=2)

    def draw_edge_glow(self, surface):
        """Draw glowing edge effect around boss bar when active."""
        if not self.active:
            return

        hp_ratio = self.display_hp / self.max_hp
        if hp_ratio >= self.RATTLE_THRESHOLD or hp_ratio <= 0:
            return

        t = pygame.time.get_ticks() / 1000.0
        pulse = (math.sin(t * 3.0) + 1.0) / 2.0
        alpha = int(40 + 30 * pulse)

        bar_w = self.BOSS_BAR_WIDTH
        bar_h = self.BOSS_BAR_HEIGHT
        bar_x = (WIDTH - bar_w) // 2
        bar_y = 20

        # Red glow border
        glow_surf = pygame.Surface((bar_w + 8, bar_h + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 30, 30, alpha), (0, 0, bar_w + 8, bar_h + 8),
                         3, border_radius=5)
        surface.blit(glow_surf, (bar_x - 4, bar_y - 4))


# Singleton instances
_boss_bar = AnimatedBossHealthBar()


def boss_bar_activate(boss_name, boss_type_id, current_hp, max_hp):
    """Public API: activate boss HP bar tracking."""
    _boss_bar.activate(boss_name, boss_type_id, current_hp, max_hp)


def boss_bar_trigger_flash(color=(0, 255, 255)):
    """Public API: trigger cyan armor hit flash."""
    _boss_bar.trigger_flash(color)


def boss_bar_deactivate():
    """Public API: deactivate boss HP bar."""
    _boss_bar.deactivate()


# Singleton instances
_hp_bar = AnimatedHealthBar()
_xp_bar = AnimatedXPBar()
_toast_mgr = ToastManager()


def spawn_toast(text, color=TEXT_PRIMARY, duration=2.0):
    """Public API to spawn a toast notification."""
    _toast_mgr.spawn(text, color, duration)

_ach_toast_mgr = AchievementToastManager()

def spawn_achievement_toast(text, subtitle="", duration=3.0):
    """Public API to spawn an achievement toast notification."""
    _ach_toast_mgr.enqueue(text, subtitle, duration)

# ============================================================
# A4: Combo System — escalating juice per tier
# ============================================================
# (threshold, label, text_scale_pulse, edge_color, slowmo_frames)
COMBO_TIERS = [
    (5,   None,       1.3,  None,              0),
    (15,  None,       1.5,  (255, 100, 50),    0),
    (30,  None,       1.8,  (255, 50, 50),     4),
    (50,  "CARNAGE",  2.0,  (200, 0, 0),       6),
    (100, "MASSACRE", 2.5,  (255, 255, 255),   8),
]


class ComboSystem:
    """Escalating combo counter with tiered visual juice.

    Tiers: 5=text pulse, 15=edge flash, 30=slowmo, 50=CARNAGE, 100=MASSACRE.
    Elastic tween on number change. Top-center display.
    """

    def __init__(self):
        self.count = 0
        self.display_count = 0.0
        self.timer = 0.0
        self.timeout = 3.0
        self.tier = -1
        self.scale_pulse = 1.0
        self.edge_flash_timer = 0.0
        self.edge_flash_color = None
        self.edge_flash_duration = 0.6
        self._velocity = 0.0
        self._last_tier_label = None

    def register_kill(self):
        """Register a kill. Returns juice dict: {'slowmo': N, 'label': str}."""
        self.count += 1
        self.timer = self.timeout

        new_tier = -1
        for i, (threshold, _, _, _, _) in enumerate(COMBO_TIERS):
            if self.count >= threshold:
                new_tier = i

        juice = {"slowmo": 0}

        if new_tier > self.tier:
            _, label, scale, edge_color, slowmo = COMBO_TIERS[new_tier]
            self.scale_pulse = max(self.scale_pulse, scale)
            if edge_color:
                self.edge_flash_color = edge_color
                self.edge_flash_timer = self.edge_flash_duration
            juice["slowmo"] = slowmo
            if label and label != self._last_tier_label:
                self._last_tier_label = label
                juice["label"] = label
            self.tier = new_tier

        return juice

    def update(self, dt):
        """Update timer, elastic tween, and flash decay."""
        if self.timer > 0:
            self.timer -= dt

            # Elastic spring tween
            diff = float(self.count) - self.display_count
            spring_force = diff * 18.0
            self._velocity += spring_force * dt
            self._velocity *= max(0, 1.0 - 8.0 * dt)
            self.display_count += self._velocity * dt

            # Scale pulse decay toward 1.0
            if self.scale_pulse > 1.01:
                self.scale_pulse = max(1.0, self.scale_pulse - 4.0 * dt)

            # Edge flash decay
            if self.edge_flash_timer > 0:
                self.edge_flash_timer = max(0, self.edge_flash_timer - dt)
        else:
            self.count = 0
            self.display_count = 0.0
            self.tier = -1
            self.scale_pulse = 1.0
            self.edge_flash_timer = 0.0
            self.edge_flash_color = None
            self._velocity = 0.0
            self._last_tier_label = None

    @property
    def active(self):
        return self.count >= 3 and self.timer > 0

    def draw(self, surface, font):
        """Draw combo counter at top-center with elastic tween."""
        if not self.active:
            return

        # Tier-based color
        if self.tier >= 4:
            color = (255, 255, 255)
        elif self.tier >= 3:
            color = (255, 50, 50)
        elif self.tier >= 2:
            color = (255, 100, 50)
        elif self.tier >= 1:
            color = (255, 150, 50)
        else:
            color = (255, 200, 50)

        display_num = max(1, int(round(self.display_count)))
        combo_str = f"x{display_num}!"

        rendered = font.render(combo_str, True, color)

        # Apply scale pulse
        if self.scale_pulse > 1.01:
            sw = max(1, int(rendered.get_width() * self.scale_pulse))
            sh = max(1, int(rendered.get_height() * self.scale_pulse))
            rendered = pygame.transform.smoothscale(rendered, (sw, sh))

        # Pulsing alpha
        t = pygame.time.get_ticks() / 1000.0
        pulse_a = int(200 + 55 * math.sin(t * 8.0))
        rendered.set_alpha(pulse_a)

        cx = WIDTH // 2
        x = cx - rendered.get_width() // 2
        y = 48

        # Glow behind text (tier >= 1)
        if self.tier >= 1:
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                glow = rendered.copy()
                glow.fill((*color, 30), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(glow, (x + dx, y + dy))

        surface.blit(rendered, (x, y))

        # Tier label below (CARNAGE / MASSACRE)
        if self.tier >= 0:
            _, label, _, _, _ = COMBO_TIERS[self.tier]
            if label:
                lbl = font.render(label, True, color)
                lbl_a = int(180 + 75 * math.sin(t * 6.0))
                lbl.set_alpha(lbl_a)
                lx = cx - lbl.get_width() // 2
                ly = y + rendered.get_height() + 4
                surface.blit(lbl, (lx, ly))

    def draw_edge_flash(self, surface):
        """Draw colored edge flash overlay (call after all rendering)."""
        if self.edge_flash_timer <= 0 or not self.edge_flash_color:
            return

        progress = self.edge_flash_timer / self.edge_flash_duration
        base_alpha = int(100 * progress * progress)
        if base_alpha <= 0:
            return

        r, g, b = self.edge_flash_color

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # 3 gradient bands: outermost strongest
        for band_idx, (alpha_mult, thickness) in enumerate(
            [(1.0, 20), (0.6, 12), (0.3, 6)]
        ):
            a = int(base_alpha * alpha_mult)
            if a <= 0:
                continue
            # Top
            overlay.fill((r, g, b, a), (0, band_idx * 5, WIDTH, thickness))
            # Bottom
            overlay.fill((r, g, b, a), (0, HEIGHT - band_idx * 5 - thickness, WIDTH, thickness))
            # Left
            overlay.fill((r, g, b, a), (band_idx * 5, 0, thickness, HEIGHT))
            # Right
            overlay.fill((r, g, b, a), (WIDTH - band_idx * 5 - thickness, 0, thickness, HEIGHT))

        surface.blit(overlay, (0, 0))


# Singleton
_combo = ComboSystem()


def combo_register_kill():
    """Public API: register a kill with the combo system."""
    return _combo.register_kill()


def combo_edge_flash(surface):
    """Public API: draw edge flash overlay."""
    _combo.draw_edge_flash(surface)


def _find_and_track_boss(enemies):
    """Find the nearest alive boss and update boss bar tracking."""
    from enemies import ENEMY_TYPES

    # Find nearest alive boss
    best_boss = None
    best_dist_sq = float('inf')

    for e in enemies:
        if not getattr(e, 'alive', False) or not getattr(e, 'is_boss', False):
            continue
        # Distance from center of screen (approx player position)
        dx = e.pos.x - WIDTH // 2
        dy = e.pos.y - HEIGHT // 2
        dist_sq = dx * dx + dy * dy
        if dist_sq < best_dist_sq:
            best_dist_sq = dist_sq
            best_boss = e

    if best_boss:
        boss_name = ENEMY_TYPES.get(best_boss.type_id, {}).get("name", best_boss.type_id)
        _boss_bar.activate(boss_name, best_boss.type_id, best_boss.hp, best_boss.max_hp)
    else:
        _boss_bar.deactivate()


def draw_hud(surface: pygame.Surface, player, wave: int, elapsed: float,
             font, small_font, enemies=None):
    """Рисует весь HUD поверх игры."""

    dt = 0.016  # approximate dt

    # === A5: Boss HP bar tracking ===
    if enemies:
        _find_and_track_boss(enemies)

    # === Update animated bars ===
    _hp_bar.update(dt, player.hp, player.max_hp)
    _xp_bar.update(dt, player.xp, player.xp_to_next)
    _toast_mgr.update(dt)
    _ach_toast_mgr.update(dt)

    # === A5: Update boss bar ===
    if _boss_bar.active:
        _boss_bar.update(dt, _boss_bar.display_hp, _boss_bar.max_hp)

    # === Boss HP Bar (top-center, overrides XP bar position) ===
    if _boss_bar.active:
        _boss_bar.draw(surface, font, small_font)
        _boss_bar.draw_edge_glow(surface)

    # === XP Bar (full-width top brazier, offset if boss bar active) ===
    _xp_bar.draw(surface, font)
    # Level badge on top-left (below brazier)
    level_text = font.render(f"Lv {player.level}", True, GOLD_LEAF)
    surface.blit(level_text, (HUD_PADDING, 18))

    # === HP Candle (top-left, below level) ===
    hp_x = HUD_PADDING
    hp_y = 38
    hp_w = 180
    hp_h = 18
    _hp_bar.draw(surface, hp_x, hp_y, hp_w, hp_h, player.max_hp, small_font)

    # === Kills + Gold (top-left, below candle — candle extends ~70px) ===
    kills_text = small_font.render(f"Kills: {player.kills}", True, TEXT_PRIMARY)
    surface.blit(kills_text, (HUD_PADDING, hp_y + hp_h + 50))
    gold_text = small_font.render(f"Gold: {player.gold}", True, GOLD_LEAF)
    surface.blit(gold_text, (HUD_PADDING, hp_y + hp_h + 64))

    # === Timer + Wave (top-right) ===
    mins = int(elapsed) // 60
    secs = int(elapsed) % 60
    timer_text = font.render(f"{mins:02d}:{secs:02d}", True, TEXT_PRIMARY)
    surface.blit(timer_text, (WIDTH - timer_text.get_width() - HUD_PADDING, 12))

    wave_text = small_font.render(f"Wave {wave}", True, TEXT_PRIMARY)
    surface.blit(wave_text, (WIDTH - wave_text.get_width() - HUD_PADDING, 32))

    # === Weapon Slots (bottom-left) ===
    slot_size = 32
    slot_gap = 4
    weapon_x = HUD_PADDING
    weapon_y = HEIGHT - slot_size - HUD_PADDING
    max_slots = 6

    # Rarity colors (из ui_theme)
    rarity_colors = RARITY_COLORS

    for i in range(max_slots):
        x = weapon_x + i * (slot_size + slot_gap)
        rect = pygame.Rect(x, weapon_y, slot_size, slot_size)

        # Background
        pygame.draw.rect(surface, (25, 20, 35), rect, border_radius=4)

        if i < len(player.weapons):
            w = player.weapons[i]
            # Rarity border
            rarity = getattr(w, 'rarity', 'common')
            border_color = rarity_colors.get(rarity, (120, 120, 120))
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=4)

            # Weapon color icon
            color = WEAPON_DEFS.get(w.weapon_id, {}).get("color", TEXT_PRIMARY)
            icon_rect = pygame.Rect(x + 6, weapon_y + 6, slot_size - 12, slot_size - 12)
            pygame.draw.rect(surface, color, icon_rect, border_radius=2)

            # Level badge
            if w.level > 1:
                lvl_text = small_font.render(f"+{w.level}", True, GOLD_LEAF)
                surface.blit(lvl_text, (x + slot_size - lvl_text.get_width() - 2, weapon_y + slot_size - 12))

            # Cooldown overlay
            if hasattr(w, 'cooldown_timer') and w.cooldown_timer > 0:
                cd_pct = w.cooldown_timer / max(0.01, w.cooldown)
                cd_h = int(slot_size * cd_pct)
                overlay = pygame.Surface((slot_size, cd_h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                surface.blit(overlay, (x, weapon_y))
        else:
            # Empty slot
            pygame.draw.rect(surface, (60, 50, 80), rect, 1, border_radius=4)

    # === Passive Slots (bottom-right) ===
    passive_x = WIDTH - HUD_PADDING - slot_size
    max_passives = 6
    passive_list = list(player.passives.items())

    for i in range(max_passives):
        x = passive_x - i * (slot_size + slot_gap)
        rect = pygame.Rect(x, weapon_y, slot_size, slot_size)

        # Background
        pygame.draw.rect(surface, (25, 20, 35), rect, border_radius=4)

        if i < len(passive_list):
            pid, lvl = passive_list[i]
            # Border
            color = PASSIVE_DEFS.get(pid, {}).get("color", TEXT_PRIMARY)
            pygame.draw.rect(surface, color, rect, 2, border_radius=4)

            # Icon
            icon_rect = pygame.Rect(x + 8, weapon_y + 8, slot_size - 16, slot_size - 16)
            pygame.draw.rect(surface, color, icon_rect, border_radius=2)

            # Level badge
            if lvl > 1:
                lvl_text = small_font.render(f"+{lvl}", True, GOLD_LEAF)
                surface.blit(lvl_text, (x + slot_size - lvl_text.get_width() - 2, weapon_y + slot_size - 12))
        else:
            # Empty slot
            pygame.draw.rect(surface, (60, 50, 80), rect, 1, border_radius=4)

    # === A4: Combo counter with escalating juice ===
    _combo.update(dt)
    _combo.draw(surface, font)

    # === Toasts ===
    _toast_mgr.draw(surface, small_font)
    _ach_toast_mgr.draw(surface, font, small_font)


def draw_enemy_indicators(surface, player, enemies, cam_x, cam_y):
    """Рисует стрелки-индикаторы на краях экрана для врагов за пределами видимости."""
    if not player or not enemies:
        return
    
    margin = 30  # отступ от края
    arrow_size = 8
    view_rect = pygame.Rect(cam_x - 50, cam_y - 50, WIDTH + 100, HEIGHT + 100)
    
    for e in enemies:
        if not getattr(e, 'alive', True):
            continue
        
        # Позиция врага в экранных координатах
        ex = e.pos.x - cam_x
        ey = e.pos.y - cam_y
        
        # Если враг в пределах экрана — не рисуем индикатор
        if -20 <= ex <= WIDTH + 20 and -20 <= ey <= HEIGHT + 20:
            continue
        
        # Направление от центра экрана к врагу
        cx, cy = WIDTH // 2, HEIGHT // 2
        dx = ex - cx
        dy = ey - cy
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 1:
            continue
        
        # Нормализуем
        nx = dx / dist
        ny = dy / dist
        
        # Позиция стрелки на краю экрана
        # Ограничиваем прямоугольником экрана
        arrow_x = cx + nx * (WIDTH // 2 - margin)
        arrow_y = cy + ny * (HEIGHT // 2 - margin)
        
        # Clamp
        arrow_x = max(margin, min(WIDTH - margin, arrow_x))
        arrow_y = max(margin, min(HEIGHT - margin, arrow_y))
        
        # Рисуем треугольник-стрелку
        import math
        angle = math.atan2(ny, nx)
        p1 = (arrow_x + nx * arrow_size, arrow_y + ny * arrow_size)
        p2 = (arrow_x + math.cos(angle + 2.5) * arrow_size * 0.6,
              arrow_y + math.sin(angle + 2.5) * arrow_size * 0.6)
        p3 = (arrow_x + math.cos(angle - 2.5) * arrow_size * 0.6,
              arrow_y + math.sin(angle - 2.5) * arrow_size * 0.6)
        
        # Цвет: красный для обычных, ярко-красный для боссов
        is_boss = getattr(e, 'is_boss', False) or getattr(e, 'enemy_type', '') in ('antichrist', 'pope')
        color = (255, 80, 80) if is_boss else (200, 60, 60)
        
        pygame.draw.polygon(surface, color, [p1, p2, p3])


def draw_minimap(surface, player, enemies, cam_x, cam_y):
    """Рисует мини-карту в правом нижнем углу."""
    from config import MAP_WIDTH, MAP_HEIGHT

    map_size = 120  # размер мини-карты на экране
    margin = 10
    mx = WIDTH - map_size - margin
    my = HEIGHT - map_size - margin
    scale_x = map_size / MAP_WIDTH
    scale_y = map_size / MAP_HEIGHT

    # Фон
    bg = pygame.Surface((map_size, map_size), pygame.SRCALPHA)
    bg.fill((10, 10, 20, 180))
    surface.blit(bg, (mx, my))

    # Рамка
    pygame.draw.rect(surface, (60, 60, 80), (mx, my, map_size, map_size), 1)

    # Зоны биомов (4 кольца)
    zones = [
        (2000, 2000, 800, (30, 30, 50)),   # Руины
        (2000, 2000, 1400, (20, 20, 40)),   # Кладбище
        (2000, 2000, 2000, (40, 20, 20)),   # Адский лес
    ]
    for cx, cy, radius, color in zones:
        sx = int(cx * scale_x) + mx
        sy = int(cy * scale_y) + my
        sr = max(2, int(radius * scale_x))
        pygame.draw.circle(surface, color, (sx, sy), sr, 1)

    # Враги (красные точки)
    for e in enemies:
        if not getattr(e, 'alive', True):
            continue
        ex = int(e.pos.x * scale_x) + mx
        ey = int(e.pos.y * scale_y) + my
        if mx <= ex <= mx + map_size and my <= ey <= my + map_size:
            is_boss = getattr(e, 'is_boss', False)
            color = (255, 80, 80) if is_boss else (200, 60, 60)
            size = 2 if is_boss else 1
            pygame.draw.circle(surface, color, (ex, ey), size)

    # Игрок (зелёная точка)
    if player and hasattr(player, 'pos'):
        px = int(player.pos.x * scale_x) + mx
        py = int(player.pos.y * scale_y) + my
        px = max(mx + 2, min(mx + map_size - 2, px))
        py = max(my + 2, min(my + map_size - 2, py))
        pygame.draw.circle(surface, (80, 255, 80), (px, py), 3)

    # Обзорная рамка (что видно на экране)
    vx = int(cam_x * scale_x) + mx
    vy = int(cam_y * scale_y) + my
    vw = int(WIDTH * scale_x)
    vh = int(HEIGHT * scale_y)
    pygame.draw.rect(surface, (100, 100, 140), (vx, vy, vw, vh), 1)
