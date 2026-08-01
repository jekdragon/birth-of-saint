# UI REDESIGN ROADMAP — Рождение Святого

> Полный редизайн всех экранов и интерфейса.
> Цель: органичные переходы, живые фоны, единый стиль, компонентная система.
> Дата: 2026-08-02

---

## 1. КАРТА ЭКРАНОВ (новая архитектура)

```
                    ┌──────────────┐
                    │   SPLASH     │  3-5 сек, click to skip
                    │  (полноэкранный арт + particles)
                    └──────┬───────┘
                           │ fade 0.5s
                    ┌──────▼───────┐
                    │  TITLE MENU  │  3 кнопки: ИГРАТЬ / НАСТРОЙКИ / ВЫХОД
                    │  (heartbeat лого, blood drips, stone)
                    └──────┬───────┘
                           │ slide-left 0.4s
                    ┌──────▼───────┐
                    │    LOBBY     │  Всё-в-одном: 6 табов
                    │  (parallax bg, particles)
                    │  ┌─────────────────────────────────┐
                    │  │ ГЕРОИ │ КАРТЫ │ МАГАЗ │ КОДЕКС │ РЕКОРДЫ │ ПРОГРЕСС │
                    │  └─────────────────────────────────┘
                    └──────┬───────┘
                           │ fade-to-black 0.5s
                    ┌──────▼───────┐
                    │    GAME      │  gameplay + HUD
                    │  └───ESC───┐ │
                    │  │  PAUSE  │ │  (оверлей: confessional booth)
                    │  └─────────┘ │
                    └──────┬───────┘
                           │ death → fade-to-red 0.8s
                    ┌──────▼───────┐
                    │  GAME OVER   │  stats, build, leaderboard
                    │  (red vignette, quill reveal)
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   LOBBY      │  (возврат)
                    └──────────────┘

    OVERLAYS (могут открыться из любого места):
    - Settings (оверлей с любого экрана)
    - ConfirmDialog (поверх любого экрана)
    - LevelUpScreen (поверх Game)
```

### Ключевые изменения:
- **Title: 7 кнопок → 3.** ПЕРСОНАЖ, КАРТА, ПРОФИЛИ убраны в лобби.
- **CharSelect + StageSelect убраны** как отдельные сцены → встроены в лобби как табы.
- **Lobby: 5 табов → 6.** Добавлен таб "Кодекс" (бестарий + оружие + эволюции).
- **Bestiary/CodexScene убраны** как отдельные сцены → встроены в лобби.
- **Settings** — оверлей, открывается из любого места.

---

## 2. ЭЛЕМЕНТЫ КАЖДОГО ЭКРАНА

### Splash Screen
| Элемент | Позиция | Описание |
|---------|---------|----------|
| Background | full | Заставка.png с parallax ±20px |
| Particles | full | 80 gold/white, upward drift, flicker |
| Logo | top 20% | "РОЖДЕНИЕ СВЯТОГО", 56px, gold, heartbeat pulse |
| Subtitle | +50px под лого | "Гнев Небес", 24px, grey |
| Prompt | bottom 30% | "НАЖМИТЕ ДЛЯ НАЧАЛА", alpha pulse sin |
| Version | bottom-right | "v0.7.0", 14px, dim grey |

### Title Menu
| Элемент | Позиция | Описание |
|---------|---------|----------|
| Background | full | Stone texture + blood drips |
| Logo | top 30% | Heartbeat pulse, gold glow aura |
| Кнопки | center | 3 кнопки: ИГРАТЬ (gold), НАСТРОЙКИ (grey), ВЫХОД (red) |
| Version | bottom-right | Dim grey |

### Lobby (всё-в-одном)
| Элемент | Позиция | Описание |
|---------|---------|----------|
| Background | full | Dark parallax bg + floating particles |
| Tab bar | top | 6 табов: Герои / Карты / Магазин / Кодекс / Рекорды / Прогресс |
| Tab content | center | Содержимое выбранного таба |
| Навигация | bottom | "В ИГРУ" (если герой+карта выбраны), "НАЗАД" |
| Info panel | right | Детали выбранного элемента |

### Game HUD
| Элемент | Позиция | Описание |
|---------|---------|----------|
| HP bar | bottom-left | Candle HP bar (animated flame) |
| XP bar | top | Brazier XP bar (embers) |
| Timer | top-right | Elapsed time |
| Kill count | top-right, below timer | Running total |
| Weapons | bottom | 6 слотов с иконками + level |
| Passives | top, below XP | 6 слотов |
| Combo | floating | Elastic tween, tier-based |
| Boss HP | top-center | Animated boss bar (appears on boss) |
| Minimap | bottom-right | 120×120 corner map |

