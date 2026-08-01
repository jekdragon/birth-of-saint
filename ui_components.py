"""
Рождение святого — UI Components Library
Базовые компоненты интерфейса на основе UIElement (из PDF-спецификации).
Все компоненты используют ui_theme для цветов и animation для анимаций.
"""
import pygame
import math
from ui_theme import (
    get_font, get_button_font, get_body_font, get_small_font, get_tiny_font,
    FONT_SIZE_BUTTON, FONT_SIZE_BODY, FONT_SIZE_SMALL,
    BG_NEAR_BLACK, BG_DARK, STONE_BASE, STONE_LIGHT, STONE_DARK,
    GOLD_LEAF, GOLD_IDLE, GOLD_GLOW, GOLD_DARK,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_DIM, TEXT_GOLD, TEXT_GREY,
    DANGER_RED, IRON, IRON_LIGHT,
    PANEL_PADDING, PANEL_RADIUS, PANEL_BORDER_W,
    BTN_MEDIUM_W, BTN_MEDIUM_H, BTN_LARGE_W, BTN_LARGE_H, BTN_GAP,
    TAB_H, TAB_GAP, TAB_RADIUS,
    SLIDER_W, SLIDER_H, SLIDER_HANDLE_R,
    TOAST_W, TOAST_H, TOAST_DURATION, TOAST_GAP,
    OVERLAY_ALPHA, STAGGER_DELAY,
    color_alpha, color_lerp, color_brighten, color_dim,
)
from animation import (
    Tween, ScalePunch, StaggerAnimator, ease_out_cubic,
)
import sound_manager


# ============================================================
# UIElement — базовый класс (из PDF-спецификации)
# ============================================================

class UIElement:
    """Base UI element with rect, hover detection, and lifecycle."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.is_focused = False  # keyboard/gamepad focus
        self.visible = True
        self.enabled = True
        self.alpha = 255

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input event. Returns True if consumed."""
        return False

    def update(self, dt: float):
        """Update logic (animations, timers)."""
        pass

    def draw(self, surface: pygame.Surface):
        """Render the element."""
        pass

    def set_position(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y

    def center_on(self, cx: int, cy: int):
        self.rect.centerx = cx
        self.rect.centery = cy


# ============================================================
# BUTTON — кнопка с hover/focus/pressed состояниями
# ============================================================

class UIButton(UIElement):
    """
    Pixel-art style button with 4 states.
    Hover: +2px offset, brighter color.
    Pressed: -1px offset, darker.
    Focus: gold border (keyboard nav).
    """

    # Style variants
    STYLE_DEFAULT = 'default'
    STYLE_PRIMARY = 'primary'   # gold accent
    STYLE_DANGER = 'danger'     # red accent
    STYLE_GHOST = 'ghost'       # transparent

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, style: str = 'default', callback=None,
                 font_size: int = FONT_SIZE_BUTTON):
        super().__init__(x, y, width, height)
        self.text = text
        self.style = style
        self.callback = callback
        self.font = get_font(font_size)
        self.punch = ScalePunch()
        self.press_timer = 0.0
        self._was_hovered = False

    def _get_colors(self) -> tuple:
        """Returns (fill, border, text_color) for current state."""
        if not self.enabled:
            return ((40, 40, 45), (60, 60, 65), (80, 80, 85))

        if self.style == self.STYLE_PRIMARY:
            if self.is_hovered:
                return ((60, 50, 30), GOLD_LEAF, GOLD_GLOW)
            return ((40, 35, 20), GOLD_IDLE, GOLD_LEAF)

        if self.style == self.STYLE_DANGER:
            if self.is_hovered:
                return ((60, 20, 20), DANGER_RED, (255, 100, 100))
            return ((40, 15, 15), (150, 40, 40), DANGER_RED)

        if self.style == self.STYLE_GHOST:
            if self.is_hovered:
                return ((30, 25, 50, 120), (180, 160, 100), TEXT_PRIMARY)
            return ((0, 0, 0, 0), (80, 75, 90), TEXT_SECONDARY)

        # Default
        if self.is_hovered:
            return (STONE_LIGHT, (180, 160, 100), TEXT_PRIMARY)
        return (STONE_BASE, (100, 95, 110), TEXT_SECONDARY)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            was = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_hovered and not was:
                sound_manager.play("ui_hover")
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.press_timer = 0.08
                sound_manager.play("ui_select")
                if self.callback:
                    self.callback()
                return True

        if event.type == pygame.KEYDOWN and self.is_focused:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.press_timer = 0.08
                sound_manager.play("ui_select")
                if self.callback:
                    self.callback()
                return True

        return False

    def update(self, dt: float):
        self.punch.update(dt)
        if self.press_timer > 0:
            self.press_timer -= dt

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        fill, border, text_color = self._get_colors()
        r = self.rect

        # Press offset (1px down)
        press_off = 1 if self.press_timer > 0 else 0
        # Hover offset (2px up-right for pixel feel)
        hover_off_x = 2 if self.is_hovered and self.press_timer <= 0 else 0
        hover_off_y = -2 if self.is_hovered and self.press_timer <= 0 else 0

        # Draw rect
        draw_rect = pygame.Rect(
            r.x + hover_off_x, r.y + hover_off_y + press_off,
            r.width, r.height
        )

        # Fill
        if len(fill) == 4:
            s = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            s.fill(fill)
            surface.blit(s, draw_rect.topleft)
        else:
            pygame.draw.rect(surface, fill, draw_rect, border_radius=8)

        # Border
        bw = 3 if self.is_focused else 2 if self.is_hovered else 1
        bc = GOLD_LEAF if self.is_focused else border
        pygame.draw.rect(surface, bc, draw_rect, bw, border_radius=8)

        # Focus inner highlight
        if self.is_focused:
            inner = draw_rect.inflate(-6, -6)
            pygame.draw.rect(surface, color_alpha(GOLD_LEAF, 40), inner, 1, border_radius=6)

        # Text
        t = self.font.render(self.text, True, text_color)
        tr = t.get_rect(center=draw_rect.center)
        surface.blit(t, tr)

    def trigger(self):
        """Programmatic click."""
        if self.enabled and self.callback:
            self.callback()


