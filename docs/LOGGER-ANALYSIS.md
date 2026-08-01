# Анализ: Аномалии и Ввод (глубокая проработка)

## 5. АНОМАЛИИ — что ловим и почему

### 5.1 Entity Lifecycle (утечки объектов)

| Что | Как ловим | Почему важно |
|-----|-----------|-------------|
| Dead enemy не удалён | `alive=False` + `hp<=0` + есть в списке enemies | Утечка памяти, slowdown |
| Projectile живёт вечно | `alive=True` + `lifetime<=0` | Утечка памяти |
| XPGem не подобран | `alive=True` + `age > 30 сек` | Утечка памяти, грязь на карте |
| GoldCoin истёк | `alive=True` + `lifetime<=0` | Утечка памяти |
| Particles > 500 | `len(particles) > 500` | FPS drop |
| Ring burst завис | `alive=True` + `duration<=0` | Визуальный баг |
| Enemy projectile остался | вражеский снаряд жив, а враг мёртв давно | unfair урон |

### 5.2 Player State (невозможные состояния)

| Что | Порог | Откуда берётся |
|-----|-------|---------------|
| HP < 0 | hp < 0 | take_damage не клампает (множественный урон за кадр) |
| HP > max_hp | hp > max_hp * 1.05 | regen тикает после pickup max_hp реликвии |
| Level без XP | level_up вызван но xp < xp_required | ошибка в calc_xp_for_level |
| Speed <= 0 | speed_mult <= 0 | множественные slow стакаются |
| Gold < 0 | gold < 0 | покупка при race condition |
| Weapon > MAX_LEVEL | weapon.level > 8 | ошибка в levelup |
| Passive > MAX_LEVEL | passive_level > 5 | ошибка в levelup |
| Weapons > 6 | len(weapons) > 6 | ошибка в levelup (не проверяет лимит) |
| Passives > 6 | len(passives) > 6 | ошибка в levelup |

### 5.3 Combat (логика боя)

| Что | Как ловим | Баг-источник |
|-----|-----------|-------------|
| Zero damage hit | damage==0 и enemy.hp не изменился | weapon с damage_mult=0 |
| Negative damage (heal) | damage < 0 | damage_mult стал отрицательным |
| Duplicate kill | `_on_killed_called=True` но kill уже засчитан | melee + projectile одновременно |
| Kill без gem drop | enemy dead + `_gem_dropped` не установлен | exception в on_enemy_killed |
| Boss без дропа | boss dead + нет сундука/гема | `_gem_dropped` race |
| Hitstop infinite | `freeze_frames > 0` после 60 кадров | не декрементится |
| Slow factor < 0 | `slow_factor < 0` | min() не клампает к 0 |
| Burn dps = 0 | `burn_timer > 0` но `burn_dps == 0` | rune не установил dps |
| Evolution без пассивки | evolution triggered но passive_level < 3 | ошибка проверки |

### 5.4 Wave/Spawn (система волн)

| Что | Как ловим | Проблема |
|-----|-----------|---------|
| Enemy count > MAX | `len(enemies) > 300` | map events игнорируют лимит |
| Spawn за картой | `x < 0` или `x > MAP_WIDTH` | SPAWN_DISTANCE от камеры за краем |
| Boss duplicate | два boss alive одновременно | `boss_alive` не сбросился |
| Wave timer drift | `abs(wave_timer - wave*WAVE_DURATION) > 5 сек` | float drift |
| No enemies spawned | wave начался но 0 врагов за 10 сек | spawn_interval = inf? |
| Despawn с orphan projectile | враг деспавнен, его снаряд жив | unfair урон |

### 5.5 Save/Load (сохранения)

| Что | Как ловим | Риск |
|-----|-----------|------|
| Save corrupt | JSON parse error при load | потеря прогресса |
| Save during levelup | save_progress вызван пока LevelUpScreen.active | неполное состояние |
| Profile mismatch | active_profile=1 но данные profile=2 | перезапись чужого профиля |
| Zero-byte save file | os.path.getsize(save_file) == 0 | disk full / crash |

### 5.6 Performance (производительность)

