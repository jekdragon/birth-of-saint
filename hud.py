"""
Рождение святого - HUD
Отрисовка интерфейса: HP, XP, таймер, оружие, пассивки.
Animated bars, weapon slots, passive slots, combo counter.
"""
import pygame
from config import (
    WIDTH, HEIGHT, WHITE, RED, GREEN, GOLD, DARK_BG,
    HP_BAR_WIDTH, HP_BAR_HEIGHT, XP_BAR_WIDTH, XP_BAR_HEIGHT, HUD_PADDING
)
from weapons import WEAPON_DEFS, PASSIVE_DEFS


def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * min(1.0, t)


class AnimatedHealthBar:
    """Dual-bar health display (Dark Souls style)."""
    def __init__(self):
        self.display_hp = 0
        self.damage_bar = 0
        self.damage_timer = 0.0

    def update(self, dt, current_hp, max_hp):
        self.display_hp = current_hp
        # Damage bar — задержка 0.5с потом lerp
        if self.damage_bar > self.display_hp:
            if self.damage_timer <= 0:
                self.damage_timer = 0.5
            self.damage_timer -= dt
            if self.damage_timer <= 0:
                self.damage_bar = lerp(self.damage_bar, self.display_hp, 5.0 * dt)
        else:
            self.damage_bar = self.display_hp
            self.damage_timer = 0.0

    def draw(self, surface, x, y, width, height, max_hp, font):
        # Background
        pygame.draw.rect(surface, (30, 15, 15), (x, y, width, height), border_radius=4)

        # Damage bar (жёлтая trailing)
        dmg_ratio = max(0, self.damage_bar / max(1, max_hp))
        dmg_w = int(width * dmg_ratio)
        if dmg_w > 0:
            pygame.draw.rect(surface, (180, 150, 50), (x, y, dmg_w, height), border_radius=4)

        # Main bar (зелёная/красная)
        hp_ratio = max(0, self.display_hp / max(1, max_hp))
        fill_w = int(width * hp_ratio)
        color = GREEN if hp_ratio > 0.5 else (255, 200, 50) if hp_ratio > 0.25 else RED
        if fill_w > 0:
            pygame.draw.rect(surface, color, (x, y, fill_w, height), border_radius=4)

        # Border
        pygame.draw.rect(surface, WHITE, (x, y, width, height), 1, border_radius=4)

        # HP text
        hp_text = font.render(f"{int(self.display_hp)}/{max_hp}", True, WHITE)
        surface.blit(hp_text, (x + width // 2 - hp_text.get_width() // 2, y + height // 2 - hp_text.get_height() // 2))


class AnimatedXPBar:
    """Full-width XP bar at top of screen."""
    def __init__(self):
        self.display_progress = 0.0
        self.target_progress = 0.0

    def update(self, dt, xp, xp_to_next):
        self.target_progress = xp / max(1, xp_to_next)
        self.display_progress = lerp(self.display_progress, self.target_progress, 8.0 * dt)

    def draw(self, surface, font):
        bar_height = 12
        y = 0

        # Background
        pygame.draw.rect(surface, (15, 15, 30), (0, y, WIDTH, bar_height))

        # Fill
        fill_w = int(WIDTH * self.display_progress)
        if fill_w > 0:
            # Base color
            pygame.draw.rect(surface, (0, 120, 200), (0, y, fill_w, bar_height))
            # Bright top edge
            pygame.draw.rect(surface, (0, 180, 255), (0, y, fill_w, 3))
            # Glow overlay
            glow = pygame.Surface((fill_w, bar_height), pygame.SRCALPHA)
            glow.fill((0, 200, 255, 40))
            surface.blit(glow, (0, y))

        # Border
        pygame.draw.rect(surface, (60, 80, 120), (0, y, WIDTH, bar_height), 1)

        # Level badge
        lvl_text = font.render(f"Lv {font}", True, GOLD)  # Will be overridden
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
            text_surf = font.render(t.text, True, t.color)
            text_surf.set_alpha(int(t.alpha))
            x = WIDTH - text_surf.get_width() - HUD_PADDING + int(t.x_offset)
            # Background
            bg = pygame.Surface((text_surf.get_width() + 16, text_surf.get_height() + 8), pygame.SRCALPHA)
            bg.fill((20, 15, 30, int(t.alpha * 0.7)))
            surface.blit(bg, (x - 8, y - 4))
            surface.blit(text_surf, (x, y))
            y -= 30


# Singleton instances
_hp_bar = AnimatedHealthBar()
_xp_bar = AnimatedXPBar()
_toast_mgr = ToastManager()


def spawn_toast(text, color=WHITE, duration=2.0):
    """Public API to spawn a toast notification."""
    _toast_mgr.spawn(text, color, duration)


def draw_hud(surface: pygame.Surface, player, wave: int, elapsed: float,
             font, small_font):
    """Рисует весь HUD поверх игры."""

    dt = 0.016  # approximate dt

    # === Update animated bars ===
    _hp_bar.update(dt, player.hp, player.max_hp)
    _xp_bar.update(dt, player.xp, player.xp_to_next)
    _toast_mgr.update(dt)

    # === XP Bar (full-width top) ===
    _xp_bar.draw(surface, font)
    # Level badge on top-left (below XP bar)
    level_text = font.render(f"Lv {player.level}", True, GOLD)
    surface.blit(level_text, (HUD_PADDING, 16))

    # === HP Bar (top-left, below level) ===
    hp_x = HUD_PADDING
    hp_y = 36
    hp_w = 180
    hp_h = 18
    _hp_bar.draw(surface, hp_x, hp_y, hp_w, hp_h, player.max_hp, small_font)

    # === Kills + Gold (top-left, below HP) ===
    kills_text = small_font.render(f"Kills: {player.kills}", True, WHITE)
    surface.blit(kills_text, (HUD_PADDING, hp_y + hp_h + 4))
    gold_text = small_font.render(f"Gold: {player.gold}", True, GOLD)
    surface.blit(gold_text, (HUD_PADDING, hp_y + hp_h + 18))

    # === Timer + Wave (top-right) ===
    mins = int(elapsed) // 60
    secs = int(elapsed) % 60
    timer_text = font.render(f"{mins:02d}:{secs:02d}", True, WHITE)
    surface.blit(timer_text, (WIDTH - timer_text.get_width() - HUD_PADDING, 12))

    wave_text = small_font.render(f"Wave {wave}", True, WHITE)
    surface.blit(wave_text, (WIDTH - wave_text.get_width() - HUD_PADDING, 32))

    # === Weapon Slots (bottom-left) ===
    slot_size = 32
    slot_gap = 4
    weapon_x = HUD_PADDING
    weapon_y = HEIGHT - slot_size - HUD_PADDING
    max_slots = 6

    # Rarity colors
    rarity_colors = {
        'common': (120, 120, 120), 'uncommon': (80, 200, 80),
        'rare': (80, 120, 255), 'epic': (180, 80, 255), 'legendary': (255, 180, 50)
    }

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
            color = WEAPON_DEFS.get(w.weapon_id, {}).get("color", WHITE)
            icon_rect = pygame.Rect(x + 6, weapon_y + 6, slot_size - 12, slot_size - 12)
            pygame.draw.rect(surface, color, icon_rect, border_radius=2)

            # Level badge
            if w.level > 1:
                lvl_text = small_font.render(f"+{w.level}", True, GOLD)
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
            color = PASSIVE_DEFS.get(pid, {}).get("color", WHITE)
            pygame.draw.rect(surface, color, rect, 2, border_radius=4)

            # Icon
            icon_rect = pygame.Rect(x + 8, weapon_y + 8, slot_size - 16, slot_size - 16)
            pygame.draw.rect(surface, color, icon_rect, border_radius=2)

            # Level badge
            if lvl > 1:
                lvl_text = small_font.render(f"+{lvl}", True, GOLD)
                surface.blit(lvl_text, (x + slot_size - lvl_text.get_width() - 2, weapon_y + slot_size - 12))
        else:
            # Empty slot
            pygame.draw.rect(surface, (60, 50, 80), rect, 1, border_radius=4)

    # === Combo counter ===
    if not hasattr(draw_hud, '_combo'):
        draw_hud._combo = 0
        draw_hud._combo_timer = 0.0
        draw_hud._last_kills = 0

    if player.kills > draw_hud._last_kills:
        draw_hud._combo += player.kills - draw_hud._last_kills
        draw_hud._combo_timer = 2.0
    draw_hud._last_kills = player.kills

    if draw_hud._combo_timer > 0:
        draw_hud._combo_timer -= dt
        if draw_hud._combo >= 3:
            combo_color = (255, 200, 50) if draw_hud._combo < 10 else (255, 100, 50)
            combo_text = font.render(f"x{draw_hud._combo}!", True, combo_color)
            surface.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 60))
    else:
        draw_hud._combo = 0

    # === Toasts ===
    _toast_mgr.draw(surface, small_font)
