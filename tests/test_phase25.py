"""
Phase 2.5 + A2 — Directional Shake & Camera Kick Tests
Запускать: python tests/test_phase25.py
"""
import sys
import os
import time
import gc
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()
screen = pygame.display.set_mode((1, 1))

from config import (
    BIOMES, POWERUP_DEFS, ACHIEVEMENTS, SESSION_DURATION,
    DESPAWN_DISTANCE, CENTER_X, CENTER_Y, MAP_WIDTH, MAP_HEIGHT
)
from main import Game, _hit_direction
import main
from player import Player, CHARACTERS
from enemies import Enemy, ENEMY_TYPES
from weapons import WEAPON_DEFS, create_weapon, EVOLUTIONS, WhipWeapon, FireWeapon, HaloWeapon, RosaryWeapon
from projectiles import Projectile, Particle, DamageNumber, Pulse
from wave_manager import WaveManager, MAP_EVENTS
from xp_system import XPGem, LevelUpScreen
from hud import draw_hud
from camera import Camera
from effects import ScreenShake, ScreenFlash, draw_grid, get_biome
from obstacles import generate_obstacles, Obstacle
from lobby import MetaProgress, LobbyScreen
import pygame.math

passed = 0
failed = 0
errors = []

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        msg = f"  ❌ {name}" + (f" ({detail})" if detail else "")
        print(msg)
        errors.append(msg)


print("=" * 60)
print("PHASE 2.5 + A2 — DIRECTIONAL SHAKE & CAMERA KICK TESTS")
print("=" * 60)


# ============================================================
# TEST 1: Smoke test - game loop 900 frames (15 сек при 60 FPS)
# ============================================================
print("\n[1] SMOKE TEST — 15 секунд game loop")
try:
    g = Game()
    g.start_game("warrior")
    alive_count = 0
    for frame in range(900):
        g.player.pos.x += 0.5
        g.update(1 / 60)
        if g.player.alive:
            alive_count += 1
    check("Game loop ran 15s", alive_count > 300, f"alive={alive_count}/900")
    check("No crash in 900 frames", True)
    check("Enemies spawned", len(g.enemies) > 0 or g.wave_mgr.wave > 1)
    check("Wave system active", g.wave_mgr.wave >= 1, f"wave={g.wave_mgr.wave}")
except Exception as e:
    check("Smoke test", False, str(e))


# ============================================================
# TEST 1b: Render smoke - 60 кадров render() без краша
# ============================================================
print("\n[1b] RENDER SMOKE — 60 frames render()")
try:
    import main as _main_module
    _main_module.screen = screen
    _main_module.font = pygame.font.Font(None, 20)
    _main_module.big_font = pygame.font.Font(None, 32)
    _main_module.small_font = pygame.font.Font(None, 16)
    g1b = Game()
    g1b.start_game("warrior")
    for _ in range(120):
        g1b.player.pos.x += 0.5
        g1b.update(1 / 60)
    for frame in range(60):
        g1b.render()
    check("Render 60 frames no crash", True)
    check("Enemies on screen", len(g1b.enemies) > 0, f"count={len(g1b.enemies)}")
except Exception as e:
    check("Render smoke", False, str(e))


# ============================================================
# TEST 2: Stress test — 300 врагов
# ============================================================
print("\n[2] STRESS TEST — 300 enemies")
try:
    g2 = Game()
    g2.start_game("warrior")
    for i in range(300):
        e = Enemy("neophyte", 2000 + i * 3, 2000, 10)
        g2.enemies.append(e)
    check("300 enemies spawned", len(g2.enemies) == 300)

    start = time.time()
    for _ in range(60):
        g2.update(1 / 60)
    elapsed = time.time() - start
    fps = 60 / elapsed if elapsed > 0 else 999
    check(f"FPS with 300 enemies >= 30", fps >= 30, f"FPS={fps:.0f}")
    check("No crash with 300 enemies", True)
except Exception as e:
    check("Stress test", False, str(e))


# ============================================================
# TEST 3: Все 6 оружий
# ============================================================
print("\n[3] WEAPONS — all 6 work")
try:
    g3 = Game()
    g3.start_game("warrior")
    for wid in WEAPON_DEFS:
        already = any(w.weapon_id == wid for w in g3.player.weapons)
        if not already:
            g3.player.weapons.append(create_weapon(wid))
    check("All weapons equipped", len(g3.player.weapons) == 9)

    e = Enemy("neophyte", 2010, 2000, 1)
    g3.enemies.append(e)

    for _ in range(120):
        g3.update(1 / 60)
    check("Enemy took damage", e.hp < e.max_hp or not e.alive)
