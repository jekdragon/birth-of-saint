# PLAN-UI-OVERHAUL.md — Birth of the Saint UI Overhaul

## 📋 Обзор
Комплексное обновление интерфейса Birth of the Saint на основе ресерча 5 игр жанра
(Vampire Survivors, HoloCure, Brotato, 20 Minutes Till Dawn, Boneraiser Minions)
и best practices для dark-themed pixel art UI.

## 🎯 Цель
HUD уровня HoloCure/Brotato с:
- Dual-bar health (Dark Souls style)
- Floating damage numbers с easing
- Animated XP bar
- Toast notification system
- Weapon cooldown indicators
- Player outline toggle
- Rarity color ladder для оружия

---

## Phase 4.0: Core HUD Redesign

### Step 4.0.1: Health Bar Overhaul
**Файл:** `hud.py`
**Что делаем:**
- Dual-bar: основная полоса + trailing damage bar (жёлтая, задержка 0.5с)
- Числовой HP поверх бара ("144/144")
- Красный pulse при <25% HP (已有 LowHPVignette — объединить)
- Вертикальный layout: portrait → HP bar → level
**Алгоритм:**
```python
class AnimatedHealthBar:
    def __init__(self):
        self.display_hp = max_hp
        self.target_hp = max_hp
        self.damage_bar = max_hp  # trailing
        self.damage_timer = 0.0

    def update(self, dt, current_hp):
        self.target_hp = current_hp
        # Основной бар — мгновенный
        self.display_hp = current_hp
        # Damage bar — задержка 0.5с потом lerp
        if self.damage_bar > self.target_hp:
            if self.damage_timer <= 0:
                self.damage_timer = 0.5
            self.damage_timer -= dt
            if self.damage_timer <= 0:
                self.damage_bar = lerp(self.damage_bar, self.target_hp, 5.0 * dt)
```

### Step 4.0.2: XP Bar Redesign
**Файл:** `hud.py`
**Что делаем:**
- Full-width XP bar в самом верху экрана (VS конвенция)
- Glow effect на заполненной части
- Smooth animation при получении XP
- Показывать "Lv 1" на баре
**Алгоритм:**
```python
class AnimatedXPBar:
    def __init__(self):
        self.display_progress = 0.0
        self.target_progress = 0.0

    def update(self, dt):
        self.display_progress = lerp(self.display_progress, self.target_progress, 8.0 * dt)

    def draw(self, surface, y=0):
        # Full width bar
        bar_rect = pygame.Rect(0, y, 1024, 6)
        # Background
        pygame.draw.rect(surface, (20, 20, 30), bar_rect)
        # Fill with glow
        fill_w = int(1024 * self.display_progress)
        pygame.draw.rect(surface, (0, 200, 255), (0, y, fill_w, 6))
        # Glow overlay
        glow = pygame.Surface((fill_w, 6), pygame.SRCALPHA)
        glow.fill((0, 200, 255, 50))
        surface.blit(glow, (0, y))
```

### Step 4.0.3: HUD Layout Restructure
**Файл:** `hud.py`
**Что делаем:**
- Top: full-width XP bar (6px)
- Top-left: Level badge + HP bar (dual-bar)
- Top-right: Timer + Wave + Kills
- Bottom: Weapon slots (6) + Passive slots (6)
- Center: Floating damage numbers
**Макет:**
```
┌─────────────────────────────────────────────────┐
│ [XP BAR ============================] Lv 1      │
│ Lv 1 [HP ████████████████] 144/144   ⏱ 05:23   │
│                                    Волна 3       │
│                                    Убийства: 47  │
│                                                 │
│              [GAME AREA]                        │
│                                                 │
│ [1⚔️][2⚡][3🔥][4💀][5🔔][6📿]  [🛡️][💎][👟] │
│                                 Passive slots   │
└─────────────────────────────────────────────────┘
```

---

## Phase 4.1: Damage Numbers & Feedback

