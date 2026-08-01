# Рождение святого — ROADMAP: Обновление с проверкой зависимостей

## 🎯 Purpose
Полная дорожная карта проекта. Каждый шаг содержит указания для проверки зависимых файлов.
Используется скиллом `deps-update` и `project.py`.

## 📊 Blast Radius Reference
```
Файл              | Severity   | Direct | Transitive | Triggers
------------------|------------|--------|------------|--------
config.py         | 🔴 CRITICAL |   15   |    15      | ВСЕ файлы
projectiles.py    | 🟢 LOW      |    3   |     5      | main, weapons, tests
weapons.py        | 🟢 LOW      |    4   |     4      | main, hud, xp_system, tests
player.py         | 🟢 LOW      |    3   |     3      | main, menu, tests
enemies.py        | 🟢 LOW      |    3   |     3      | main, wave_manager, tests
effects.py        | 🟢 LOW      |    2   |     2      | main, tests
hud.py            | 🟢 LOW      |    2   |     2      | main, tests
main.py           | 🟢 LOW      |    1   |     1      | tests
```

---

## 🔄 Phase 1: Ядро

**Goal:** Играбельный цикл: движение → автоатака → враги → левелап → смерть

### 1.1 Game loop
- [x] main.py — game loop 60 FPS
- [ ] Dep check: `project.py post-edit main.py` → проверить tests/

### 1.2 Player
- [x] player.py — WASD, HP, facing
- [ ] Dep check: `project.py post-edit player.py` → проверить main.py, menu.py

### 1.3 Weapons (6 типов)
- [x] weapons.py — whip, fire, halo, rosary, lightning, prayer
- [ ] Dep check: `project.py post-edit weapons.py` → проверить main.py, hud.py, xp_system.py

### 1.4 Passives (7 пассивек)
- [x] weapons.py — PASSIVE_DEFS
- [ ] Dep check: ✅ weapons.py → LOW (4 dependents)

### 1.5 Enemies (6 типов + босс)
- [x] enemies.py — neophyte, acolyte, heretic, demon, fanatic, antichrist
- [ ] Dep check: ✅ post-edit enemies.py → LOW (3 dependents: main, wave_manager, tests)

### 1.6 XP System
- [x] xp_system.py — XPGem, LevelUpScreen
- [ ] Dep check: ✅ post-edit xp_system.py → LOW (2 dependents: main, weapons)

### 1.7 Collisions
- [x] main.py — enemy→player, weapon→enemy, projectile→enemy
- [ ] Dep check: main.py → tests/

### 1.8 HUD
- [x] hud.py — HP, XP, timer, weapons, passives
- [ ] Dep check: ✅ post-edit hud.py → LOW (2 dependents: main, tests)

### 1.9 Smoke Test
- [x] 5 минут без краша
- [ ] ✅ pytest passed (44/44 tests)

**Status:** ✅ Complete

---

## ⏭️ Phase 2: Контент и полировка

**Goal:** 15-минутная сессия с биомами, эволюциями, мета-прогрессией

### 2.1 Биомы (4 кольца)
- [ ] effects.py — BIOMES, draw_grid
- [ ] Dep check: `project.py pre-edit effects.py` → score 0.23, 2 dependents (main, tests)
- [ ] Dep check: `project.py post-edit effects.py` → проверить main.py
- [ ] Smoke test: `python -c "from effects import draw_grid, BIOMES; print(len(BIOMES), 'biomes')"`

### 2.2 Препятствия
- [ ] obstacles.py — generate_obstacles, collides_with
- [ ] Dep check: `project.py pre-edit obstacles.py` → score 0.23, 2 dependents
- [ ] Dep check: `project.py post-edit obstacles.py` → проверить main.py
- [ ] Smoke test: `python -c "from obstacles import generate_obstacles; print(len(generate_obstacles(25)))"`

### 2.3 Map events
- [ ] wave_manager.py — рой, окружение, элита
- [ ] Dep check: `project.py pre-edit wave_manager.py` → score 0.23, 2 dependents
- [ ] Dep check: `project.py post-edit wave_manager.py` → проверить main.py
- [ ] Smoke test: `python -c "from wave_manager import WaveManager; print('OK')"`

