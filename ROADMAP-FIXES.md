# Birth of the Saint — Code Review Fix Roadmap

## 🎯 Vision
Устранить 15 проблем найденных при code review: 2 критических бага, 4 проблемы производительности, 7 архитектурных, 2 качества кода. Проект остаётся стабильным (788/788 тестов) после каждого фикса.

## 📊 Format: Now-Next-Later

---

## 🔄 NOW — Критические + Быстрые победы (40 мин)

### Phase 1: Critical Fixes
**Goal:** Устранить баги которые ломают gameplay
**Status:** ⬜ Not started

#### Milestones:
- [ ] **BUG-1: spawn_damage is_crit** — criteria: WhipWeapon и LightningWeapon передают `is_crit` вместо `player` в `floating_numbers.spawn_damage()`. Обычные удары = белые, криты = жёлтые. Файл: weapons.py:298,575. Время: 5 мин. Риск: низкий.
- [ ] **BUG-2: CharSelectScene/StageSelectScene API** — criteria: оба класса наследуют `Scene`, имеют `handle_events(list)` вместо `handle_event(event)`. SceneManager не крашится при переходе. Файлы: char_select.py, stage_select.py. Время: 15 мин. Риск: средний.
- [ ] **QUAL-1: 47 unused импортов** — criteria: zero unused imports по результатам AST-анализа. 16 файлов. Время: 10 мин. Риск: низкий.
- [ ] **QUAL-2: damage_numbers_unused параметр** — criteria: удалён из сигнатуры всех 10 weapon update() + из вызова в main.py. Время: 10 мин. Риск: средний.

**Dependencies:** BUG-1 независимо. BUG-2 → ARCH-2, ARCH-4. QUAL-1 → QUAL-2.
**Test gate:** `python tests/test_phase25.py` — 788/788 после каждого milestone.

---

## ⏭️ NEXT — Производительность (50 мин)

### Phase 2: Performance Fixes
**Goal:** Убрать лишние аллокации каждый кадр
**Status:** ⬜ Not started

#### Milestones:
- [ ] **PERF-3: random.seed() глобальное состояние** — criteria: `random.seed(42)` и `random.seed(i*37)` в menu.py заменены на `random.Random(seed)` (локальный генератор). Глобальный random не затронут. Файл: menu.py. Время: 5 мин. Риск: низкий.
- [ ] **PERF-4: pygame.time.get_ticks() в headless** — criteria: `game_over_screen.py:422` использует `animator.timer` вместо `pygame.time.get_ticks()`. Кнопки пульсируют в headless тестах. Время: 3 мин. Риск: низкий.
- [ ] **PERF-1: Шрифты пересоздаются каждый кадр** — criteria: `_font_cache` модульный кэш добавлен в char_select.py, stage_select.py, game_over_screen.py, confirm_dialog.py. `pygame.font.Font(None, N)` вызывается 0 раз в draw(). Время: 10 мин. Риск: низкий.
- [ ] **PERF-2: Surface без кэша** — criteria: виньетка, арка, кнопки в menu.py/scenes.py/splash.py кэшированы. Dirty-флаг обновляет кэш при selection/resize. FPS ≥ 60 с 300 врагами. Время: 30 мин. Риск: средний.

**Dependencies:** Все независимы друг от друга.
**Test gate:** `python tests/test_phase25.py` — 788/788 + FPS check.

---

## 🔮 LATER — Архитектурный рефакторинг (115 мин)

### Phase 3: Architecture Cleanup
**Goal:** Единые источники правды, чистые интерфейсы
**Status:** ⬜ Not started