### Step 4.1.1: Floating Damage Numbers
**Файл:** `projectiles.py` (已有 DamageNumber — расширяем)
**Что делаем:**
- Easing: ease_out_cubic для вертикального движения
- Alpha fade: 255→0 за 0.8с
- Варианты: обычный (белый), crit (жёлтый, 1.3x scale), heal (зелёный), XP (cyan)
- Manager для auto-cleanup
**Алгоритм:**
```python
def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

class FloatingNumberManager:
    def __init__(self):
        self.numbers = []

    def spawn(self, x, y, text, color, scale=1.0):
        self.numbers.append(FloatingNumber(x, y, text, color, scale))

    def update(self, dt):
        for n in self.numbers:
            n.timer += dt
            n.y -= 60 * dt * ease_out_cubic(min(1, n.timer / n.lifetime))
            n.alpha = int(255 * (1 - n.timer / n.lifetime))
        self.numbers = [n for n in self.numbers if n.timer < n.lifetime]
```

### Step 4.1.2: Hit Feedback Enhancement
**Файл:** `enemies.py`, `main.py`
**Что делаем:**
- Hitstop: 30ms пауза при критическом ударе
- Sprite flash: белый flash на 1 кадр при получении урона
- Screen shake intensity scale: 2 (normal), 5 (crit), 8 (boss hit)
- Combo counter: "x3!" при 3+ убийствах за 2 секунды (已有 — проверить)

---

## Phase 4.2: Weapon & Inventory UI

### Step 4.2.1: Weapon Slot Icons
**Файл:** `hud.py`
**Что делаем:**
- 6 слотов оружия внизу экрана
- Иконки: процедурные (оружие на цветном фоне)
- Rarity border: белый(обычное) → синий(улучш) → фиолетовый(эволюция)
- Cooldown overlay: затемнение + countdown arc
- Level badge: "+3" в углу слота
**Алгоритм cooldown:**
```python
def draw_weapon_slot(surface, weapon, x, y):
    # Background
    pygame.draw.rect(surface, (30, 25, 40), (x, y, 40, 40))
    # Rarity border
    border_color = RARITY_COLORS.get(weapon.rarity, (100, 100, 100))
    pygame.draw.rect(surface, border_color, (x, y, 40, 40), 2)
    # Icon
    draw_weapon_icon(surface, weapon.type_id, x + 4, y + 4)
    # Cooldown overlay
    if weapon.cooldown_timer > 0:
        pct = weapon.cooldown_timer / weapon.cooldown
        overlay = pygame.Surface((40, int(40 * pct)), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (x, y))
    # Level badge
    if weapon.level > 1:
        draw_text(surface, f"+{weapon.level}", x + 28, y + 28, (255, 200, 0), font_small)
```

### Step 4.2.2: Passive Slot Icons
**Файл:** `hud.py`
**Что делаем:**
- 6 слотов пассивок рядом с оружием
- Иконки: процедурные (форма + цвет)
- Level badge
- Tooltip при наведении (для будущего — сейчас только иконки)

### Step 4.2.3: Rarity Color System
**Файл:** `config.py`
**Что делаем:**
- Rarity ladder: Common(серый) → Uncommon(зелёный) → Rare(синий) → Epic(фиолетовый) → Legendary(оранжевый)
- Применить к: оружие, пассивки, эволюции
- Использовать в HUD, LevelUpScreen, Game Over

---

## Phase 4.3: Notifications & Transitions

### Step 4.3.1: Toast Notification System
**Файл:** `hud.py` (новый класс)
**Что делаем:**
- 3-state lifecycle: ENTERING → VISIBLE → EXITING
- Slide-from-right + alpha fade
- Типы: item pickup (зелёный), level up (золотой), warning (красный), wave (синий)
- Max 3 видимых одновременно, queue для остальных
**Алгоритм:**
```python
class Toast:
    ENTERING = 0; VISIBLE = 1; EXITING = 2
    def __init__(self, text, color, duration=2.0):
        self.text = text
        self.color = color
        self.state = self.ENTERING
        self.timer = 0.0
        self.duration = duration
        self.x_offset = 200  # за экраном
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
```

### Step 4.3.2: Level Up Screen Polish
**Файл:** `main.py` (LevelUpScreen)
**Что делаем:**
- Rarity border на картах выбора
- Описание оружия/пассивки
- Текущий уровень предмета
- Hover effect: подсветка + scale
- Золотой glow на эволюциях

