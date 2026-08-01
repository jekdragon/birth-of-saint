# Birth of the Saint — UI Polish Roadmap v2

> Дата: 2026-08-01
> Источники: 3 web-ресерча (game juice, dark fantasy UI, VS-like UX)
> Статус: В очереди

---

## Направление A: Game Juice (5 шагов)

### A1. Hitstop + Selective Freeze
**Улучшение:** При попадании по врагу — короткая заморозка (2-6 кадров) только для атакующего и цели. Камера и фон продолжают работать.
**Источник:** Game juice research 2025
**Файлы:** enemies.py (freeze flag), weapons.py (trigger), main.py (skip update)
**Приоритет:** Высокий — самый ощутимый эффект за минимальный код

### A2. Directional Shake + Camera Kick
**Улучшение:** Заменить случайный screen shake на направленный (в сторону удара). Однокадровый kick при сильном попадании.
**Источник:** Game juice research 2025
**Файлы:** main.py (CameraShake class), enemies.py (direction on hit)
**Приоритет:** Высокий — drop-in replacement существующего shake

### A3. Tiered Hit Particles
**Улучшение:** 4 уровня частиц при ударе (light/medium/heavy/crit). Крит = 30+ частиц с магентой. Убийство = burst с кольцом.
**Источник:** Game juice research 2025
**Файлы:** projectiles.py (PARTICLE_PRESETS, emit_hit_burst)
**Приоритет:** Средний — уже есть базовые частицы

### A4. Combo Counter с Escalation
**Улучшение:** Счётчик комбо (2с таймер). 5 убийств = scale pulse. 15 = edge flash. 30 = slowmo 4 кадра. 100 = "MASSACRE" + white flash.
**Источник:** Game juice research 2025
**Файлы:** hud.py (ComboSystem + draw), main.py (register_kill)
**Приоритет:** Средний — уже есть базовый combo counter

### A5. Boss HP Bar с Death Rattle
**Улучшение:** Boss HP bar: серый trailing bar + cyan flash при armor hit + shake при <25%. Сегментированная полоска.
**Источник:** Game juice research 2025
**Файлы:** hud.py (AnimatedBossHealthBar), enemies.py (boss flag)
**Приоритет:** Низкий — только для боссов

---

## Направление B: Dark Fantasy UI (5 шагов)

### B1. Sacred Bleed — переработка MainMenu
**Улучшение:** Каменный алтарь-триптих вместо blur-фона. Кровь, сочащаяся по камню. Золотые рамки. Пульсирующее свечение.
**Источник:** Dark fantasy UI research 2025
**Файлы:** menu.py (draw_main), assets/ (текстуры)
**Приоритет:** Высокий — первое что видит игрок

### B2. Census of the Damned — переработка Bestiary
**Улучшение:** Витражная сетка вместо плоского списка. Стеклянные осколки для locked. Свет через стекло для unlocked. Пергаментные панели.
**Источник:** Dark fantasy UI research 2025
**Файлы:** bestiary.py (draw)
**Приоритет:** Средний

### B3. Pyre of Grace — HP bar как свеча
**Улучшение:** HP bar = свеча с 5 состояниями пламени. Wax-drip при уроне. XP bar = бrazier с sacred fire.
**Источник:** Dark fantasy UI research 2025
**Файлы:** hud.py (AnimatedHealthBar)
**Приоритет:** Средний — сложная графика

### B4. Catechism of Ruin — текст как манускрипт
**Улучшение:** Все текстовые элементы в стиле illuminated manuscript. Torn parchment backgrounds. Quill-scratch reveal анимация.
**Источник:** Dark fantasy UI research 2025
**Файлы:** все UI-файлы (шрифты, стили)
**Приоритет:** Низкий — требует кастомных шрифтов

### B5. The Confessional — пауза как исповедальня
**Улучшение:** Экран паузы = деревянная исповедальня. Меню items = каменные таблички. Слайдеры = песочные часы. Toggle = крест-молоток.
**Источник:** Dark fantasy UI research 2025
**Файлы:** scenes.py (PauseOverlay draw)
**Приоритет:** Низкий

---

## Направление C: VS-like UX (5 шагов)

### C1. Item Ban System
**Улучшение:** Бан до 8 нежелательных предметов из пула левелапа. Токены = награда за достижения.
**Источник:** Brotato "New Dawn" DLC 2025
**Файлы:** lobby.py (бан-меню), xp_system.py (фильтр)
**Приоритет:** Высокий — огромный QoL при низкой стоимости

### C2. In-Game Codex (расширенный бестиарий)
**Улучшение:** Бестиарий + описание оружия + скрытые рецепты эволюций. Kill tracking. Не нужно alt-tab.
**Источник:** Brotato, HoloCure, Halls of Torment
**Файлы:** bestiary.py (расширение), codex.py (новый)
**Приоритет:** Средний — уже есть бестиарий

### C3. Rune Socketing
**Улучшение:** 3 слота рун на оружие (уровни 1/5/10). Руны от боссов. Модифицируют поведение оружия.
**Источник:** Conquest Dark 2025
**Файлы:** weapons.py (rune slots), lobby.py (rune UI)
**Приоритет:** Низкий — новая механика

### C4. Multi-Vector Meta-Progression
**Улучшение:** 4+ независимых линии прогресса (altars, weapon archive, factions, obelisks). Каждый ран что-то продвигает.
**Источник:** Conquest Dark, Ascend to Zero
**Файлы:** lobby.py (новые табы), save_system.py
**Приоритет:** Средний

### C5. Save Profiles + Run Prep Screen
**Улучшение:** 3 слота сохранений. Pre-run экран выбора loadout перед стартом.
**Источник:** Brotato "New Dawn", HoloCure v0.7
**Файлы:** save_system.py (profiles), scenes.py (RunPrepScene)
**Приоритет:** Средний

---

## Порядок реализации (по ROI)

| # | Шаг | Направление | Время | Описание |
|---|------|-------------|-------|----------|
| 1 | A1 | Juice | 20м | Hitstop + selective freeze |
| 2 | A2 | Juice | 15м | Directional shake + camera kick |
| 3 | C1 | UX | 25м | Item ban system |
| 4 | A3 | Juice | 20м | Tiered hit particles |
| 5 | B1 | UI | 30м | Sacred Bleed main menu |
| 6 | A4 | Juice | 25м | Combo counter escalation |
| 7 | C2 | UX | 30м | In-game codex |
| 8 | B2 | UI | 25м | Census of the Damned bestiary |
| 9 | A5 | Juice | 20м | Boss HP bar death rattle |
| 10 | C4 | UX | 35м | Multi-vector meta-progression |
| 11 | B3 | UI | 30м | Pyre of Grace HP bar |
| 12 | C5 | UX | 25м | Save profiles + run prep |
| 13 | B4 | UI | 30м | Catechism of Ruin text |
| 14 | C3 | UX | 30м | Rune socketing |
| 15 | B5 | UI | 25м | The Confessional pause |

**Общее время: ~6.5 часов**

---

## Исследовательские файлы
- `C:\Users\jekdr\AppData\Local\hermes\cache\delegation\subagent-summary-0-20260801_002959_942353.txt` — Game Juice
- `C:\Users\jekdr\oko\agent-roadmap\birth-of-saint-ui-research-2026.md` — Dark Fantasy UI
- `C:\Users\jekdr\survivors-like-uiux-research.md` — VS-like UX
