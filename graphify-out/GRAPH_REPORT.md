# Graph Report - birth-of-saint  (2026-07-30)

## Corpus Check
- 22 files · ~12,098 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 283 nodes · 449 edges · 11 communities
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 41 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b786b35c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DamageNumber
- config.py
- Game
- Боевая система — "Рождение святого"
- main.py
- Рождение святого — SPEC.md
- WaveManager
- Рождение святого — ROADMAP
- AGENTS.md — Birth of the Saint
- MainMenu
- Рождение святого

## God Nodes (most connected - your core abstractions)
1. `Game` - 21 edges
2. `DamageNumber` - 21 edges
3. `Рождение святого — SPEC.md` - 21 edges
4. `Player` - 19 edges
5. `Weapon` - 19 edges
6. `Particle` - 17 edges
7. `Pulse` - 17 edges
8. `Рождение святого — ROADMAP` - 14 edges
9. `Projectile` - 13 edges
10. `LevelUpScreen` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Game` --uses--> `ScreenShake`  [INFERRED]
  main.py → effects.py
- `Game` --uses--> `ScreenFlash`  [INFERRED]
  main.py → effects.py
- `Game` --uses--> `MainMenu`  [INFERRED]
  main.py → menu.py
- `Game` --uses--> `Player`  [INFERRED]
  main.py → player.py
- `Game` --uses--> `DamageNumber`  [INFERRED]
  main.py → projectiles.py

## Import Cycles
- None detected.

## Communities (11 total, 0 thin omitted)

### Community 0 - "DamageNumber"
Cohesion: 0.08
Nodes (19): DamageNumber, Particle, Projectile, Pulse, Surface, Рождение святого — Projectiles & Particles Снаряды, частицы, визуальные эффекты, Расширяющийся круг (для AoE атак)., Короткоживущая частица (спарк при попадании). (+11 more)

### Community 1 - "config.py"
Cohesion: 0.09
Nodes (16): Рождение святого — Camera Камера следит за игроком, скроллит карту., calc_area_mult(), calc_cooldown_mult(), calc_damage_mult(), calc_max_hp(), calc_pickup_range(), calc_regen(), calc_speed_mult() (+8 more)

### Community 2 - "Game"
Cohesion: 0.09
Nodes (14): Camera, Следит за целевой позицией (игрок)., calc_xp_for_level(), XP, необходимый для перехода на следующий уровень., Game, create_weapon(), LevelUpScreen, Surface (+6 more)

### Community 3 - "Боевая система — "Рождение святого""
Cohesion: 0.06
Nodes (31): 10. Техническая архитектура (для реализации), 1.1 Святой кнут (Starter — Воин), 1.2 Священный огонь (Sacred Fire), 1.3 Орбитальная аура (Holy Halo), 1.4 Чётки (Rosary), 1.5 Божественная молния (Divine Lightning), 1.6 Молитвенная волна (Prayer Wave), 1. Оружие (до 6 слотов) (+23 more)

### Community 4 - "main.py"
Cohesion: 0.09
Nodes (17): draw_grid(), Surface, Рождение святого — Visual Effects Screen shake, flash, grid rendering., Рисует фоновую сетку., ScreenFlash, ScreenShake, draw_hud(), Surface (+9 more)

### Community 5 - "Рождение святого — SPEC.md"
Cohesion: 0.08
Nodes (25): HUD, MVP чек-лист, User Flow, Визуальный стиль, Враги, Выбор персонажа, Запуск, Звуки (+17 more)

### Community 6 - "WaveManager"
Cohesion: 0.13
Nodes (10): Enemy, Surface, Vector2, Рождение святого — Enemies Типы врагов, спавн, AI, урон., Возвращает True если враг умер., Рождение святого — Wave Manager Система волн: спавн врагов, нарастающая сложност, Возвращает типы врагов, доступные на текущей волне., Спавнит врага за экраном. (+2 more)

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

## Knowledge Gaps
- **77 isolated node(s):** `Project`, `Stack`, `Setting`, `Session`, `Visual` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Game` connect `Game` to `DamageNumber`, `config.py`, `main.py`, `WaveManager`, `MainMenu`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `Player` connect `config.py` to `Game`, `main.py`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `WaveManager` connect `WaveManager` to `Game`, `main.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Game` (e.g. with `Camera` and `ScreenFlash`) actually correct?**
  _`Game` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `DamageNumber` (e.g. with `Game` and `FireWeapon`) actually correct?**
  _`DamageNumber` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Weapon` (e.g. with `DamageNumber` and `Particle`) actually correct?**
  _`Weapon` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Project`, `Stack`, `Setting` to the rest of the system?**
  _77 weakly-connected nodes found - possible documentation gaps or missing edges._