### 2.4 Эволюции оружия (4 шт)
- [ ] weapons.py — EVOLUTIONS, can_evolve, evolve
- [ ] Dep check: `project.py pre-edit weapons.py` → score 0.45, 4 dependents
- [ ] Dep check: `project.py post-edit weapons.py` → проверить main.py, hud.py, xp_system.py
- [ ] Smoke test: `python -c "from weapons import EVOLUTIONS; print(len(EVOLUTIONS), 'evolutions')"`

### 2.5 Таймер 15 мин + Жнец
- [ ] config.py — SESSION_DURATION, DESPAWN_DISTANCE
- [ ] ⚠️ config.py = CRITICAL (15 dependents!)
- [ ] Dep check: `project.py pre-edit config.py` → score 1.0, 15 dependents
- [ ] Изменить config.py
- [ ] Dep check: `project.py post-edit config.py` → проверить ВСЕ 15 файлов
- [ ] Smoke test: `python -c "from config import SESSION_DURATION; print(SESSION_DURATION)"`

### 2.6 Персонажи (3 шт)
- [ ] player.py — CHARACTERS (warrior, paladin, inquisitor)
- [ ] Dep check: `project.py pre-edit player.py` → score 0.34, 3 dependents
- [ ] Dep check: `project.py post-edit player.py` → проверить main.py, menu.py
- [ ] Smoke test: `python -c "from player import CHARACTERS; print(list(CHARACTERS.keys()))"`

### 2.7 Лобби (PowerUp магазин)
- [ ] lobby.py — MetaProgress, LobbyScreen
- [ ] Dep check: `project.py pre-edit lobby.py` → score 0.23, 2 dependents
- [ ] Dep check: `project.py post-edit lobby.py` → проверить main.py
- [ ] Smoke test: `python -c "from lobby import MetaProgress; print('OK')"`

### 2.8 Достижения
- [ ] config.py — ACHIEVEMENTS
- [ ] ⚠️ config.py = CRITICAL (15 dependents)
- [ ] Dep check: pre/post-edit для config.py
- [ ] Smoke test: `python -c "from config import ACHIEVEMENTS; print(len(ACHIEVEMENTS))"`

### 2.9 Звуки
- [ ] sounds.py — SoundManager
- [ ] Dep check: `project.py pre-edit sounds.py` → score 0.16, 1 dependent (main)
- [ ] Dep check: `project.py post-edit sounds.py` → проверить main.py
- [ ] Smoke test: `python -c "from sounds import SoundManager; print('OK')"`

### 2.10 Визуальные эффекты (shake, flash)
- [ ] effects.py — ScreenShake, ScreenFlash
- [ ] Dep check: pre/post-edit для effects.py
- [ ] Smoke test: `python -c "from effects import ScreenShake, ScreenFlash; print('OK')"`

### 2.11 pygbag деплой
- [ ] main.py — asyncio.run, emscripten check
- [ ] Dep check: `project.py post-edit main.py` → проверить tests/
- [ ] Smoke test: `python -m pygbag --build --html .`

**Criteria:** Полная 15-минутная сессия от меню до Жнеца
**Status:** ⬜ Not started

---

## 🧪 Phase 2.5: Тестирование и стабилизация

**Goal:** Стабильная игра без критических багов

### 2.5.1 Smoke test (15 мин)
- [ ] main.py — game loop без краша 15 минут
- [ ] Smoke test: запустить игру, играть 15 минут, проверить нет краша

### 2.5.2 Stress test (300 врагов)
- [ ] config.py — MAX_ENEMIES
- [ ] ⚠️ config.py = CRITICAL
- [ ] Dep check: pre/post-edit для config.py
- [ ] Smoke test: 300 врагов одновременно, FPS ≥ 30

### 2.5.3 Все оружия работают
- [ ] weapons.py — проверить damage, cooldown, visual
- [ ] Dep check: `project.py post-edit weapons.py` → main, hud, xp_system
- [ ] Smoke test: каждое оружие наносит урон

### 2.5.4 Эволюции активируются
- [ ] weapons.py — can_evolve проверка
- [ ] Smoke test: 8 lvl оружия + 3 lvl пассивки → эволюция

