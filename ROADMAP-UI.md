# ROADMAP-UI.md — UI Overhaul Roadmap

Полная дорожная карта обновления UI Birth of the Saint.
Каждый шаг: файл → dep-check → smoke test.

---

## Phase 4.0: Core HUD Redesign

### 4.0.1 Health Bar Overhaul
- Pre-edit: `hud.py`
- Change: AnimatedHealthBar класс (dual-bar, trailing damage)
- Post-edit: `hud.py`
- Dep-check: `main.py` (вызывает hud.draw), `player.py` (hp data)
- Smoke: HP bar отображается, trailing bar виден при получении урона

### 4.0.2 XP Bar Redesign
- Pre-edit: `hud.py`
- Change: AnimatedXPBar, full-width top bar с glow
- Post-edit: `hud.py`
- Dep-check: `main.py` (xp data), `config.py` (BAR_WIDTH)
- Smoke: XP bar вверху экрана, glow effect, smooth animation

### 4.0.3 HUD Layout Restructure
- Pre-edit: `hud.py`
- Change: Новый layout (XP top, HP top-left, weapons bottom)
- Post-edit: `hud.py`
- Dep-check: `main.py` (render order), `config.py` (screen size)
- Smoke: Все элементы HUD видны, не перекрывают друг друга

---

## Phase 4.1: Damage Numbers & Feedback

### 4.1.1 Floating Damage Numbers
- Pre-edit: `projectiles.py`
- Change: FloatingNumberManager (easing, alpha, variants)
- Post-edit: `projectiles.py`
- Dep-check: `main.py` (update/draw calls), `weapons.py` (spawn numbers)
- Smoke: Damage numbers появляются при ударах, исчезают с easing

### 4.1.2 Hit Feedback Enhancement
- Pre-edit: `enemies.py`, `main.py`
- Change: Hitstop 30ms, sprite flash, enhanced shake
- Post-edit: `enemies.py`, `main.py`
- Dep-check: `player.py` (hit detection), `weapons.py` (crit flag)
- Smoke: Визуальный feedback при ударах, криты видны

---

## Phase 4.2: Weapon & Inventory UI

### 4.2.1 Weapon Slot Icons
- Pre-edit: `hud.py`
- Change: 6 слотов с rarity border + cooldown overlay + level badge
- Post-edit: `hud.py`
- Dep-check: `weapons.py` (weapon data), `config.py` (RARITY_COLORS)
- Smoke: Все 6 слотов видны, cooldown работает

### 4.2.2 Passive Slot Icons
- Pre-edit: `hud.py`
- Change: 6 слотов пассивок с level badge
- Post-edit: `hud.py`
- Dep-check: `player.py` (passive data)
- Smoke: Пассивки отображаются, level badge корректен

### 4.2.3 Rarity Color System
- Pre-edit: `config.py`
- Change: RARITY_COLORS dict (5 уровней)
- Post-edit: `config.py`
- Dep-check: `hud.py`, `main.py` (LevelUpScreen), `weapons.py`
- Smoke: Цвета применяются к оружию и UI

---

## Phase 4.3: Notifications & Transitions

### 4.3.1 Toast Notification System
- Pre-edit: `hud.py`
- Change: Toast + ToastManager классы
- Post-edit: `hud.py`
- Dep-check: `main.py` (spawn toasts), `enemies.py` (kill events)
- Smoke: Toast появляются при событиях, анимация корректна

### 4.3.2 Level Up Screen Polish
- Pre-edit: `main.py`
- Change: Rarity border, описание, hover effect
- Post-edit: `main.py`
- Dep-check: `weapons.py` (rarity data), `hud.py` (fonts)
- Smoke: LevelUpScreen отображается с новым дизайном

### 4.3.3 Screen Transitions
- Pre-edit: `main.py`
- Change: ScreenFader класс (fade out/in 0.3с)
- Post-edit: `main.py`
- Dep-check: None (isolated)
- Smoke: Переходы между экранами с fade

---

## Phase 4.4: Visual Polish

### 4.4.1 Player Outline Toggle
- Pre-edit: `player.py`, `config.py`
- Change: draw_with_outline(), toggle key O
- Post-edit: `player.py`, `config.py`
- Dep-check: `main.py` (key handling)
- Smoke: Outline виден, toggle работает

### 4.4.2 Projectile Color Coding
- Pre-edit: `projectiles.py`, `weapons.py`
- Change: Тёплые = игрок, холодные = враги
- Post-edit: `projectiles.py`, `weapons.py`
- Dep-check: `enemies.py` (enemy projectiles)
- Smoke: Визуальное различие снарядов

### 4.4.3 Pixel Font Integration
- Pre-edit: `config.py`, `hud.py`
- Change: Загрузка Press Start 2P + VT323, fallback
- Post-edit: `config.py`, `hud.py`
- Dep-check: `main.py` (font init)
- Smoke: Шрифты загружаются, fallback работает

---

## Phase 4.5: Final Integration

### 4.5.1 Smoke Test
- Pre-edit: None
- Change: 15 минут без краша с новым HUD
- Post-edit: None
- Dep-check: Все файлы Phase 4
- Smoke: 15 минут, FPS ≥ 55

### 4.5.2 Visual Verification
- Pre-edit: None
- Change: Скриншоты всех экранов
- Post-edit: None
- Dep-check: None
- Smoke: Все скриншоты сохранены

### 4.5.3 pygbag Rebuild
- Pre-edit: None
- Change: `python -m pygbag --build --html --disable-sound-format-error .`
- Post-edit: None
- Dep-check: None
- Smoke: Browser test OK

---

## 📊 Итого

| Phase | Steps | Файлы | Priority |
|-------|-------|-------|----------|
| 4.0 Core HUD | 3 | hud.py | P0 |
| 4.1 Damage | 2 | projectiles.py, enemies.py, main.py | P0 |
| 4.2 Weapon UI | 3 | hud.py, config.py | P1 |
| 4.3 Notifications | 3 | hud.py, main.py | P1 |
| 4.4 Polish | 3 | player.py, projectiles.py, weapons.py, config.py, hud.py | P2 |
| 4.5 Integration | 3 | All | P0 |
| **Total** | **17** | **7 файлов** | |

## 🔗 Критический путь
4.0.1 → 4.0.2 → 4.0.3 → 4.1.1 → 4.2.1 → 4.3.1 → 4.5.1

## ⚠️ Blockers
- Phase 3.5 VFX Integration (complete ✅)
- sprite-gen v2.1 (complete ✅)
- Press Start 2P font file (нужно скачать)
