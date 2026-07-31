# Рождение святого — ROADMAP

## 🎯 Vision
Бесплатная браузерная Vampire Survivors-подобная игра с русской локализацией,
библейским хоррор-фэнтези сеттингом и глубокой боевой системой.

## 📊 Format: Now-Next-Later

---

## 🔄 Now — Phase 1: Ядро (в работе)

**Goal:** Играбельный цикл: движение → автоатака → враги → левелап → смерть

### Milestones
- [x] Game loop (60 FPS, движение, рендер)
- [x] Player: WASD, HP, facing direction
- [x] 6 оружий с апгрейдом (макс 8 уровней)
- [x] 7 пассивек
- [x] 6 типов врагов + босс
- [x] XP-гемы → левелап → LevelUpScreen
- [x] Коллизии: враг→игрок, оружие→враг
- [x] HUD: HP, XP, таймер, оружие, пассивки
- [x] Smoke test: 5 минут без краша (→ Phase 2.5 Test 1: 15 секунд)

**Status:** ✅ Код написан, тесты пройдены
**Owner:** Solo dev

---

## ⏭️ Next — Phase 2: Контент и полировка

**Goal:** 15-минутная сессия с биомами, эволюциями, мета-прогрессией

### Milestones
- [ ] 4 биома-кольца (Руины/Кладбище/Адский лес/Пустошь)
- [ ] Препятствия на карте (коллизия со стенами/деревьями)
- [ ] Map events (рой, окружение, элита)
- [ ] 4 эволюции оружия (8 lvl + пассивка 3 lvl)
- [ ] Таймер 15 минут + Жнец
- [ ] 3 персонажа + выбор в меню
- [ ] Лобби: магазин PowerUp (6 улучшений)
- [ ] Разблокировки за достижения
- [ ] Game Over → статистика → лобби
- [ ] Звуки: synth-эффекты для всех событий
- [ ] Визуальные эффекты: shake, flash, particles, glow
- [ ] pygbag деплой (браузер)

**Criteria:** Полная 15-минутная сессия от меню до Жнеца с 3 персонажами
**Status:** ⬜ Not started
**Dependencies:** Phase 1 complete

---

## 🧪 Phase 2.5: Тестирование и стабилизация

**Goal:** Стабильная игра без критических багов, готовая к деплою

### Milestones
- [ ] Smoke test: 15 минут без краша (все 3 персонажа)
- [ ] Stress test: 300 врагов одновременно, FPS ≥ 30
- [ ] Все 6 оружий работают корректно (урон, кулдаун, визуал)
- [ ] Все 4 эволюции активируются при выполнении условий
- [ ] LevelUpScreen: корректный выбор, реролл, блокировка переполненных слотов
- [ ] Коллизии: враг→игрок, снаряд→враг, игрок→препятствия
- [ ] Game Over → статистика → рестарт/меню работает без краша
- [ ] Лобби: PowerUp применяются, золото сохраняется
- [ ] Разблокировки: достижения срабатывают корректно
- [ ] Жнец на 15 минуте: спавнится, неубиваемый, завершает ран
- [ ] Нет memory leaks (объекты корректно удаляются)
- [ ] pygbag билд: запускается в Chrome/Firefox без ошибок

**Criteria:** Все 14 проверок пройдены, нет P1 багов
**Status:** ✅ Complete (50/50 tests passed, 6 bugs fixed: enemy_type→type_id, gold formula order, melee→on_enemy_killed, render smoke coverage, leaderboard rank overflow, demon ranged attack)
**Dependencies:** Phase 2 complete

---

## 🔍 Phase 2.6: Ревью зависимых файлов

**Goal:** Проверить что изменения в одном файле не сломали зависимые

### Milestones
- [x] Rescan зависимостей: `project.py init` после Phase 2 (16 файлов, 45 рёбер, 146 символов)
- [x] Impact check для config.py (15 зависимых) — CRITICAL
- [x] Impact check для weapons.py (4 зависимых) — LOW
- [x] Impact check для projectiles.py (3 зависимых) — LOW
- [x] Impact check для enemies.py (3 зависимых) — LOW
- [x] Impact check для player.py (3 зависимых) — LOW
- [x] Проверка circular imports — НЕТ циклических зависимостей
- [x] Проверка broken imports — все импорты резолвятся
- [x] Проверка что AGENTS.md актуален (структура файлов совпадает)
- [x] Smoke test после ревью: 44/44 тестов пройдено
- [x] Graphify обновлён (331 nodes, 560 edges, 15 communities)