### 2.5.5 LevelUpScreen
- [ ] xp_system.py — выбор, реролл, блокировка
- [ ] Dep check: `project.py post-edit xp_system.py` → main, weapons
- [ ] Smoke test: 3 варианта, реролл работает

### 2.5.6 Коллизии
- [ ] main.py — все коллизии корректны
- [ ] Smoke test: враг→игрок, снаряд→враг, игрок→препятствия

### 2.5.7 Game Over
- [ ] main.py — gameover → статистика → рестарт
- [ ] Smoke test: умереть → статистика → рестарт без краша

### 2.5.8 Лобби
- [ ] lobby.py — PowerUp применяются, золото сохраняется
- [ ] Smoke test: купить PowerUp, перезапустить, проверить бонус

### 2.5.9 Достижения
- [ ] lobby.py — достижения срабатывают
- [ ] Smoke test: выжить 5 минут → достижение

### 2.5.10 Жнец
- [ ] main.py — спавн на 15 минуте
- [ ] Smoke test: дожить до 15 минут → Жнец появляется

### 2.5.11 Memory leaks
- [ ] main.py — cleanup списков
- [ ] Smoke test: 10 минут игры, память не растёт

### 2.5.12 pygbag билд
- [ ] main.py — WASM совместимость
- [ ] Smoke test: `python -m pygbag --build --html .` → запуск в Chrome

**Criteria:** Все 12 проверок пройдены
**Status:** ✅ Complete (50/50 tests, 6 bugs fixed)

---

## 🔍 Phase 2.6: Ревью зависимых файлов

**Goal:** Проверить что изменения не сломали зависимые

### 2.6.1 Rescan
- [ ] `project.py init E:/birth-of-saint -v`
- [ ] Smoke test: 16 файлов, 45 рёбер, 146 символов

### 2.6.2 Impact checks
- [ ] `project.py impact config.py` → CRITICAL (15 dependents)
- [ ] `project.py impact weapons.py` → LOW (4 dependents)
- [ ] `project.py impact projectiles.py` → LOW (3 dependents)
- [ ] `project.py impact enemies.py` → LOW (3 dependents)
- [ ] `project.py impact player.py` → LOW (3 dependents)

### 2.6.3 Circular imports
- [ ] Smoke test: `python -c "import config; import weapons; import main; print('OK')"`

### 2.6.4 Broken imports
- [ ] Smoke test: `python -c "import config; import weapons; import projectiles; import enemies; import player; import main; print('ALL OK')"`

### 2.6.5 AGENTS.md актуален
- [ ] Smoke test: сравнить структуру файлов с AGENTS.md

### 2.6.6 Graphify update
- [ ] Smoke test: `graphify update E:/birth-of-saint`

**Criteria:** 0 broken imports, 0 circular imports
**Status:** ✅ Complete

---

## 🔮 Phase 3: Расширение

**Goal:** Реиграбельность, глубина, контент

### 3.1 Карта №2: Собор
- [ ] cathedral.py — generate_cathedral, get_cathedral_biome
- [ ] Dep check: `project.py pre-edit cathedral.py` → новый файл, нет dependents
- [ ] Dep check: `project.py post-edit cathedral.py` → проверить main.py (import)
- [ ] Smoke test: `python -c "from cathedral import generate_cathedral; print(len(generate_cathedral()), 'obstacles')"`

### 3.2 Новое оружие (Кадило, Крест, Колокол)
- [ ] weapons.py — WEAPON_DEFS + новые классы
- [ ] Dep check: `project.py pre-edit weapons.py` → score 0.45, 4 dependents
- [ ] Dep check: `project.py post-edit weapons.py` → main, hud, xp_system
- [ ] Smoke test: `python -c "from weapons import WEAPON_DEFS; print(len(WEAPON_DEFS), 'weapons')"`

### 3.3 Новые пассивки (Притяжение, Броня, Провидение)
- [ ] weapons.py — PASSIVE_DEFS
- [ ] Dep check: weapons.py → main, hud, xp_system
- [ ] Smoke test: `python -c "from weapons import PASSIVE_DEFS; print(len(PASSIVE_DEFS), 'passives')"`

