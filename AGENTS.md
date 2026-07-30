# AGENTS.md — Birth of the Saint

## Project
Roguelike-survivors (Vampire Survivors clone) on Python/pygame-ce.
Browser deployment via pygbag (WebAssembly).

## Stack
- Python 3.12+ / pygame-ce
- pygbag (browser deployment)
- No external assets in MVP (procedural sounds via synth)

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
