# Ресерч: UI/UX "Рождение святого" — Полный отчёт

> Дата: 2026-07-30
> Источники: Vampire Survivors Wiki, Behance (Game UI Redesign VS), Medium (Unity Case Study VS), Terresquall Blog, Catador Portfolio, Anvil Survivors, Godot Survivor, SU-93 Survivor, Another Survivor, CodeWithC, PatternsGameProg, GameUI Database, Monster Survivors, Juicy Navigation, our skills (pixel-art-sprites, game-modifier-patterns, godot-ui-ux-patterns)

---

## ЧАСТЬ 1: ГЕЙМПЛЕЙНЫЙ HUD

### ✅ УЖЕ ЕСТЬ

| Элемент | Статус | Файл |
|---------|--------|------|
| HP-бар | ✅ Работает | main.py |
| XP-бар (верх экрана) | ✅ Работает | main.py |
| Таймер волны | ✅ Работает | main.py |
| Счёт убийств | ✅ Работает | main.py |
| Low HP vignette | ✅ Работает | effects.py |
| Screen shake | ✅ Работает | main.py |
| Combo counter | ✅ Работает | hud.py |
| Damage numbers | ✅ Работает | projectiles.py |
| Death particles | ✅ Работает | main.py |
| Level up burst | ✅ Работает | main.py |
| Crit flash | ✅ Работает | projectiles.py |
| WhipSweep / LightningBolt / RingWave VFX | ✅ Работает | projectiles.py |

### ⚠️ МОЖНО УЛУЧШИТЬ

| Что | Текущее состояние | Что сделать | Сложность |
|-----|-------------------|-------------|-----------|
| Flash on hit | Partial (не на всех врагах) | Системный flash на ВСЕХ врагах при ударе (белый, 2-3 кадра) | Низкая |
| VFX эволюции | VFX сгенерирован (evolution_glow), не подключён | Подключить evolution_glow к системе эволюций | Низкая |
| Death fade | Есть, но простой | Alpha fade с задержкой 0.3s + particle burst | Низкая |
| Screen shake | Есть | Добавить вариации: слабый (обычный удар), сильный (босс/крит) | Низкая |

### ❌ НЕТ

| Что | Описание | Источник | Сложность |
|-----|----------|----------|-----------|
| Индикатор направления врагов | Стрелки по краям экрана указывающие на врагов за пределами видимости | Catador, SU-93 Survivor | Средняя |
| Пульсация HP-бара | Анимация пульса при HP < 30% | Anvil Survivors, Godot Survivor | Низкая |
| Heartbeat звук при низком HP | Ритмичный звук при критическом HP | The Long Dark, Godot Survivor | Низкая |
| Индикатор pickup range | Визуальный круг вокруг игрока показывающий радиус подбора | Vampire Survivors | Низкая |
| Damage numbers вариации | Размер/цень варьируется от урона (мелкий = обычный, крупный = крит) | Vampire Survivors, Another Survivor | Низкая |

---

## ЧАСТЬ 2: ЭКРАН LEVEL UP

### ✅ УЖЕ ЕСТЬ

| Элемент | Статус | Файл |
|---------|--------|------|
| Пауза геймплея | ✅ Работает | main.py |
| 3 карточки на выбор | ✅ Работает | main.py |
| Описание предметов | ✅ Работает | main.py |
| Оружие + пассивки в одном пуле | ✅ Работает | main.py |

### ⚠️ МОЖНО УЛУЧШИТЬ

| Что | Текущее состояние | Что сделать | Сложность |
|-----|-------------------|-------------|-----------|
| Появление карточек | Мгновенное | Stagger fade-in (карточки появляются с задержкой 0.1s каждая) | Низкая |
| Hover-эффект | Нет | Подсветка + scale 1.05 выбранной карточки | Низкая |
| Визуал карточек | Текст | Иконка предмета + уровень + полоска прогресса | Средняя |
| Краткая неуязвимость | Нет | 0.5s неуязвимости после выбора (как в VS) | Низкая |

### ❌ НЕТ

| Что | Описание | Источник | Сложность |
|-----|----------|----------|-----------|
| Текущий билд на экране | Показать текущие оружия и их уровни на экране левелапа | Vampire Survivors | Средняя |
| Reroll / Skip / Banish | PowerUps для манипуляции выбором (мета-прогрессия) | Vampire Survivors | Средняя |
| Описание эволюции | Подсказка "сочетается с X для эволюции" | Vampire Survivors | Низкая |
| Звук левелапа | Отдельный SFX | — | Низкая |
| Анимация "дождь из гемов" | XP-гемы падают сверху при левелапе | Vampire Survivors | Средняя |