#### Milestones:
- [ ] **ARCH-5: Единый dict карт** — criteria: `MAP_DEFS` + `MAP_ORDER` в config.py. menu.py и stage_select.py импортируют оттуда, локальные MAPS/STAGES удалены. 4 карты (arena, cathedral, catacombs, hellgate). Файлы: config.py, menu.py, stage_select.py. Время: 15 мин. Риск: средний.
- [ ] **ARCH-3: Top-level import sound_manager** — criteria: `import sound_manager` добавлен в top-level lobby.py, menu.py, scenes.py, confirm_dialog.py. 38 inline импортов удалены. Нет циклических зависимостей. Время: 10 мин. Риск: низкий.
- [ ] **ARCH-4: Адаптер handle_event/handle_events** — criteria: `SceneManager.handle_events()` имеет адаптер — если сцена имеет `handle_event` (ед.ч.), вызывает его в цикле по events. Обратная совместимость сохранена. Файл: scene_manager.py. Время: 20 мин. Риск: средний.
- [ ] **ARCH-2: Убрать дублированный flow** — criteria: CharSelectScene и StageSelectScene удалены из регистрации в SceneManager (main.py:889-890). Файлы остаются как legacy. Lobby flow (LobbyScene → RunPrepScene → GameScene) — единственный рабочий путь. Время: 30 мин. Риск: высокий.
- [ ] **ARCH-6: Settings применяются** — criteria: `SettingsScene.apply()` вызывает `sound_manager.set_volume()` при изменении громкости. Значения восстанавливаются при `enter()`. Время: 20 мин. Риск: средний.
- [ ] **ARCH-7: PauseOverlay draw() ≤ 40 строк** — criteria: `PauseOverlay.draw()` разбит на 6 helper-методов (`_draw_arch_frame`, `_draw_title_plaque`, `_draw_stats_panel`, `_draw_tablets`, `_draw_candles`, `_draw_hint`). Арка кэширована. Поведение не изменилось. Время: 20 мин. Риск: низкий.

**Dependencies:** ARCH-4 зависит от BUG-2. ARCH-2 зависит от BUG-2.
**Test gate:** `python tests/test_phase25.py` — 788/788 после каждого milestone.

---

## 🔗 Dependency Map

```
Phase 1 (NOW)          Phase 2 (NEXT)         Phase 3 (LATER)
─────────────          ──────────────         ───────────────
BUG-1 ───────────┐
BUG-2 ───────────┼──→  PERF-3 ──────────┐
QUAL-1 ──────────┤     PERF-4 ──────────┤    ARCH-5 ──────────
QUAL-2 ──────────┤     PERF-1 ──────────┤    ARCH-3 ──────────
                 │     PERF-2 ──────────┤    ARCH-4 ←── BUG-2
                 │                      │    ARCH-2 ←── BUG-2
                 └──────────────────────┘    ARCH-6 ──────────
                                             ARCH-7 ──────────
```

## 📈 KPIs

| Метрика | Baseline | Target | Как мерить |
|---------|----------|--------|------------|
| Тесты | 788/788 | 788/788 | `python tests/test_phase25.py` |
| Критические баги | 2 | 0 | Code review items |
| Unused imports | 47 | 0 | AST analysis script |
| FPS (300 enemies) | ~45 | ≥60 | Stress test |
| PauseOverlay draw() | 190 строк | ≤40 строк | `wc -l` on methods |

## ⚠️ Top Risks

1. **ARCH-2 (удаление flow)** — может сломать menu→game переход если что-то зависит от CharSelectScene. Mitigation: проверить все пути вручную, оставить файлы как legacy.
2. **PERF-2 (Surface кэш)** — dirty-флаг может не обновиться при неожиданном событии. Mitigation: fallback на пересоздание при exception.
3. **QUAL-2 (удаление параметра)** — если где-то есть внешний код который вызывает weapon.update с 7 аргументами. Mitigation: grep перед удалением.

## 📍 Current State

**Мы здесь:** Phase 1, Milestone 0 (ничего не начато)
**Обновлено:** 2026-08-02
**Файлы:** `CODE-REVIEW-2026-08-02.md` (ревью), `FIX-PLAN-2026-08-02.md` (план), `ROADMAP-FIXES.md` (эта дорожная карта)

## 📅 Review Cadence

- **После Phase 1:** проверить что баги исправлены, тесты зелёные
- **После Phase 2:** замерить FPS, сравнить с baseline
- **После Phase 3:** полный code review повторить, убедиться что 0 проблем
