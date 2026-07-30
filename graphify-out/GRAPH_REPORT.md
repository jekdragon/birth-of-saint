# Graph Report - birth-of-saint  (2026-07-30)

## Corpus Check
- 26 files · ~15,627 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 331 nodes · 560 edges · 15 communities
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `387a43d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DamageNumber
- config.py
- main.py
- Боевая система — "Рождение святого"
- test_phase25.py
- Рождение святого — SPEC.md
- Enemy
- Рождение святого — ROADMAP
- AGENTS.md — Birth of the Saint
- MainMenu
- Рождение святого
- MetaProgress
- SoundManager
- Obstacle
- Assets — Рождение святого

## God Nodes (most connected - your core abstractions)
1. `Game` - 25 edges
2. `DamageNumber` - 22 edges
3. `Рождение святого — SPEC.md` - 21 edges
4. `Player` - 20 edges
5. `Weapon` - 19 edges
6. `Particle` - 18 edges
7. `Pulse` - 18 edges
8. `Enemy` - 15 edges
9. `WaveManager` - 15 edges
10. `Projectile` - 14 edges

## Surprising Connections (you probably didn't know these)
- `Game` --uses--> `ScreenShake`  [INFERRED]
  main.py → effects.py
- `Game` --uses--> `ScreenFlash`  [INFERRED]
  main.py → effects.py
- `Game` --uses--> `Enemy`  [INFERRED]
  main.py → enemies.py
- `Game` --uses--> `MetaProgress`  [INFERRED]
  main.py → lobby.py
- `Game` --uses--> `LobbyScreen`  [INFERRED]
  main.py → lobby.py

## Import Cycles
- None detected.

## Communities (15 total, 0 thin omitted)

### Community 0 - "DamageNumber"
Cohesion: 0.08
Nodes (19): DamageNumber, Particle, Projectile, Pulse, Surface, Рождение святого — Projectiles & Particles Снаряды, частицы, визуальные эффекты, Расширяющийся круг (для AoE атак)., Короткоживущая частица (спарк при попадании). (+11 more)

### Community 1 - "config.py"
Cohesion: 0.11
Nodes (14): calc_area_mult(), calc_cooldown_mult(), calc_damage_mult(), calc_max_hp(), calc_pickup_range(), calc_regen(), calc_speed_mult(), Рождение святого — Configuration Все константы, настройки экрана, формулы. (+6 more)

### Community 2 - "main.py"
Cohesion: 0.07
Nodes (23): Camera, Рождение святого — Camera Камера следит за игроком, скроллит карту., Следит за целевой позицией (игрок)., calc_xp_for_level(), XP, необходимый для перехода на следующий уровень., Game, init_pygame(), init_sounds() (+15 more)

### Community 3 - "Боевая система — "Рождение святого""
Cohesion: 0.06
Nodes (31): 10. Техническая архитектура (для реализации), 1.1 Святой кнут (Starter — Воин), 1.2 Священный огонь (Sacred Fire), 1.3 Орбитальная аура (Holy Halo), 1.4 Чётки (Rosary), 1.5 Божественная молния (Divine Lightning), 1.6 Молитвенная волна (Prayer Wave), 1. Оружие (до 6 слотов) (+23 more)

### Community 4 - "test_phase25.py"
Cohesion: 0.11
Nodes (13): draw_grid(), get_biome(), Surface, Рождение святого — Visual Effects Screen shake, flash, grid rendering., Определяет биом по расстоянию от центра карты., Рисует фоновую сетку с учётом биома., ScreenFlash, ScreenShake (+5 more)

### Community 5 - "Рождение святого — SPEC.md"
Cohesion: 0.08
Nodes (25): HUD, MVP чек-лист, User Flow, Визуальный стиль, Враги, Выбор персонажа, Запуск, Звуки (+17 more)

### Community 6 - "Enemy"
Cohesion: 0.11
Nodes (14): Enemy, Surface, Vector2, Рождение святого — Enemies Типы врагов, спавн, AI, урон., Возвращает True если враг умер., Vector2, Рождение святого — Wave Manager Система волн: спавн врагов, нарастающая сложност, Рой — много врагов с одной стороны. (+6 more)

### Community 7 - "Рождение святого — ROADMAP"
Cohesion: 0.10
Nodes (20): 📍 Current State, 🔗 Dependency Map, 📊 Format: Now-Next-Later, 📈 KPIs, 🔮 Later — Phase 3: Расширение, 🔮 Later — Phase 4: Публикация, Milestones, Milestones (+12 more)

### Community 8 - "AGENTS.md — Birth of the Saint"
Cohesion: 0.17
Nodes (11): AGENTS.md — Birth of the Saint, Commands, Critical Files (do NOT edit without impact check), Meta-progression (между ранами), Project, Rules, Session, Setting (+3 more)

### Community 9 - "MainMenu"
Cohesion: 0.36
Nodes (3): MainMenu, Surface, Возвращает: 'start', 'char_select', None

### Community 10 - "Рождение святого"
Cohesion: 0.22
Nodes (8): Запуск, Запуск в браузере (pygbag), Лицензия, Оружие, Персонажи, Рождение святого, Стек, Управление

### Community 11 - "MetaProgress"
Cohesion: 0.12
Nodes (9): LobbyScreen, MetaProgress, Surface, Рождение святого — Lobby Магазин PowerUp между ранами. Достижения. Мета-прогресс, Возвращает: 'play', None, Глобальный прогресс между ранами., Возвращает бонус от powerup., Проверяет и разблокирует достижения. (+1 more)

### Community 12 - "SoundManager"
Cohesion: 0.32
Nodes (3): Sound, Рождение святого — Sound System Генерация звуков через synth (без внешних файлов, SoundManager

### Community 13 - "Obstacle"
Cohesion: 0.33
Nodes (4): Obstacle, Surface, Vector2, Проверяет коллизию с объектом.

### Community 14 - "Assets — Рождение святого"
Cohesion: 0.40
Nodes (4): Assets — Рождение святого, Правила, Структура, Цветовые палитры (для генерации спрайтов)

## Knowledge Gaps
- **80 isolated node(s):** `Project`, `Stack`, `Setting`, `Session`, `Visual` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Game` connect `main.py` to `DamageNumber`, `config.py`, `test_phase25.py`, `Enemy`, `MainMenu`, `MetaProgress`, `SoundManager`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `Player` connect `config.py` to `main.py`, `test_phase25.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `WaveManager` connect `Enemy` to `main.py`, `test_phase25.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Game` (e.g. with `Camera` and `ScreenFlash`) actually correct?**
  _`Game` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `DamageNumber` (e.g. with `Game` and `FireWeapon`) actually correct?**
  _`DamageNumber` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Weapon` (e.g. with `DamageNumber` and `Particle`) actually correct?**
  _`Weapon` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Project`, `Stack`, `Setting` to the rest of the system?**
  _80 weakly-connected nodes found - possible documentation gaps or missing edges._