---

## ЧАСТЬ 3: ЭКРАН GAME OVER

### ✅ УЖЕ ЕСТЬ

| Элемент | Статус | Файл |
|---------|--------|------|
| Экран Game Over | ✅ Работает | main.py |
| Выбор: Заново / В меню | ✅ Работает | main.py |

### ⚠️ МОЖНО УЛУЧШИТЬ

| Что | Текущее состояние | Что сделать | Сложность |
|-----|-------------------|-------------|-----------|
| Статистика | Минимальная | Показать: время, убийства, уровень, золото, оружия | Низкая |
| Анимация | Нет | Fade-in статистики, scale punch на цифрах | Низкая |

### ❌ НЕТ

| Что | Описание | Источник | Сложность |
|-----|----------|----------|-----------|
| Лидерборд на экране | Показать топ-5 результатов | Vampire Survivors | Средняя |
| Сохранение прогресса | Золото + достижения сохраняются | — | Уже есть в мета |

---

## ЧАСТЬ 4: ГЛАВНОЕ МЕНЮ

### ✅ УЖЕ ЕСТЬ

| Элемент | Статус |
|---------|--------|
| Базовое главное меню | ✅ Есть |

### ⚠️ МОЖНО УЛУЧШИТЬ

| Что | Текущее состояние | Что сделать | Сложность |
|-----|-------------------|-------------|-----------|
| Навигация | Базовая | Up/Down + Enter + Escape + мышь hover/click | Средняя |
| Визуал | Базовый | Логотип + анимированная кнопка "Начать" | Средняя |
| Звук | Нет | Hover-клик + select-звук | Низкая |

### ❌ НЕТ

| Что | Описание | Источник | Сложность |
|-----|----------|----------|-----------|
| "НАЖМИТЕ ДЛЯ НАЧАЛА" | Title screen с flash-промптом перед меню | Vampire Survivors | Низкая |
| Прогрессивное разблокирование | Пункты меню появляются после достижений | Vampire Survivors | Средняя |
| Quick Start | Случайный персонаж + случайная карта | Vampire Survivors | Низкая |
| Бестарий | Список врагов с описаниями | Vampire Survivors | Средняя |
| Коллекция | Список оружий/пассивок | Vampire Survivors | Средняя |
| Top navigation | Account / Options / Quit сверху | Vampire Survivors | Низкая |

---

## ЧАСТЬ 5: ЭКРАН ПАУЗЫ

### ✅ УЖЕ ЕСТЬ

| Элемент | Статус |
|---------|--------|
| Toggle паузы (Escape) | ✅ Есть |

### ⚠️ МОЖНО УЛУЧШИТЬ

| Что | Текущее состояние | Что сделать | Сложность |
|-----|-------------------|-------------|-----------|
| Затемнение | Нет/базовое | Полупрозрачный чёрный слой (alpha 150) | Низкая |
| Пункты меню | Нет | Продолжить, Настройки, Выход | Низкая |

### ❌ НЕТ

| Что | Описание | Источник | Сложность |
|-----|----------|----------|-----------|
| Текущий билд | Показать оружия + уровни + пассивки | Vampire Survivors | Средняя |
| Статистика сессии | Убийства, время, уровень | Vampire Survivors | Низкая |
| Overlay архитектура | Game continues render, update заморожен | PatternsGameProg | Средняя |
| Навигация | Up/Down + Enter + Escape | — | Низкая |
| Options подменю | Громкость, fullscreen, FPS | — | Средняя |

---

## ЧАСТЬ 6: ЛОББИ (МЕТА-ЭКРАН)

### ✅ УЖЕ ЕСТЬ

| Элемент | Статус | Файл |
|---------|--------|------|
| Выбор персонажа | ✅ Работает | main.py |
| PowerUp магазин | ✅ Работает | main.py |
| Арканы (5 шт) | ✅ Работает | main.py |
| Реликвии (8 шт) | ✅ Работает | main.py |
| Достижения | ✅ Работает | main.py |

### ⚠️ МОЖНО УЛУЧШИТЬ

| Что | Текущее состояние | Что сделать | Сложность |
|-----|-------------------|-------------|-----------|
| Визуал персонажей | Базовый | Портрет + стартовое оружие + статы | Средняя |
| Навигация | Базовая | Табы (Герои, Арканы, Магазин, Рекорды) | Средняя |
| Анимации | Нет | Fade-in, slide при переключении табов | Низкая |