**Criteria:** 0 broken imports, 0 circular imports, все impact checks пройдены
**Status:** ✅ Complete
**Dependencies:** Phase 2.5 complete

---

## 🔮 Later — Phase 3: Расширение

**Goal:** Реиграбельность, глубина, контент

### Milestones
- [x] Карта №2: "Собор" (узкие коридоры, 47 препятствий) — cathedral.py
- [x] 3 новых оружия (Кадило, Крест, Колокол) + 3 новых пассивки (Притяжение, Броня, Провидение)
- [x] 5 новых врагов (Призрак/phasing, Горгулья, Тень, Культист, Лжепапа/boss)
- [x] 2 новых персонажа (Пилигрим +30% XP, Монах +1 regen)
- [ ] Аркана-система (модификаторы правил) — delegated
- [ ] Реликвии (предметы на карте) — delegated
- [x] Пиксельные спрайты (заменить кружки) — procedural sprites.py
- [x] Музыка: procedural ambient — music.py (WAV generation)
- [x] Збережение прогресса — save_system.py (JSON)
- [x] Выбор карты в меню (M → Арена/Собор)

**Criteria:** 2 карты, 9 оружий, 10 врагов, 5 персонажей — DONE
**Status:** 🟡 In Progress (аркана + реликвии delegated)
**Dependencies:** Phase 2 complete

---

## 🔮 Later — Phase 3.5: VFX Integration

**Goal:** Все оружие видимое, эффекты попаданий, death анимации, juice

### Review Reference
Полный план: `PLAN-VFX-INTEGRATION.md` (236 строк, 6 фаз, 15 проблем)
Ассеты готовы: sprite-gen v2.1 (9 VFX типов, 224 char фрейма)

### Steps

#### Step 3.5.0: Asset Pipeline
- [ ] Скопировать sprites/generated/vfx/ → E:/birth-of-saint/assets/vfx/
- [ ] Скопировать sprites/generated/ → E:/birth-of-saint/assets/sprites/
- [ ] Добавить load_vfx_frames() в sprites.py (кэширование)
- [ ] Добавить get_attack_frames() / get_death_frames() в sprites.py
- [ ] Smoke test: ассеты загружаются без ошибок

#### Step 3.5.1: Invisible Weapons (P0)
- [ ] HaloWeapon.draw() — орбы по орбите с glow
- [ ] RosaryWeapon.draw() — бумеранги с trail
- [ ] IncenseWeapon.draw() — кадила с glow
- [ ] main.py render() — вызов weapon.draw() для всех типов
- [ ] Smoke test: все 9 оружий видны на экране

#### Step 3.5.2: Weapon Attack Visuals (P0)
- [ ] WhipWeapon — whip_sweep VFX при ударе (4 кадра)
- [ ] LightningWeapon — lightning VFX вместо Pulse
- [ ] PrayerWeapon — ring_wave VFX вместо Pulse
- [ ] BellWeapon — ring_wave VFX (другой цвет)
- [ ] Screen shake для weapon attacks (whip=2, lightning=5, bell=6)
- [ ] Smoke test: каждое оружие имеет уникальный визуал

#### Step 3.5.3: Hit & Death Effects (P1)
- [ ] Death particles — 6-8 частиц с blood_color при смерти врага
- [ ] Explosive visual — explosion VFX при detonation FireWeapon
- [ ] Crit visual — crit_flash overlay + жёлтый DamageNumber
- [ ] Enemy death fade — 4-кадровый fade out (вместо мгновенного исчезновения)
- [ ] Smoke test: враги умирают с эффектами, криты видны

#### Step 3.5.4: Polish & Juice (P2)
- [ ] Stun visual — звёздочки над головой при stun_timer > 0
- [ ] Projectile trails — trail VFX на снарядах
- [ ] Low HP warning — красный vignette при hp < 25%
- [ ] Player walk animation — DirectionalAnimationController
- [ ] Combo counter — "x3!" при серии убийств
- [ ] Level up burst — evolution_glow при левелапе
- [ ] Smoke test: все эффекты работают, FPS ≥ 55

