"""
Рождение святого - HUD
Отрисовка интерфейса: HP, XP, таймер, оружие, пассивки.
"""
import pygame
from config import (
    WIDTH, HEIGHT, WHITE, RED, GREEN, GOLD, DARK_BG,
    HP_BAR_WIDTH, HP_BAR_HEIGHT, XP_BAR_WIDTH, XP_BAR_HEIGHT, HUD_PADDING
)
from weapons import WEAPON_DEFS, PASSIVE_DEFS


def draw_hud(surface: pygame.Surface, player, wave: int, elapsed: float,
             font, small_font):
    """Рисует весь HUD поверх игры."""

    # === XP-бар (сверху по центру) ===
    xp_ratio = player.xp / max(1, player.xp_to_next)
    xp_x = WIDTH // 2 - XP_BAR_WIDTH // 2
    xp_y = HUD_PADDING

    # Фон
    pygame.draw.rect(surface, (30, 30, 50), (xp_x, xp_y, XP_BAR_WIDTH, XP_BAR_HEIGHT), border_radius=3)
    # Заполнение
    fill_w = int(XP_BAR_WIDTH * xp_ratio)
    pygame.draw.rect(surface, GREEN, (xp_x, xp_y, fill_w, XP_BAR_HEIGHT), border_radius=3)
    # Рамка
    pygame.draw.rect(surface, WHITE, (xp_x, xp_y, XP_BAR_WIDTH, XP_BAR_HEIGHT), 1, border_radius=3)

    # Уровень
    level_text = font.render(f"Lv {player.level}", True, GOLD)
    surface.blit(level_text, (xp_x - level_text.get_width() - 10, xp_y - 2))

    # === Таймер + волна (верх-право) ===
    mins = int(elapsed) // 60
    secs = int(elapsed) % 60
    timer_text = font.render(f"{mins:02d}:{secs:02d}", True, WHITE)
    surface.blit(timer_text, (WIDTH - timer_text.get_width() - HUD_PADDING, HUD_PADDING))

    wave_text = small_font.render(f"Волна {wave}", True, WHITE)
    surface.blit(wave_text, (WIDTH - wave_text.get_width() - HUD_PADDING, HUD_PADDING + 22))

    # === HP-бар (снизу по центру) ===
    hp_ratio = max(0, player.hp / max(1, player.max_hp))
    hp_x = WIDTH // 2 - HP_BAR_WIDTH // 2
    hp_y = HEIGHT - HP_BAR_HEIGHT - HUD_PADDING

    pygame.draw.rect(surface, (50, 20, 20), (hp_x, hp_y, HP_BAR_WIDTH, HP_BAR_HEIGHT), border_radius=3)
    fill_w = int(HP_BAR_WIDTH * hp_ratio)
    color = RED if hp_ratio > 0.3 else (255, 100, 100)
    pygame.draw.rect(surface, color, (hp_x, hp_y, fill_w, HP_BAR_HEIGHT), border_radius=3)
    pygame.draw.rect(surface, WHITE, (hp_x, hp_y, HP_BAR_WIDTH, HP_BAR_HEIGHT), 1, border_radius=3)

    hp_text = small_font.render(f"{int(player.hp)}/{player.max_hp}", True, WHITE)
    surface.blit(hp_text, (hp_x + HP_BAR_WIDTH // 2 - hp_text.get_width() // 2, hp_y - 1))

    # === Оружие (нижний-лево) ===
    weapon_x = HUD_PADDING
    weapon_y = HEIGHT - 40
    for i, w in enumerate(player.weapons):
        color = WEAPON_DEFS.get(w.weapon_id, {}).get("color", WHITE)
        # Иконка (маленький квадрат)
        rect = pygame.Rect(weapon_x + i * 28, weapon_y, 24, 24)
        pygame.draw.rect(surface, (40, 30, 60), rect, border_radius=4)
        pygame.draw.rect(surface, color, rect, 2, border_radius=4)
        # Уровень
        lvl_text = small_font.render(str(w.level), True, WHITE)
        surface.blit(lvl_text, (rect.x + 8, rect.y + 5))

    # === Пассивки (нижний-право) ===
    passive_x = WIDTH - HUD_PADDING - 24
    passive_y = HEIGHT - 40
    for i, (pid, lvl) in enumerate(player.passives.items()):
        color = PASSIVE_DEFS.get(pid, {}).get("color", WHITE)
        rect = pygame.Rect(passive_x - i * 28, passive_y, 24, 24)
        pygame.draw.rect(surface, (40, 30, 60), rect, border_radius=4)
        pygame.draw.rect(surface, color, rect, 2, border_radius=4)
        lvl_text = small_font.render(str(lvl), True, WHITE)
        surface.blit(lvl_text, (rect.x + 8, rect.y + 5))

    # === Счёт (верх-лево) ===
    kills_text = small_font.render(f"Убийства: {player.kills}", True, WHITE)
    surface.blit(kills_text, (HUD_PADDING, HUD_PADDING + 22))

    gold_text = small_font.render(f"Золото: {player.gold}", True, GOLD)
    surface.blit(gold_text, (HUD_PADDING, HUD_PADDING + 38))
