# Birth of the Saint — Сводный Code Review
> Дата: 2026-08-02 | Файлов: 32 | Строк: ~10,000 | Тестов: 788/788

---

## I. КРИТИЧЕСКИЕ БАГИ (краш / неверное поведение)

### BUG-1: player передаётся как is_crit в spawn_damage
- **Файл:** weapons.py:298, weapons.py:575
- **Суть:** `floating_numbers.spawn_damage(x, y, dmg, color, player)` — 5-й аргумент `is_crit=False`, а передаётся объект Player (truthy)
- **Эффект:** каждый удар показывается как критический (жёлтый, увеличенный)
- **Затронутые оружия:** WhipWeapon, LightningWeapon
- **Фикс:** заменить `player` на `is_crit` (переменная уже вычислена строкой выше)

### BUG-2: CharSelectScene / StageSelectScene — сломан API
- **Файл:** char_select.py:10, stage_select.py:38
- **Суть:** не наследуют `Scene`, имеют `handle_event()` (ед.ч.) вместо `handle_events()` (мн.ч.)
- **Эффект:** `SceneManager.handle_events()` вызывает `scene.handle_events(events)` → AttributeError при переходе на "char_select" или "stage_select"
- **Почему не крашится сейчас:** lobby flow идёт через RunPrepScene, эти экраны не активируются
- **Фикс:** наследовать от Scene, переименовать handle_event → handle_events, принимать list

---

## II. ПРОБЛЕМЫ ПРОИЗВОДИТЕЛЬНОСТИ

### PERF-1: Шрифты пересоздаются каждый кадр
- **Где:** char_select.py:56-58, stage_select.py:67-69, game_over_screen.py:246-250, confirm_dialog.py:73-75
- **Что:** `pygame.font.Font(None, N)` вызывается в draw(), ~8 раз/кадр
- **Правильно:** scenes.py использует `_font_cache` — образец для остальных
- **Фикс:** модульный кэш или передавать шрифты через параметры

### PERF-2: Surface создаётся каждый кадр без кэша
- **menu.py:** 13 Surface() — виньетка, кнопки, свечения
- **scenes.py:** 9 Surface() — арка, таблички, пергамент PauseOverlay
- **splash.py:** 6 Surface() — частицы, fade оверлеи
- **Фикс:** кэшировать статичные элементы (виньетка, арка, дерево), обновлять только при resize

### PERF-3: random.seed() ломает глобальное состояние
- **Где:** menu.py:137 (`seed(42)`), menu.py:488 (`seed(i*37)`)
- **Эффект:** сбивает последовательность глобального random (частицы, спавн)
- **Фикс:** `rng = random.Random(seed)` — локальный генератор

### PERF-4: pygame.time.get_ticks() в headless
- **Где:** game_over_screen.py:422
- **Эффект:** не работает в dummy SDL (тесты), кнопки не пульсируют
- **Фикс:** считать от animator.timer

---

## III. АРХИТЕКТУРНЫЕ ПРОБЛЕМЫ

### ARCH-1: Дублированный unused import DamageNumber
- **Где:** main.py:15, weapons.py:780
- **Суть:** `DamageNumber` импортируется но не используется напрямую (используется через floating_numbers)
- **Дополнительно:** 47 unused импортов по всему проекту (config.py, bestiary.py, cathedral.py и др.)
- **Фикс:** удалить неиспользуемые импорты

### ARCH-2: Два параллельных flow для выбора персонажа/карты
- **Menu flow:** MainMenu → state="char_select"/"map_select" (внутренний стейт-машина)
- **Lobby flow:** LobbyScene → RunPrepScene → GameScene
- CharSelectScene и StageSelectScene зарегистрированы в SceneManager, но не используются
- **Фикс:** удалить дубли или объединить в один flow

### ARCH-3: 38 inline `import sound_manager` внутри методов
- lobby.py — 22, menu.py — 7, scenes.py — 4, confirm_dialog.py — 4
- Каждый import — lookup в sys.modules (~нс, но антипаттерн)
- **Фикс:** top-level import или модульный кэш

