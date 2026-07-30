# AGENTS.md — Birth of the Saint

## Project
"Рождение святого" — Roguelike-survivors (Vampire Survivors clone).
Библейский хоррор-фэнтези. Python/pygame-ce, браузер через pygbag.

## Stack
- Python 3.12+ / pygame-ce
- pygbag (browser deployment)
- No external assets in MVP (procedural sounds via synth)

## Setting
Библейский хоррор-фэнтези. Святой против сил ада.
Мир пал, церкви в руинах, из трещин лезет нечисть.
Среди руин рождается один — не от плоти, а от веры.

## Session
- Длительность: 15 минут (900 сек) → Жнец
- Карта: бесконечная арена 4000x4000, 4 кольца-биома
- Кольцо 1 (0-1000px): Руины — серо-синий фон
- Кольцо 2 (1000-2000px): Кладбище — зелёный туман
- Кольцо 3 (2000-3000px): Адский лес — красный
- Кольцо 4 (3000-4000px): Пустошь — чёрный, кости
- Препятствия: руины, надгробия, деревья (блокируют движение и снаряды)
- Map events: рой, окружение, элита

## Visual
- Пиксель-арт, 16x16 / 32x32
- Игрок 28x28, враги 24-34, босс 76, гемы 6-10, снаряды 12-14
- Glow вокруг снарядов/гемов, белая вспышка при ударе врага
- Шрифт MVP: pygame default (встроенный)
- Палитры по биомам в config.py: BIOME_COLORS dict

## Meta-progression (между ранами)
- Золото сохраняется после смерти
- Лобби: магазин PowerUp (Мощь/Стойкость/Проворство/Жадность/Удача/Воскрешение)
- Разблокировки за достижения: персонажи, оружия
- Статистика: лучшая волна, время, убийства, золото, количество ран

## Structure
```
main.py          — entry point, game loop (async for pygbag)
config.py        — constants, formulas, ALL shared config
player.py        — Player class, 3 characters
weapons.py       — 6 weapon types, evolutions, passive items
enemies.py       — 6 enemy types, AI
projectiles.py   — Projectile, Particle, DamageNumber, Pulse
wave_manager.py  — wave system, enemy spawning
xp_system.py     — XP gems, LevelUpScreen
hud.py           — HP/XP bars, weapon/passive icons
camera.py        — camera follow, scroll
effects.py       — screen shake, flash, grid rendering
sounds.py        — synth-based sound generation
menu.py          — main menu, character select, game over
assets/          — sprites, sounds, tiles (docs in assets/README.md)
graphify-out/    — dependency graph (283 nodes, 449 edges)
```

## Rules
1. ALL shared constants go in config.py — never hardcode in other files
2. Weapon types: add to WEAPON_DEFS dict + create Weapon subclass in weapons.py
3. Enemy types: add to ENEMY_TYPES dict in enemies.py
4. Passive items: add to PASSIVE_DEFS in weapons.py + update Player.update_stats()
5. Game loop is async (await asyncio.sleep(0)) — required for pygbag
6. No external file dependencies in MVP — all sounds generated via synth
7. pygame-ce only (not pygame) — community edition has better WASM support
8. Player movement: WASD + arrows, all in player.py handle_input()
9. Camera follows player — never hardcode screen positions for game objects

## Critical Files (do NOT edit without impact check)
- config.py (12 dependents) — changing formulas affects ALL weapons/enemies
- weapons.py (3 dependents) — weapon changes affect combat + HUD
- projectiles.py (4 dependents) — projectile changes affect all ranged weapons

## Commands
```bash
# Run locally
cd E:/birth-of-saint && python main.py

# Build for browser
pip install pygbag
pygbag --build .

# Dependency scan
python scripts/project.py init E:/birth-of-saint -v

# Impact check before edit
python scripts/project.py impact <file> -p E:/birth-of-saint
```