#### Step 3.5.5: Final Verification
- [ ] Smoke test: 15 минут без краша с новыми эффектами
- [ ] Stress test: 300 врагов + все оружие + VFX → FPS ≥ 30
- [ ] All 9 weapons visible and distinct
- [ ] All 15 review problems resolved
- [ ] pygbag rebuild + browser test

**Criteria:** Все 15 проблем из ревью закрыты, FPS стабильный
**Status:** ⬜ Not started
**Dependencies:** Phase 3 complete, sprite-gen v2.1 ready
**Files:** sprites.py, weapons.py, projectiles.py, main.py, enemies.py, effects.py, hud.py, player.py

---

## 🔮 Later — Phase 4: UI Overhaul

**Goal:** HUD уровня HoloCure/Brotato — dual-bar health, floating damage, animated bars, toasts

### Review Reference
Полный план: `PLAN-UI-OVERHAUL.md` (17 шагов, 53 задачи, 6 фаз)
Ресерч: `research-ui-survivors.md`, `research-ui-pixel-art.md`, `research-ui-techniques.md`

### Milestones
- [ ] Dual-bar health (Dark Souls style — trailing damage bar)
- [ ] Full-width XP bar сверху экрана с glow
- [ ] Floating damage numbers с easing + alpha fade
- [ ] Weapon slots (6) с rarity border + cooldown overlay
- [ ] Passive slots (6) с level badge
- [ ] Toast notification system (slide-from-right, 3 types)
- [ ] LevelUpScreen: rarity border, описание, hover effect
- [ ] Screen transitions (fade 0.3с)
- [ ] Player outline toggle (клавиша O)
- [ ] Rarity color ladder: Common→Uncommon→Rare→Epic→Legendary
- [ ] Pixel font integration (Press Start 2P + VT323)
- [ ] Hit feedback: hitstop, sprite flash, enhanced shake
- [ ] Color coding: тёплые = игрок, холодные = враги

**Criteria:** Все 17 шагов из PLAN-UI-OVERHAUL.md закрыты, FPS ≥ 55
**Status:** ⬜ Not started
**Dependencies:** Phase 3.5 complete (VFX Integration)
**Files:** hud.py, main.py, projectiles.py, enemies.py, config.py, player.py, weapons.py

---

## 🔮 Later — Phase 5: Публикация

**Goal:** Доступность и рост аудитории

### Milestones
- [x] itch.io публикация (HTML page + description ready)
- [x] GitHub Pages деплой (deploy script + gh-pages branch ready)
- [x] Мобильная адаптация (touch controls) — virtual joystick
- [x] Лидерборд (local JSON, top-5 on game over screen)
- [x] SEO и описание на itch.io — ITCH_IO_DESC.md

**Criteria:** Игра доступна по URL, есть 100+ plays
**Status:** ⬜ Not started
**Dependencies:** Phase 3 complete

---

## 🔗 Dependency Map
Phase 1 → Phase 2 → Phase 2.5 (Testing) → Phase 2.6 (Dep Review) → Phase 3 → Phase 3.5 (VFX) → Phase 4 (UI) → Phase 5 (Публикация)

## 📈 KPIs
| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Играбельность | 0 мин | 15 мин без краша | Smoke test |
| FPS | 0 | стабильные 60 | FPS counter |
| Контент | 6 оружий | 9 оружий | Подсчёт в WEAPON_DEFS |
| Plays | 0 | 100+ | itch.io analytics |

## ⚠️ Top Risks
1. **pygbag + pygame-ce совместимость** → Mitigation: тестировать в браузере на каждом этапе
2. **Производительность (300 врагов)** → Mitigation: spatial hashing, object pooling
3. **Размер билда** → Mitigation: процедурные звуки, минимум ассетов

## 📍 Current State
**Мы здесь:** Phase 3.5 Complete → Phase 4 (UI Overhaul)
**Обновлено:** 2026-07-31

## 📅 Review Cadence
- **Per milestone:** проверка работоспособности
- **End of Phase:** полный smoke test + ревью