### ARCH-4: Несогласованные сигнатуры handle_event/handle_events
| Класс | Сигнатура | Принимает |
|-------|-----------|-----------|
| Scene (базовый) | handle_events(events) | list |
| PauseOverlay | handle_events(events) | list |
| MainMenu | handle_event(event) | один event |
| LobbyScreen | handle_event(event) | один event |
| BestiaryScreen | handle_event(event) | один event |
| CodexScreen | handle_event(event) | один event |
| CharSelectScene | handle_event(event) | один event |
| StageSelectScene | handle_event(event) | один event |
| ConfirmDialog | handle_event(event) | один event |
- SceneManager ожидает handle_events (мн.ч.) у всех зарегистрированных сцен
- **Фикс:** единый интерфейс — либо все handle_events(list), либо SceneManager вызывает handle_event в цикле

### ARCH-5: STAGES не синхронизированы с MAPS
- stage_select.py: cathedral, catacombs, hellgate
- menu.py: arena, cathedral
- Два независимых источника правды
- **Фикс:** единый dict карт в config.py

### ARCH-6: Settings не применяются
- SettingsScene хранит volume/fullscreen/show_fps, но не вызывает pygame.mixer / display
- **Фикс:** применять значения при изменении и при закрытии экрана

### ARCH-7: PauseOverlay — 190 строк в draw()
- scenes.py:370-560 — генерация дерева, арки, табличек, частиц, свечей inline
- **Фикс:** вынести в helper-функции, кэшировать статичные элементы

---

## IV. КАЧЕСТВО КОДА

### QUAL-1: 47 unused импортов
- config.py (math), bestiary.py (RED, GREEN, PARCH_DARK/MID/BASE/LIGHT), cathedral.py (random, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE), effects.py (MAP_WIDTH, MAP_HEIGHT), enemies.py (WHITE), game_over_screen.py (DARK_BG, WEAPON_DEFS, generate_parchment, PARCH_*), main.py (DamageNumber, Particle, pygame.math, ENEMY_TYPES, PauseOverlay, _tb, CATHEDRAL_COLORS), menu.py (DARK_BG, RED), music.py (random), obstacles.py (MAP_WIDTH, MAP_HEIGHT, TILE_SIZE), relics.py (GREEN), scenes.py (RED), stage_select.py (GREEN), wave_manager.py (CENTER_X, CENTER_Y), weapons.py (calc_damage_mult, calc_cooldown_mult, calc_area_mult, RUNE_DEFS, Pulse, make_damage_number, DamageNumber, Particle)

### QUAL-2: damage_numbers_unused — мёртвый параметр
- Все 10 weapon update() принимают `damage_numbers_unused` — параметр-заглушка из прошлой версии API
- **Фикс:** удалить из сигнатуры

---

## V. ЧТО РАБОТАЕТ ХОРОШО

- ✅ 224/224 символов проверено — ноль битых импортов
- ✅ 788/788 тестов зелёные
- ✅ Нет циклических зависимостей
- ✅ SceneManager — чистая архитектура, overlay pattern
- ✅ FadeManager — простой и правильный
- ✅ SplashScreen — красивый параллакс с частицами
- ✅ GameOverAnimator — каскадная анимация с фазами
- ✅ generate_parchment — процедурные текстуры с кэшированием
- ✅ ConfessionalCandle — __slots__ для частиц
- ✅ B5 Confessional Pause — визуально сильно
- ✅ FloatingNumberManager — централизованное управление числами
- ✅ Комбо-система с эластичным tween
- ✅ Boss HP Bar с delayed trail и death rattle

---

## VI. ИТОГО

| Категория | Кол-во | Приоритет |
|-----------|--------|-----------|
| Критические баги | 2 | 🔴 Фиксить сразу |
| Производительность | 4 | 🟡 Оптимизировать |
| Архитектурные | 7 | 🟠 Рефакторинг |
| Качество кода | 2 | 🟢 Чистка |
| **Всего** | **15** | |

### Рекомендуемый порядок фиксов:
1. BUG-1 (spawn_damage is_crit) — 2 строки, мгновенный эффект
2. BUG-2 (CharSelectScene API) — наследование + переименование
3. QUAL-1 (unused imports) — bulk удаление
4. PERF-3 (random.seed) — замена на Random(seed)
5. ARCH-5 (единый dict карт) — config.py
6. PERF-1 (шрифты) — кэширование
7. ARCH-3 (inline imports) — top-level
8. ARCH-4 (сигнатуры) — единый интерфейс
9. Остальное — по мере необходимости