### Pause (оверлей)
| Элемент | Позиция | Описание |
|---------|---------|----------|
| Background | full | Confessional booth (wood slats + stone tablet) |
| Title | top | "ПАУЗА" |
| Weapons | center-top | Список оружия с level bar |
| Passives | center | Список пассивок |
| Stats | center-bottom | Time, kills, level, wave |
| Buttons | bottom | ПРОДОЛЖИТЬ / ВЫЙТИ В ЛОББИ |

### Game Over
| Элемент | Позиция | Описание |
|---------|---------|----------|
| Background | full | Red vignette, dark overlay |
| Title | top | "ПАЛ В БОЮ" — quill reveal |
| Stats | center | Stagger animation: wave, time, kills, level, gold |
| Build | center-bottom | Weapons + passives with rarity colors |
| Leaderboard | right | Top 5 scores |
| Buttons | bottom | ЗАНОВО / В ЛОББИ |

### Settings (оверлей)
| Элемент | Позиция | Описание |
|---------|---------|----------|
| Overlay | full | Dim + panel |
| Title | top | "НАСТРОЙКИ" |
| Sliders | center | SFX volume, Music volume |
| Toggle | center-bottom | Fullscreen toggle |
| Button | bottom | НАЗАД |

---

## 3. НАВИГАЦИЯ И УПРАВЛЕНИЕ

| Действие | Клавиатура | Мышь/Тач |
|----------|-----------|----------|
| Навигация | Up/Down или Left/Right | Hover + Click |
| Выбор | Enter/Space | Click |
| Назад | Escape | Кнопка "Назад" |
| Смена таба | Left/Right (в таб-баре) | Click на таб |
| Пауза | Escape (в игре) | — |

Правила:
- Wrap-around: конец → начало
- Hover + Focus работают одновременно
- Escape = "назад" везде, кроме геймплея (там = пауза)
- Звуки: hover (тихий), select (подтверждение), back (отмена)

---

## 4. ЦВЕТОВАЯ СИСТЕМА

| Роль | Цвет | Hex | Где |
|------|------|-----|-----|
| Фон | Near-black | #0a0e14 | Все экраны |
| Stone base | Dark purple-grey | #1c1820 | Title, panels |
| Stone hover | Lighter | #2a2630 | Hover states |
| Blood | Dark red | #8c1414 | Drips, accents |
| Gold leaf | Gold | #ffd700 | Заголовки, акценты |
| Gold idle | Muted gold | #b49600 | Неактивные акценты |
| Sacred | Cyan/Blue | #00bfff | Святые эффекты |
| Danger | Red | #dc2626 | Урон, Game Over |
| XP | Green→Gold | #44ff44→#ffd700 | XP bar |
| HP | Red | #ff3333 | HP bar |
| Text primary | White | #ffffff | Основной текст |
| Text secondary | Grey | #b4b4b4 | Описания |
| Text dim | Dim grey | #505050 | Версия, подсказки |
| Rarity common | Grey | #787878 | Common items |
| Rarity uncommon | Green | #50c850 | Uncommon |
| Rarity rare | Blue | #5078ff | Rare |
| Rarity epic | Purple | #b450ff | Epic |
| Rarity legendary | Gold | #ffb432 | Legendary |

---

## 5. ТИПОГРАФИКА

| Роль | Шрифт | Размер | Где |
|------|-------|--------|-----|
| Logo | big_font | 56px | Splash, Title |
| Заголовки экранов | big_font | 48px | Lobby, Game Over |
| Текст кнопок | font | 24px | Все кнопки |
| Tab labels | font | 22px | Tab bar |
| Описания | small_font | 18px | Подсказки, lore |
| Статы | small_font | 18px | HUD, Game Over |
| Version | small_font | 14px | Углы экранов |

---

## 6. АНИМАЦИИ И ПЕРЕХОДЫ

### Переходы между экранами
| Из | В | Анимация | Длительность |
|----|---|----------|-------------|
| Splash | Title | Fade-to-black | 0.5s |
| Title | Lobby | Slide-left | 0.4s |
| Lobby | Lobby (tab) | Crossfade content | 0.2s |
| Lobby | Game | Fade-to-black | 0.5s |
| Game | Game Over | Fade-to-red | 0.8s |
| Game Over | Lobby | Fade-to-black | 0.4s |
| Any → Settings | Overlay slide-down | 0.3s |
| Settings → Any | Overlay slide-up | 0.2s |

### Анимации элементов
| Элемент | Анимация | Длительность |
|---------|----------|-------------|
| Кнопки | Hover: scale 1.05 + glow | Instant |
| Кнопки | Appear: stagger fade-in + slide-up | 0.12s each |
| Tab switch | Content crossfade | 0.2s |
| HP bar | Pulse при <30% | 5Hz sin |
| XP bar | Burst на level up | 0.3s |
| Combo | Elastic tween scale | 0.5s |
| Game Over title | Quill reveal (letter-by-letter) | 0.05s/char |
| Stats | Stagger punch | 0.1s each |
| Particles | Continuous drift | Per-frame |
| Boss HP | Death rattle at <25% | Per-frame |