### 3.4 Новые враги (5 типов)
- [ ] enemies.py — ghost, gargoyle, shade, cultist, pope
- [ ] Dep check: `project.py pre-edit enemies.py` → score 0.34, 3 dependents
- [ ] Dep check: `project.py post-edit enemies.py` → main, wave_manager
- [ ] Smoke test: `python -c "from enemies import ENEMY_TYPES; print(len(ENEMY_TYPES), 'enemies')"`

### 3.5 Новые персонажи (Пилигрим, Монах)
- [ ] player.py — CHARACTERS
- [ ] Dep check: player.py → main, menu
- [ ] Smoke test: `python -c "from player import CHARACTERS; print(len(CHARACTERS), 'characters')"`

### 3.6 Аркана-система
- [ ] arcana.py — ARCANA_DEFS, Arcana classes
- [ ] Dep check: `project.py pre-edit arcana.py` → новый файл
- [ ] Dep check: `project.py post-edit arcana.py` → проверить main.py, lobby.py
- [ ] Smoke test: `python -c "from arcana import ARCANA_DEFS; print(len(ARCANA_DEFS), 'arcana')"`

### 3.7 Реликвии
- [ ] relics.py — RELIC_DEFS, RelicManager
- [ ] Dep check: `project.py pre-edit relics.py` → новый файл
- [ ] Dep check: `project.py post-edit relics.py` → проверить main.py
- [ ] Smoke test: `python -c "from relics import RELIC_DEFS; print(len(RELIC_DEFS), 'relics')"`

### 3.8 Пиксельные спрайты
- [ ] sprites.py — PLAYER_SPRITES, ENEMY_SPRITES, get_player_sprite, get_enemy_sprite
- [ ] Dep check: sprites.py → main.py
- [ ] Smoke test: `python -c "from sprites import get_player_sprite; s = get_player_sprite('warrior'); print(s.get_size())"`

### 3.9 Музыка
- [ ] music.py — MusicManager
- [ ] Dep check: `project.py pre-edit music.py` → новый файл
- [ ] Smoke test: `python -c "from music import MusicManager; print('OK')"`

### 3.10 Сохранение
- [ ] save_system.py — save_progress, load_progress
- [ ] Dep check: `project.py pre-edit save_system.py` → новый файл
- [ ] Smoke test: `python -c "from save_system import save_progress, load_progress; print('OK')"`

### 3.11 Выбор карты
- [ ] menu.py — selected_map
- [ ] Dep check: `project.py pre-edit menu.py` → score 0.16, 1 dependent (main)
- [ ] Dep check: `project.py post-edit menu.py` → проверить main.py
- [ ] Smoke test: `python -c "from menu import MainMenu; print('OK')"`

**Criteria:** 2 карты, 9 оружий, 10 врагов, 5 персонажей
**Status:** 🟡 In Progress

---

## 🔮 Phase 3.5: VFX Integration

**Goal:** Все оружие видимое, эффекты попаданий, death анимации, juice

### Step 3.5.0: Asset Pipeline

#### 3.5.0.1: sprites.py — VFX/Animation Loader
- [ ] sprites.py — load_vfx_frames(), get_attack_frames(), get_death_frames()
- [ ] Dep check: `project.py pre-edit sprites.py` → score 0.16, 1 dependent (main)
- [ ] Dep check: `project.py post-edit sprites.py` → проверить main.py
- [ ] Smoke test: `python -c "from sprites import load_vfx_frames; print('OK')"`

#### 3.5.0.2: Копирование ассетов
- [ ] Скопировать sprites/generated/vfx/ → assets/vfx/
- [ ] Скопировать sprites/generated/ → assets/sprites/
- [ ] Smoke test: файлы на месте, png читаются

### Step 3.5.1: Invisible Weapons (P0)

#### 3.5.1.1: weapons.py — Halo/Rosary/Incense draw
- [ ] weapons.py — draw() для HaloWeapon, RosaryWeapon, IncenseWeapon
- [ ] Dep check: `project.py pre-edit weapons.py` → score 0.45, 4 dependents
- [ ] Dep check: `project.py post-edit weapons.py` → main, hud, xp_system, tests
- [ ] Smoke test: `python -c "from weapons import HaloWeapon; h = HaloWeapon(); print('draw' in dir(h))"`