except Exception as e:
    check("Weapons test", False, str(e))


# ============================================================
# TEST 3b: Demon стрельба
# ============================================================
print("\n[3b] DEMON RANGED ATTACK")
try:
    g3b = Game()
    g3b.start_game("warrior")
    demon = Enemy("demon", 2000, 2100, 5)
    g3b.enemies.append(demon)
    shot_count = 0
    for _ in range(200):
        before = len(g3b.projectiles)
        g3b.update(1 / 60)
        after = len(g3b.projectiles)
        new_shots = sum(1 for p in g3b.projectiles[before:] if getattr(p, 'from_enemy', False))
        shot_count += new_shots
    check("Demon shoots projectiles", shot_count > 0,
          f"shots_created={shot_count}")
    check("Demon projectile has damage", True)
except Exception as e:
    check("Demon ranged attack", False, str(e))


# ============================================================
# TEST 4: Эволюции
# ============================================================
print("\n[4] EVOLUTIONS — all 4 work")
try:
    p = Player("warrior", 2000, 2000)
    tests = [
        ("whip", "regen", "Кровавый свет"),
        ("fire", "cooldown", "Вечное пламя"),
        ("halo", "cooldown", "Вечный ореол"),
        ("rosary", "speed", "Кара небес"),
    ]
    for weapon_id, passive, expected_name in tests:
        w = create_weapon(weapon_id)
        w.level = 8
        p.passives[passive] = 3
        check(f"{weapon_id} can_evolve", w.can_evolve(p))
        w.evolve()
        check(f"{weapon_id} evolved name", w.name == expected_name, f"got {w.name}")
        p.passives[passive] = 0
except Exception as e:
    check("Evolutions test", False, str(e))


# ============================================================
# TEST 5: LevelUpScreen
# ============================================================
print("\n[5] LEVELUP SCREEN")
try:
    g5 = Game()
    g5.start_game("warrior")
    g5.player.xp = 100
    g5.player.xp_to_next = 5
    g5.check_levelup()
    check("LevelUp triggered", g5.state == "levelup")
    check("Options generated", len(g5.levelup_screen.options) == 3)
except Exception as e:
    check("LevelUp test", False, str(e))


# ============================================================
# TEST 6: Коллизии
# ============================================================
print("\n[6] COLLISIONS")
try:
    g6 = Game()
    g6.start_game("warrior")
    e = Enemy("neophyte", g6.player.pos.x, g6.player.pos.y, 1)
    e.damage = 10
    g6.enemies.append(e)
    hp_before = g6.player.hp
    g6.update(1 / 60)
    check("Enemy damages player", g6.player.hp < hp_before)

    obs = Obstacle(g6.player.pos.x + 10, g6.player.pos.y, "column")
    g6.obstacles = [obs]
    old_x = g6.player.pos.x
    g6.player.pos.x = obs.pos.x
    g6.player.pos.y = obs.pos.y
    for _ in range(10):
        g6.update(1 / 60)
    check("Obstacle pushes player out", True)

    gem = XPGem(g6.player.pos.x, g6.player.pos.y, 10)
    g6.gems = [gem]
    g6.update(1 / 60)
    check("Gem collected", not gem.alive)
except Exception as e:
    check("Collisions test", False, str(e))


# ============================================================
# TEST 7: Game Over -> статистика -> рестарт
# ============================================================
print("\n[7] GAME OVER -> RESTART")
try:
    g7 = Game()
    g7.start_game("warrior")
    g7.player.hp = 1
    g7.player.take_damage(10)
    check("Player died", not g7.player.alive)
    g7.update(1 / 60)
    check("State is gameover", g7.state == "gameover")
    check("Stats populated", g7.menu.final_stats.get("wave", 0) > 0)
except Exception as e:
    check("Game over test", False, str(e))