### Ease functions
```python
def ease_out_cubic(t): return 1.0 - (1.0 - t) ** 3
def ease_out_elastic(t): 
    if t <= 0 or t >= 1: return t
    return 2**(-10*t) * math.sin((t*10-0.75)*(2*math.pi)/3) + 1
def ease_in_out(t): return 3*t*t - 2*t*t*t
```

---

## 7. ЗВУКИ UI

| Действие | Звук | Описание |
|----------|------|----------|
| Hover на кнопке | ui_hover | Тихий клик |
| Выбор пункта | ui_select | Подтверждение |
| Назад | ui_back | Отмена |
| Подтверждение | ui_confirm | Финальное действие |
| Смерть | game_over | Мрачный аккорд |
| Level up | levelup | Колокольчик |
| Пауза | — | Тишина (mute) |

---

## 8. КОМПОНЕНТНАЯ БИБЛИОТЕКА (ui_components.py)

### 8.1 Button
- Состояния: default, hover, pressed, disabled, focused
- Варианты: primary (gold), default (grey), danger (red), ghost (transparent)
- Размеры: small (100×32), medium (160×40), large (240×50), custom
- Анимации: appear (stagger fade-in + slide-up), hover (scale 1.05 + glow), press (scale 0.98)

### 8.2 Panel
- Background: stone texture или parchment
- Border: gold-leaf frame или iron frame
- Padding: 16px
- Shadow: drop shadow (2px offset, 60 alpha)

### 8.3 TabBar
- Horizontal tabs with gold underline on active
- Keyboard: Left/Right to switch
- Mouse: click to switch
- Animation: crossfade content

### 8.4 Card
- Icon + Name + Description + Stats
- Hover: scale 1.05 + border glow
- Selected: gold border + fill brighter
- States: default, hover, selected, locked

### 8.5 Slider
- Track: filled + empty segments
- Handle: circle with glow
- Label + percentage text
- Keyboard: Left/Right ±5%
- Mouse: click to position

### 8.6 ProgressBar
- Animated fill with lerp
- Color transitions (green→yellow→red for HP)
- Pulse on change

### 8.7 Toast
- Slide-in from right, auto-fade after 2s
- Achievement: gold border + icon
- Info: grey border

### 8.8 ConfirmDialog
- Overlay dim + centered panel
- Title + body + ДА/НЕТ buttons
- Escape = cancel

### 8.9 ParticleSystem
- Configurable: count, colors, speed, size, alpha, direction
- Modes: upward, outward, random, attract
- Per-screen customization

### 8.10 Tooltip
- Appears on hover after 0.5s delay
- Follows cursor with offset
- Auto-clamp to screen bounds

---

## 9. ПРИОРИТЕТЫ РЕАЛИЗАЦИИ

| Фаза | Описание | Файлы | Зависимости |
|------|----------|-------|-------------|
| Phase 0 | Дизайн-система + компоненты | ui_components.py, ui_theme.py | — |
| Phase 1 | Animation engine + transitions | animation.py, scene_manager.py | Phase 0 |
| Phase 2 | Splash + Title | splash.py, menu.py | Phase 1 |
| Phase 3 | Lobby (всё-в-одном) | lobby.py, char_select.py, stage_select.py | Phase 2 |
| Phase 4 | HUD | hud.py | Phase 1 |
| Phase 5 | Pause + Game Over | scenes.py, game_over_screen.py | Phase 1 |
| Phase 6 | Settings | scenes.py | Phase 1 |
| Phase 7 | Интеграция + тесты | main.py, tests/ | All |

---

## 10. ЗАВИСИМОСТИ

```
Phase 0: ui_components.py, ui_theme.py
    └── Phase 1: animation.py, scene_manager.py обновлён
        ├── Phase 2: splash.py, menu.py
        ├── Phase 3: lobby.py (char_select + stage_select встроены)
        ├── Phase 4: hud.py
        ├── Phase 5: scenes.py (pause), game_over_screen.py
        └── Phase 6: scenes.py (settings)
            └── Phase 7: main.py интеграция + тесты
```

---

## PITFALLS

1. **Не ломать существующий gameplay** — Game логика (main.py Game class) НЕ трогаем, только UI-обёртки.
2. **Сохранить все данные** — MetaProgress, save_system, leaderboard API остаются как есть.
3. **WASM совместимость** — никаких внешних шрифтов/библиотек, только pygame.draw.
4. **Headless тесты** — все компоненты должны работать с SDL_VIDEODRIVER=dummy.
5. **Кэширование процедурных текстур** — генерировать один раз, переиспользовать.
6. **Не перегружать частицами** — 50-80 частиц на экран, не больше.
7. **Wrap-around навигация** — всегда, на всех списках и табах.
8. **Escape handler** — на каждом экране/оверлее.
9. **Sound sync** — каждый UI-действие = звук.
10. **Font caching** — создавать шрифты один раз, не в draw().