### ❌ НЕТ

| Что | Описание | Источник | Сложность |
|-----|----------|----------|-----------|
| Выбор карты | Визуальное превью карты с информацией | Vampire Survivors (Stage Selection) | Средняя |
| Статистика сессий | Лучший счёт, время, убийства по персонажам | Vampire Survivors | Средняя |
| Quick Start | Случайный персонаж + карта | Vampire Survivors | Низкая |
| Описание аркан | Подсказки при выборе арканы | — | Низкая |

---

## ЧАСТЬ 7: НАСТРОЙКИ

### ❌ НЕТ ВСЁ

| Что | Описание | Источник | Сложность |
|-----|----------|----------|-----------|
| Громкость | Слайдер или ←→ | pygame patterns | Низкая |
| Fullscreen toggle | Переключение fullscreen/windowed | pygame patterns | Низкая |
| Показ FPS | Toggle | — | Низкая |
| Управление | Переназначение клавиш | — | Средняя |
| Кнопка "Назад" | Escape возвращает в предыдущий экран | — | Низкая |

---

## ЧАСТЬ 8: УПРАВЛЕНИЕ И НАВИГАЦИЯ

### Универсальная схема

| Действие | Клавиатура | Геймпад | Мышь/Тач |
|----------|-----------|---------|----------|
| Навигация в меню | ↑↓ / WASD | D-pad / L-stick | Hover |
| Выбор | Enter / Space | A button | Click |
| Назад | Escape | B button | Back button |
| Переключить вкладку | Tab / ←→ | LB / RB | Click на вкладку |
| Пауза | P / Escape | Start | — |
| Быстрые слоты (лобби) | 1-8 | — | — |

### Правила навигации

1. **Первый элемент автоматически выделен** при открытии меню
2. **Wrap-around** — конец списка → переход в начало
3. **Hover + Focus** — мышь и клавиатура работают одновременно
4. **Визуальный фокус** — подсветка (border, glow, arrow) выбранного элемента
5. **Escape = "назад"** везде, кроме геймплея (там = пауза)
6. **Звук** — hover (тихий клик), select (подтверждение), back (отмена)

---

## ЧАСТЬ 9: ВИЗУАЛЬНЫЙ СТИЛЬ

### Цветовая система (библейский хоррор-фэнтези)

| Роль | Цвет | Hex |
|------|-------|-----|
| Фон | Near-black | #0a0e14 — #141414 |
| Святость (акцент) | Gold/amber | #FFD600 / #F5A623 |
| Кровь/Ад | Red | #DC2626 |
| Божественное | Cyan | #22D3EE |
| XP гемы | Зелёный/золотой | #4ADE80 / #FBBF24 |
| Опасность | Красный + pulse | #EF4444 |
| Текст основной | Белый | #FFFFFF |
| Текст вторичный | Серый | #9CA3AF |

### Шрифты

| Роль | Шрифт | Размер |
|------|--------|--------|
| Заголовки | Space Grotesk Bold | 32-48px |
| Текст | Space Grotesk Regular | 16-20px |
| Моно (числа, таймер) | JetBrains Mono | 14-18px |
| Пиксельный (ретро) | Press Start 2P | 8-12px |

---

## ЧАСТЬ 10: АРХИТЕКТУРА ЭКРАНОВ

### Scene Manager Pattern (рекомендуемый)

```python
from enum import Enum

class GameState(Enum):
    TITLE = "title"
    LOBBY = "lobby"
    GAME = "game"
    PAUSE = "pause"        # overlay поверх GAME
    GAME_OVER = "game_over"
    SETTINGS = "settings"
    LEADERBOARD = "leaderboard"
    BESTIARY = "bestiary"

# Каждый экран — класс с 3 методами:
class BaseScreen:
    def handle_events(self, events: list) -> str:
        """Обработка ввода. Возвращает имя следующего экрана или self."""
        pass
    def update(self):
        """Логика обновления."""
        pass
    def draw(self, screen: pygame.Surface):
        """Рендер."""
        pass

# Overlay Pattern для паузы:
# - Пауза НЕ отдельная сцена, а overlay поверх game
# - game.render() вызывается ВСЕГДА
# - game.update() НЕ вызывается
# - Затемнение: Surface(SRCALPHA) + draw.rect((0,0,0,150))
```

### Структура меню

