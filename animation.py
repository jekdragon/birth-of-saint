"""
Рождение святого — Animation Engine
Easing functions, tweens, transitions, and animated value helpers.
"""
import math
import pygame
from ui_theme import SCREEN_W, SCREEN_H


# ============================================================
# EASING FUNCTIONS
# ============================================================

def ease_linear(t: float) -> float:
    return t

def ease_in_quad(t: float) -> float:
    return t * t

def ease_out_quad(t: float) -> float:
    return t * (2 - t)

def ease_in_out_quad(t: float) -> float:
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2

def ease_out_cubic(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3

def ease_in_out_cubic(t: float) -> float:
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2

def ease_out_elastic(t: float) -> float:
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1

def ease_out_bounce(t: float) -> float:
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375

def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2

# Default ease for UI
EASE_OUT = ease_out_cubic
EASE_IN_OUT = ease_in_out_cubic


# ============================================================
# TWEEN — animated value
# ============================================================

class Tween:
    """Animates a single value from start to end over duration."""

    __slots__ = ('start', 'end', 'duration', 'elapsed', 'ease', 'value', 'done')

    def __init__(self, start: float, end: float, duration: float, ease=EASE_OUT):
        self.start = start
        self.end = end
        self.duration = max(0.001, duration)
        self.elapsed = 0.0
        self.ease = ease
        self.value = start
        self.done = False

    def update(self, dt: float):
        if self.done:
            return
        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        self.value = self.start + (self.end - self.start) * self.ease(t)
        if t >= 1.0:
            self.done = True
            self.value = self.end

    def reset(self, start=None, end=None, duration=None):
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end
        if duration is not None:
            self.duration = max(0.001, duration)
        self.elapsed = 0.0
        self.value = self.start
        self.done = False

    @property
    def progress(self) -> float:
        return min(1.0, self.elapsed / self.duration)


# ============================================================
# ANIMATED ALPHA
# ============================================================

class AnimatedAlpha:
    """Fade in/out with callback."""

    __slots__ = ('alpha', 'target', 'speed', 'callback', '_fading_out')

    def __init__(self, initial=255):
        self.alpha = initial
        self.target = initial
        self.speed = 5.0
        self.callback = None
        self._fading_out = False

    def fade_in(self, speed=5.0, callback=None):
        self.target = 255
        self.speed = speed
        self.callback = callback
        self._fading_out = False

    def fade_out(self, speed=5.0, callback=None):
        self.target = 0
        self.speed = speed
        self.callback = callback
        self._fading_out = True

    def update(self, dt: float):
        if self.alpha == self.target:
            if self.callback:
                cb = self.callback
                self.callback = None
                cb()
            return
        diff = self.target - self.alpha
        step = self.speed * dt * 255
        if abs(diff) < step:
            self.alpha = self.target
        else:
            self.alpha += step if diff > 0 else -step
        self.alpha = max(0, min(255, int(self.alpha)))


# ============================================================
# STAGGER ANIMATION — sequential element appearance
# ============================================================

class StaggerAnimator:
    """Animates a list of elements appearing one by one."""

    __slots__ = ('elements', 'delay', 'elapsed', 'duration', 'ease')

    def __init__(self, count: int, delay: float = 0.08, duration: float = 0.3, ease=EASE_OUT):
        self.elements = [{'alpha': 0.0, 'offset_y': 20.0, 'scale': 0.9} for _ in range(count)]
        self.delay = delay
        self.elapsed = 0.0
        self.duration = duration
        self.ease = ease

    def update(self, dt: float):
        self.elapsed += dt
        for i, elem in enumerate(self.elements):
            start_time = i * self.delay
            if self.elapsed < start_time:
                continue
            t = min(1.0, (self.elapsed - start_time) / self.duration)
            e = self.ease(t)
            elem['alpha'] = e
            elem['offset_y'] = 20.0 * (1.0 - e)
            elem['scale'] = 0.9 + 0.1 * e

    def reset(self):
        self.elapsed = 0.0
        for elem in self.elements:
            elem['alpha'] = 0.0
            elem['offset_y'] = 20.0
            elem['scale'] = 0.9

    def get(self, index: int) -> dict:
        if 0 <= index < len(self.elements):
            return self.elements[index]
        return {'alpha': 1.0, 'offset_y': 0.0, 'scale': 1.0}

    @property
    def all_visible(self) -> bool:
        return all(e['alpha'] >= 1.0 for e in self.elements)


# ============================================================
# SCALE PUNCH — hover/select feedback
# ============================================================

class ScalePunch:
    """Quick scale-up then return to 1.0 (punch effect)."""

    __slots__ = ('scale', 'target', 'punch_amount', 'speed')

    def __init__(self):
        self.scale = 1.0
        self.target = 1.0
        self.punch_amount = 1.15
        self.speed = 8.0

    def punch(self, amount=1.15):
        self.scale = amount
        self.punch_amount = amount

    def update(self, dt: float):
        if self.scale > 1.001:
            self.scale += (1.0 - self.scale) * self.speed * dt
            if self.scale < 1.001:
                self.scale = 1.0


# ============================================================
# HEARTBEAT PULSE — lub-dub waveform
# ============================================================

def heartbeat_value(time: float, period: float = 2.0) -> float:
    """
    Returns 0.0-1.0 heartbeat waveform.
    Lub at t=0.0 (peak 1.0), dub at t=0.5 (peak 0.6), rest at 0.0.
    """
    t_norm = (time % period) / period
    if t_norm < 0.1:
        return math.sin(t_norm / 0.1 * math.pi)
    elif t_norm < 0.2:
        return math.sin((t_norm - 0.1) / 0.1 * math.pi) * 0.6
    return 0.0


# ============================================================
# TRANSITION ENGINE — scene transitions
# ============================================================

class TransitionType:
    FADE = 'fade'
    SLIDE_LEFT = 'slide_left'
    SLIDE_RIGHT = 'slide_right'
    SLIDE_UP = 'slide_up'
    SLIDE_DOWN = 'slide_down'
    CROSSFADE = 'crossfade'
    FADE_TO_RED = 'fade_to_red'
    ZOOM_IN = 'zoom_in'


class Transition:
    """Scene transition animation."""

    __slots__ = ('type', 'duration', 'elapsed', 'phase', 'alpha', 'offset',
                 'callback', 'active', 'color', 'surfaces')

    def __init__(self):
        self.type = TransitionType.FADE
        self.duration = 0.3
        self.elapsed = 0.0
        self.phase = 'none'  # 'out', 'in', 'none'
        self.alpha = 0
        self.offset = 0
        self.callback = None
        self.active = False
        self.color = (0, 0, 0)
        self.surfaces = {}  # for crossfade

    def start(self, trans_type: str, duration: float = 0.3,
              color=(0, 0, 0), callback=None):
        self.type = trans_type
        self.duration = max(0.001, duration)
        self.elapsed = 0.0
        self.phase = 'out'
        self.alpha = 0
        self.offset = 0
        self.callback = callback
        self.active = True
        self.color = color

    def update(self, dt: float):
        if not self.active:
            return
        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        e = EASE_OUT(t)

        if self.phase == 'out':
            self.alpha = int(255 * e)
            self.offset = int(SCREEN_W * e)
            if t >= 1.0:
                self.phase = 'in'
                self.elapsed = 0.0
                if self.callback:
                    cb = self.callback
                    self.callback = None
                    cb()
        elif self.phase == 'in':
            self.alpha = int(255 * (1.0 - e))
            self.offset = int(SCREEN_W * (1.0 - e))
            if t >= 1.0:
                self.active = False
                self.phase = 'none'

    def draw(self, screen: pygame.Surface):
        if not self.active:
            return

        if self.type == TransitionType.FADE:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((*self.color, self.alpha))
            screen.blit(overlay, (0, 0))

        elif self.type == TransitionType.FADE_TO_RED:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            # Red tint that intensifies
            r = min(255, 40 + self.alpha // 3)
            overlay.fill((r, 10, 10, self.alpha))
            screen.blit(overlay, (0, 0))

        elif self.type == TransitionType.SLIDE_LEFT:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((*self.color, min(200, self.alpha)))
            screen.blit(overlay, (0, 0))

        elif self.type == TransitionType.CROSSFADE:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((*self.color, self.alpha))
            screen.blit(overlay, (0, 0))

    @property
    def is_out_phase(self) -> bool:
        return self.active and self.phase == 'out'

    @property
    def is_in_phase(self) -> bool:
        return self.active and self.phase == 'in'


# ============================================================
# PARALLAX — mouse-driven background offset
# ============================================================

class Parallax:
    """Smooth parallax offset based on mouse position."""

    __slots__ = ('offset_x', 'offset_y', 'max_offset', 'lerp_speed')

    def __init__(self, max_offset: float = 20.0, lerp_speed: float = 5.0):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.max_offset = max_offset
        self.lerp_speed = lerp_speed

    def update(self, dt: float, mouse_pos: tuple):
        mx, my = mouse_pos
        target_x = (mx - SCREEN_W / 2) / (SCREEN_W / 2) * self.max_offset
        target_y = (my - SCREEN_H / 2) / (SCREEN_H / 2) * self.max_offset
        self.offset_x += (target_x - self.offset_x) * self.lerp_speed * dt
        self.offset_y += (target_y - self.offset_y) * self.lerp_speed * dt


# ============================================================
# PROCEDURAL BACKGROUND HELPERS
# ============================================================

def generate_stone_texture(w: int, h: int, seed: int = 42) -> pygame.Surface:
    """Procedural stone block texture (cached)."""
    import random as _rng
    surf = pygame.Surface((w, h))
    rng = _rng.Random(seed)
    surf.fill(STONE_BASE if 'STONE_BASE' in dir() else (28, 24, 32))

    # Noise blocks
    block = 8
    for bx in range(0, w, block):
        for by in range(0, h, block):
            ga = rng.randint(-15, 15)
            base = (28, 24, 32)
            col = tuple(max(0, min(255, c + ga)) for c in base)
            pygame.draw.rect(surf, col, (bx, by, block, block))

    # Mortar lines (vertical ~128px, horizontal ~96px staggered)
    for x in range(0, w, 128):
        pygame.draw.line(surf, (16, 12, 20), (x, 0), (x, h), rng.randint(1, 2))
    for y in range(0, h, 96):
        offset = rng.randint(-32, 32)
        pygame.draw.line(surf, (16, 12, 20), (0, y + offset), (w, y + offset), 1)

    return surf


def draw_vignette(surface: pygame.Surface, margin_top=80, margin_bottom=80,
                  margin_left=60, margin_right=60, max_alpha=180):
    """Draw gradient vignette overlay on screen edges."""
    sw, sh = surface.get_size()

    # Top
    for i in range(margin_top):
        alpha = int(max_alpha * (1 - i / margin_top) ** 2)
        pygame.draw.line(surface, (0, 0, 0, alpha), (0, i), (sw, i))
    # Bottom
    for i in range(margin_bottom):
        alpha = int(max_alpha * (1 - i / margin_bottom) ** 2)
        pygame.draw.line(surface, (0, 0, 0, alpha), (0, sh - i), (sw, sh - i))
    # Left
    for i in range(margin_left):
        alpha = int(max_alpha * (1 - i / margin_left) ** 2)
        pygame.draw.line(surface, (0, 0, 0, alpha), (i, 0), (i, sh))
    # Right
    for i in range(margin_right):
        alpha = int(max_alpha * (1 - i / margin_right) ** 2)
        pygame.draw.line(surface, (0, 0, 0, alpha), (sw - i, 0), (sw - i, sh))