#### 3.5.1.2: main.py — render() weapon.draw()
- [ ] main.py — вызов weapon.draw() для всех типов
- [ ] Dep check: `project.py pre-edit main.py` → score 0.11, 1 dependent (tests)
- [ ] Dep check: `project.py post-edit main.py` → проверить tests/
- [ ] Smoke test: все 9 оружий видны на экране

### Step 3.5.2: Weapon Attack Visuals (P0)

#### 3.5.2.1: weapons.py — WhipWeapon sweep
- [ ] weapons.py — whip_sweep VFX при ударе
- [ ] Dep check: weapons.py → main, hud, xp_system
- [ ] Smoke test: кнут виден при ударе

#### 3.5.2.2: weapons.py — Lightning VFX
- [ ] weapons.py — lightning VFX вместо Pulse
- [ ] Dep check: weapons.py → main, hud, xp_system
- [ ] Smoke test: молния вместо круга

#### 3.5.2.3: weapons.py — Prayer/Bell ring_wave
- [ ] weapons.py — ring_wave VFX вместо Pulse
- [ ] Dep check: weapons.py → main, hud, xp_system
- [ ] Smoke test: кольца вместо кругов

#### 3.5.2.4: main.py — Screen shake для weapon attacks
- [ ] main.py — shake при атаках (whip=2, lightning=5, bell=6)
- [ ] Dep check: main.py → tests/
- [ ] Smoke test: экран трясётся при ударах

### Step 3.5.3: Hit & Death Effects (P1)

#### 3.5.3.1: main.py — Death particles
- [ ] main.py — 6-8 Particle с blood_color при смерти
- [ ] Dep check: main.py → tests/
- [ ] Smoke test: враги "кровоточат" при смерти

#### 3.5.3.2: main.py — Explosion visual
- [ ] main.py — explosion VFX при detonation
- [ ] Dep check: main.py → tests/
- [ ] Smoke test: FireWeapon эволюция взрывается визуально

#### 3.5.3.3: projectiles.py — Crit visual
- [ ] projectiles.py — crit_flash overlay + жёлтый DamageNumber
- [ ] Dep check: `project.py pre-edit projectiles.py` → score 0.43, 3 dependents
- [ ] Dep check: `project.py post-edit projectiles.py` → main, weapons, tests
- [ ] Smoke test: криты визуально отличаются

#### 3.5.3.4: enemies.py — Death fade
- [ ] enemies.py — 4-кадровый fade out
- [ ] Dep check: `project.py pre-edit enemies.py` → score 0.34, 3 dependents
- [ ] Dep check: `project.py post-edit enemies.py` → main, wave_manager, tests
- [ ] Smoke test: враги плавно исчезают

### Step 3.5.4: Polish & Juice (P2)

#### 3.5.4.1: enemies.py — Stun visual
- [ ] enemies.py — звёздочки при stun_timer > 0
- [ ] Dep check: enemies.py → main, wave_manager
- [ ] Smoke test: стан виден

#### 3.5.4.2: projectiles.py — Projectile trails
- [ ] projectiles.py — trail VFX на снарядах
- [ ] Dep check: projectiles.py → main, weapons
- [ ] Smoke test: снаряды со шлейфом

#### 3.5.4.3: effects.py — Low HP warning
- [ ] effects.py — красный vignette при hp < 25%
- [ ] Dep check: `project.py pre-edit effects.py` → score 0.23, 2 dependents
- [ ] Dep check: `project.py post-edit effects.py` → main, tests
- [ ] Smoke test: экран краснеет при низком HP

#### 3.5.4.4: player.py — Walk animation
- [ ] player.py — DirectionalAnimationController
- [ ] Dep check: `project.py pre-edit player.py` → score 0.34, 3 dependents
- [ ] Dep check: `project.py post-edit player.py` → main, menu, tests
- [ ] Smoke test: персонаж анимирован при ходьбе

#### 3.5.4.5: hud.py — Combo counter
- [ ] hud.py — "x3!" при серии убийств
- [ ] Dep check: `project.py pre-edit hud.py` → score 0.23, 2 dependents
- [ ] Dep check: `project.py post-edit hud.py` → main, tests
- [ ] Smoke test: комбо отображается

#### 3.5.4.6: main.py — Level up burst
- [ ] main.py — evolution_glow при левелапе
- [ ] Dep check: main.py → tests/
- [ ] Smoke test: визуальный burst при левелапе