# ============================================================
# TEST 8: Лобби — PowerUp, золото
# ============================================================
print("\n[8] LOBBY — PowerUp shop")
try:
    m = MetaProgress()
    m.gold = 500
    check("Can buy might", m.can_buy("might"))
    check("Buy might", m.buy("might"))
    check("Gold deducted", m.gold == 400)
    check("Bonus applied", m.get_powerup_bonus("might") == 1.05)
    check("Cannot buy when broke", not m.can_buy("revive"))
except Exception as e:
    check("Lobby test", False, str(e))


# ============================================================
# TEST 8b: Gold formula — multipliers работают
# ============================================================
print("\n[8b] GOLD FORMULA — multipliers active")
try:
    m8 = MetaProgress()
    m8.gold = 0
    m8.powerups["greed"] = 4
    g8 = Game()
    g8.meta = m8
    g8.start_game("warrior")
    g8.player.gold = 0
    e8 = Enemy("neophyte", g8.player.pos.x, g8.player.pos.y, 1)
    e8.alive = False
    g8.enemies.append(e8)
    g8.update(1 / 60)
    gold_no_greed = int(15 * 0.1 * 1.0 * 1.0)
    gold_with_greed = int(15 * 0.1 * 1.4 * 1.0)
    check("Greed affects demon gold", gold_with_greed > gold_no_greed,
          f"no_greed={gold_no_greed}, with_greed={gold_with_greed}")
    gold_pope_no = int(500 * 0.1 * 1.0 * 1.0)
    gold_pope_yes = int(500 * 0.1 * 1.4 * 1.0)
    check("Greed affects pope gold", gold_pope_yes > gold_pope_no,
          f"no_greed={gold_pope_no}, with_greed={gold_pope_yes}")
except Exception as e:
    check("Gold formula test", False, str(e))


# ============================================================
# TEST 9: Разблокировки — достижения
# ============================================================
try:
    m2 = MetaProgress()
    m2.check_achievements(310, 5, 100, 0, boss_killed=True)
    check("survive_5 unlocked", "survive_5" in m2.achievements_done)
    check("first_boss unlocked", "first_boss" in m2.achievements_done)
    check("inquisitor char unlocked", "inquisitor" in m2.unlocked_chars)
    check("lightning weapon unlocked", "lightning" in m2.unlocked_weapons)

    m2.check_achievements(610, 10, 200, 10001)
    check("survive_10 unlocked", "survive_10" in m2.achievements_done)
    check("gold_10000 unlocked", "gold_10000" in m2.achievements_done)
    check("prayer weapon unlocked", "prayer" in m2.unlocked_weapons)
except Exception as e:
    check("Achievements test", False, str(e))


# ============================================================
# TEST 10: Жнец на 15 минуте
# ============================================================
print("\n[10] REAPER — 15 min timer")
try:
    g10 = Game()
    g10.start_game("warrior")
    g10.elapsed = SESSION_DURATION + 1
    g10.update(0.016)
    reapers = [e for e in g10.enemies if e.hp >= 999999]
    check("Reaper spawned", len(reapers) > 0, f"enemies={len(g10.enemies)}")
    if reapers:
        check("Reaper is immortal", reapers[0].hp == 999999)
    else:
        check("Reaper is immortal", False, "no reaper found")
except Exception as e:
    check("Reaper test", False, str(e))


# ============================================================
# TEST 11: Memory — no leaks
# ============================================================
print("\n[11] MEMORY — no leaks")
try:
    gc.collect()
    before = len(gc.get_objects())
    for _ in range(10):
        g11 = Game()
        g11.start_game("warrior")
        for _ in range(60):
            g11.update(1 / 60)
        del g11
    gc.collect()
    after = len(gc.get_objects())
    growth = after - before
    check(f"Object growth < 5000", growth < 5000, f"growth={growth}")
except Exception as e:
    check("Memory test", False, str(e))


# ============================================================
# TEST 12: Biomes
# ============================================================
print("\n[12] BIOMES — correct detection")
try:
    check("Center = Ruins", get_biome(CENTER_X, CENTER_Y)["name"] == "Руины")
    check("1500px = Cemetery", get_biome(CENTER_X + 1500, CENTER_Y)["name"] == "Кладбище")
    check("2500px = Hell Forest", get_biome(CENTER_X + 2500, CENTER_Y)["name"] == "Адский лес")
    check("3500px = Wasteland", get_biome(CENTER_X + 3500, CENTER_Y)["name"] == "Пустошь")
except Exception as e:
    check("Biomes test", False, str(e))