### Step 4.3.3: Screen Transitions
**Файл:** `main.py`
**Что делаем:**
- Fade transition между экранами (menu → game → game over)
- Duration: 0.3с fade out, 0.3с fade in
- Чёрный overlay с alpha

---

## Phase 4.4: Visual Polish

### Step 4.4.1: Player Outline Toggle
**Файл:** `player.py`, `config.py`
**Что делаем:**
- Player outline: белый 1px outline вокруг игрока
- Toggle в настройках (клавиша O)
- Помогает видеть персонажа на тёмном фоне
**Алгоритм:**
```python
def draw_with_outline(sprite, surface, x, y):
    mask = pygame.mask.from_surface(sprite)
    outline = mask.outline()
    if outline:
        outline_surf = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
        for point in outline:
            pygame.draw.circle(outline_surf, (255, 255, 255, 180), point, 1)
        surface.blit(outline_surf, (x - 1, y - 1))
        surface.blit(outline_surf, (x + 1, y - 1))
        surface.blit(outline_surf, (x - 1, y + 1))
        surface.blit(outline_surf, (x + 1, y + 1))
    surface.blit(sprite, (x, y))
```

### Step 4.4.2: Project Color Coding
**Файл:** `projectiles.py`, `weapons.py`
**Что делаем:**
- Игрок: тёплые цвета (жёлтый, оранжевый, белый)
- Враги: холодные цвета (фиолетовый, синий, зелёный)
- Избегать low-contrast ловушки (20MTD проблема)

### Step 4.4.3: Pixel Font Integration
**Файл:** `config.py`, `hud.py`
**Что делаем:**
- Загрузить Press Start 2P (заголовки, damage numbers)
- Загрузить VT323 (UI body, описания)
- Fallback на pygame default если шрифт не найден
- Табличные цифры для HP counters

---

## Phase 4.5: Final Integration

### Step 4.5.1: Smoke Test
- 15 минут без краша с новым HUD
- Все элементы отображаются корректно
- FPS ≥ 55 с floating numbers + toasts

### Step 4.5.2: Visual Verification
- Скриншот: game area с HUD
- Скриншот: level up screen
- Скриншот: game over screen
- Скриншот: weapon slots + passive slots

### Step 4.5.3: pygbag Rebuild
- `python -m pygbag --build --html --disable-sound-format-error .`
- Browser test: HUD отображается корректно
- Mobile test: touch controls работают с новым HUD

---

## 📊 Сводка

| Phase | Steps | Tasks | Priority |
|-------|-------|-------|----------|
| 4.0 Core HUD | 3 | 12 | P0 |
| 4.1 Damage & Feedback | 2 | 8 | P0 |
| 4.2 Weapon UI | 3 | 9 | P1 |
| 4.3 Notifications | 3 | 9 | P1 |
| 4.4 Visual Polish | 3 | 9 | P2 |
| 4.5 Final Integration | 3 | 6 | P0 |
| **Total** | **17** | **53** | |

## 🔗 Dependencies
- Phase 3.5 VFX Integration (complete)
- sprite-gen v2.1 (complete)
- Research files: research-ui-survivors.md, research-ui-pixel-art.md, research-ui-techniques.md

## 📁 Затронутые файлы
| Файл | Изменения |
|------|-----------|
| `hud.py` | Dual-bar HP, XP bar, weapon slots, passive slots, toasts |
| `main.py` | LevelUpScreen polish, screen transitions, layout |
| `projectiles.py` | FloatingNumberManager expansion |
| `enemies.py` | Hitstop, sprite flash |
| `config.py` | Rarity colors, font config, outline toggle |
| `player.py` | Outline rendering |
| `weapons.py` | Rarity property, cooldown display |

## ⚠️ Risks
1. **FPS drop** — floating numbers + toasts + outline = дополнительная нагрузка. Mitigation: object pooling, max 50 floating numbers
2. **Font loading** — Press Start 2P может не загрузиться в pygbag. Mitigation: fallback на pygame default
3. **Complexity** — 17 шагов = большой scope. Mitigation: Phase 4.0 и 4.1 = MVP, остальное = polish