| Что | Порог | Что делать |
|-----|-------|-----------|
| FPS < 30 | fps < 30 | лог + perf snapshot |
| FPS < 15 | fps < 15 | лог + warning |
| Entity total > 1000 | enemies+gems+coins+projectiles > 1000 | лог |
| Frame dt > 100ms | dt > 0.1 | лог (лаг-спайк) |
| Memory trend | memory растёт > 10 МБ за 60 сек | лог (утечка) |

---

## 6. ВВОД + ПЕРЕХОДЫ — что ловим и почему

### 6.1 Карта переходов (все возможные)

```
splash ──(any_key/click)──→ title
title ──(click ИГРАТЬ)────→ lobby
title ──(click НАСТРОЙКИ)──→ settings (overlay)
title ──(click ВЫХОД)──────→ exit
title ──(ESC)──────────────→ (ничего, уже в главном)
lobby ──(TAB)──────────────→ lobby (смена таба)
lobby ──(click В ИГРУ)────→ run_prep
lobby ──(ESC)──────────────→ title
lobby ──(C key)────────────→ codex tab
run_prep ──(ENTER)─────────→ game
run_prep ──(ESC)───────────→ lobby
game ──(ESC)───────────────→ pause (overlay)
game ──(HP<=0)─────────────→ game_over
game ──(level up)──────────→ levelup_screen (пауза внутри game)
pause ──(Продолжить)───────→ game (pop overlay)
pause ──(Настройки)────────→ settings (overlay на overlay)
pause ──(Выход в меню)─────→ lobby
game_over ──(Заново)───────→ game
game_over ──(В лобби)──────→ lobby
settings ──(ESC)───────────→ return_to (title/pause/lobby)
```

### 6.2 Что логируем при каждом вводе

```json
{
  "type": "INPUT",
  "event": "mouse_click",
  "button": 1,
  "pos": [512, 400],
  "scene": "title",
  "element": "btn_ИГРАТЬ",
  "result": "scene_change",
  "new_scene": "lobby",
  "time_in_scene": 3.2
}
```

### 6.3 Что логируем при каждом переходе

```json
{
  "type": "TRANSITION",
  "from": "title",
  "to": "lobby",
  "trigger": "click_ИГРАТЬ",
  "duration_in_from": 3.2,
  "overlay_active": false,
  "fade_type": "slide_left",
  "state_snapshot": {
    "selected_char": "warrior",
    "gold": 1500,
    "best_wave": 12
  }
}
```

### 6.4 Edge cases ввода (что может сломаться)

| Ситуация | Что происходит | Что логируем |
|----------|---------------|-------------|
| Клик во время fade | fade прерывается? | INPUT + "during_fade" |
| ESC во время перехода | следующая сцена сразу закрывается | INPUT + "during_transition" |
| Двойной ENTER | два levelup выбора подряд | INPUT + "duplicate" |
| Mouse hover + keyboard | hover подсвечивает A, enter нажимает B | INPUT + "conflict" |
| TAB во время анимации | анимация обрывается | INPUT + "during_animation" |
| Клик мимо кнопок | ничего не происходит | INPUT + "miss" (не логируем — слишком много) |
| Клавиша в неактивной сцене | сцена не обрабатывает | INPUT + "ignored" |

### 6.5 Что логируем при levelup

```json
{
  "type": "LEVELUP",
  "level": 5,
  "xp_required": 50,
  "choices": [
    {"type": "weapon", "id": "whip", "current_level": 2},
    {"type": "passive", "id": "faith", "current_level": 0},
    {"type": "weapon", "id": "fire", "current_level": 0}
  ],
  "chosen_index": 0,
  "chosen_item": "whip",
  "rerolls_used": 0,
  "time_to_choose": 2.1,
  "player_state": {"hp": 80, "kills": 42, "wave": 3}
}
```

### 6.6 Что логируем при паузе

```json
{
  "type": "PAUSE",
  "action": "open",
  "scene": "game",
  "game_state": {"wave": 5, "elapsed": 120, "kills": 200, "hp": 60}
}

{
  "type": "PAUSE",
  "action": "resume",
  "pause_duration": 15.3
}

{
  "type": "PAUSE",
  "action": "quit_to_lobby",
  "pause_duration": 5.0,
  "game_state": {"wave": 5, "elapsed": 120, "kills": 200}
}
```