```
Title Screen
    └── Main Menu
        ├── Start → Lobby → Game → Pause (overlay) → Game Over
        ├── Quick Start → Game (случайный)
        ├── Heroes → Character Select → Lobby
        ├── Arcanas → Arcana Select → Lobby
        ├── PowerUps → Shop → Lobby
        ├── Bestiary → Enemy List
        ├── Collection → Item List
        ├── Leaderboard → Score Table
        ├── Settings → Options
        └── Quit
```

---

## ЧАСТЬ 11: ПАТТЕРНЫ ИЗ СКИЛЛОВ

### pixel-art-sprites (v2.1)

| Что | Статус | Применение |
|-----|--------|------------|
| 9 VFX-типов | ✅ Сгенерированы | explosion, lightning, slash, trail, particle, crit_flash, evolution_glow, whip_sweep, ring_wave |
| 8 палитр | ✅ Есть | fire, holy, lightning, blood, poison, ice, dark, slash |
| 7 состояний | ✅ Есть | idle + 4 walk + attack_down + death |
| Python API | ✅ Работает | `from vfx_generator import generate_vfx` |

### game-modifier-patterns

| Что | Статус | Применение |
|-----|--------|------------|
| Arcana-система | ✅ Работает | 5 аркан с apply() hooks |
| Relic spawner | ✅ Работает | ground cap, pool sampling, uniqueness |
| Explicit multipliers | ✅ Работает | damage_mult, cooldown_mult, area_mult |
| Headless testing | ✅ Работает | SDL dummy driver, fixed dt |

### godot-ui-ux-patterns (переносимые для pygame)

| Паттерн | Описание | Применение |
|---------|----------|------------|
| Tween fade-in | 0.3s появление | Меню, карточки левелапа |
| Tween slide-in | Элемент въезжает сбоку | Переходы между экранами |
| Staggered buttons | 0.1s задержка между кнопками | Пункты меню |
| Shake effect | intensity 5.0, duration 0.3s | Криты, удары по игроку |
| Horror UI | near-black + cyan акценты | Весь стиль игры |

---

## ЧАСТЬ 12: ПРИОРИТЕТЫ РЕАЛИЗАЦИИ

### P0 — Критично (сделать сразу)

1. **Scene Manager** — базовая архитектура для всех экранов
2. **Flash on hit** — самый дешёвый juice (1 строка)
3. **Эволюция glow** — evolution_glow уже готов

### P1 — Важно (сделать скоро)

4. **Главное меню** — title + кнопки + навигация
5. **Пауза** — overlay + текущий билд + статистика
6. **Game Over** — статистика + кнопки
7. **Анимация карточек левелапа** — stagger + fade-in
8. **Пульсация HP-бара** — при <30% HP

### P2 — Желательно (сделать позже)

9. **Настройки** — громкость + fullscreen
10. **Индикатор направления врагов** — стрелки за краем экрана
11. **Лидерборд** — локальное сохранение
12. **Статистика в лобби** — лучший счёт, время, убийства
13. **Табы в лобби** — навигация между секциями

### P3 — Бонус (когда будет время)

14. **Reroll / Skip / Banish** — мета-прогрессия левелапа
15. **Бестарий** — список врагов с описаниями
16. **Коллекция** — список оружий/пассивок
17. **Quick Start** — случайный запуск
18. **Анимация "дождь из гемов"** — при левелапе
19. **Heartbeat звук** — при низком HP

---

## ИСТОЧНИКИ

- Vampire Survivors Wiki: vampire.survivors.wiki
- Game UI Redesign VS (Behance): behance.net/gallery/206783911
- Unity Case Study VS (Medium): medium.com/@simon.nordon
- Creating a Rogue-like (Terresquall): blog.terresquall.com
- Catador Portfolio: edward-tsai.com/catador
- Anvil Survivors (YouTube): visual clarity in survivor-likes
- Godot Survivor (kekkorider): itch.io devlog
- SU-93 Survivor: itch.io devlog
- Another Survivor (FxGames): itch.io devlog
- Game Modes Pattern: patternsgameprog.com
- Pygame Menus: elijahlopez.ca, medium.com/@fulton_shaun, codeforc.com
- Monster Survivors Navigation: october-studio.gitbook.io
- Juicy Navigation Overlay: minaristudio.itch.io
- Game UI Database: gameuidatabase.com
- Long Dark HUD: gamedeveloper.com
- Pixel Art UI/GUI: jesseeisenbart.itch.io
