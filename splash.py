"""
Рождение святого — Splash Screen (v2)
Полноэкранный сплеш с параллаксом, частицами, heartbeat-логотипом.
Использует: ui_theme, animation, ui_components
"""
import pygame
import math
from config import WIDTH, HEIGHT
from ui_theme import (
    GOLD_LEAF, GOLD_GLOW, TEXT_PRIMARY, TEXT_DIM,
    get_font, get_logo_font, get_small_font,
    PARTICLE_COUNT_SPLASH, SCREEN_W, SCREEN_H,
)
from animation import Parallax, heartbeat_value, AnimatedAlpha, ease_out_cubic
from ui_components import UIParticleSystem


class SplashScreen:
    """Splash-экран с параллаксом, частицами, heartbeat-логотипом."""

    def __init__(self):
        # Фон (заставка.png)
        try:
            raw = pygame.image.load("заставка.png").convert_alpha()
            iw, ih = raw.get_size()
            scale = max(WIDTH / iw, HEIGHT / ih)
            sw, sh = int(iw * scale), int(ih * scale)
            scaled = pygame.transform.smoothscale(raw, (sw, sh))
            cx, cy = (sw - WIDTH) // 2, (sh - HEIGHT) // 2
            self.bg = scaled.subsurface((cx, cy, WIDTH, HEIGHT)).copy()
        except Exception:
            self.bg = pygame.Surface((WIDTH, HEIGHT))
            self.bg.fill((10, 10, 20))

        # Частицы
        self.particles = UIParticleSystem(
            count=PARTICLE_COUNT_SPLASH,
            colors=[(200, 180, 100), (255, 215, 0), (255, 255, 255)],
            speed_range=(-0.5, -0.15),
            size_range=(1, 4),
        )

        # Параллакс
        self.parallax = Parallax(max_offset=20.0, lerp_speed=5.0)

        # Fade
        self.fade_in = AnimatedAlpha(255)
        self.fade_out = AnimatedAlpha(0)

        # Состояние
        self.timer = 0.0
        self.done = False

        # Звук
        self.ambient = None
        try:
            self.ambient = pygame.mixer.Sound("assets/sounds/ambient.wav")
            self.ambient.set_volume(0.15)
            self.ambient.play(-1)
        except Exception:
            pass

    def stop_sound(self):
        if self.ambient:
            self.ambient.fadeout(500)

    def update(self, dt):
        self.timer += dt

        # Fade-in
        if self.fade_in.alpha > 0:
            self.fade_in.fade_in(speed=5.0)

        # Fade-out
        if self.fade_out.target == 255:
            self.fade_out.fade_in(speed=8.5, callback=self._finish)

        self.fade_in.update(dt)
        self.fade_out.update(dt)

        # Частицы
        self.particles.update(dt)

        # Параллакс
        self.parallax.update(dt, pygame.mouse.get_pos())

    def _finish(self):
        self.done = True

    def handle_events(self, events):
        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if self.fade_in.alpha <= 10 and self.fade_out.alpha == 0:
                    self.fade_out.fade_out(speed=8.5, callback=self._finish)
                    self.stop_sound()
        return None

    def draw(self, screen):
        # === Фон с параллаксом ===
        ox, oy = int(self.parallax.offset_x), int(self.parallax.offset_y)
        screen.blit(self.bg, (ox, oy))

        # === Мерцание витража ===
        flicker = 0.95 + 0.05 * math.sin(self.timer * (2 * math.pi / 4.0))
        if flicker < 1.0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            darken = int((1.0 - flicker) * 60)
            overlay.fill((0, 0, 0, darken))
            cx, cy = WIDTH // 2, HEIGHT // 2
            brighten = int((1.0 - flicker) * 40)
            glow = pygame.Surface((300, 300), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 215, 0, brighten), (0, 0, 300, 300))
            overlay.blit(glow, (cx - 150, cy - 150))
            screen.blit(overlay, (0, 0))

        # === Частицы ===
        self.particles.draw(screen)

        # === Heartbeat логотип ===
        hb = heartbeat_value(self.timer, period=2.0)
        logo_font = get_logo_font()
        logo_text = logo_font.render("РОЖДЕНИЕ СВЯТОГО", True, GOLD_LEAF)
        # Pulsating glow behind logo
        if hb > 0.01:
            glow_size = int(20 + 30 * hb)
            glow_surf = pygame.Surface((logo_text.get_width() + glow_size * 2,
                                        logo_text.get_height() + glow_size * 2), pygame.SRCALPHA)
            glow_alpha = int(40 * hb)
            pygame.draw.ellipse(glow_surf, (*GOLD_GLOW[:3], glow_alpha),
                                glow_surf.get_rect())
            screen.blit(glow_surf,
                        (WIDTH // 2 - glow_surf.get_width() // 2,
                         HEIGHT // 3 - glow_surf.get_height() // 2))
        # Logo text
        screen.blit(logo_text,
                    (WIDTH // 2 - logo_text.get_width() // 2,
                     HEIGHT // 3 - logo_text.get_height() // 2))

        # === Подзаголовок ===
        sub_font = get_font(22)
        sub_text = sub_font.render("Гнев Небес", True, TEXT_DIM)
        screen.blit(sub_text,
                    (WIDTH // 2 - sub_text.get_width() // 2,
                     HEIGHT // 3 + logo_text.get_height() // 2 + 10))

        # === Промпт ===
        prompt_font = get_font(24)
        prompt_alpha = int(127 + 128 * math.sin(self.timer * (2 * math.pi / 1.5)))
        prompt_alpha = max(1, min(255, prompt_alpha))
        prompt = prompt_font.render("НАЖМИТЕ ДЛЯ НАЧАЛА", True, TEXT_PRIMARY)
        prompt.set_alpha(prompt_alpha)
        screen.blit(prompt,
                    (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 80))

        # === Версия ===
        ver_font = get_small_font()
        ver = ver_font.render("v0.7.0", True, TEXT_DIM)
        screen.blit(ver, (WIDTH - ver.get_width() - 10, HEIGHT - ver.get_height() - 10))

        # === Fade overlays ===
        if self.fade_in.alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.fade_in.alpha))
            screen.blit(fade, (0, 0))

        if self.fade_out.alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.fade_out.alpha))
            screen.blit(fade, (0, 0))