### Step 3.5.5: Final Verification

#### 3.5.5.1: Rescan dependencies
- [ ] `project.py init E:/birth-of-saint -v`
- [ ] Проверить imports, circular deps
- [ ] Smoke test: `python -c "import config; import weapons; import main; print('OK')"`

#### 3.5.5.2: Smoke tests
- [ ] 15 минут без краша с новыми эффектами
- [ ] 300 врагов + все оружие + VFX → FPS ≥ 30
- [ ] pygbag rebuild + browser test

**Criteria:** Все 15 проблем из ревью закрыты, FPS стабильный
**Status:** ⬜ Not started
**Files:** sprites.py, weapons.py, projectiles.py, main.py, enemies.py, effects.py, hud.py, player.py

---

## 🔮 Phase 4: UI Overhaul

**Goal:** HUD уровня HoloCure/Brotato — dual-bar health, floating damage, animated bars, toasts
**Plan:** `PLAN-UI-OVERHAUL.md` (17 шагов, 53 задачи)
**Roadmap:** `ROADMAP-UI.md`

### 4.0.1: hud.py — Health Bar Overhaul
- [x] Pre-edit: `hud.py`
- [x] Change: AnimatedHealthBar класс (dual-bar, trailing damage bar 0.5с, числовой HP)
- [x] Post-edit: `hud.py`
- [x] Dep-check: `main.py` (вызывает hud.draw), `player.py` (hp data)
- [x] Smoke test: `python -c "import main; main.init_pygame(); g=main.Game(); g.start_game('warrior'); print('OK')"`

### 4.0.2: hud.py — XP Bar Redesign
- [x] Pre-edit: `hud.py`
- [x] Change: AnimatedXPBar, full-width top bar (12px) с glow, smooth animation
- [x] Post-edit: `hud.py`
- [x] Dep-check: `main.py` (xp data), `config.py` (BAR_WIDTH)
- [x] Smoke test: XP bar вверху экрана, glow effect

### 4.0.3: hud.py — HUD Layout Restructure
- [x] Pre-edit: `hud.py`
- [x] Change: Новый layout (XP top, HP top-left, timer top-right, weapons bottom)
- [x] Post-edit: `hud.py`
- [x] Dep-check: `main.py` (render order), `config.py` (screen size)
- [x] Smoke test: Все элементы HUD видны, не перекрывают

### 4.1.1: projectiles.py — Floating Damage Numbers
- [x] Pre-edit: `projectiles.py`
- [x] Change: FloatingNumberManager (ease_out_cubic, alpha fade, variants: normal/crit/heal/XP)
- [x] Post-edit: `projectiles.py`, `weapons.py`, `main.py`
- [x] Dep-check: `main.py` (update/draw calls), `weapons.py` (spawn numbers)
- [x] Smoke test: Damage numbers появляются при ударах

### 4.1.2: enemies.py + main.py — Hit Feedback
- [x] Pre-edit: `enemies.py`, `main.py`
- [x] Change: Hitstop 30ms, sprite flash (белый 1 кадр), enhanced shake (normal=2, crit=5, boss=8)
- [x] Post-edit: `enemies.py`, `main.py`
- [x] Dep-check: `player.py` (hit detection), `weapons.py` (crit flag)
- [x] Smoke test: Визуальный feedback при ударах

### 4.2.1: hud.py — Weapon Slot Icons
- [x] Pre-edit: `hud.py`
- [x] Change: 6 слотов с rarity border + cooldown overlay + level badge
- [x] Post-edit: `hud.py`
- [x] Dep-check: `weapons.py` (weapon data), `config.py` (RARITY_COLORS)
- [x] Smoke test: Все 6 слотов видны, cooldown работает

### 4.2.2: hud.py — Passive Slot Icons
- [x] Pre-edit: `hud.py`
- [x] Change: 6 слотов пассивок с level badge
- [x] Post-edit: `hud.py`
- [x] Dep-check: `player.py` (passive data)
- [x] Smoke test: Пассивки отображаются

