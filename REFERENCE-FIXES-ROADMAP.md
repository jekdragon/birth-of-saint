# Reference Fixes Roadmap (ref_vs_clone.py → birth-of-saint)

> Created: 2026-08-01
> Source: E:/birth-of-saint/ref_vs_clone.py (3617 lines)
> Status: 10/13 DONE (1-10 complete, 11-13 advanced)

---

## DONE ✅

| # | Fix | File | Impact |
|---|-----|------|--------|
| 1 | i-frames after hit (0.75с) | player.py | CRITICAL — game was unplayable |
| 2 | Multi-level XP (while loop) | main.py | HIGH — big XP gems lost levels |
| 3 | Spawn distance 40→200 | config.py | HIGH — enemies spawned in walls |
| 4 | Half-cooldown retry | weapons.py | MEDIUM — weapon dead air |
| 5 | Slow/freeze status | enemies.py, weapons.py | MEDIUM — Bell=freeze, Lightning=slow, blue tint |
| 6 | Enemy world clamp | enemies.py | MEDIUM — enemies can't walk off map |
| 7 | Weapon idle retry ALL types | weapons.py | MEDIUM — all 9 weapons have half-cooldown retry |
| 8 | Gold coin pickups | projectiles.py, main.py, config.py | MEDIUM — 40% drop, magnet, boss rain |
| 9 | Achievement toasts in-run | hud.py, main.py | MEDIUM — periodic check 2s, toast queue |
| 10 | Telegraphed lightning | projectiles.py, weapons.py | MEDIUM — shrinking ring warning 0.3s, on_strike callback for delayed damage |

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
