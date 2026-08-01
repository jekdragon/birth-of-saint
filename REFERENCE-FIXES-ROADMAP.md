# Reference Fixes Roadmap (ref_vs_clone.py → birth-of-saint)

> Created: 2026-08-01
> Source: E:/birth-of-saint/ref_vs_clone.py (3617 lines)
> Status: 4/9 DONE

---

## DONE ✅

| # | Fix | File | Impact |
|---|-----|------|--------|
| 1 | i-frames after hit (0.75с) | player.py | CRITICAL — game was unplayable |
| 2 | Multi-level XP (while loop) | main.py | HIGH — big XP gems lost levels |
| 3 | Spawn distance 40→200 | config.py | HIGH — enemies spawned in walls |
| 4 | Half-cooldown retry | weapons.py | MEDIUM — weapon dead air |

## TODO ⏳

### Tier 1: Gameplay Feel (30 min)

| # | Fix | File(s) | Description | Difficulty |
|---|-----|---------|-------------|------------|
| 5 | Slow/freeze status | enemies.py, weapons.py | Add `apply_slow(factor, duration)` and `apply_freeze(duration)` to Enemy. Wire to Bell weapon. Visual: tint blue when slowed. | Easy |
| 6 | Enemy world clamp | enemies.py | `pos.x = clamp(pos.x, 0, MAP_WIDTH)` in update(). Prevents enemies walking off map. | Easy |
| 7 | Weapon idle retry for ALL types | weapons.py | Whip, Lightning, Bell, Prayer also use half-cooldown when no targets. Currently only Fire+Incense fixed. | Easy |

### Tier 2: Content from Reference (1-2 hours)

| # | Fix | File(s) | Description | Difficulty |
|---|-----|---------|-------------|------------|
| 8 | Gold coin pickups | projectiles.py, main.py, config.py | 40% drop chance per kill. Physical coin entity with magnet attract. Boss = coin rain. Replace auto-credit `score*0.1`. | Medium |
| 9 | Achievement toasts in-run | hud.py, main.py | Show animated toast when achievement unlocked DURING gameplay (not just on death). ToastManager already exists. | Medium |
| 10 | Telegraphed lightning | projectiles.py | LightningBolt shows shrinking ring 18 frames before strike. Player can dodge. | Medium |

### Tier 3: Advanced (2+ hours)

| # | Fix | File(s) | Description | Difficulty |
|---|-----|---------|-------------|------------|
| 11 | Boss ranged attacks | enemies.py, projectiles.py | Boss fires radial projectiles on timer. Separate Boss class with attack patterns. | Hard |
| 12 | Summoner enemy | enemies.py, wave_manager.py | Necromancer spawns minions that track summoner. New ENEMY_TYPES entry. | Hard |
| 13 | Chest → Drone/Turret | projectiles.py, main.py | Chest drop grants orbiting drone or placed turret ally. New entity type. | Hard |

---

## Execution Order

```
5 → 6 → 7 (quick wins, 30 min)
    ↓
8 → 9 → 10 (content, 1-2 hours)
    ↓
11 → 12 → 13 (advanced, 2+ hours)
```

## Verification

After each fix:
1. `python tests/test_phase25.py` — must pass
2. Ad-hoc test for the specific change
3. Manual playtest if gameplay change

## Notes

- Fix #8 (gold coins) is the highest-impact content addition — changes the entire economy feel
- Fix #10 (telegraphed lightning) is the best bang-for-buck visual improvement
- Fix #11-13 are optional — game is complete without them
- Reference file: E:/birth-of-saint/ref_vs_clone.py