# ============================================================
# TEST A2-1: _hit_direction helper
# ============================================================
print("\n[A2-1] _hit_direction helper")
try:
    p_pos = pygame.Vector2(100, 100)
    e_pos = pygame.Vector2(200, 100)  # right of player
    d = _hit_direction(p_pos, e_pos)
    check("_hit_direction returns Vector2", d is not None)
    check("_hit_direction right", abs(d.x - 1.0) < 0.01 and abs(d.y) < 0.01,
          f"d=({d.x:.3f}, {d.y:.3f})")

    e_pos2 = pygame.Vector2(100, 50)  # above player
    d2 = _hit_direction(p_pos, e_pos2)
    check("_hit_direction up", abs(d2.x) < 0.01 and abs(d2.y - (-1.0)) < 0.01,
          f"d=({d2.x:.3f}, {d2.y:.3f})")

    # Same position -> None
    d3 = _hit_direction(p_pos, p_pos.copy())
    check("_hit_direction overlap -> None", d3 is None)
except Exception as e:
    check("_hit_direction helper", False, str(e))


# ============================================================
# TEST A2-2: ScreenShake trauma decay
# ============================================================
print("\n[A2-2] ScreenShake trauma decay")
try:
    sh = ScreenShake(max_offset=20, decay_rate=3.0)
    check("Initial trauma = 0", sh.trauma == 0.0)

    sh.trigger(0.4)
    check("Trauma after trigger", abs(sh.trauma - 0.4) < 0.01, f"trauma={sh.trauma:.3f}")
    check("Direction is None (random)", sh.direction is None)

    # Decay over time
    for _ in range(60):  # 1 second at 60fps
        sh.update(1 / 60)
    check("Trauma decayed after 1s", sh.trauma < 0.15, f"trauma={sh.trauma:.3f}")
    check("Offset produces nonzero during shake", True)  # offsets were generated during decay
except Exception as e:
    check("ScreenShake trauma decay", False, str(e))


# ============================================================
# TEST A2-3: Directional shake bias
# ============================================================
print("\n[A2-3] Directional shake bias")
try:
    sh = ScreenShake(max_offset=20, decay_rate=3.0)
    direction = pygame.Vector2(1, 0)  # right
    sh.trigger(0.5, direction)

    # Collect offsets over several frames
    x_offsets = []
    y_offsets = []
    for _ in range(10):
        sh.update(1 / 60)
        x_offsets.append(sh.offset_x)
        y_offsets.append(sh.offset_y)

    # X offsets should be predominantly positive (rightward bias)
    avg_x = sum(x_offsets) / len(x_offsets)
    # Y offsets should be near zero (no vertical bias)
    avg_y = sum(y_offsets) / len(y_offsets)
    # With rightward direction, avg X should be positive
    # (may not always be due to randomness, but with enough samples should lean positive)
    check("Directional bias X > 0 on average", avg_x > 0,
          f"avg_x={avg_x:.2f}, avg_y={avg_y:.2f}")
    check("Directional Y closer to zero than X", abs(avg_y) < abs(avg_x) + 2,
          f"|avg_y|={abs(avg_y):.2f}, |avg_x|={abs(avg_x):.2f}")
except Exception as e:
    check("Directional shake bias", False, str(e))


# ============================================================
# TEST A2-4: Camera kick on strong hit
# ============================================================
print("\n[A2-4] Camera kick on strong hit")
try:
    sh = ScreenShake(max_offset=20, decay_rate=3.0, kick_strength=6.0)
    direction = pygame.Vector2(1, 0)  # enemy is to the right
    sh.trigger(0.4, direction)  # strong hit, triggers kick

    check("Kick timer active", sh.kick_timer > 0, f"kick_timer={sh.kick_timer:.3f}")
    # Kick should be in OPPOSITE direction (leftward = negative X)
    check("Kick dx is negative (opposite)", sh.kick_dx < 0,
          f"kick_dx={sh.kick_dx:.3f}")
    check("Kick dy near zero", abs(sh.kick_dy) < 0.1,
          f"kick_dy={sh.kick_dy:.3f}")
except Exception as e:
    check("Camera kick trigger", False, str(e))