# ============================================================
# PANEL — панель с рамкой и фоном
# ============================================================

class UIPanel(UIElement):
    """Stone-styled panel with border and optional title."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 title: str = "", border_color=None):
        super().__init__(x, y, width, height)
        self.title = title
        self.border_color = border_color or IRON_LIGHT
        self.fill_color = STONE_BASE
        self.title_font = get_font(FONT_SIZE_BUTTON)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        r = self.rect

        # Shadow
        shadow = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 60))
        surface.blit(shadow, (r.x + 3, r.y + 3))

        # Fill
        pygame.draw.rect(surface, self.fill_color, r, border_radius=PANEL_RADIUS)

        # Border
        pygame.draw.rect(surface, self.border_color, r, PANEL_BORDER_W, border_radius=PANEL_RADIUS)

        # Inner highlight
        inner = r.inflate(-4, -4)
        pygame.draw.rect(surface, color_brighten(self.fill_color, 10), inner, 1, border_radius=PANEL_RADIUS - 2)

        # Title
        if self.title:
            t = self.title_font.render(self.title, True, GOLD_LEAF)
            tr = t.get_rect(centerx=r.centerx, top=r.top + 12)
            surface.blit(t, tr)
            # Divider
            div_y = tr.bottom + 8
            pygame.draw.line(surface, IRON, (r.left + 20, div_y), (r.right - 20, div_y), 1)


# ============================================================
# TAB BAR — горизонтальная полоса вкладок
# ============================================================

class UITabBar(UIElement):
    """Horizontal tab bar with keyboard/mouse navigation."""

    def __init__(self, x: int, y: int, width: int, tabs: list,
                 font_size: int = 22, on_change=None):
        super().__init__(x, y, width, TAB_H)
        self.tabs = tabs  # list of str
        self.active = 0
        self.hover_tab = -1
        self.font = get_font(font_size)
        self.on_change = on_change
        self.tab_rects = []
        self._calc_rects()

    def _calc_rects(self):
        n = len(self.tabs)
        if n == 0:
            return
        total_gap = TAB_GAP * (n - 1)
        tab_w = (self.rect.width - total_gap) // n
        self.tab_rects = []
        for i in range(n):
            tx = self.rect.x + i * (tab_w + TAB_GAP)
            self.tab_rects.append(pygame.Rect(tx, self.rect.y, tab_w, self.rect.height))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hover_tab = -1
            for i, tr in enumerate(self.tab_rects):
                if tr.collidepoint(event.pos):
                    self.hover_tab = i
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover_tab >= 0 and self.hover_tab != self.active:
                old = self.active
                self.active = self.hover_tab
                sound_manager.play("ui_select")
                if self.on_change:
                    self.on_change(old, self.active)
                return True

        if event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_LEFT:
                old = self.active
                self.active = (self.active - 1) % len(self.tabs)
                sound_manager.play("ui_hover")
                if self.on_change:
                    self.on_change(old, self.active)
                return True
            if event.key == pygame.K_RIGHT:
                old = self.active
                self.active = (self.active + 1) % len(self.tabs)
                sound_manager.play("ui_hover")
                if self.on_change:
                    self.on_change(old, self.active)
                return True

        return False

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        for i, tr in enumerate(self.tab_rects):
            is_active = (i == self.active)
            is_hover = (i == self.hover_tab)

            # Background
            if is_active:
                fill = STONE_LIGHT
                border = GOLD_LEAF
                text_color = GOLD_LEAF
            elif is_hover:
                fill = color_brighten(STONE_BASE, 8)
                border = GOLD_IDLE
                text_color = TEXT_PRIMARY
            else:
                fill = STONE_DARK
                border = IRON
                text_color = TEXT_GREY

            pygame.draw.rect(surface, fill, tr, border_radius=TAB_RADIUS)
            pygame.draw.rect(surface, border, tr, 2 if is_active else 1, border_radius=TAB_RADIUS)

            # Gold underline for active
            if is_active:
                pygame.draw.line(surface, GOLD_LEAF,
                                 (tr.left + 8, tr.bottom - 2),
                                 (tr.right - 8, tr.bottom - 2), 2)

            # Text
            t = self.font.render(self.tabs[i], True, text_color)
            tr_text = t.get_rect(center=tr.center)
            surface.blit(t, tr_text)


# ============================================================
# CARD — карточка выбора (персонаж, оружие, аркана)
# ============================================================

class UICard(UIElement):
    """Selectable card with icon, name, description."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 name: str = "", description: str = "", icon_color=None,
                 callback=None):
        super().__init__(x, y, width, height)
        self.name = name
        self.description = description
        self.icon_color = icon_color or (120, 120, 120)
        self.selected = False
        self.locked = False
        self.callback = callback
        self.name_font = get_font(FONT_SIZE_BUTTON)
        self.desc_font = get_font(FONT_SIZE_SMALL)
        self.punch = ScalePunch()

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or self.locked:
            return False

        if event.type == pygame.MOUSEMOTION:
            was = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_hovered and not was:
                sound_manager.play("ui_hover")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.selected = True
                self.punch.punch(1.08)
                sound_manager.play("ui_select")
                if self.callback:
                    self.callback()
                return True

        return False

    def update(self, dt: float):
        self.punch.update(dt)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        r = self.rect

        # Card background
        fill = STONE_LIGHT if self.is_hovered or self.selected else STONE_BASE
        border = GOLD_LEAF if self.selected else (GOLD_IDLE if self.is_hovered else IRON)
        bw = 2 if self.selected else (1 if self.is_hovered else 1)

        pygame.draw.rect(surface, fill, r, border_radius=10)
        pygame.draw.rect(surface, border, r, bw, border_radius=10)

        # Icon area (top portion)
        icon_rect = pygame.Rect(r.x + 10, r.y + 10, r.width - 20, 60)
        pygame.draw.rect(surface, color_dim(self.icon_color, 0.3), icon_rect, border_radius=6)
        pygame.draw.rect(surface, self.icon_color, icon_rect, 1, border_radius=6)

        # Icon placeholder (filled rect)
        icon_inner = icon_rect.inflate(-10, -10)
        pygame.draw.rect(surface, self.icon_color, icon_inner, border_radius=4)

        # Name
        name_color = TEXT_PRIMARY if not self.locked else TEXT_DIM
        n = self.name_font.render(self.name, True, name_color)
        nr = n.get_rect(centerx=r.centerx, top=icon_rect.bottom + 8)
        surface.blit(n, nr)

        # Description
        if self.description:
            d = self.desc_font.render(self.description[:30], True, TEXT_SECONDARY)
            dr = d.get_rect(centerx=r.centerx, top=nr.bottom + 4)
            surface.blit(d, dr)

        # Lock overlay
        if self.locked:
            overlay = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, r.topleft)
            lock_t = self.name_font.render("???", True, TEXT_DIM)
            lock_r = lock_t.get_rect(center=r.center)
            surface.blit(lock_t, lock_r)