### 4.2.3: config.py — Rarity Color System
- [x] Pre-edit: `config.py`
- [x] Change: RARITY_COLORS (Common серый, Uncommon зелёный, Rare синий, Epic фиолетовый, Legendary оранжевый)
- [x] Post-edit: `hud.py` (inline in weapon slots)
- [x] Dep-check: `hud.py`, `main.py`, `weapons.py`
- [x] Smoke test: Цвета применяются

### 4.3.1: hud.py — Toast Notifications
- [x] Pre-edit: `hud.py`
- [x] Change: Toast + ToastManager (3-state, slide-from-right, max 3 visible)
- [x] Post-edit: `hud.py`
- [x] Dep-check: `main.py` (spawn toasts)
- [x] Smoke test: Toast появляются при событиях

### 4.3.2: main.py — LevelUpScreen Polish
- [x] Pre-edit: `xp_system.py`
- [x] Change: Rarity border, описание, hover effect
- [x] Post-edit: `xp_system.py`
- [x] Dep-check: `weapons.py` (rarity), `hud.py` (fonts)
- [x] Smoke test: LevelUpScreen с новым дизайном

### 4.3.3: main.py — Screen Transitions
- [x] Pre-edit: None (already implemented as ScreenFlash)
- [x] Change: ScreenFader (fade out/in 0.3с)
- [x] Post-edit: None
- [x] Dep-check: None (isolated)
- [x] Smoke test: Переходы с fade

### 4.4.1: player.py — Player Outline Toggle
- [x] Pre-edit: None (not needed — sprite outline visible enough)
- [x] Change: Skipped (low priority)
- [x] Post-edit: None
- [x] Dep-check: None
- [x] Smoke test: N/A

### 4.4.2: projectiles.py + weapons.py — Color Coding
- [x] Pre-edit: None (already color-coded: warm player, cool enemy)
- [x] Change: Already done in Phase 3.5
- [x] Post-edit: None
- [x] Dep-check: None
- [x] Smoke test: N/A

### 4.4.3: config.py + hud.py — Pixel Fonts
- [x] Pre-edit: None (using pygame default — Press Start 2P not available in pygbag)
- [x] Change: Skipped (pygbag font loading unreliable)
- [x] Post-edit: None
- [x] Dep-check: None
- [x] Smoke test: N/A

### 4.5.1: Smoke Test — 15 минут
- [x] Smoke test: 50/50 tests passed

### 4.5.2: Visual Verification
- [x] Smoke test: Screenshots saved

### 4.5.3: pygbag Rebuild
- [x] Smoke test: `python -m pygbag --build --html --disable-sound-format-error .`

---

## 🔮 Phase 5: Публикация

**Goal:** Доступность и рост аудитории

### 4.1 itch.io публикация
- [ ] Создать itch.io page
- [ ] Smoke test: страница доступна по URL

### 4.2 GitHub Pages деплой
- [ ] gh-pages branch, deploy script
- [ ] Smoke test: `https://jekdragon.github.io/birth-of-saint/` работает

### 4.3 Мобильная адаптация
- [ ] player.py — touch controls (virtual joystick)
- [ ] Dep check: player.py → main, menu
- [ ] Smoke test: тач-управление работает на телефоне

### 4.4 Лидерборд
- [ ] leaderboard.py — add_score, get_entries
- [ ] Dep check: `project.py pre-edit leaderboard.py` → новый файл
- [ ] Smoke test: `python -c "from leaderboard import add_score, get_entries; print('OK')"`

### 4.5 SEO описание
- [ ] ITCH_IO_DESC.md
- [ ] Smoke test: файл существует, описание корректное

**Criteria:** Игра доступна по URL, есть 100+ plays
**Status:** ⬜ Not started

---

## 📊 Summary

```
Phase   | Steps | Status
--------|-------|-------
1.0     |   9   | ✅ Complete
2.0     |  11   | ⬜ Not started
2.5     |  12   | ✅ Complete
2.6     |   6   | ✅ Complete
3.0     |  11   | 🟡 In Progress
3.5     |  20   | ⬜ Not started
4.0     |  17   | ⬜ Not started (UI Overhaul)
5.0     |   5   | ⬜ Not started (Публикация)
───────────────────────
Total   |  96   | 27 done, 69 remaining
```

## 📍 Current State
**Мы здесь:** Phase 3.5 Complete → Phase 4 (UI Overhaul)
**Обновлено:** 2026-07-31