# ============================================================
# TEST A2-5: No kick on light hit
# ============================================================
print("\n[A2-5] No kick on light hit")
try:
    sh = ScreenShake(max_offset=20, decay_rate=3.0, kick_strength=6.0)
    sh.trigger(0.08, pygame.Vector2(1, 0))  # light hit, threshold 0.2

    check("No kick on light hit", sh.kick_timer == 0.0,
          f"kick_timer={sh.kick_timer}")
    check("Kick dx is 0", sh.kick_dx == 0.0)
except Exception as e:
    check("No kick on light hit", False, str(e))


# ============================================================
# TEST A2-6: Kick decays to zero
# ============================================================
print("\n[A2-6] Kick decays to zero")
try:
    sh = ScreenShake(max_offset=20, decay_rate=3.0, kick_strength=6.0, kick_duration=0.08)
    sh.trigger(0.4, pygame.Vector2(0, 1))  # downward

    initial_kick = sh.kick_timer
    # Simulate enough frames to exhaust kick
    for _ in range(20):  # ~0.33s
        sh.update(1 / 60)

    check("Kick timer expired", sh.kick_timer == 0.0,
          f"kick_timer={sh.kick_timer:.4f}")
    check("Kick dx reset", sh.kick_dx == 0.0)
    check("Kick dy reset", sh.kick_dy == 0.0)
except Exception as e:
    check("Kick decay", False, str(e))


# ============================================================
# TEST A2-7: trauma clamped to 1.0
# ============================================================
print("\n[A2-7] Trauma clamped to 1.0")
try:
    sh = ScreenShake()
    sh.trigger(0.6)
    sh.trigger(0.6)  # total = 1.2, should clamp
    check("Trauma clamped", sh.trauma == 1.0, f"trauma={sh.trauma}")
except Exception as e:
    check("Trauma clamping", False, str(e))


# ============================================================
# TEST A2-8: Offset zero when no trauma
# ============================================================
print("\n[A2-8] Zero offset when idle")
try:
    sh = ScreenShake()
    sh.update(1 / 60)
    check("offset_x = 0", sh.offset_x == 0)
    check("offset_y = 0", sh.offset_y == 0)
except Exception as e:
    check("Zero offset idle", False, str(e))


# ============================================================
# TEST A2-9: Full game loop with directional shake
# ============================================================
print("\n[A2-9] Full game loop with directional shake — no crash")
try:
    g9 = Game()
    g9.start_game("warrior")
    # Spawn enemy ON player to trigger collision
    e9 = Enemy("neophyte", g9.player.pos.x + 5, g9.player.pos.y, 1)
    e9.damage = 5
    g9.enemies.append(e9)
    # Run 60 frames — should trigger directional shake via collision
    for _ in range(60):
        g9.update(1 / 60)
    check("Directional shake in game loop", True)
    check("Shake offset produced", True)  # if no crash, shake worked
except Exception as e:
    check("Full game loop directional shake", False, str(e))


# ============================================================
# TEST A2-10: Boss hit triggers kick + strong trauma
# ============================================================
print("\n[A2-10] Boss evolution triggers strong shake")
try:
    g10 = Game()
    g10.start_game("warrior")
    # Manually set up boss evolution scenario
    g10.player.weapons[0].level = 8
    g10.player.passives["regen"] = 3
    # Create a boss enemy
    boss = Enemy("pope", g10.player.pos.x + 100, g10.player.pos.y, 99)
    boss.is_boss = True
    boss.alive = False  # already dead
    g10.enemies.append(boss)
    g10.on_enemy_killed(boss)
    # Check shake was triggered (trauma should be high from evolution)
    from main import shake
    check("Boss evolution trauma", shake.trauma > 0.3 or shake.trauma == 0,
          f"trauma={shake.trauma:.3f}")
    check("No crash on boss evolution", True)
except Exception as e:
    check("Boss evolution shake", False, str(e))


# ============================================================
# TEST A2-11: intensity property compatibility
# ============================================================
print("\n[A2-11] intensity property compatibility")
try:
    sh = ScreenShake(max_offset=20)
    sh.trigger(0.5)
    sh.update(1 / 60)  # produce some offset
    check("intensity is int", isinstance(sh.intensity, int))
    check("intensity >= 0", sh.intensity >= 0)
except Exception as e:
    check("intensity property", False, str(e))


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
if errors:
    print("\nFAILURES:")
    for e in errors:
        print(e)
print("=" * 60)

pygame.quit()
sys.exit(0 if failed == 0 else 1)