# ============================================================
# SLIDER — ползунок громкости/настроек
# ============================================================

class UISlider(UIElement):
    """Horizontal slider with label and percentage display."""

    def __init__(self, x: int, y: int, width: int,
                 label: str, value: float = 0.5, on_change=None):
        super().__init__(x, y, width, SLIDER_H + 24)
        self.label = label
        self.value = max(0.0, min(1.0, value))
        self.on_change = on_change
        self.label_font = get_font(FONT_SIZE_BODY)
        self.val_font = get_font(FONT_SIZE_SMALL)
        self.dragging = False
        self._track_rect = pygame.Rect(x, y + 20, width, SLIDER_H)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._track_rect.inflate(0, 20).collidepoint(event.pos):
                self.dragging = True
                self._update_from_mouse(event.pos[0])
                return True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_from_mouse(event.pos[0])
            return True

        if event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_LEFT:
                self.value = max(0.0, self.value - 0.05)
                sound_manager.play("ui_hover")
                if self.on_change:
                    self.on_change(self.value)
                return True
            if event.key == pygame.K_RIGHT:
                self.value = min(1.0, self.value + 0.05)
                sound_manager.play("ui_hover")
                if self.on_change:
                    self.on_change(self.value)
                return True

        return False

    def _update_from_mouse(self, mx: int):
        rel = (mx - self._track_rect.x) / self._track_rect.width
        self.value = max(0.0, min(1.0, rel))
        if self.on_change:
            self.on_change(self.value)

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return

        # Label
        label_color = GOLD_LEAF if self.is_focused else TEXT_PRIMARY
        l = self.label_font.render(self.label, True, label_color)
        surface.blit(l, (self.rect.x, self.rect.y))

        # Track background
        tr = self._track_rect
        pygame.draw.rect(surface, (40, 40, 50), tr, border_radius=SLIDER_H // 2)

        # Filled portion
        fill_w = int(tr.width * self.value)
        if fill_w > 0:
            fill_rect = pygame.Rect(tr.x, tr.y, fill_w, tr.height)
            pygame.draw.rect(surface, GOLD_IDLE, fill_rect, border_radius=SLIDER_H // 2)

        # Handle
        hx = tr.x + int(tr.width * self.value)
        hy = tr.centery
        pygame.draw.circle(surface, GOLD_LEAF, (hx, hy), SLIDER_HANDLE_R)
        pygame.draw.circle(surface, GOLD_GLOW, (hx, hy), SLIDER_HANDLE_R - 3)

        # Focus ring
        if self.is_focused:
            pygame.draw.circle(surface, GOLD_LEAF, (hx, hy), SLIDER_HANDLE_R + 2, 1)

        # Value text
        vt = self.val_font.render(f"{int(self.value * 100)}%", True, TEXT_SECONDARY)
        surface.blit(vt, (tr.right + 12, tr.centery - vt.get_height() // 2))


# ============================================================
# PROGRESS BAR — полоса прогресса (HP, XP)
# ============================================================

class UIProgressBar(UIElement):
    """Animated progress bar with color transitions."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 value: float = 1.0, max_value: float = 1.0,
                 color=GOLD_LEAF, bg_color=None):
        super().__init__(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.display_value = value  # animated lerp
        self.color = color
        self.bg_color = bg_color or (30, 30, 35)
        self.lerp_speed = 4.0

    def set_value(self, value: float):
        self.value = max(0, min(self.max_value, value))

    def update(self, dt: float):
        diff = self.value - self.display_value
        if abs(diff) > 0.01:
            self.display_value += diff * self.lerp_speed * dt
        else:
            self.display_value = self.value

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        r = self.rect

        # Background
        pygame.draw.rect(surface, self.bg_color, r, border_radius=r.height // 2)

        # Fill
        ratio = self.display_value / max(0.001, self.max_value)
        fill_w = int(r.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(r.x, r.y, fill_w, r.height)
            pygame.draw.rect(surface, self.color, fill_rect, border_radius=r.height // 2)

        # Border
        pygame.draw.rect(surface, IRON, r, 1, border_radius=r.height // 2)


# ============================================================
# TOAST — всплывающее уведомление
# ============================================================

class Toast:
    """Single toast notification."""

    __slots__ = ('text', 'timer', 'duration', 'alpha', 'offset_x', 'icon_color')

    def __init__(self, text: str, duration: float = TOAST_DURATION, icon_color=None):
        self.text = text
        self.timer = 0.0
        self.duration = duration
        self.alpha = 255
        self.offset_x = 300  # starts off-screen
        self.icon_color = icon_color or GOLD_LEAF

    def update(self, dt: float):
        self.timer += dt
        # Slide in
        if self.timer < 0.2:
            t = self.timer / 0.2
            self.offset_x = int(300 * (1.0 - ease_out_cubic(t)))
        # Hold
        elif self.timer < self.duration - 0.3:
            self.offset_x = 0
        # Fade out
        else:
            t = (self.timer - (self.duration - 0.3)) / 0.3
            self.offset_x = 0
            self.alpha = int(255 * (1.0 - t))

    @property
    def alive(self) -> bool:
        return self.timer < self.duration


class ToastManager:
    """Manages a queue of toast notifications."""

    def __init__(self, x: int = -1, y: int = 100):
        self.toasts: list[Toast] = []
        self.x = x  # -1 = right-aligned
        self.y = y

    def add(self, text: str, duration: float = TOAST_DURATION, icon_color=None):
        self.toasts.append(Toast(text, duration, icon_color))

    def update(self, dt: float):
        for t in self.toasts:
            t.update(dt)
        self.toasts = [t for t in self.toasts if t.alive]

    def draw(self, surface: pygame.Surface):
        sw = surface.get_width()
        for i, toast in enumerate(self.toasts):
            ty = self.y + i * (TOAST_H + TOAST_GAP)
            tx = (sw - TOAST_W - 20 + toast.offset_x) if self.x < 0 else self.x + toast.offset_x

            # Background
            s = pygame.Surface((TOAST_W, TOAST_H), pygame.SRCALPHA)
            s.fill((30, 25, 40, min(220, toast.alpha)))
            pygame.draw.rect(s, color_alpha(toast.icon_color, toast.alpha), (0, 0, TOAST_W, TOAST_H), 1, border_radius=8)
            surface.blit(s, (tx, ty))

            # Text
            font = get_small_font()
            t = font.render(toast.text, True, color_alpha(TEXT_PRIMARY, toast.alpha))
            surface.blit(t, (tx + 12, ty + (TOAST_H - t.get_height()) // 2))


# ============================================================
# CONFIRM DIALOG — диалог подтверждения
# ============================================================

class UIConfirmDialog(UIElement):
    """Overlay dialog with title, body, ДА/НЕТ buttons."""

    def __init__(self, title: str = "Вы уверены?", body: str = "",
                 yes_text: str = "ДА", no_text: str = "НЕТ",
                 on_yes=None, on_no=None):
        sw, sh = 1024, 768
        super().__init__((sw - 400) // 2, (sh - 180) // 2, 400, 180)
        self.title = title
        self.body = body
        self.selected = 1  # 0=yes, 1=no (default no — safer)
        self.active = False
        self.result = None
        self.timer = 0.0

        btn_y = self.rect.bottom - 55
        self.btn_yes = UIButton(self.rect.x + 40, btn_y, 140, 40,
                                yes_text, 'primary', on_yes)
        self.btn_no = UIButton(self.rect.right - 180, btn_y, 140, 40,
                               no_text, 'ghost', on_no)
        self.buttons = [self.btn_yes, self.btn_no]

    def show(self):
        self.active = True
        self.selected = 1
        self.result = None
        self.timer = 0.0
        self.btn_yes.is_focused = False
        self.btn_no.is_focused = True

    def handle_event(self, event: pygame.event.Event):
        if not self.active:
            return None

        self.timer += 0.016  # approximate

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return False
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.selected = 1 - self.selected
                self.btn_yes.is_focused = (self.selected == 0)
                self.btn_no.is_focused = (self.selected == 1)
                sound_manager.play("ui_hover")
                return None
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.selected == 0:
                    self.active = False
                    return True
                else:
                    self.active = False
                    return False

        # Mouse
        for btn in self.buttons:
            btn.handle_event(event)

        return None

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        # Dim overlay
        overlay = pygame.Surface((1024, 768), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        # Panel
        r = self.rect
        pygame.draw.rect(surface, STONE_BASE, r, border_radius=12)
        pygame.draw.rect(surface, IRON_LIGHT, r, 2, border_radius=12)

        # Title
        tf = get_button_font()
        tt = tf.render(self.title, True, TEXT_PRIMARY)
        surface.blit(tt, tt.get_rect(centerx=r.centerx, top=r.top + 16))

        # Body
        if self.body:
            bf = get_body_font()
            bt = bf.render(self.body, True, TEXT_SECONDARY)
            surface.blit(bt, bt.get_rect(centerx=r.centerx, top=r.top + 55))

        # Buttons
        for btn in self.buttons:
            btn.draw(surface)


# ============================================================
# DIALOGUE BOX — typewriter текст (из PDF)
# ============================================================

class UIDialogueBox(UIElement):
    """Typewriter-effect dialogue box for lore/descriptions."""

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.text = ""
        self.displayed_chars = 0
        self.char_timer = 0.0
        self.char_delay = 0.03  # seconds per character
        self.font = get_body_font()
        self.complete = False
        self.speaker = ""
        self.speaker_font = get_button_font()

    def set_text(self, text: str, speaker: str = ""):
        self.text = text
        self.speaker = speaker
        self.displayed_chars = 0
        self.char_timer = 0.0
        self.complete = False

    def skip(self):
        """Show all text immediately."""
        self.displayed_chars = len(self.text)
        self.complete = True

    def update(self, dt: float):
        if self.complete:
            return
        self.char_timer += dt
        while self.char_timer >= self.char_delay and self.displayed_chars < len(self.text):
            self.char_timer -= self.char_delay
            self.displayed_chars += 1
        if self.displayed_chars >= len(self.text):
            self.complete = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            if not self.complete:
                self.skip()
                return True
            return False  # already complete, signal to close
        return False

    def draw(self, surface: pygame.Surface):
        if not self.visible or not self.text:
            return
        r = self.rect

        # Background
        pygame.draw.rect(surface, (20, 18, 25, 230), r, border_radius=8)
        pygame.draw.rect(surface, GOLD_DARK, r, 2, border_radius=8)

        # Speaker name
        y_offset = r.top + 12
        if self.speaker:
            st = self.speaker_font.render(self.speaker, True, GOLD_LEAF)
            surface.blit(st, (r.left + 16, y_offset))
            y_offset += st.get_height() + 6

        # Typewriter text
        visible = self.text[:self.displayed_chars]
        # Word wrap
        words = visible.split(' ')
        lines = []
        current = ""
        for word in words:
            test = current + (" " if current else "") + word
            if self.font.size(test)[0] > r.width - 32:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)

        for i, line in enumerate(lines):
            lt = self.font.render(line, True, TEXT_PRIMARY)
            surface.blit(lt, (r.left + 16, y_offset + i * (lt.get_height() + 2)))

        # Blinking cursor indicator when complete
        if self.complete:
            t = pygame.time.get_ticks() / 1000.0
            if int(t * 2) % 2 == 0:
                cursor_y = y_offset + len(lines) * (self.font.get_height() + 2) + 4
                pygame.draw.polygon(surface, GOLD_LEAF, [
                    (r.right - 30, cursor_y),
                    (r.right - 20, cursor_y + 5),
                    (r.right - 30, cursor_y + 10),
                ])


# ============================================================
# PARTICLE SYSTEM — конфигурируемый
# ============================================================

class UIParticle:
    """Single UI particle."""

    __slots__ = ('x', 'y', 'vx', 'vy', 'size', 'alpha', 'max_alpha',
                 'life', 'max_life', 'color', 'phase')

    def __init__(self, x, y, color, size=2, speed_y=-0.3, max_life=4.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = speed_y
        self.size = size
        self.alpha = 0
        self.max_alpha = 180
        self.life = 0.0
        self.max_life = max_life
        self.color = color
        self.phase = 0.0

    def update(self, dt: float):
        self.life += dt
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.x += math.sin(self.life * 0.8 + self.phase) * 0.3

        t = self.life / self.max_life
        if t < 0.2:
            self.alpha = int(self.max_alpha * (t / 0.2))
        elif t > 0.8:
            self.alpha = int(self.max_alpha * (1.0 - (t - 0.8) / 0.2))
        else:
            self.alpha = self.max_alpha

        self.alpha *= 0.8 + 0.2 * math.sin(self.life * 2.0 + self.phase)
        self.alpha = max(0, min(255, int(self.alpha)))

    @property
    def alive(self) -> bool:
        return self.life < self.max_life and self.alpha > 0


class UIParticleSystem:
    """Configurable particle system for backgrounds."""

    def __init__(self, count: int = 60, colors=None, speed_range=(-0.5, -0.15),
                 size_range=(1, 4), bounds=None):
        import random
        self.particles: list[UIParticle] = []
        self.colors = colors or [(200, 180, 100), (255, 215, 0), (255, 255, 255)]
        self.speed_range = speed_range
        self.size_range = size_range
        self.bounds = bounds or (0, 0, 1024, 768)
        self._init_particles(count, random)

    def _init_particles(self, count, rng):
        for _ in range(count):
            x = rng.uniform(self.bounds[0], self.bounds[0] + self.bounds[2])
            y = rng.uniform(self.bounds[1], self.bounds[1] + self.bounds[3])
            color = rng.choice(self.colors)
            size = rng.uniform(*self.size_range)
            speed = rng.uniform(*self.speed_range)
            life = rng.uniform(0, 4.0)  # stagger start
            p = UIParticle(x, y, color, size, speed)
            p.life = life
            p.phase = rng.uniform(0, math.pi * 2)
            p.max_alpha = rng.randint(60, 200)
            self.particles.append(p)

    def update(self, dt: float):
        import random
        for p in self.particles:
            p.update(dt)
            if not p.alive:
                # Respawn
                p.x = random.uniform(self.bounds[0], self.bounds[0] + self.bounds[2])
                p.y = self.bounds[1] + self.bounds[3] + 10
                p.life = 0.0
                p.alpha = 0
                p.phase = random.uniform(0, math.pi * 2)

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            if p.alpha <= 0:
                continue
            s = pygame.Surface((int(p.size * 2), int(p.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p.color, p.alpha), (int(p.size), int(p.size)), int(p.size))
            surface.blit(s, (int(p.x - p.size), int(p.y - p.size)))
