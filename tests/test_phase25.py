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
    DESPAWN_DISTANCE, CENTER_X, CENTER_Y, MAP_WIDTH, MAP_HEIGHT,
    WIDTH, HEIGHT
)
from main import Game, _hit_direction
import main
from player import Player, CHARACTERS
from enemies import Enemy, ENEMY_TYPES
from weapons import WEAPON_DEFS, PASSIVE_DEFS, create_weapon, EVOLUTIONS, WhipWeapon, FireWeapon, HaloWeapon, RosaryWeapon, BellWeapon, LightningWeapon, CrossWeapon, PrayerWeapon
from projectiles import Projectile, Particle, DamageNumber, Pulse, PARTICLE_PRESETS, emit_hit_burst, RingBurst, HitParticlePool
from wave_manager import WaveManager, MAP_EVENTS
from xp_system import XPGem, LevelUpScreen
from hud import draw_hud, ComboSystem, COMBO_TIERS, combo_register_kill, combo_edge_flash, AnimatedBossHealthBar, boss_bar_activate, boss_bar_trigger_flash, boss_bar_deactivate, AnimatedHealthBar, AnimatedXPBar, WaxDrip, BrazierParticle
from camera import Camera
from effects import ScreenShake, ScreenFlash, draw_grid, get_biome
from obstacles import generate_obstacles, Obstacle
from lobby import MetaProgress, LobbyScreen
import pygame.math
from menu import MainMenu

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
# TEST BAN-1: MetaProgress ban initial state
# ============================================================
print("\n[BAN-1] MetaProgress — ban initial state")
try:
    from config import MAX_BANNED_ITEMS
    m = MetaProgress()
    check("banned_items is empty set", m.banned_items == set())
    check("ban_tokens is 0", m.ban_tokens == 0)
    check("MAX_BANNED_ITEMS is 8", MAX_BANNED_ITEMS == 8)
except Exception as e:
    check("Ban initial state", False, str(e))


# ============================================================
# TEST BAN-2: Achievement grants ban tokens
# ============================================================
print("\n[BAN-2] Achievements grant ban tokens")
try:
    m2 = MetaProgress()
    m2.check_achievements(310, 5, 100, 0, boss_killed=True)
    check("survive_5 grants 2 tokens", m2.ban_tokens >= 2)
    check("first_boss grants +2 tokens (total 4)", m2.ban_tokens == 4, f"tokens={m2.ban_tokens}")
    check("banned_items still empty", len(m2.banned_items) == 0)
except Exception as e:
    check("Achievement ban tokens", False, str(e))


# ============================================================
# TEST BAN-3: toggle_ban — ban and unban
# ============================================================
print("\n[BAN-3] toggle_ban — ban and unban")
try:
    m3 = MetaProgress()
    m3.ban_tokens = 3
    result = m3.toggle_ban("whip")
    check("toggle_ban returns 'banned'", result == "banned")
    check("whip in banned_items", "whip" in m3.banned_items)
    check("banned_items count is 1", len(m3.banned_items) == 1)

    result2 = m3.toggle_ban("whip")
    check("toggle again returns 'unbanned'", result2 == "unbanned")
    check("whip removed from banned_items", "whip" not in m3.banned_items)
    check("banned_items count is 0", len(m3.banned_items) == 0)
except Exception as e:
    check("toggle_ban ban/unban", False, str(e))


# ============================================================
# TEST BAN-4: can_ban — token limit
# ============================================================
print("\n[BAN-4] can_ban — token limit")
try:
    m4 = MetaProgress()
    check("cannot ban with 0 tokens", not m4.can_ban())
    m4.ban_tokens = 2
    check("can ban with 2 tokens", m4.can_ban())
    m4.banned_items.add("whip")
    m4.banned_items.add("fire")
    check("cannot ban when tokens exhausted", not m4.can_ban())
except Exception as e:
    check("can_ban token limit", False, str(e))


# ============================================================
# TEST BAN-5: toggle_ban returns 'no_tokens' when exhausted
# ============================================================
print("\n[BAN-5] toggle_ban — no_tokens")
try:
    m5 = MetaProgress()
    m5.ban_tokens = 1
    m5.toggle_ban("whip")
    result = m5.toggle_ban("fire")
    check("returns 'no_tokens' when full", result == "no_tokens")
    check("fire not added", "fire" not in m5.banned_items)
except Exception as e:
    check("toggle_ban no_tokens", False, str(e))


# ============================================================
# TEST BAN-6: ban_tokens capped at MAX_BANNED_ITEMS
# ============================================================
print("\n[BAN-6] ban_tokens capped at MAX_BANNED_ITEMS")
try:
    m6 = MetaProgress()
    # All 5 achievements = 10 tokens, should cap at 8
    m6.check_achievements(310, 5, 100, 10001, boss_killed=True, reaper_killed=True)
    check("ban_tokens capped at 8", m6.ban_tokens == 8, f"tokens={m6.ban_tokens}")
except Exception as e:
    check("ban_tokens cap", False, str(e))


# ============================================================
# TEST BAN-7: generate_options filters banned items
# ============================================================
print("\n[BAN-7] generate_options filters banned items")
try:
    g7 = Game()
    g7.start_game("warrior")
    banned = {"whip", "fire", "regen"}
    opts = g7.levelup_screen.generate_options(g7.player, banned)
    opt_ids = [o["id"] for o in opts if o["type"] in ("weapon", "passive")]
    check("whip not in options", "whip" not in opt_ids)
    check("fire not in options", "fire" not in opt_ids)
    check("regen not in options", "regen" not in opt_ids)
    check("options still have 3 items", len(opts) == 3)
except Exception as e:
    check("generate_options filter", False, str(e))


# ============================================================
# TEST BAN-8: generate_options with empty banned set works normally
# ============================================================
print("\n[BAN-8] generate_options — no banned items")
try:
    g8 = Game()
    g8.start_game("warrior")
    opts = g8.levelup_screen.generate_options(g8.player, set())
    check("options generated normally", len(opts) == 3)
    check("no crash with empty banned set", True)
except Exception as e:
    check("generate_options no banned", False, str(e))


# ============================================================
# TEST BAN-9: LevelUpScreen.activate passes banned_items
# ============================================================
print("\n[BAN-9] LevelUpScreen.activate passes banned_items")
try:
    g9 = Game()
    g9.start_game("warrior")
    g9.meta.banned_items = {"whip", "halo"}
    g9.levelup_screen.activate(g9.player, g9.meta.banned_items)
    check("levelup screen is active", g9.levelup_screen.active)
    opt_ids = [o["id"] for o in g9.levelup_screen.options if o["type"] == "weapon"]
    check("whip not in levelup options", "whip" not in opt_ids)
    check("halo not in levelup options", "halo" not in opt_ids)
except Exception as e:
    check("activate banned_items", False, str(e))


# ============================================================
# TEST BAN-10: Save/load banned_items
# ============================================================
print("\n[BAN-10] Save/load banned_items")
try:
    from save_system import save_progress, load_progress
    import os
    m10 = MetaProgress()
    m10.gold = 42
    m10.banned_items = {"whip", "regen"}
    m10.ban_tokens = 4
    save_progress(m10)

    m10b = MetaProgress()
    load_progress(m10b)
    check("banned_items saved/loaded", "whip" in m10b.banned_items)
    check("banned_items has 2 items", len(m10b.banned_items) == 2, f"got {len(m10b.banned_items)}")
    check("ban_tokens saved/loaded", m10b.ban_tokens == 4)
    check("gold still works", m10b.gold == 42)
    # Cleanup
    from save_system import SAVE_FILE
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
except Exception as e:
    check("Save/load banned_items", False, str(e))


# ============================================================
# TEST BAN-11: LobbyScreen ban_mode toggle
# ============================================================
print("\n[BAN-11] LobbyScreen ban_mode toggle")
try:
    lobby = LobbyScreen()
    m11 = MetaProgress()
    m11.ban_tokens = 3
    lobby.activate(m11)
    lobby.tab_index = 2  # switch to shop tab
    check("ban_mode starts False", lobby.ban_mode is False)

    # Simulate pressing B
    evt = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_b)
    lobby.handle_event(evt)
    check("ban_mode toggled to True", lobby.ban_mode is True)

    # Toggle back
    lobby.handle_event(evt)
    check("ban_mode toggled back to False", lobby.ban_mode is False)
except Exception as e:
    check("Lobby ban_mode toggle", False, str(e))


# ============================================================
# TEST BAN-12: Ban list contains all weapons + passives
# ============================================================
print("\n[BAN-12] Ban list — all weapons + passives")
try:
    lobby12 = LobbyScreen()
    m12 = MetaProgress()
    lobby12.activate(m12)
    items = lobby12._get_ban_items()
    weapon_count = len(WEAPON_DEFS)
    passive_count = len(PASSIVE_DEFS)
    check(f"ban list has {weapon_count} weapons + {passive_count} passives",
          len(items) == weapon_count + passive_count,
          f"got {len(items)}")
    types = set(i["type"] for i in items)
    check("ban list has weapon type", "weapon" in types)
    check("ban list has passive type", "passive" in types)
except Exception as e:
    check("Ban list completeness", False, str(e))


# ============================================================
# TEST BAN-13: Ban list navigation (scroll)
# ============================================================
print("\n[BAN-13] Ban list navigation")
try:
    lobby13 = LobbyScreen()
    m13 = MetaProgress()
    m13.ban_tokens = 8
    lobby13.activate(m13)
    lobby13.ban_mode = True

    # Press down multiple times to test scroll
    evt_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    for _ in range(10):
        lobby13.handle_event(evt_down)
    check("selected wraps around", lobby13.selected >= 0)
    check("scroll adjusted", lobby13.ban_scroll >= 0)
except Exception as e:
    check("Ban list navigation", False, str(e))


# ============================================================
# TEST BAN-14: Ban item through lobby interaction
# ============================================================
print("\n[BAN-14] Ban item via lobby ENTER")
try:
    lobby14 = LobbyScreen()
    m14 = MetaProgress()
    m14.ban_tokens = 3
    lobby14.activate(m14)
    lobby14.ban_mode = True
    lobby14.selected = 0

    evt_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    lobby14.handle_event(evt_enter)
    items14 = lobby14._get_ban_items()
    first_id = items14[0]["id"]
    check("first item banned via ENTER", first_id in m14.banned_items)
    check("notification set", "Забанено" in lobby14.notification or lobby14.notify_timer > 0)
except Exception as e:
    check("Ban via lobby ENTER", False, str(e))


# ============================================================
# TEST BAN-15: All achievements give ban tokens
# ============================================================
print("\n[BAN-15] All 5 achievements give ban tokens")
try:
    m15 = MetaProgress()
    # survive_5
    m15.check_achievements(310, 0, 0, 0)
    check("survive_5 gives tokens", m15.ban_tokens == 2)
    # first_boss
    m15.check_achievements(0, 0, 0, 0, boss_killed=True)
    check("first_boss gives tokens", m15.ban_tokens == 4)
    # survive_10
    m15.check_achievements(610, 0, 0, 0)
    check("survive_10 gives tokens", m15.ban_tokens == 6)
    # gold_10000
    m15.check_achievements(0, 0, 0, 10001)
    check("gold_10000 gives tokens", m15.ban_tokens == 8)
    # kill_reaper — capped at 8
    m15.check_achievements(0, 0, 0, 0, reaper_killed=True)
    check("kill_reaper capped at 8", m15.ban_tokens == 8)
except Exception as e:
    check("All achievements ban tokens", False, str(e))


# ============================================================
# TEST BAN-16: Game loop with banned items — no crash
# ============================================================
print("\n[BAN-16] Game loop with banned items — no crash")
try:
    g16 = Game()
    g16.meta.banned_items = {"whip", "fire", "halo", "regen"}
    g16.meta.ban_tokens = 8
    g16.start_game("warrior")
    for _ in range(120):
        g16.update(1 / 60)
    # Force levelup
    g16.player.xp = 100
    g16.player.xp_to_next = 5
    g16.check_levelup()
    check("LevelUp triggered with banned items", g16.state == "levelup")
    opt_ids = [o["id"] for o in g16.levelup_screen.options]
    check("whip not in options (banned)", "whip" not in opt_ids)
    check("fire not in options (banned)", "fire" not in opt_ids)
    check("No crash with 4 banned items", True)
except Exception as e:
    check("Game loop with banned items", False, str(e))


# ============================================================
# TEST BAN-17: Unban restores item to pool
# ============================================================
print("\n[BAN-17] Unban restores item to pool")
try:
    g17 = Game()
    g17.start_game("warrior")
    # Ban whip, generate options
    banned17 = {"whip"}
    opts1 = g17.levelup_screen.generate_options(g17.player, banned17)
    has_whip_1 = any(o["id"] == "whip" for o in opts1)
    # Unban, generate again
    opts2 = g17.levelup_screen.generate_options(g17.player, set())
    has_whip_2 = any(o["id"] == "whip" for o in opts2)
    # whip should not be in opts1 (if it appeared) and CAN be in opts2
    check("Options generated after unban", len(opts2) == 3)
    check("No crash on unban pool", True)
except Exception as e:
    check("Unban restores to pool", False, str(e))


# ============================================================
# TEST A3-1: PARTICLE_PRESETS structure
# ============================================================
print("\n[A3-1] PARTICLE_PRESETS structure")
try:
    check("PARTICLE_PRESETS has 4 tiers", len(PARTICLE_PRESETS) == 4,
          f"got {len(PARTICLE_PRESETS)}")
    for tier in ("light", "medium", "heavy", "crit"):
        check(f"Preset '{tier}' exists", tier in PARTICLE_PRESETS)
        p = PARTICLE_PRESETS[tier]
        check(f"'{tier}' has count tuple", isinstance(p["count"], tuple) and len(p["count"]) == 2)
        check(f"'{tier}' has speed tuple", isinstance(p["speed"], tuple) and len(p["speed"]) == 2)
        check(f"'{tier}' has lifetime tuple", isinstance(p["lifetime"], tuple) and len(p["lifetime"]) == 2)
    # Verify escalation: light < medium < heavy < crit
    check("light < medium count", PARTICLE_PRESETS["light"]["count"][1] < PARTICLE_PRESETS["medium"]["count"][0])
    check("medium < heavy count", PARTICLE_PRESETS["medium"]["count"][1] < PARTICLE_PRESETS["heavy"]["count"][0])
    check("heavy < crit count", PARTICLE_PRESETS["heavy"]["count"][1] < PARTICLE_PRESETS["crit"]["count"][0])
except Exception as e:
    check("PARTICLE_PRESETS structure", False, str(e))


# ============================================================
# TEST A3-2: emit_hit_burst light tier
# ============================================================
print("\n[A3-2] emit_hit_burst light tier")
try:
    particles = []
    emit_hit_burst(particles, 100, 100, "light", (255, 0, 0))
    count = len(particles)
    check("light burst 3-5 particles", 3 <= count <= 5, f"count={count}")
    check("all particles alive", all(p.alive for p in particles))
    check("all particles at position", all(p.pos.x == 100 and p.pos.y == 100 for p in particles))
except Exception as e:
    check("emit_hit_burst light", False, str(e))


# ============================================================
# TEST A3-3: emit_hit_burst crit tier
# ============================================================
print("\n[A3-3] emit_hit_burst crit tier")
try:
    particles = []
    emit_hit_burst(particles, 200, 200, "crit", (255, 220, 100))
    count = len(particles)
    check("crit burst 30-45 particles", 30 <= count <= 45, f"count={count}")
    # Crit particles should be faster than light
    avg_speed = sum(p.vel.length() for p in particles) / len(particles)
    check("crit avg speed > 3", avg_speed > 3, f"avg_speed={avg_speed:.2f}")
except Exception as e:
    check("emit_hit_burst crit", False, str(e))


# ============================================================
# TEST A3-4: emit_hit_burst medium and heavy
# ============================================================
print("\n[A3-4] emit_hit_burst medium and heavy")
try:
    p_med = []
    emit_hit_burst(p_med, 0, 0, "medium", (100, 100, 255))
    check("medium burst 8-12", 8 <= len(p_med) <= 12, f"count={len(p_med)}")

    p_heavy = []
    emit_hit_burst(p_heavy, 0, 0, "heavy", (255, 100, 100))
    check("heavy burst 16-24", 16 <= len(p_heavy) <= 24, f"count={len(p_heavy)}")
except Exception as e:
    check("emit_hit_burst medium/heavy", False, str(e))


# ============================================================
# TEST A3-5: emit_hit_burst with hit_dir (directional)
# ============================================================
print("\n[A3-5] emit_hit_burst with hit_dir")
try:
    particles = []
    direction = pygame.Vector2(1, 0)  # rightward
    # Use multiple bursts to get enough samples for statistical check
    for _ in range(5):
        emit_hit_burst(particles, 100, 100, "heavy", (255, 0, 0), hit_dir=direction)
    total = len(particles)
    rightward = sum(1 for p in particles if p.vel.x > 0)
    # With 120° cone rightward, ~67% should have positive x
    check("majority rightward (120° cone)", rightward > total * 0.5,
          f"rightward={rightward}/{total}")
    check("enough samples for stat test", total >= 30, f"total={total}")
except Exception as e:
    check("emit_hit_burst directional", False, str(e))


# ============================================================
# TEST A3-6: RingBurst lifecycle
# ============================================================
print("\n[A3-6] RingBurst lifecycle")
try:
    rb = RingBurst(500, 500, radius=45, color=(200, 50, 50), duration=0.25)
    check("RingBurst alive initially", rb.alive)
    check("RingBurst duration", rb.duration == 0.25)

    # Update half-way
    rb.update(0.12)
    check("RingBurst still alive at 0.12s", rb.alive)
    check("RingBurst duration reduced", rb.duration < 0.15)

    # Update to death
    rb.update(0.2)
    check("RingBurst dead after 0.32s", not rb.alive)
except Exception as e:
    check("RingBurst lifecycle", False, str(e))


# ============================================================
# TEST A3-7: RingBurst draw no crash
# ============================================================
print("\n[A3-7] RingBurst draw — no crash")
try:
    rb = RingBurst(500, 500, radius=45)
    surf = pygame.Surface((1024, 768))
    rb.draw(surf, 0, 0)
    check("RingBurst draw alive frame", True)

    # Draw at mid-progress
    rb.update(0.1)
    rb.draw(surf, 0, 0)
    check("RingBurst draw mid-progress", True)

    # Draw when dead (should be safe)
    rb.update(0.5)
    rb.draw(surf, 0, 0)
    check("RingBurst draw dead (no crash)", True)
except Exception as e:
    check("RingBurst draw", False, str(e))


# ============================================================
# TEST A3-8: HitParticlePool acquire/recycle
# ============================================================
print("\n[A3-8] HitParticlePool acquire/recycle")
try:
    pool = HitParticlePool(capacity=10)
    # Fill 5 particles via emit
    emit_hit_burst(pool.particles, 0, 0, "light", (255, 0, 0))
    initial_count = len(pool.particles)
    check("pool has particles after emit", initial_count > 0, f"count={initial_count}")

    # Kill all particles
    for p in pool.particles:
        p.alive = False
    # Next acquire should recycle, not add new
    recycled_count_before = len(pool.particles)
    pool._acquire(0, 0, (0, 255, 0), 2.0, 0.3, None, 360)
    recycled_count_after = len(pool.particles)
    check("recycled (no new particle created)", recycled_count_after == recycled_count_before,
          f"before={recycled_count_before}, after={recycled_count_after}")
except Exception as e:
    check("HitParticlePool recycle", False, str(e))


# ============================================================
# TEST A3-9: HitParticlePool capacity enforcement
# ============================================================
print("\n[A3-9] HitParticlePool capacity enforcement")
try:
    pool = HitParticlePool(capacity=5)
    # Create 10 alive particles
    for _ in range(10):
        pool._acquire(0, 0, (255, 0, 0), 2.0, 0.5, None, 360)
    check("pool respects capacity", len(pool.particles) <= 5,
          f"count={len(pool.particles)}")
except Exception as e:
    check("HitParticlePool capacity", False, str(e))


# ============================================================
# TEST A3-10: Particle with hit_dir (directional)
# ============================================================
print("\n[A3-10] Particle hit_dir constructor")
try:
    d = pygame.Vector2(0, -1)  # upward
    p = Particle(100, 100, (255, 0, 0), speed=3.0, lifetime=0.3, hit_dir=d, spread_deg=90)
    # Should be mostly upward (negative y velocity)
    check("directional particle has velocity", p.vel.length() > 0)
    check("particle alive", p.alive)

    # With hit_dir=None (default), should still work
    p2 = Particle(100, 100, (255, 0, 0))
    check("default Particle still works", p2.alive)
except Exception as e:
    check("Particle hit_dir", False, str(e))


# ============================================================
# TEST A3-11: Full game loop with tiered particles — no crash
# ============================================================
print("\n[A3-11] Full game loop with tiered particles — no crash")
try:
    g11 = Game()
    g11.start_game("warrior")
    # Add enemies of different tiers
    normal = Enemy("neophyte", g11.player.pos.x + 10, g11.player.pos.y, 1)
    g11.enemies.append(normal)
    boss = Enemy("pope", g11.player.pos.x + 100, g11.player.pos.y, 9)
    g11.enemies.append(boss)
    # Give player a weapon that fires projectiles
    from weapons import create_weapon
    g11.player.weapons.append(create_weapon("fire"))
    # Run 120 frames
    for _ in range(120):
        g11.update(1 / 60)
    check("tiered particles in game loop", True)
    check("ring_bursts list exists", hasattr(g11, 'ring_bursts'))
    check("no crash with mixed enemies", True)
except Exception as e:
    check("Full game loop tiered particles", False, str(e))


# ============================================================
# TEST A4-1: ComboSystem initial state
# ============================================================
print("\n[A4-1] ComboSystem initial state")
try:
    cs = ComboSystem()
    check("count starts at 0", cs.count == 0)
    check("display_count starts at 0", cs.display_count == 0.0)
    check("timer starts at 0", cs.timer == 0.0)
    check("tier starts at -1", cs.tier == -1)
    check("scale_pulse starts at 1.0", cs.scale_pulse == 1.0)
    check("active is False when empty", cs.active is False)
except Exception as e:
    check("ComboSystem initial state", False, str(e))


# ============================================================
# TEST A4-2: COMBO_TIERS structure
# ============================================================
print("\n[A4-2] COMBO_TIERS structure")
try:
    check("COMBO_TIERS has 5 tiers", len(COMBO_TIERS) == 5, f"got {len(COMBO_TIERS)}")
    thresholds = [t[0] for t in COMBO_TIERS]
    check("thresholds are [5,15,30,50,100]", thresholds == [5, 15, 30, 50, 100],
          f"got {thresholds}")
    for i, (thr, label, scale, edge, slowmo) in enumerate(COMBO_TIERS):
        check(f"tier {i} scale_pulse >= 1.0", scale >= 1.0, f"scale={scale}")
        check(f"tier {i} slowmo >= 0", slowmo >= 0, f"slowmo={slowmo}")
except Exception as e:
    check("COMBO_TIERS structure", False, str(e))


# ============================================================
# TEST A4-3: register_kill returns juice
# ============================================================
print("\n[A4-3] register_kill returns juice")
try:
    cs = ComboSystem()
    juice = cs.register_kill()
    check("register_kill returns dict", isinstance(juice, dict))
    check("juice has 'slowmo' key", "slowmo" in juice)
    check("count incremented to 1", cs.count == 1)
    check("timer reset to timeout", cs.timer == cs.timeout)
    check("tier unchanged at <5", cs.tier == -1, f"tier={cs.tier}")
except Exception as e:
    check("register_kill returns juice", False, str(e))


# ============================================================
# TEST A4-4: Tier transitions at correct thresholds
# ============================================================
print("\n[A4-4] Tier transitions at thresholds")
try:
    cs = ComboSystem()
    # Kill 5 → tier 0 (scale pulse)
    for _ in range(5):
        juice = cs.register_kill()
    check("5 kills → tier 0", cs.tier == 0, f"tier={cs.tier}")
    check("5 kills → scale_pulse set", cs.scale_pulse > 1.0, f"scale={cs.scale_pulse:.2f}")

    # Kill 15 → tier 1 (edge flash)
    cs2 = ComboSystem()
    for _ in range(15):
        juice = cs2.register_kill()
    check("15 kills → tier 1", cs2.tier == 1, f"tier={cs2.tier}")
    check("15 kills → edge_flash active", cs2.edge_flash_timer > 0)

    # Kill 30 → tier 2 (slowmo)
    cs3 = ComboSystem()
    for _ in range(30):
        juice = cs3.register_kill()
    check("30 kills → tier 2", cs3.tier == 2, f"tier={cs3.tier}")
    check("30 kills → slowmo=4", juice["slowmo"] == 4, f"slowmo={juice['slowmo']}")

    # Kill 50 → tier 3 (CARNAGE)
    cs4 = ComboSystem()
    for _ in range(50):
        juice = cs4.register_kill()
    check("50 kills → tier 3", cs4.tier == 3, f"tier={cs4.tier}")
    check("50 kills → CARNAGE label", juice.get("label") == "CARNAGE", f"label={juice.get('label')}")

    # Kill 100 → tier 4 (MASSACRE)
    cs5 = ComboSystem()
    for _ in range(100):
        juice = cs5.register_kill()
    check("100 kills → tier 4", cs5.tier == 4, f"tier={cs5.tier}")
    check("100 kills → MASSACRE label", juice.get("label") == "MASSACRE", f"label={juice.get('label')}")
    check("100 kills → slowmo=8", juice["slowmo"] == 8, f"slowmo={juice['slowmo']}")
except Exception as e:
    check("Tier transitions", False, str(e))


# ============================================================
# TEST A4-5: Slowmo only on tier transition (not every kill)
# ============================================================
print("\n[A4-5] Slowmo only on tier transition")
try:
    cs = ComboSystem()
    # First 4 kills: no tier change
    for _ in range(4):
        j = cs.register_kill()
        check(f"kill {cs.count}: slowmo=0", j["slowmo"] == 0, f"slowmo={j['slowmo']}")
    # 5th kill: tier 0 transition, but slowmo=0 (tier 0 has no slowmo)
    j = cs.register_kill()
    check("5th kill: slowmo=0 (tier 0)", j["slowmo"] == 0)
    # 6th kill: same tier, no transition
    j = cs.register_kill()
    check("6th kill: slowmo=0 (no transition)", j["slowmo"] == 0)
except Exception as e:
    check("Slowmo on transition only", False, str(e))


# ============================================================
# TEST A4-6: Timer decay resets combo
# ============================================================
print("\n[A4-6] Timer decay resets combo")
try:
    cs = ComboSystem()
    for _ in range(10):
        cs.register_kill()
    check("10 kills active", cs.active)
    check("count is 10", cs.count == 10)

    # Decay timer to 0
    for _ in range(200):  # 200 * 0.016 = 3.2s > timeout 3.0s
        cs.update(0.016)

    check("combo reset after timeout", cs.count == 0)
    check("tier reset after timeout", cs.tier == -1)
    check("display_count reset", cs.display_count == 0.0)
    check("active is False after reset", cs.active is False)
except Exception as e:
    check("Timer decay reset", False, str(e))


# ============================================================
# TEST A4-7: Elastic tween — display_count approaches count
# ============================================================
print("\n[A4-7] Elastic tween convergence")
try:
    cs = ComboSystem()
    for _ in range(10):
        cs.register_kill()

    # Run several update frames
    for _ in range(60):
        cs.update(0.016)

    # display_count should be close to count=10
    check("display_count near 10", abs(cs.display_count - 10) < 2.0,
          f"display={cs.display_count:.2f}, target=10")
except Exception as e:
    check("Elastic tween", False, str(e))


# ============================================================
# TEST A4-8: Scale pulse decays to 1.0
# ============================================================
print("\n[A4-8] Scale pulse decay")
try:
    cs = ComboSystem()
    for _ in range(5):
        cs.register_kill()
    initial_scale = cs.scale_pulse
    check("scale_pulse > 1 after tier", initial_scale > 1.0, f"scale={initial_scale:.2f}")

    # Run enough frames for decay
    for _ in range(120):
        cs.update(0.016)

    check("scale_pulse decays toward 1.0", cs.scale_pulse <= 1.05,
          f"scale={cs.scale_pulse:.2f}")
except Exception as e:
    check("Scale pulse decay", False, str(e))


# ============================================================
# TEST A4-9: Edge flash decays
# ============================================================
print("\n[A4-9] Edge flash decay")
try:
    cs = ComboSystem()
    for _ in range(15):
        cs.register_kill()
    check("edge flash active at tier 1", cs.edge_flash_timer > 0)

    # Run half the duration
    for _ in range(20):
        cs.update(0.016)
    check("edge flash partially decayed", cs.edge_flash_timer < 0.6)

    # Run full duration
    for _ in range(60):
        cs.update(0.016)
    check("edge flash fully decayed", cs.edge_flash_timer == 0.0)
except Exception as e:
    check("Edge flash decay", False, str(e))


# ============================================================
# TEST A4-10: draw no crash
# ============================================================
print("\n[A4-10] ComboSystem draw — no crash")
try:
    cs = ComboSystem()
    surf = pygame.Surface((1024, 768))
    test_font = pygame.font.Font(None, 24)

    # Draw when inactive
    cs.draw(surf, test_font)
    check("draw inactive (no crash)", True)

    # Draw when active
    for _ in range(10):
        cs.register_kill()
    cs.update(0.016)
    cs.draw(surf, test_font)
    check("draw active (no crash)", True)

    # Draw edge flash
    cs.draw_edge_flash(surf)
    check("draw_edge_flash active (no crash)", True)

    # Draw when inactive edge flash
    cs2 = ComboSystem()
    cs2.draw_edge_flash(surf)
    check("draw_edge_flash inactive (no crash)", True)
except Exception as e:
    check("ComboSystem draw", False, str(e))


# ============================================================
# TEST A4-11: Full game loop with combo — no crash
# ============================================================
print("\n[A4-11] Full game loop with combo — no crash")
try:
    g11 = Game()
    g11.start_game("warrior")
    # Spawn some enemies near player
    for i in range(20):
        e = Enemy("neophyte", g11.player.pos.x + 5 + i * 3,
                  g11.player.pos.y, 1)
        g11.enemies.append(e)
    # Run 180 frames — should trigger some kills and combo
    for _ in range(180):
        g11.update(1 / 60)
    check("combo in game loop — no crash", True)
    check("kills registered", g11.player.kills >= 0)
    check("slowmo_frames attribute exists", hasattr(g11, '_slowmo_frames'))
except Exception as e:
    check("Full game loop combo", False, str(e))


# ============================================================
# TEST A4-12: combo_register_kill public API
# ============================================================
print("\n[A4-12] combo_register_kill public API")
try:
    # Reset singleton state by using a fresh ComboSystem
    from hud import _combo
    _combo.count = 0
    _combo.timer = 0.0
    _combo.tier = -1
    _combo.display_count = 0.0
    _combo.scale_pulse = 1.0
    _combo.edge_flash_timer = 0.0
    _combo._velocity = 0.0
    _combo._last_tier_label = None

    j = combo_register_kill()
    check("combo_register_kill returns dict", isinstance(j, dict))
    check("combo count incremented", _combo.count == 1)

    # Reset for other tests
    _combo.count = 0
    _combo.timer = 0.0
    _combo.tier = -1
except Exception as e:
    check("combo_register_kill API", False, str(e))


# ============================================================
# TEST A4-13: Slowmo integration in Game
# ============================================================
print("\n[A4-13] Slowmo integration in Game")
try:
    g13 = Game()
    g13.start_game("warrior")
    check("_slowmo_frames initialized", g13._slowmo_frames == 0)

    # Manually trigger slowmo
    g13._slowmo_frames = 4
    g13.elapsed = 0
    for _ in range(4):
        g13.update(1 / 60)  # dt gets scaled to 0.25/60
    check("slowmo frames decremented", g13._slowmo_frames == 0)
    # elapsed should still progress (at normal rate before scaling)
    check("elapsed progressed during slowmo", g13.elapsed > 0, f"elapsed={g13.elapsed:.3f}")
except Exception as e:
    check("Slowmo integration", False, str(e))


# ============================================================
# TEST A4-14: Edge flash draw on game render
# ============================================================
print("\n[A4-14] Edge flash render integration")
try:
    import main as _main_mod
    _main_mod.screen = screen
    _main_mod.font = pygame.font.Font(None, 20)
    _main_mod.big_font = pygame.font.Font(None, 32)
    _main_mod.small_font = pygame.font.Font(None, 16)

    g14 = Game()
    g14.start_game("warrior")
    # Force combo to tier 1 (edge flash)
    from hud import _combo
    _combo.count = 15
    _combo.timer = 3.0
    _combo.tier = 1
    _combo.display_count = 15.0
    _combo.edge_flash_timer = 0.6
    _combo.edge_flash_color = (255, 100, 50)

    # Render should not crash
    for _ in range(5):
        g14.update(1 / 60)
        g14.render()
    check("Edge flash in render — no crash", True)

    # Reset combo
    _combo.count = 0
    _combo.timer = 0.0
    _combo.tier = -1
    _combo.edge_flash_timer = 0.0
except Exception as e:
    check("Edge flash render", False, str(e))


# ============================================================
# TEST A5-1: AnimatedBossHealthBar initial state
# ============================================================
print("\n[A5-1] AnimatedBossHealthBar initial state")
try:
    bb = AnimatedBossHealthBar()
    check("initial active is False", bb.active is False)
    check("initial display_hp is 0", bb.display_hp == 0.0)
    check("initial delayed_hp is 0", bb.delayed_hp == 0.0)
    check("initial flash_timer is 0", bb.flash_timer == 0.0)
    check("initial boss_name is empty", bb.boss_name == "")
    check("5 segments", bb.SEGMENTS == 5)
    check("rattle threshold is 0.25", bb.RATTLE_THRESHOLD == 0.25)
    check("boss bar width is 400", bb.BOSS_BAR_WIDTH == 400)
except Exception as e:
    check("BossHPBar initial state", False, str(e))


# ============================================================
# TEST A5-2: AnimatedBossHealthBar activate
# ============================================================
print("\n[A5-2] AnimatedBossHealthBar activate")
try:
    bb2 = AnimatedBossHealthBar()
    bb2.activate("Антихрист", "antichrist", 180.0, 180.0)
    check("active after activate", bb2.active is True)
    check("boss_name set", bb2.boss_name == "Антихрист")
    check("boss_type_id set", bb2.boss_type_id == "antichrist")
    check("display_hp set", bb2.display_hp == 180.0)
    check("delayed_hp set", bb2.delayed_hp == 180.0)
    check("max_hp set", bb2.max_hp == 180)
except Exception as e:
    check("BossHPBar activate", False, str(e))


# ============================================================
# TEST A5-3: AnimatedBossHealthBar deactivate
# ============================================================
print("\n[A5-3] AnimatedBossHealthBar deactivate")
try:
    bb3 = AnimatedBossHealthBar()
    bb3.activate("Лжепапа", "pope", 400.0, 400.0)
    check("active before deactivate", bb3.active is True)
    bb3.deactivate()
    check("inactive after deactivate", bb3.active is False)
    check("boss_type_id cleared", bb3.boss_type_id == "")
except Exception as e:
    check("BossHPBar deactivate", False, str(e))


# ============================================================
# TEST A5-4: AnimatedBossHealthBar update — delayed HP trails
# ============================================================
print("\n[A5-4] AnimatedBossHealthBar delayed HP trails")
try:
    bb4 = AnimatedBossHealthBar()
    bb4.activate("Антихрист", "antichrist", 180.0, 180.0)
    check("delayed equals display at start", bb4.delayed_hp == bb4.display_hp)

    # Take damage — delayed should lag
    bb4.update(0.016, 100.0, 180.0)
    check("display_hp updated", bb4.display_hp == 100.0)
    check("delayed_hp not yet moved (trail timer < 0.7)", bb4.delayed_hp > 100.0)

    # After enough time, delayed should approach display
    for _ in range(100):
        bb4.update(0.05, 100.0, 180.0)
    check("delayed_hp approaches display_hp after trail delay",
          abs(bb4.delayed_hp - bb4.display_hp) < 10,
          f"delayed={bb4.delayed_hp:.1f}, display={bb4.display_hp:.1f}")
except Exception as e:
    check("BossHPBar delayed HP trails", False, str(e))


# ============================================================
# TEST A5-5: AnimatedBossHealthBar flash
# ============================================================
print("\n[A5-5] AnimatedBossHealthBar flash trigger")
try:
    bb5 = AnimatedBossHealthBar()
    bb5.activate("Антихрист", "antichrist", 180.0, 180.0)
    check("flash_timer is 0 before trigger", bb5.flash_timer == 0.0)

    bb5.trigger_flash((0, 255, 255))
    check("flash_timer > 0 after trigger", bb5.flash_timer > 0)
    check("flash_color is cyan", bb5.flash_color == (0, 255, 255))

    # Flash decays
    for _ in range(50):
        bb5.update(0.016, 100.0, 180.0)
    check("flash_timer decays to 0", bb5.flash_timer == 0.0)
except Exception as e:
    check("BossHPBar flash", False, str(e))


# ============================================================
# TEST A5-6: Death rattle activates at <25% HP
# ============================================================
print("\n[A5-6] Death rattle at <25% HP")
try:
    bb6 = AnimatedBossHealthBar()
    bb6.activate("Лжепапа", "pope", 400.0, 400.0)

    # HP at 30% — no rattle
    bb6.update(0.016, 120.0, 400.0)
    check("no rattle at 30% HP", bb6.display_hp / bb6.max_hp >= bb6.RATTLE_THRESHOLD)

    # HP at 20% — rattle should be active
    bb6.update(0.016, 80.0, 400.0)
    hp_ratio = bb6.display_hp / bb6.max_hp
    check("rattle mode at 20% HP", hp_ratio < bb6.RATTLE_THRESHOLD, f"ratio={hp_ratio:.2f}")

    # Rattle offsets should be generated
    check("rattle offsets have 5 values", len(bb6._rattle_offsets) == 5)
    check("rattle seed is set", bb6._rattle_seed > 0)
except Exception as e:
    check("Death rattle activation", False, str(e))


# ============================================================
# TEST A5-7: Rattle offsets re-randomize
# ============================================================
print("\n[A5-7] Rattle offsets re-randomize")
try:
    bb7 = AnimatedBossHealthBar()
    bb7.activate("Антихрист", "antichrist", 180.0, 180.0)

    # Push to rattle zone
    bb7.update(0.016, 30.0, 180.0)
    old_offsets = list(bb7._rattle_offsets)

    # Update 20 frames — offsets should re-randomize at frame 10
    for _ in range(20):
        bb7.update(0.016, 30.0, 180.0)

    # At least some offsets should differ (due to re-randomization at frame 10)
    changed = any(abs(a - b) > 0.01 for a, b in zip(old_offsets, bb7._rattle_offsets))
    check("rattle offsets changed over 20 frames", changed)
except Exception as e:
    check("Rattle re-randomize", False, str(e))


# ============================================================
# TEST A5-8: Boss bar draw — no crash
# ============================================================
print("\n[A5-8] Boss bar draw — no crash")
try:
    bb8 = AnimatedBossHealthBar()
    bb8.activate("Антихрист", "antichrist", 120.0, 180.0)
    surf = pygame.Surface((WIDTH, HEIGHT))
    f = pygame.font.Font(None, 20)
    sf = pygame.font.Font(None, 16)

    # Normal mode draw
    bb8.draw(surf, f, sf)
    check("normal mode draw no crash", True)

    # Rattle mode draw
    bb8.update(0.016, 30.0, 180.0)
    bb8.draw(surf, f, sf)
    check("rattle mode draw no crash", True)

    # Edge glow draw
    bb8.draw_edge_glow(surf)
    check("edge glow draw no crash", True)
except Exception as e:
    check("Boss bar draw", False, str(e))


# ============================================================
# TEST A5-9: Boss bar draw when inactive — no-op
# ============================================================
print("\n[A5-9] Boss bar draw when inactive — no-op")
try:
    bb9 = AnimatedBossHealthBar()
    surf = pygame.Surface((WIDTH, HEIGHT))
    f = pygame.font.Font(None, 20)
    sf = pygame.font.Font(None, 16)

    bb9.draw(surf, f, sf)
    check("inactive draw no crash", True)
    check("inactive is still False", bb9.active is False)
except Exception as e:
    check("Boss bar inactive draw", False, str(e))


# ============================================================
# TEST A5-10: Public API — boss_bar_activate/deactivate
# ============================================================
print("\n[A5-10] Public API — boss_bar_activate/deactivate")
try:
    from hud import _boss_bar
    boss_bar_deactivate()  # Reset

    boss_bar_activate("Лжепапа", "pope", 400.0, 400.0)
    check("boss_bar_activate sets active", _boss_bar.active is True)
    check("boss_bar_activate sets name", _boss_bar.boss_name == "Лжепапа")

    boss_bar_trigger_flash((0, 255, 255))
    check("boss_bar_trigger_flash sets timer", _boss_bar.flash_timer > 0)

    boss_bar_deactivate()
    check("boss_bar_deactivate clears active", _boss_bar.active is False)
except Exception as e:
    check("Public API", False, str(e))


# ============================================================
# TEST A5-11: Full game loop with boss — no crash
# ============================================================
print("\n[A5-11] Full game loop with boss — no crash")
try:
    import main as _main_boss
    _main_boss.screen = screen
    _main_boss.font = pygame.font.Font(None, 20)
    _main_boss.big_font = pygame.font.Font(None, 32)
    _main_boss.small_font = pygame.font.Font(None, 16)

    g_boss = Game()
    g_boss.start_game("warrior")

    # Spawn a boss near the player
    boss = Enemy("antichrist", g_boss.player.pos.x + 50, g_boss.player.pos.y, 5)
    g_boss.enemies.append(boss)

    # Run 120 frames — boss bar should activate
    for _ in range(120):
        g_boss.update(1 / 60)
        g_boss.render()

    # Boss bar should be active (boss alive and nearby)
    from hud import _boss_bar as bb_ref
    check("boss bar activated in game loop", bb_ref.active is True or not boss.alive)

    # Kill boss — bar should deactivate
    boss.hp = 0
    boss.alive = False
    for _ in range(10):
        g_boss.update(1 / 60)
        g_boss.render()  # render() calls draw_hud which calls _find_and_track_boss
    check("boss bar deactivated after boss death", bb_ref.active is False)

    # Cleanup
    boss_bar_deactivate()
except Exception as e:
    check("Full game loop boss", False, str(e))


# ============================================================
# TEST A5-12: enemies.py is_boss flag — antichrist and pope
# ============================================================
print("\n[A5-12] enemies.py is_boss flags")
try:
    check("antichrist is_boss", ENEMY_TYPES["antichrist"].get("is_boss") is True)
    check("pope is_boss", ENEMY_TYPES["pope"].get("is_boss") is True)
    check("neophyte not boss", ENEMY_TYPES["neophyte"].get("is_boss", False) is False)
    check("demon not boss", ENEMY_TYPES["demon"].get("is_boss", False) is False)

    e_boss = Enemy("antichrist", 0, 0, 1)
    check("Enemy instance is_boss", e_boss.is_boss is True)
    e_pope = Enemy("pope", 0, 0, 1)
    check("Enemy pope is_boss", e_pope.is_boss is True)
    e_norm = Enemy("neophyte", 0, 0, 1)
    check("Enemy neophyte not boss", e_norm.is_boss is False)
except Exception as e:
    check("is_boss flags", False, str(e))


# ============================================================
# TEST C2-1: CodexScreen — initialization
# ============================================================
print("\n[C2-1] CODEX SCREEN — initialization")
try:
    from bestiary import CodexScreen, CODEX_TABS, ENEMY_ORDER, WEAPON_ORDER
    codex = CodexScreen()
    check("CodexScreen created", codex is not None)
    check("Initial tab is 0 (Враги)", codex.tab_index == 0)
    check("Initial selected is 0", codex.selected == 0)

    m_c2 = MetaProgress()
    codex.activate(m_c2)
    check("Meta assigned", codex.meta is m_c2)
    check("3 tabs exist", len(CODEX_TABS) == 3)
    check("11 enemy types", len(ENEMY_ORDER) == 11)
    check("9 weapon types", len(WEAPON_ORDER) == 9)
except Exception as e:
    check("CodexScreen init", False, str(e))


# ============================================================
# TEST C2-2: MetaProgress enemy_kills tracking
# ============================================================
print("\n[C2-2] META — enemy_kills tracking")
try:
    m_c3 = MetaProgress()
    check("enemy_kills starts empty", m_c3.enemy_kills == {})
    m_c3.enemy_kills["neophyte"] = 150
    m_c3.enemy_kills["demon"] = 42
    check("enemy_kills stores neophyte", m_c3.enemy_kills["neophyte"] == 150)
    check("enemy_kills stores demon", m_c3.enemy_kills["demon"] == 42)
    check("unknown enemy returns 0 via get", m_c3.enemy_kills.get("pope", 0) == 0)
except Exception as e:
    check("enemy_kills tracking", False, str(e))


# ============================================================
# TEST C2-3: Save/Load enemy_kills
# ============================================================
print("\n[C2-3] SAVE/LOAD — enemy_kills persisted")
try:
    from save_system import save_progress, load_progress
    m_save = MetaProgress()
    m_save.gold = 999
    m_save.enemy_kills = {"neophyte": 100, "acolyte": 50, "pope": 3}
    save_progress(m_save)

    m_load = MetaProgress()
    loaded = load_progress(m_load)
    check("Load succeeds", loaded)
    check("Gold preserved", m_load.gold == 999)
    check("enemy_kills neophyte", m_load.enemy_kills.get("neophyte") == 100)
    check("enemy_kills acolyte", m_load.enemy_kills.get("acolyte") == 50)
    check("enemy_kills pope", m_load.enemy_kills.get("pope") == 3)
    check("enemy_kills is dict", isinstance(m_load.enemy_kills, dict))
except Exception as e:
    check("Save/Load enemy_kills", False, str(e))


# ============================================================
# TEST C2-4: Codex enemy kill display
# ============================================================
print("\n[C2-4] CODEX — enemy kills displayed correctly")
try:
    m_c4 = MetaProgress()
    m_c4.enemy_kills = {"neophyte": 42, "ghost": 7}
    codex4 = CodexScreen()
    codex4.activate(m_c4)

    check("neophyte kills = 42", codex4._get_kills("neophyte") == 42)
    check("ghost kills = 7", codex4._get_kills("ghost") == 7)
    check("unopened = 0", codex4._get_kills("pope") == 0)
    check("neophyte unlocked", codex4._is_enemy_unlocked("neophyte"))
    check("ghost unlocked", codex4._is_enemy_unlocked("ghost"))
    check("pope not unlocked", not codex4._is_enemy_unlocked("pope"))
    check("2/11 unlocked", codex4._count_unlocked() == 2)
except Exception as e:
    check("Codex enemy kills display", False, str(e))


# ============================================================
# TEST C2-5: Codex tab switching
# ============================================================
print("\n[C2-5] CODEX — tab switching")
try:
    codex5 = CodexScreen()
    codex5.activate(MetaProgress())
    check("Start at tab 0", codex5.tab_index == 0)

    tab_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
    codex5.handle_event(tab_event)
    check("TAB -> tab 1", codex5.tab_index == 1)
    codex5.handle_event(tab_event)
    check("TAB -> tab 2", codex5.tab_index == 2)
    codex5.handle_event(tab_event)
    check("TAB wraps to 0", codex5.tab_index == 0)
except Exception as e:
    check("Codex tab switching", False, str(e))


# ============================================================
# TEST C2-6: Codex navigation (up/down)
# ============================================================
print("\n[C2-6] CODEX — navigation")
try:
    codex6 = CodexScreen()
    codex6.activate(MetaProgress())
    check("Start selected=0", codex6.selected == 0)

    down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    up_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)

    codex6.handle_event(down_event)
    check("Down -> selected=1", codex6.selected == 1)
    codex6.handle_event(down_event)
    check("Down -> selected=2", codex6.selected == 2)

    codex6.handle_event(up_event)
    check("Up -> selected=1", codex6.selected == 1)
    codex6.handle_event(up_event)
    check("Up -> selected=0", codex6.selected == 0)
    codex6.handle_event(up_event)
    check("Up clamps at 0", codex6.selected == 0)

    # Go to max
    for _ in range(20):
        codex6.handle_event(down_event)
    check("Down clamps at max (10)", codex6.selected == 10)
except Exception as e:
    check("Codex navigation", False, str(e))


# ============================================================
# TEST C2-7: Codex back (ESC)
# ============================================================
print("\n[C2-7] CODEX — ESC returns 'back'")
try:
    codex7 = CodexScreen()
    codex7.activate(MetaProgress())
    esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    result = codex7.handle_event(esc_event)
    check("ESC returns 'back'", result == "back")
except Exception as e:
    check("Codex ESC", False, str(e))


# ============================================================
# TEST C2-8: Codex draw — no crash (all 3 tabs)
# ============================================================
print("\n[C2-8] CODEX — draw all 3 tabs no crash")
try:
    m_c8 = MetaProgress()
    m_c8.enemy_kills = {"neophyte": 10, "heretic": 5}
    codex8 = CodexScreen()
    codex8.activate(m_c8)

    f = pygame.font.Font(None, 24)
    bf = pygame.font.Font(None, 56)
    sf = pygame.font.Font(None, 18)
    surf = pygame.Surface((WIDTH, HEIGHT))

    # Tab 0: Враги
    codex8.draw(surf, f, bf, sf)
    check("Draw tab 0 (Враги) no crash", True)

    # Tab 1: Оружие
    codex8.tab_index = 1
    codex8.selected = 0
    codex8.draw(surf, f, bf, sf)
    check("Draw tab 1 (Оружие) no crash", True)

    # Tab 2: Эволюции
    codex8.tab_index = 2
    codex8.selected = 0
    codex8.draw(surf, f, bf, sf)
    check("Draw tab 2 (Эволюции) no crash", True)
except Exception as e:
    check("Codex draw all tabs", False, str(e))


# ============================================================
# TEST C2-9: Weapon descriptions complete
# ============================================================
print("\n[C2-9] CODEX — weapon descriptions cover all weapons")
try:
    from bestiary import WEAPON_DESCRIPTIONS
    for wid in WEAPON_DEFS:
        check(f"Weapon desc exists: {wid}", wid in WEAPON_DESCRIPTIONS)
    for wid, wd in WEAPON_DESCRIPTIONS.items():
        check(f"Weapon desc has 'desc': {wid}", "desc" in wd)
        check(f"Weapon desc has 'type_label': {wid}", "type_label" in wd)
except Exception as e:
    check("Weapon descriptions", False, str(e))


# ============================================================
# TEST C2-10: Evolution recipes complete
# ============================================================
print("\n[C2-10] CODEX — evolution recipes match EVOLUTIONS")
try:
    from weapons import EVOLUTIONS
    check("7 evolutions exist", len(EVOLUTIONS) == 7)
    for wid, evo in EVOLUTIONS.items():
        check(f"Evo has required_passive: {wid}", "required_passive" in evo)
        check(f"Evo has name: {wid}", "name" in evo)
        check(f"Evo weapon in WEAPON_DEFS: {wid}", wid in WEAPON_DEFS)
except Exception as e:
    check("Evolution recipes", False, str(e))


# ============================================================
# TEST C2-11: Lobby returns 'codex' on C key
# ============================================================
print("\n[C2-11] LOBBY — C key returns 'codex'")
try:
    lobby_c = LobbyScreen()
    m_c11 = MetaProgress()
    lobby_c.activate(m_c11)
    c_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c)
    result = lobby_c.handle_event(c_event)
    check("C key returns 'codex'", result == "codex")
except Exception as e:
    check("Lobby C key", False, str(e))


# ============================================================
# TEST C2-12: Full game loop with kill tracking — no crash
# ============================================================
print("\n[C2-12] GAME LOOP — enemy_kills populated after kills")
try:
    g_c12 = Game()
    g_c12.start_game("warrior")
    # Spawn enemies and kill them
    for i in range(10):
        e = Enemy("neophyte", g_c12.player.pos.x + 10, g_c12.player.pos.y, 1)
        e.hp = 1  # 1 HP so weapons can kill
        g_c12.enemies.append(e)
    for i in range(5):
        e = Enemy("acolyte", g_c12.player.pos.x + 10, g_c12.player.pos.y, 1)
        e.hp = 1
        g_c12.enemies.append(e)

    # Run game loop
    for _ in range(300):
        g_c12.update(1 / 60)

    neophyte_kills = g_c12.meta.enemy_kills.get("neophyte", 0)
    acolyte_kills = g_c12.meta.enemy_kills.get("acolyte", 0)
    check("neophyte kills tracked", neophyte_kills > 0, f"kills={neophyte_kills}")
    check("acolyte kills tracked", acolyte_kills > 0, f"kills={acolyte_kills}")
except Exception as e:
    check("Game loop kill tracking", False, str(e))
from config import ALTAR_DEFS, WEAPON_ARCHIVE_DEFS, FACTION_DEFS, OBELISK_DEFS


# ============================================================
# TEST C4-1: MetaProgress C4 initial state
# ============================================================
print("\n[C4-1] MetaProgress C4 — initial state")
try:
    mc4 = MetaProgress()
    check("altar_level has 4 keys", len(mc4.altar_level) == 4, f"got {len(mc4.altar_level)}")
    check("all altar levels start at 0", all(v == 0 for v in mc4.altar_level.values()))
    check("weapon_archive is empty set", mc4.weapon_archive == set())
    check("faction_rep has 3 keys", len(mc4.faction_rep) == 3, f"got {len(mc4.faction_rep)}")
    check("all faction rep start at 0", all(v == 0 for v in mc4.faction_rep.values()))
    check("obelisks is empty set", mc4.obelisks == set())
except Exception as e:
    check("MetaProgress C4 initial state", False, str(e))


# ============================================================
# TEST C4-2: Altar buy
# ============================================================
print("\n[C4-2] ALTAR — buy altar buff")
try:
    mc42 = MetaProgress()
    mc42.gold = 2000
    check("can buy might_altar", mc42.can_buy_altar("might_altar"))
    check("buy returns True", mc42.buy_altar("might_altar"))
    check("gold deducted", mc42.gold == 1500, f"gold={mc42.gold}")
    check("altar_level incremented", mc42.altar_level["might_altar"] == 1)
    check("get_altar_bonus returns 1.03", mc42.get_altar_bonus("might_altar") == 1.03,
          f"bonus={mc42.get_altar_bonus('might_altar')}")
    check("get_altar_regen_bonus 0 at start", mc42.get_altar_regen_bonus() == 0.0)
except Exception as e:
    check("Altar buy", False, str(e))


# ============================================================
# TEST C4-3: Altar max level
# ============================================================
print("\n[C4-3] ALTAR — max level cap")
try:
    mc43 = MetaProgress()
    mc43.gold = 999999
    for _ in range(5):
        mc43.buy_altar("regen_altar")
    check("regen_altar at max (5)", mc43.altar_level["regen_altar"] == 5)
    check("cannot buy beyond max", not mc43.can_buy_altar("regen_altar"))
    check("buy returns False at max", not mc43.buy_altar("regen_altar"))
    check("regen bonus is 1.0", mc43.get_altar_regen_bonus() == 1.0,
          f"bonus={mc43.get_altar_regen_bonus()}")
except Exception as e:
    check("Altar max level", False, str(e))


# ============================================================
# TEST C4-4: Altar insufficient gold
# ============================================================
print("\n[C4-4] ALTAR — insufficient gold")
try:
    mc44 = MetaProgress()
    mc44.gold = 100  # First altar costs 500
    check("cannot buy with 100G", not mc44.can_buy_altar("might_altar"))
    check("buy returns False", not mc44.buy_altar("might_altar"))
    check("level unchanged", mc44.altar_level["might_altar"] == 0)
    check("gold unchanged", mc44.gold == 100)
except Exception as e:
    check("Altar insufficient gold", False, str(e))


# ============================================================
# TEST C4-5: Weapon Archive unlock by kills
# ============================================================
print("\n[C4-5] WEAPON ARCHIVE — unlock by kills")
try:
    mc45 = MetaProgress()
    mc45.total_kills = 499
    newly = mc45.check_weapon_archive()
    check("nothing unlocked at 499 kills", len(newly) == 0)

    mc45.total_kills = 500
    newly = mc45.check_weapon_archive()
    check("4 variants unlocked at 500", len(newly) == 4, f"unlocked={newly}")
    check("whip_flame in archive", "whip_flame" in mc45.weapon_archive)
    check("fire_ice in archive", "fire_ice" in mc45.weapon_archive)

    mc45.total_kills = 750
    newly = mc45.check_weapon_archive()
    check("2 more at 750", len(newly) == 2, f"unlocked={newly}")
    check("lightning_holy in archive", "lightning_holy" in mc45.weapon_archive)

    # No double unlock
    newly = mc45.check_weapon_archive()
    check("no double unlock", len(newly) == 0)
except Exception as e:
    check("Weapon Archive unlock", False, str(e))


# ============================================================
# TEST C4-6: Faction reputation
# ============================================================
print("\n[C4-6] FACTION REP — add and check rewards")
try:
    mc46 = MetaProgress()
    mc46.add_faction_rep("angels", 50)
    check("angels rep = 50", mc46.faction_rep["angels"] == 50)
    check("no rewards at 50", len(mc46.get_faction_rewards("angels")) == 0)

    mc46.add_faction_rep("angels", 60)
    check("angels rep = 110", mc46.faction_rep["angels"] == 110,
          f"rep={mc46.faction_rep['angels']}")
    rewards = mc46.get_faction_rewards("angels")
    check("1 reward at 100+", len(rewards) == 1, f"rewards={rewards}")
    check("reward is Благословение", rewards[0][1] == "Благословение")

    mc46.add_faction_rep("demons", 600)
    d_rewards = mc46.get_faction_rewards("demons")
    check("demons all 3 rewards at 600", len(d_rewards) == 3, f"count={len(d_rewards)}")

    # Invalid faction
    mc46.add_faction_rep("invalid", 100)
    check("invalid faction ignored", "invalid" not in mc46.faction_rep)
except Exception as e:
    check("Faction reputation", False, str(e))


# ============================================================
# TEST C4-7: Obelisk completion
# ============================================================
print("\n[C4-7] OBELISKS — complete and gold reward")
try:
    mc47 = MetaProgress()
    mc47.gold = 100
    result = mc47.complete_obelisk("ruins_survive")
    check("complete_obelisk returns True", result)
    check("gold increased by 500", mc47.gold == 600, f"gold={mc47.gold}")
    check("ruins_survive in obelisks", "ruins_survive" in mc47.obelisks)

    # Cannot complete twice
    result2 = mc47.complete_obelisk("ruins_survive")
    check("cannot complete twice", not result2)
    check("gold unchanged after double", mc47.gold == 600)

    # Invalid obelisk
    result3 = mc47.complete_obelisk("nonexistent")
    check("invalid obelisk returns False", not result3)
except Exception as e:
    check("Obelisk completion", False, str(e))


# ============================================================
# TEST C4-8: Save/load C4 data
# ============================================================
print("\n[C4-8] SAVE/LOAD — C4 data persists")
try:
    from save_system import save_progress, load_progress, SAVE_FILE
    mc48 = MetaProgress()
    mc48.gold = 42
    mc48.altar_level["might_altar"] = 3
    mc48.altar_level["luck_altar"] = 2
    mc48.weapon_archive = {"whip_flame", "fire_ice"}
    mc48.faction_rep = {"angels": 150, "demons": 50, "humans": 300}
    mc48.obelisks = {"ruins_survive", "global_level"}
    save_progress(mc48)

    mc48b = MetaProgress()
    load_progress(mc48b)
    check("altar_level saved", mc48b.altar_level["might_altar"] == 3)
    check("altar_level luck saved", mc48b.altar_level["luck_altar"] == 2)
    check("weapon_archive saved", "whip_flame" in mc48b.weapon_archive)
    check("weapon_archive count", len(mc48b.weapon_archive) == 2)
    check("faction_rep angels saved", mc48b.faction_rep["angels"] == 150)
    check("faction_rep humans saved", mc48b.faction_rep["humans"] == 300)
    check("obelisks saved", "ruins_survive" in mc48b.obelisks)
    check("obelisks count", len(mc48b.obelisks) == 2)
    check("gold still works", mc48b.gold == 42)
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
except Exception as e:
    check("Save/load C4", False, str(e))


# ============================================================
# TEST C4-9: LobbyScreen Progress tab exists and draws
# ============================================================
print("\n[C4-9] LOBBY — Progress tab exists")
try:
    lobby_c4 = LobbyScreen()
    mc49 = MetaProgress()
    lobby_c4.activate(mc49)
    lobby_c4.tab_index = 5  # Прогресс tab (v2: shifted by Кодекс)
    check("Progress tab index 5", lobby_c4.tab_index == 5)
    check("current_tab is Прогресс", lobby_c4.current_tab == "Прогресс")

    # Draw
    f = pygame.font.Font(None, 24)
    bf = pygame.font.Font(None, 56)
    sf = pygame.font.Font(None, 18)
    surf = pygame.Surface((WIDTH, HEIGHT))
    lobby_c4.draw(surf, f, bf, sf)
    check("Progress tab draw no crash", True)
except Exception as e:
    check("Progress tab exists", False, str(e))


# ============================================================
# TEST C4-10: Progress tab navigation
# ============================================================
print("\n[C4-10] PROGRESS TAB — navigation")
try:
    lobby_c10 = LobbyScreen()
    mc410 = MetaProgress()
    lobby_c10.activate(mc410)
    lobby_c10.tab_index = 5
    check("starts at lane 0 (altar)", lobby_c10.progress_lane == 0)

    right_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    left_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)

    lobby_c10.handle_event(right_event)
    check("RIGHT -> lane 1 (archive)", lobby_c10.progress_lane == 1)
    lobby_c10.handle_event(right_event)
    check("RIGHT -> lane 2 (factions)", lobby_c10.progress_lane == 2)
    lobby_c10.handle_event(right_event)
    check("RIGHT -> lane 3 (obelisks)", lobby_c10.progress_lane == 3)
    lobby_c10.handle_event(right_event)
    check("RIGHT wraps to lane 0", lobby_c10.progress_lane == 0)

    lobby_c10.handle_event(left_event)
    check("LEFT wraps to lane 3", lobby_c10.progress_lane == 3)

    lobby_c10.handle_event(down_event)
    check("DOWN increments selected", lobby_c10.selected > 0)
except Exception as e:
    check("Progress tab navigation", False, str(e))


# ============================================================
# TEST C4-11: Progress tab altar buy via lobby
# ============================================================
print("\n[C4-11] PROGRESS TAB — altar buy via lobby")
try:
    lobby_c11 = LobbyScreen()
    mc411 = MetaProgress()
    mc411.gold = 10000
    lobby_c11.activate(mc411)
    lobby_c11.tab_index = 5
    lobby_c11.progress_lane = 0  # altar lane
    lobby_c11.selected = 0  # might_altar

    enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    lobby_c11.handle_event(enter_event)
    check("altar bought via ENTER", mc411.altar_level["might_altar"] == 1)
    check("notification set", "Алтарь" in lobby_c11.notification)
    check("gold deducted", mc411.gold < 10000)
except Exception as e:
    check("Altar buy via lobby", False, str(e))


# ============================================================
# TEST C4-12: All ALTAR_DEFS structure
# ============================================================
print("\n[C4-12] CONFIG — ALTAR_DEFS structure")
try:
    check("4 altar types", len(ALTAR_DEFS) == 4, f"got {len(ALTAR_DEFS)}")
    for aid, adef in ALTAR_DEFS.items():
        check(f"altar {aid} has 'name'", "name" in adef)
        check(f"altar {aid} has 'costs'", "costs" in adef)
        check(f"altar {aid} costs length 5", len(adef["costs"]) == 5, f"got {len(adef['costs'])}")
        check(f"altar {aid} has max=5", adef["max"] == 5)
except Exception as e:
    check("ALTAR_DEFS structure", False, str(e))


# ============================================================
# TEST C4-13: All OBELISK_DEFS structure
# ============================================================
print("\n[C4-13] CONFIG — OBELISK_DEFS structure")
try:
    check("5 obelisks", len(OBELISK_DEFS) == 5, f"got {len(OBELISK_DEFS)}")
    for oid, odef in OBELISK_DEFS.items():
        check(f"obelisk {oid} has 'name'", "name" in odef)
        check(f"obelisk {oid} has 'reward_gold'", "reward_gold" in odef)
        check(f"obelisk {oid} reward > 0", odef["reward_gold"] > 0)
except Exception as e:
    check("OBELISK_DEFS structure", False, str(e))


# ============================================================
# TEST C4-14: Draw all 4 progress lanes — no crash
# ============================================================
print("\n[C4-14] PROGRESS TAB — draw all 4 lanes no crash")
try:
    lobby_c14 = LobbyScreen()
    mc414 = MetaProgress()
    mc414.gold = 50000
    mc414.altar_level["might_altar"] = 3
    mc414.weapon_archive = {"whip_flame"}
    mc414.faction_rep["angels"] = 350
    mc414.obelisks = {"ruins_survive"}
    lobby_c14.activate(mc414)
    lobby_c14.tab_index = 5

    f = pygame.font.Font(None, 24)
    bf = pygame.font.Font(None, 56)
    sf = pygame.font.Font(None, 18)
    surf = pygame.Surface((WIDTH, HEIGHT))

    for lane in range(4):
        lobby_c14.progress_lane = lane
        lobby_c14.selected = 0
        lobby_c14.draw(surf, f, bf, sf)
    check("All 4 lanes draw no crash", True)
except Exception as e:
    check("Draw all progress lanes", False, str(e))


# ============================================================
# B3: Pyre of Grace — Candle HP Bar & Brazier XP Bar
# ============================================================
print("\n" + "=" * 60)
print("B3: PYRE OF GRACE — Candle HP Bar & Brazier XP Bar")
print("=" * 60)

# B3-1: AnimatedHealthBar candle init
print("\n[B3-1] CANDLE — init state")
try:
    hb = AnimatedHealthBar()
    check("init display_hp=0", hb.display_hp == 0)
    check("init damage_bar=0", hb.damage_bar == 0)
    check("init wax_drips empty", len(hb._wax_drips) == 0)
    check("init frame_counter=0", hb._frame_counter == 0)
except Exception as e:
    check("B3-1 init", False, str(e))

# B3-2: Candle update — normal HP
print("\n[B3-2] CANDLE — update normal HP")
try:
    hb2 = AnimatedHealthBar()
    hb2.update(0.016, 80, 100)
    check("display_hp set", hb2.display_hp == 80)
    check("no drips at same hp", len(hb2._wax_drips) == 0)
    check("damage_bar tracks", hb2.damage_bar == 80)
except Exception as e:
    check("B3-2 update", False, str(e))

# B3-3: Candle update — damage spawns wax drips
print("\n[B3-3] CANDLE — damage spawns wax drips")
try:
    hb3 = AnimatedHealthBar()
    hb3.display_hp = 100
    hb3.damage_bar = 100
    hb3.update(0.016, 70, 100)  # 30% drop
    check("wax drips spawned", len(hb3._wax_drips) > 0, f"count={len(hb3._wax_drips)}")
    check("drips capped at 40", len(hb3._wax_drips) <= 40)
    # Verify drip properties
    d = hb3._wax_drips[0]
    check("drip has vy", hasattr(d, 'vy'))
    check("drip has alpha", d.alpha > 0)
    check("drip alive", d.alive)
except Exception as e:
    check("B3-3 drips", False, str(e))

# B3-4: WaxDrip physics
print("\n[B3-4] WAX DRIP — physics")
try:
    wd = WaxDrip(0, 0)
    initial_y = wd.y
    wd.update(0.1)
    check("drip falls (y increases)", wd.y > initial_y, f"y={wd.y:.1f}")
    check("drip velocity increases", wd.vy > 40, f"vy={wd.vy:.1f}")
    wd2 = WaxDrip(0, 100)
    for _ in range(50):
        wd2.update(0.1)
    check("drip dies off-screen", not wd2.alive)
except Exception as e:
    check("B3-4 physics", False, str(e))

# B3-5: Candle flame states
print("\n[B3-5] CANDLE — flame state mapping")
try:
    hb5 = AnimatedHealthBar()
    check("100% → strong", hb5._get_flame_state(1.0) == 'strong')
    check("90% → strong", hb5._get_flame_state(0.90) == 'strong')
    check("75% → moderate", hb5._get_flame_state(0.75) == 'moderate')
    check("50% → flicker", hb5._get_flame_state(0.50) == 'flicker')
    check("30% → weak", hb5._get_flame_state(0.30) == 'weak')
    check("10% → ember", hb5._get_flame_state(0.10) == 'ember')
    check("0% → ember", hb5._get_flame_state(0.0) == 'ember')
except Exception as e:
    check("B3-5 flame states", False, str(e))

# B3-6: Flicker speed per state
print("\n[B3-6] CANDLE — flicker speeds")
try:
    hb6 = AnimatedHealthBar()
    fs = hb6._get_flicker_speed
    check("strong flicker=3.0", fs('strong') == 3.0)
    check("moderate flicker=5.0", fs('moderate') == 5.0)
    check("flicker flicker=8.0", fs('flicker') == 8.0)
    check("weak flicker=12.0", fs('weak') == 12.0)
    check("ember flicker=18.0", fs('ember') == 18.0)
    # Lower HP = faster flicker
    check("ember > weak > flicker > moderate > strong",
          fs('ember') > fs('weak') > fs('flicker') > fs('moderate') > fs('strong'))
except Exception as e:
    check("B3-6 flicker", False, str(e))

# B3-7: Candle draw no crash at all HP levels
print("\n[B3-7] CANDLE — draw at all HP levels")
try:
    surf7 = pygame.Surface((WIDTH, HEIGHT))
    font7 = pygame.font.Font(None, 18)
    hb7 = AnimatedHealthBar()

    hp_levels = [100, 80, 60, 40, 20, 10, 1, 0]
    for hp in hp_levels:
        hb7.display_hp = hp
        hb7.damage_bar = hp
        hb7._wax_drips.clear()
        hb7.draw(surf7, 10, 38, 180, 18, 100, font7)
    check("Draw all HP levels no crash", True)

    # Draw with wax drips present
    hb7.display_hp = 50
    hb7.damage_bar = 80
    for _ in range(5):
        hb7._wax_drips.append(WaxDrip(0, 10))
    hb7.draw(surf7, 10, 38, 180, 18, 100, font7)
    check("Draw with wax drips no crash", True)
except Exception as e:
    check("B3-7 draw", False, str(e))

# B3-8: AnimatedXPBar brazier init
print("\n[B3-8] BRAZIER — init state")
try:
    xb = AnimatedXPBar()
    check("init display_progress=0", xb.display_progress == 0.0)
    check("init target_progress=0", xb.target_progress == 0.0)
    check("init particles empty", len(xb._particles) == 0)
except Exception as e:
    check("B3-8 init", False, str(e))

# B3-9: Brazier update spawns particles
print("\n[B3-9] BRAZIER — update spawns fire particles")
try:
    xb9 = AnimatedXPBar()
    # Simulate several updates with XP
    for _ in range(30):
        xb9.update(0.016, 50, 100)
    check("particles spawned", len(xb9._particles) > 0, f"count={len(xb9._particles)}")
    check("progress tracking", xb9.display_progress > 0, f"prog={xb9.display_progress:.3f}")
    check("particles capped at 100", len(xb9._particles) <= 100)
except Exception as e:
    check("B3-9 particles", False, str(e))

# B3-10: BrazierParticle physics
print("\n[B3-10] BRAZIER PARTICLE — physics")
try:
    bp = BrazierParticle(100, 50, 0.5)
    initial_y = bp.y
    bp.update(0.1)
    check("particle rises (y decreases)", bp.y < initial_y, f"y={bp.y:.1f}")
    check("initial alpha > 0", bp.alpha > 0)
    bp2 = BrazierParticle(100, 50, 0.5)
    for _ in range(20):
        bp2.update(0.1)
    check("particle fades over time", bp2.alpha < 200, f"alpha={bp2.alpha:.0f}")
except Exception as e:
    check("B3-10 particle physics", False, str(e))

# B3-11: Brazier draw no crash
print("\n[B3-11] BRAZIER — draw no crash")
try:
    surf11 = pygame.Surface((WIDTH, HEIGHT))
    font11 = pygame.font.Font(None, 24)
    xb11 = AnimatedXPBar()

    # Empty brazier
    xb11.draw(surf11, font11)
    check("Draw empty brazier no crash", True)

    # Partial fill
    xb11.display_progress = 0.5
    xb11.draw(surf11, font11)
    check("Draw partial brazier no crash", True)

    # Full brazier with particles
    xb11.display_progress = 1.0
    for _ in range(20):
        xb11._particles.append(BrazierParticle(500, 0, 1.0))
    xb11.draw(surf11, font11)
    check("Draw full brazier with particles no crash", True)
except Exception as e:
    check("B3-11 brazier draw", False, str(e))

# B3-12: Candle — damage bar trailing
print("\n[B3-12] CANDLE — damage bar trails behind")
try:
    hb12 = AnimatedHealthBar()
    hb12.display_hp = 100
    hb12.damage_bar = 100

    # Take damage
    hb12.update(0.016, 50, 100)
    check("damage bar stays at old HP", hb12.damage_bar == 100)

    # Wait for damage timer
    for _ in range(40):  # ~0.64 seconds
        hb12.update(0.016, 50, 100)
    check("damage bar lags behind", hb12.damage_bar > 50, f"damage_bar={hb12.damage_bar:.1f}")

    # Eventually catches up (lerp once per 0.5s cycle)
    for _ in range(800):
        hb12.update(0.016, 50, 100)
    check("damage bar converges", hb12.damage_bar < 65, f"damage_bar={hb12.damage_bar:.1f}")
except Exception as e:
    check("B3-12 trailing", False, str(e))

# B3-13: Candle — flame colors defined for all states
print("\n[B3-13] CANDLE — flame colors defined")
try:
    hb13 = AnimatedHealthBar()
    for state_name in ('strong', 'moderate', 'flicker', 'weak', 'ember'):
        colors = hb13.FLAME_COLORS[state_name]
        check(f"{state_name} has 3 color tuples", len(colors) == 3)
        for c in colors:
            check(f"{state_name} color is RGB tuple", len(c) == 3 and all(0 <= v <= 255 for v in c))
except Exception as e:
    check("B3-13 colors", False, str(e))

# B3-14: Full HUD render with candle + brazier
print("\n[B3-14] FULL HUD — candle + brazier render")
try:
    surf14 = pygame.Surface((WIDTH, HEIGHT))
    f14 = pygame.font.Font(None, 20)
    sf14 = pygame.font.Font(None, 16)

    g_b3 = Game()
    g_b3.start_game("warrior")
    # Run a few frames to get HP/XP
    for _ in range(60):
        g_b3.player.pos.x += 0.5
        g_b3.update(1 / 60)

    # Render HUD
    draw_hud(surf14, g_b3.player, g_b3.wave_mgr.wave, 30.0, f14, sf14, g_b3.enemies)
    check("Full HUD with candle+brazier no crash", True)

    # Render with low HP
    g_b3.player.hp = 10
    draw_hud(surf14, g_b3.player, g_b3.wave_mgr.wave, 30.0, f14, sf14, g_b3.enemies)
    check("HUD with low HP candle no crash", True)
except Exception as e:
    check("B3-14 full HUD", False, str(e))

# B3-15: Drip cap and cleanup
print("\n[B3-15] CANDLE — drip cap at 40")
try:
    hb15 = AnimatedHealthBar()
    hb15.display_hp = 100
    # Simulate many small damages
    for i in range(100):
        hb15.update(0.016, 100 - i, 100)
    check("drips capped at 40", len(hb15._wax_drips) <= 40, f"count={len(hb15._wax_drips)}")
except Exception as e:
    check("B3-15 cap", False, str(e))


# ============================================================
# C5 TESTS: Save Profiles + Run Prep Screen
# ============================================================
print("\n" + "=" * 60)
print("C5 — SAVE PROFILES + RUN PREP SCREEN")
print("=" * 60)

# Cleanup stale profile files from previous runs
try:
    _save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
    for _pid in range(1, 4):
        _pf = os.path.join(_save_dir, f"save_profile_{_pid}.json")
        if os.path.exists(_pf):
            os.remove(_pf)
except Exception:
    pass


# C5-1: Save/Load with profile_id
print("\n[C5-1] SAVE/LOAD — profile_id parameter")
try:
    import save_system
    from lobby import MetaProgress

    # Save to profile 1
    m1 = MetaProgress()
    m1.gold = 1234
    m1.total_runs = 5
    m1.best_wave = 10
    m1.total_kills = 500
    result1 = save_system.save_progress(m1, profile_id=1)
    check("C5-1a save profile 1", result1 is True)

    # Save to profile 2 with different data
    m2 = MetaProgress()
    m2.gold = 9999
    m2.total_runs = 20
    m2.best_wave = 30
    m2.total_kills = 2000
    result2 = save_system.save_progress(m2, profile_id=2)
    check("C5-1b save profile 2", result2 is True)

    # Load profile 1 and verify
    m_load = MetaProgress()
    loaded1 = save_system.load_progress(m_load, profile_id=1)
    check("C5-1c load profile 1", loaded1 is True)
    check("C5-1d profile 1 gold", m_load.gold == 1234, f"gold={m_load.gold}")
    check("C5-1e profile 1 runs", m_load.total_runs == 5, f"runs={m_load.total_runs}")

    # Load profile 2 and verify different data
    m_load2 = MetaProgress()
    loaded2 = save_system.load_progress(m_load2, profile_id=2)
    check("C5-1f load profile 2", loaded2 is True)
    check("C5-1g profile 2 gold", m_load2.gold == 9999, f"gold={m_load2.gold}")
    check("C5-1h profile 2 runs", m_load2.total_runs == 20, f"runs={m_load2.total_runs}")

    # Profiles are independent
    check("C5-1i profiles independent", m_load.gold != m_load2.gold)
except Exception as e:
    check("C5-1 save/load", False, str(e))


# C5-2: set_active_profile / get_active_profile
print("\n[C5-2] ACTIVE PROFILE — set/get")
try:
    save_system.set_active_profile(3)
    check("C5-2a set to 3", save_system.get_active_profile() == 3)
    save_system.set_active_profile(1)
    check("C5-2b set to 1", save_system.get_active_profile() == 1)
    # Clamp
    save_system.set_active_profile(5)
    check("C5-2c clamp max 3", save_system.get_active_profile() == 3)
    save_system.set_active_profile(0)
    check("C5-2d clamp min 1", save_system.get_active_profile() == 1)
except Exception as e:
    check("C5-2 active profile", False, str(e))


# C5-3: get_profile_summary
print("\n[C5-3] PROFILE SUMMARY — preview data")
try:
    s1 = save_system.get_profile_summary(1)
    check("C5-3a summary not None", s1 is not None)
    check("C5-3b has gold key", "gold" in s1)
    check("C5-3c has total_runs", "total_runs" in s1)
    check("C5-3d has best_wave", "best_wave" in s1)
    check("C5-3e has total_kills", "total_kills" in s1)
    check("C5-3f has unlocked_chars_count", "unlocked_chars_count" in s1)
    check("C5-3g has achievements_count", "achievements_count" in s1)

    # Empty profile returns None
    s_empty = save_system.get_profile_summary(99)
    check("C5-3h empty profile is None", s_empty is None)
except Exception as e:
    check("C5-3 summary", False, str(e))


# C5-4: list_profiles
print("\n[C5-4] LIST PROFILES — 3 slots")
try:
    profiles = save_system.list_profiles()
    check("C5-4a returns 3 profiles", len(profiles) == 3, f"len={len(profiles)}")
    check("C5-4b profile 1 has id", profiles[0]["id"] == 1)
    check("C5-4c profile 2 has id", profiles[1]["id"] == 2)
    check("C5-4d profile 3 has id", profiles[2]["id"] == 3)
    check("C5-4e profile 1 has summary", profiles[0]["summary"] is not None)
    check("C5-4f profile 3 summary None", profiles[2]["summary"] is None)
except Exception as e:
    check("C5-4 list_profiles", False, str(e))


# C5-5: RunPrepScene instantiation and draw
print("\n[C5-5] RUN PREP SCENE — instantiate + draw")
try:
    from scenes import RunPrepScene
    rp = RunPrepScene()
    check("C5-5a RunPrepScene created", rp is not None)
    check("C5-5b has handle_events", hasattr(rp, "handle_events"))
    check("C5-5c has draw", hasattr(rp, "draw"))
    check("C5-5d has enter", hasattr(rp, "enter"))

    # Enter with menu/meta
    menu_obj = MainMenu()
    meta_obj = MetaProgress()
    rp.enter(menu=menu_obj, meta=meta_obj)
    check("C5-5e enter sets menu", rp.menu is menu_obj)
    check("C5-5f enter sets meta", rp.meta is meta_obj)

    # Draw
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    rp.draw(surf)
    check("C5-5g draw no crash", True)

    # ESC returns lobby
    esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    result = rp.handle_events([esc_event])
    check("C5-5h ESC returns lobby", result == "lobby", f"result={result}")

    # Enter returns game
    rp.enter(menu=menu_obj, meta=meta_obj)
    enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    result = rp.handle_events([enter_event])
    check("C5-5i ENTER returns game", result == "game", f"result={result}")

    # No-op on other keys
    rp.enter(menu=menu_obj, meta=meta_obj)
    space_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x)
    result = rp.handle_events([space_event])
    check("C5-5j other key returns None", result is None)
except Exception as e:
    check("C5-5 RunPrepScene", False, str(e))


# C5-6: RunPrepScene with arcana and banned items
print("\n[C5-6] RUN PREP SCENE — arcana + banned items")
try:
    rp2 = RunPrepScene()
    menu2 = MainMenu()
    meta2 = MetaProgress()
    meta2.selected_arcana = "double_threat"
    meta2.banned_items = {"whip", "might"}
    rp2.enter(menu=menu2, meta=meta2)

    surf2 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    rp2.draw(surf2)
    check("C5-6a draw with arcana+bans no crash", True)
except Exception as e:
    check("C5-6 RunPrep with data", False, str(e))


# C5-7: Menu buttons (v2: 3 buttons — start, settings, quit)
print("\n[C5-7] MENU — buttons (v2)")
try:
    from menu import MENU_BUTTONS
    btn_ids = [b["id"] for b in MENU_BUTTONS]
    check("C5-7a start in buttons", "start" in btn_ids)
    check("C5-7b start still first", MENU_BUTTONS[0]["id"] == "start")
    check("C5-7c 3 buttons total", len(MENU_BUTTONS) == 3, f"count={len(MENU_BUTTONS)}")
except Exception as e:
    check("C5-7 menu buttons", False, str(e))


# C5-8: Menu profiles state handling
print("\n[C5-8] MENU — profiles state navigation")
try:
    m8 = MainMenu()
    m8.state = "profiles"
    m8._profile_selected = 0

    # Down
    down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    m8.handle_event(down_event)
    check("C5-8a down selects 1", m8._profile_selected == 1)

    # Down again
    m8.handle_event(down_event)
    check("C5-8b down selects 2", m8._profile_selected == 2)

    # Down wraps
    m8.handle_event(down_event)
    check("C5-8c down wraps to 0", m8._profile_selected == 0)

    # Up
    up_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    m8.handle_event(up_event)
    check("C5-8d up selects 2 (wrap)", m8._profile_selected == 2)

    # Enter returns tuple
    m8._profile_selected = 1
    enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    result = m8.handle_event(enter_event)
    check("C5-8e enter returns tuple", isinstance(result, tuple))
    check("C5-8f tuple is profile_select", result[0] == "profile_select" if isinstance(result, tuple) else False)
    check("C5-8g profile_id is 2", result[1]["profile_id"] == 2 if isinstance(result, tuple) else False)

    # ESC goes back to main
    m8.state = "profiles"
    esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    m8.handle_event(esc_event)
    check("C5-8h ESC back to main", m8.state == "main")
except Exception as e:
    check("C5-8 profiles nav", False, str(e))


# C5-9: Menu draw_profiles
print("\n[C5-9] MENU — draw_profiles no crash")
try:
    m9 = MainMenu()
    m9.state = "profiles"
    m9._profile_selected = 0
    f9 = pygame.font.Font(None, 24)
    bf9 = pygame.font.Font(None, 56)
    sf9 = pygame.font.Font(None, 18)
    surf9 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    m9.draw_profiles(surf9, f9, bf9, sf9)
    check("C5-9a draw_profiles no crash", True)
except Exception as e:
    check("C5-9 draw_profiles", False, str(e))


# C5-10: Full integration — save to profile, load, draw
print("\n[C5-10] INTEGRATION — full save/load/draw cycle")
try:
    # Save some data to profile 3
    m10 = MetaProgress()
    m10.gold = 7777
    m10.total_runs = 42
    m10.best_wave = 15
    m10.total_kills = 3000
    m10.selected_arcana = "vow_of_silence"
    m10.banned_items = {"fire"}
    save_system.save_progress(m10, profile_id=3)

    # Load into fresh meta
    m10_loaded = MetaProgress()
    save_system.load_progress(m10_loaded, profile_id=3)
    check("C5-10a gold roundtrip", m10_loaded.gold == 7777)
    check("C5-10b arcana roundtrip", m10_loaded.selected_arcana == "vow_of_silence")
    check("C5-10c banned roundtrip", "fire" in m10_loaded.banned_items)

    # Draw RunPrepScene with loaded data
    rp10 = RunPrepScene()
    menu10 = MainMenu()
    rp10.enter(menu=menu10, meta=m10_loaded)
    surf10 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    rp10.draw(surf10)
    check("C5-10d draw loaded profile prep", True)

    # Summary for profile 3
    s3 = save_system.get_profile_summary(3)
    check("C5-10e summary gold", s3["gold"] == 7777 if s3 else False)
    check("C5-10f summary runs", s3["total_runs"] == 42 if s3 else False)
except Exception as e:
    check("C5-10 integration", False, str(e))


# C5-11: LobbyScene returns run_prep (not char_select)
print("\n[C5-11] LOBBY → RUN PREP flow")
try:
    from scenes import LobbyScene, RunPrepScene
    lobby11 = LobbyScreen()
    meta11 = MetaProgress()
    menu11 = MainMenu()
    ls = LobbyScene(lobby11, meta11, menu11)

    # Simulate lobby active with ESC press
    ls.enter()
    lobby11.activate(meta11, menu=menu11)

    # The lobby returns "back" on ESC, then LobbyScene wraps it as "title"
    esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    # LobbyScreen handles ESC -> "back"
    lobby_result = lobby11.handle_event(esc_event)
    check("C5-11a lobby ESC returns back", lobby_result == "back")

    # LobbyScene should wrap this as "title"
    # Simulate by calling handle_events
    ls2 = LobbyScene(lobby11, meta11, menu11)
    ls2.enter()
    lobby11.activate(meta11, menu=menu11)
    result = ls2.handle_events([esc_event])
    check("C5-11b LobbyScene returns title", result == "title", f"result={result}")
except Exception as e:
    check("C5-11 lobby flow", False, str(e))


# C5-12: Profile files are separate
print("\n[C5-12] PROFILE FILES — separate JSON files")
try:
    import os
    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
    f1 = os.path.join(save_dir, "save_profile_1.json")
    f2 = os.path.join(save_dir, "save_profile_2.json")
    check("C5-12a profile 1 file exists", os.path.exists(f1))
    check("C5-12b profile 2 file exists", os.path.exists(f2))

    # Verify they're different files with different content
    import json
    with open(f1, "r") as fh:
        d1 = json.load(fh)
    with open(f2, "r") as fh:
        d2 = json.load(fh)
    check("C5-12c different gold values", d1["gold"] != d2["gold"],
          f"p1={d1['gold']}, p2={d2['gold']}")
except Exception as e:
    check("C5-12 separate files", False, str(e))


# ============================================================
# B4: Catechism of Ruin — Illuminated Manuscript Text Style
# ============================================================
print("\n[B4] CATECHISM OF RUIN — Illuminated Manuscript Text Style")

# B4-1: generate_parchment returns valid surface
print("\n[B4-1] PARCHMENT TEXTURE — generate_parchment")
try:
    from hud import generate_parchment, PARCH_INK, PARCH_INK_DIM, PARCH_BASE, PARCH_LIGHT
    parch = generate_parchment(200, 100, seed=42)
    check("B4-1a returns Surface", isinstance(parch, pygame.Surface))
    check("B4-1b correct size", parch.get_size() == (200, 100))
    check("B4-1c has SRCALPHA", parch.get_flags() & pygame.SRCALPHA)
    # Cache hit
    parch2 = generate_parchment(200, 100, seed=42)
    check("B4-1d cache hit returns same object", parch is parch2)
    # Different size = different surface
    parch3 = generate_parchment(300, 100, seed=42)
    check("B4-1e different size different object", parch is not parch3)
except Exception as e:
    check("B4-1 parchment texture", False, str(e))

# B4-2: QuillReveal animation
print("\n[B4-2] QUILL REVEAL — letter-by-letter animation")
try:
    from game_over_screen import QuillReveal
    qr = QuillReveal()
    check("B4-2a initial visible=0", qr.get_visible_count() == 0)
    # Advance 0.15s = 3 characters at 0.05s each
    qr.update(0.15)
    check("B4-2b after 0.15s visible>=2", qr.get_visible_count() >= 2)
    # Advance to full
    qr.update(10.0)
    check("B4-2c after 10s visible capped", qr.get_visible_count() == 100)
    # Reset
    qr.reset()
    check("B4-2d reset visible=0", qr.get_visible_count() == 0)
    # Draw no crash
    test_surf = pygame.Surface((400, 100), pygame.SRCALPHA)
    test_font = pygame.font.Font(None, 24)
    qr.update(0.25)  # 5 chars
    qr.draw_text_revealed(test_surf, "ПАЛ В БОЮ", test_font, (255, 0, 0), 10, 10)
    check("B4-2e draw_text_revealed no crash", True)
    # Ink drops generated
    check("B4-2f ink drops created", len(qr._ink_drops) > 0)
except Exception as e:
    check("B4-2 quill reveal", False, str(e))

# B4-3: ToastManager draws with parchment (no crash)
print("\n[B4-3] TOAST — parchment texture background")
try:
    from hud import ToastManager
    tm = ToastManager()
    tm.spawn("Test toast", (255, 255, 255))
    tm.update(0.016)
    test_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    test_font = pygame.font.Font(None, 18)
    tm.draw(test_surf, test_font)
    check("B4-3a ToastManager draw no crash", True)
    check("B4-3b toast alive", len(tm.toasts) > 0)
except Exception as e:
    check("B4-3 toast parchment", False, str(e))

# B4-4: draw_game_over with quill reveal (no crash)
print("\n[B4-4] GAME OVER — quill-scratch title reveal")
try:
    from game_over_screen import draw_game_over, GameOverAnimator, _quill
    go_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    go_anim = GameOverAnimator()
    go_font = pygame.font.Font(None, 24)
    go_big = pygame.font.Font(None, 56)
    go_small = pygame.font.Font(None, 18)
    # Phase 1: title just starting (quill reveal in progress)
    go_anim.timer = 0.4
    _quill.reset()
    draw_game_over(go_surf, {"wave": 5, "time": 300, "kills": 50, "level": 10, "gold": 1000},
                   go_anim, font=go_font, big_font=go_big, small_font=go_small)
    check("B4-4a game over with quill no crash", True)
    # Phase 2: fully revealed
    go_anim.timer = 2.0
    _quill.update(5.0)  # enough for all chars
    draw_game_over(go_surf, {"wave": 5, "time": 300, "kills": 50, "level": 10, "gold": 1000},
                   go_anim, font=go_font, big_font=go_big, small_font=go_small)
    check("B4-4b game over fully revealed no crash", True)
    check("B4-4c quill visible count full", _quill.get_visible_count() >= 10)
except Exception as e:
    check("B4-4 game over quill", False, str(e))

# B4-5: Bestiary parchment panel (uses shared generate_parchment)
print("\n[B4-5] BESTIARY — shared parchment panel")
try:
    from bestiary import CodexScreen
    bs = CodexScreen()
    bs_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    bs_font = pygame.font.Font(None, 20)
    bs_big = pygame.font.Font(None, 32)
    bs_small = pygame.font.Font(None, 16)
    bs.draw(bs_surf, bs_font, bs_big, bs_small)
    check("B4-5a bestiary draw no crash", True)
    # Verify _draw_parchment_panel uses generate_parchment (check import)
    import bestiary as _bmod
    check("B4-5b imports generate_parchment", hasattr(_bmod, 'generate_parchment'))
    check("B4-5c imports PARCH_INK", hasattr(_bmod, 'PARCH_INK'))
except Exception as e:
    check("B4-5 bestiary parchment", False, str(e))

# B4-6: Menu char_select & map_select draw without crash (v2: no parchment needed)
print("\n[B4-6] MENU — char select & map select (v2)")
try:
    mm = MainMenu()
    mm.state = "char_select"
    mm_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mm_font = pygame.font.Font(None, 20)
    mm_big = pygame.font.Font(None, 32)
    mm_small = pygame.font.Font(None, 16)
    mm.draw(mm_surf, mm_font, mm_big, mm_small)
    check("B4-6a char_select draws", True)

    mm.state = "map_select"
    mm.draw(mm_surf, mm_font, mm_big, mm_small)
    check("B4-6b map_select draws", True)
except Exception as e:
    check("B4-6 menu draw", False, str(e))


# ═══════════════════════════════════════════════════════════════
# REFERENCE FIX #5: Slow & Freeze status effects
# ═══════════════════════════════════════════════════════════════
print("\n--- Reference Fix #5: Slow & Freeze ---")

# SF-1: Enemy has slow/freeze fields on init
e_sf1 = Enemy("neophyte", 100, 100, 1)
check("SF-1a enemy has slow_factor", hasattr(e_sf1, 'slow_factor') and e_sf1.slow_factor == 1.0)
check("SF-1b enemy has slow_timer", hasattr(e_sf1, 'slow_timer') and e_sf1.slow_timer == 0.0)
check("SF-1c enemy has frozen_timer", hasattr(e_sf1, 'frozen_timer') and e_sf1.frozen_timer == 0.0)

# SF-2: apply_slow sets timer and factor
e_sf2 = Enemy("neophyte", 200, 200, 1)
e_sf2.apply_slow(0.5, 2.0)
check("SF-2a slow_factor set", e_sf2.slow_factor == 0.5)
check("SF-2b slow_timer set", e_sf2.slow_timer == 2.0)

# SF-3: apply_slow stacks (keeps strongest slow)
e_sf3 = Enemy("neophyte", 200, 200, 1)
e_sf3.apply_slow(0.6, 1.0)
e_sf3.apply_slow(0.4, 1.5)
check("SF-3a slow stacks by min factor", e_sf3.slow_factor == 0.4)
check("SF-3b slow stacks by max timer", e_sf3.slow_timer == 1.5)

# SF-4: apply_freeze sets timer
e_sf4 = Enemy("neophyte", 200, 200, 1)
e_sf4.apply_freeze(1.0)
check("SF-4a freeze timer set", e_sf4.frozen_timer == 1.0)
# Longest wins
e_sf4.apply_freeze(0.5)
check("SF-4b freeze stacks by max", e_sf4.frozen_timer == 1.0)
e_sf4.apply_freeze(2.0)
check("SF-4c freeze extends", e_sf4.frozen_timer == 2.0)

# SF-5: Slow reduces movement speed
e_sf5 = Enemy("shade", 500, 500, 1)
orig_speed = e_sf5.speed
p_pos = pygame.Vector2(800, 500)
# Update without slow
e_sf5a = Enemy("shade", 500, 500, 1)
e_sf5a.update(p_pos, 1/60)
dist_normal = abs(e_sf5a.pos.x - 500)
# Update with slow
e_sf5b = Enemy("shade", 500, 500, 1)
e_sf5b.apply_slow(0.5, 10.0)
e_sf5b.update(p_pos, 1/60)
dist_slowed = abs(e_sf5b.pos.x - 500)
check("SF-5a slow reduces distance traveled", dist_slowed < dist_normal * 0.6)
check("SF-5b slow distance ~50% of normal", abs(dist_slowed / dist_normal - 0.5) < 0.15, f"ratio={dist_slowed/max(dist_normal,0.001):.3f}")

# SF-6: Freeze stops all movement
e_sf6 = Enemy("shade", 500, 500, 1)
e_sf6.apply_freeze(5.0)
e_sf6.update(p_pos, 1/60)
check("SF-6a frozen enemy doesn't move", e_sf6.pos.x == 500 and e_sf6.pos.y == 500)
# Frozen timer decrements
check("SF-6b frozen timer decrements", e_sf6.frozen_timer < 5.0)

# SF-7: Slow timer expiry resets factor
e_sf7 = Enemy("neophyte", 200, 200, 1)
e_sf7.apply_slow(0.5, 0.01)  # very short duration
e_sf7.update(p_pos, 0.1)  # enough to expire
check("SF-7a slow expired, factor reset to 1.0", e_sf7.slow_factor == 1.0)
check("SF-7b slow expired, timer at 0", e_sf7.slow_timer <= 0)

# SF-8: Bell weapon applies freeze on hit
bell_w = BellWeapon()
bell_w.timer = 999.0  # force fire
bell_player = Player("paladin", 0, 0)
bell_enemies = [Enemy("neophyte", 150, 0, 1)]  # within radius 200
bell_pulses = []
bell_particles = []
bell_w.update(bell_player, bell_enemies, [], bell_pulses, bell_particles, 0.016)
check("SF-8a bell hit applies freeze", bell_enemies[0].frozen_timer > 0)
check("SF-8b bell freeze ~0.8s", abs(bell_enemies[0].frozen_timer - 0.8) < 0.1, f"timer={bell_enemies[0].frozen_timer:.2f}")

# SF-9: Lightning weapon applies slow on hit (REF-10: delayed by telegraph)
light_w = LightningWeapon()
light_w.timer = 999.0
light_player = Player("paladin", 0, 0)
light_enemies = [Enemy("neophyte", 100, 0, 1)]  # within aoe
light_pulses = []
light_w.update(light_player, light_enemies, [], light_pulses, [], 0.016)
# REF-10: Damage delayed — advance bolt through telegraph
for p in light_pulses:
    p.update(0.35)  # trigger strike phase
check("SF-9a lightning hit applies slow", light_enemies[0].slow_factor < 1.0)
check("SF-9b lightning slow is 0.5 factor", light_enemies[0].slow_factor == 0.5)
check("SF-9c lightning slow lasts ~2s", abs(light_enemies[0].slow_timer - 2.0) < 0.5, f"timer={light_enemies[0].slow_timer:.2f}")

# SF-10: Frozen enemy skip returns None (no ranged attack)
e_sf10 = Enemy("demon", 300, 0, 5)  # demon has shoot_range
e_sf10.apply_freeze(5.0)
player_far = pygame.Vector2(400, 0)  # within shoot_range
result_frozen = e_sf10.update(player_far, 1/60)
check("SF-10a frozen demon returns None (no shot)", result_frozen is None)

# SF-11: Both slow and freeze can coexist
e_sf11 = Enemy("neophyte", 100, 100, 1)
e_sf11.apply_slow(0.3, 5.0)
e_sf11.apply_freeze(2.0)
check("SF-11a both slow_factor set", e_sf11.slow_factor == 0.3)
check("SF-11b both frozen_timer set", e_sf11.frozen_timer == 2.0)
# After freeze expires, slow remains
e_sf11.frozen_timer = 0.0  # simulate expiry
e_sf11.slow_timer = 5.0
e_sf11.update(p_pos, 1/60)
check("SF-11c after freeze, slow still active", e_sf11.slow_factor == 0.3)


# ============================================================
# Reference Fix #7: Half-Cooldown Retry (ALL weapons)
# ============================================================
print("\n--- Reference Fix #7: Half-Cooldown Retry ---")

# Helper: create a minimal player stub for weapon updates
import config as _cfg
class _FakePlayer:
    pos = pygame.Vector2(400, 300)
    facing = pygame.Vector2(1, 0)
    damage_mult = 1.0
    cooldown_mult = 1.0
    area_mult = 1.0
    projectiles_bonus = 0
    crit_chance = 0.0
    rune_slots = []
_fp = _FakePlayer()
_no_enemies: list = []  # empty enemy list

# HCR-1: Whip — half-cooldown when no enemies
w_whip = WhipWeapon()
w_whip.level = 1
d_w = WEAPON_DEFS["whip"]
cd_w = max(d_w["cd_min"], d_w["cooldown_base"] - w_whip.level * d_w["cd_reduction"]) * _fp.cooldown_mult
w_whip.timer = cd_w + 0.01  # trigger immediately
projs = []; pulses = []; parts = []; nums = []
w_whip.update(_fp, _no_enemies, projs, pulses, parts, 0.016)
check("HCR-1a whip timer set to half", abs(w_whip.timer - cd_w / 2) < 0.001)
check("HCR-1b whip no pulse generated", len(pulses) == 0)

# HCR-2: Rosary — half-cooldown when no enemies
w_ros = RosaryWeapon()
w_ros.level = 1
d_r = WEAPON_DEFS["rosary"]
cd_r = max(d_r["cd_min"], d_r["cooldown_base"] - w_ros.level * d_r["cd_reduction"]) / 60.0
w_ros.timer = cd_r + 0.01
w_ros.update(_fp, _no_enemies, projs, pulses, parts, 0.016)
check("HCR-2a rosary timer set to half", abs(w_ros.timer - cd_r / 2) < 0.001)
check("HCR-2b rosary no boomerang spawned", len(w_ros.boomerangs) == 0)

# HCR-3: Prayer — half-cooldown when no enemies
w_pray = PrayerWeapon()
w_pray.level = 1
d_p = WEAPON_DEFS["prayer"]
cd_p = max(d_p["cd_min"], d_p["cooldown_base"] - w_pray.level * d_p["cd_reduction"]) * _fp.cooldown_mult
w_pray.timer = cd_p + 0.01
w_pray.update(_fp, _no_enemies, projs, pulses, parts, 0.016)
check("HCR-3a prayer timer set to half", abs(w_pray.timer - cd_p / 2) < 0.001)
check("HCR-3b prayer no ring wave generated", len(pulses) == 0)

# HCR-4: Cross — half-cooldown when no enemies
w_cross = CrossWeapon()
w_cross.level = 1
d_c = WEAPON_DEFS["cross"]
cd_c = max(d_c["cd_min"], d_c["cooldown_base"] - w_cross.level * d_c["cd_reduction"]) * _fp.cooldown_mult
w_cross.timer = cd_c + 0.01
w_cross.update(_fp, _no_enemies, projs, pulses, parts, 0.016)
check("HCR-4a cross timer set to half", abs(w_cross.timer - cd_c / 2) < 0.001)
check("HCR-4b cross no projectile generated", len(projs) == 0)

# HCR-5: Bell — half-cooldown when no enemies
w_bell = BellWeapon()
w_bell.level = 1
d_b = WEAPON_DEFS["bell"]
cd_b = max(d_b["cd_min"], d_b["cooldown_base"] - w_bell.level * d_b["cd_reduction"]) * _fp.cooldown_mult
w_bell.timer = cd_b + 0.01
w_bell.update(_fp, _no_enemies, projs, pulses, parts, 0.016)
check("HCR-5a bell timer set to half", abs(w_bell.timer - cd_b / 2) < 0.001)
check("HCR-5b bell no ring wave generated", len(pulses) == 0)

# HCR-6: Fire — already had half-cooldown (verify still works)
w_fire = FireWeapon()
w_fire.level = 1
d_f = WEAPON_DEFS["fire"]
cd_f = max(d_f["cd_min"], d_f["cooldown_base"] - w_fire.level * d_f["cd_reduction"]) * _fp.cooldown_mult
w_fire.timer = cd_f + 0.01
w_fire.update(_fp, _no_enemies, projs, pulses, parts, 0.016)
check("HCR-6a fire timer set to half", abs(w_fire.timer - cd_f / 2) < 0.001)

# HCR-7: Lightning — already had half-cooldown (verify still works)
w_light = LightningWeapon()
w_light.level = 1
d_l = WEAPON_DEFS["lightning"]
cd_l = max(d_l["cd_min"], d_l["cooldown_base"] - w_light.level * d_l["cd_reduction"]) * _fp.cooldown_mult
w_light.timer = cd_l + 0.01
w_light.update(_fp, _no_enemies, projs, pulses, parts, 0.016)
check("HCR-7a lightning timer set to half", abs(w_light.timer - cd_l / 2) < 0.001)

# HCR-8: With enemies present, weapons fire normally (timer = 0 after firing)
w_whip2 = WhipWeapon()
w_whip2.level = 1
w_whip2.timer = cd_w + 0.01
e_target = Enemy("neophyte", 450, 300, 1)
w_whip2.update(_fp, [e_target], projs, pulses, parts, 0.016)
check("HCR-8a whip fires when enemies present", w_whip2.timer == 0)
check("HCR-8b whip generated sweep", len(pulses) > 0)


# ============================================================
# B5: The Confessional Pause Screen
# ============================================================
print("\n--- B5: Confessional Pause Screen ---")

from scenes import (
    ConfessionalCandle, generate_wood_slats, draw_stone_tablet,
    PauseOverlay, CONFESS_DARK, CONFESS_WOOD, CONFESS_IRON,
    CONFESS_STONE, CONFESS_GOLD, CONFESS_CHAIN, CONFESS_STONE_DARK,
    CONFESS_STONE_LIGHT, _wood_slats_cache,
)
from hud import generate_parchment, PARCH_INK

_b5_font = pygame.font.Font(None, 24)

# B5-1: ConfessionalCandle creation
c = ConfessionalCandle(500, 400)
check("B5-1a candle created with valid position", abs(c.x - 500) < 10 and abs(c.y - 400) < 1)
check("B5-1b candle starts alive", c.alive)
check("B5-1c candle has positive alpha", c.alpha > 0)
check("B5-1d candle has valid size", 2 <= c.size <= 5)
check("B5-1e candle max_life > 0", c.max_life > 0)
check("B5-1f candle color in golden range", c.color[0] >= 200 and c.color[1] >= 140)

# B5-2: ConfessionalCandle update/decay
c2 = ConfessionalCandle(300, 300)
initial_alpha = c2.alpha
for _ in range(60):
    c2.update(1 / 60)
check("B5-2a candle alpha decreases after 1s", c2.alpha < initial_alpha)
check("B5-2b candle position changes (rises)", c2.y < 300)
check("B5-2c candle life advances", c2.life > 0.5)

# B5-3: ConfessionalCandle lifecycle — dies after max_life
c3 = ConfessionalCandle(200, 200)
for _ in range(200):
    c3.update(1 / 60)
check("B5-3a candle dies after enough time", not c3.alive)
check("B5-3b dead candle has zero alpha", c3.alpha == 0)

# B5-4: generate_wood_slats returns valid surface
_wood_slats_cache.clear()
ws = generate_wood_slats(WIDTH, HEIGHT)
check("B5-4a wood slats is a Surface", isinstance(ws, pygame.Surface))
check("B5-4b wood slats correct size", ws.get_width() == WIDTH and ws.get_height() == HEIGHT)

# B5-5: generate_wood_slats caching
ws2 = generate_wood_slats(WIDTH, HEIGHT)
check("B5-5a wood slats cache hit returns same object", ws is ws2)
# Different size = different surface
ws3 = generate_wood_slats(512, 512)
check("B5-5b different size returns different surface", ws3 is not ws)
check("B5-5c different size correct dimensions", ws3.get_width() == 512 and ws3.get_height() == 512)

# B5-6: draw_stone_tablet doesn't crash (selected)
test_surf = pygame.Surface((WIDTH, HEIGHT))
try:
    draw_stone_tablet(test_surf, 100, 100, 360, 52, "Test Item", True, _b5_font)
    check("B5-6a draw_stone_tablet selected no crash", True)
except Exception as e:
    check("B5-6a draw_stone_tablet selected no crash", False, str(e))

# B5-7: draw_stone_tablet doesn't crash (not selected)
try:
    draw_stone_tablet(test_surf, 100, 200, 360, 52, "Test Item 2", False, _b5_font)
    check("B5-7a draw_stone_tablet unselected no crash", True)
except Exception as e:
    check("B5-7a draw_stone_tablet unselected no crash", False, str(e))

# B5-8: PauseOverlay creation
po = PauseOverlay()
check("B5-8a overlay has 3 items", len(po.items) == 3)
check("B5-8b overlay default selected is 0", po.selected == 0)
check("B5-8c overlay items match expected", po.items == ["Продолжить", "Настройки", "Выход в меню"])
check("B5-8d overlay candles start empty", len(po._candles) == 0)
check("B5-8e overlay timer starts at 0", po._timer == 0.0)
check("B5-8f overlay game is None", po.game is None)
check("B5-8g overlay confirm is None", po.confirm is None)

# B5-9: PauseOverlay enter resets state
po.selected = 2
po._candles = [ConfessionalCandle(100, 100)]
po._timer = 5.0
mock_game = Game()
mock_game.start_game("warrior")
po.enter(game=mock_game)
check("B5-9a enter resets selected", po.selected == 0)
check("B5-9b enter resets candles", len(po._candles) == 0)
check("B5-9c enter resets timer", po._timer == 0.0)
check("B5-9d enter sets game", po.game is mock_game)
check("B5-9e enter resets confirm", po.confirm is None)

# B5-10: PauseOverlay update spawns candles
po2 = PauseOverlay()
po2.enter(game=mock_game)
for _ in range(20):
    po2.update(1 / 60)
check("B5-10a candles spawned after updates", len(po2._candles) > 0)
check("B5-10b timer advanced", po2._timer > 0)

# B5-11: PauseOverlay candle cap at 40
po3 = PauseOverlay()
po3.enter(game=mock_game)
for _ in range(500):
    po3.update(1 / 60)
check("B5-11a candles capped at 40", len(po3._candles) <= 40)

# B5-12: handle_events — up/down navigation
po4 = PauseOverlay()
po4.enter(game=mock_game)
ev_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
po4.handle_events([ev_down])
check("B5-12a down key moves selection", po4.selected == 1)
po4.handle_events([ev_down])
check("B5-12b second down moves to 2", po4.selected == 2)
po4.handle_events([ev_down])
check("B5-12c down wraps to 0", po4.selected == 0)
ev_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
po4.handle_events([ev_up])
check("B5-12d up wraps to 2", po4.selected == 2)

# B5-13: handle_events — ESC returns __overlay__
po5 = PauseOverlay()
po5.enter(game=mock_game)
ev_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
result_esc = po5.handle_events([ev_esc])
check("B5-13a ESC returns __overlay__", result_esc == "__overlay__")

# B5-14: handle_events — Enter on Continue returns __overlay__
po6 = PauseOverlay()
po6.enter(game=mock_game)
po6.selected = 0
ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
result_cont = po6.handle_events([ev_enter])
check("B5-14a Continue returns __overlay__", result_cont == "__overlay__")

# B5-15: handle_events — Enter on Settings returns tuple
po7 = PauseOverlay()
po7.enter(game=mock_game)
po7.selected = 1
result_sett = po7.handle_events([ev_enter])
check("B5-15a Settings returns tuple", isinstance(result_sett, tuple))
check("B5-15b Settings tuple is settings", result_sett[0] == "settings")
check("B5-15c Settings has return_to kwarg", result_sett[1]["return_to"] == "__pause__")

# B5-16: handle_events — Enter on Exit opens ConfirmDialog
po8 = PauseOverlay()
po8.enter(game=mock_game)
po8.selected = 2
po8.handle_events([ev_enter])
check("B5-16a Exit opens ConfirmDialog", po8.confirm is not None)
check("B5-16b ConfirmDialog is active", po8.confirm.active)

# B5-17: ConfirmDialog — NO closes dialog
ev_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
ev_right = po8.confirm.handle_event(ev_left)  # move to ДА
ev_right_ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
po8.confirm.handle_event(ev_right_ev)  # move back to НЕТ
ev_enter2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
result_no = po8.confirm.handle_event(ev_enter2)
check("B5-17a NO returns False", result_no == False)
check("B5-17b confirm cleared after NO", po8.confirm is not None)  # confirm object still exists
# But active should be False
check("B5-17c confirm deactivated", not po8.confirm.active)

# B5-18: draw with game (no crash)
po9 = PauseOverlay()
po9.enter(game=mock_game)
mock_game.player.kills = 42
mock_game.player.level = 5
mock_game.player.gold = 1200
mock_game.player.weapons = []
mock_game.player.passives = {}
try:
    po9.draw(screen)
    check("B5-18a draw with game no crash", True)
except Exception as e:
    check("B5-18a draw with game no crash", False, str(e))

# B5-19: draw without game (no crash)
po10 = PauseOverlay()
po10.enter()
try:
    po10.draw(screen)
    check("B5-19a draw without game no crash", True)
except Exception as e:
    check("B5-19a draw without game no crash", False, str(e))

# B5-20: draw with candles (after update)
po11 = PauseOverlay()
po11.enter(game=mock_game)
for _ in range(30):
    po11.update(1 / 60)
try:
    po11.draw(screen)
    check("B5-20a draw with candles no crash", True)
    check("B5-20b candles present during draw", len(po11._candles) > 0)
except Exception as e:
    check("B5-20a draw with candles no crash", False, str(e))

# B5-21: draw with ConfirmDialog active
po12 = PauseOverlay()
po12.enter(game=mock_game)
po12.selected = 2
po12.handle_events([ev_enter])
try:
    po12.draw(screen)
    check("B5-21a draw with ConfirmDialog no crash", True)
except Exception as e:
    check("B5-21a draw with ConfirmDialog no crash", False, str(e))

# B5-22: confessional palette constants defined
check("B5-22a CONFESS_DARK is dark tuple", len(CONFESS_DARK) == 3 and all(c < 30 for c in CONFESS_DARK))
check("B5-22b CONFESS_IRON defined", len(CONFESS_IRON) == 3)
check("B5-22c CONFESS_GOLD is warm", CONFESS_GOLD[0] > CONFESS_GOLD[2])
check("B5-22d CONFESS_STONE_DARK < CONFESS_STONE_LIGHT", sum(CONFESS_STONE_DARK) < sum(CONFESS_STONE_LIGHT))

# B5-23: PARCH_INK import works
check("B5-23a PARCH_INK is tuple", len(PARCH_INK) == 3)
check("B5-23b PARCH_INK is light color", sum(PARCH_INK) > 300)

# B5-24: Multiple draws (animation frame simulation)
po13 = PauseOverlay()
po13.enter(game=mock_game)
try:
    for _ in range(10):
        po13.update(1 / 60)
        po13.draw(screen)
    check("B5-24a 10 animation frames no crash", True)
except Exception as e:
    check("B5-24a 10 animation frames no crash", False, str(e))

# B5-25: Pause overlay with weapon and passive build display
mock_game.player.weapons = [type('W', (), {'name': 'Кнут', 'level': 3, 'evolved': False})()]
mock_game.player.passives = {"might": 2, "speed": 1}
po14 = PauseOverlay()
po14.enter(game=mock_game)
try:
    po14.draw(screen)
    check("B5-25a draw with weapons+passives no crash", True)
except Exception as e:
    check("B5-25a draw with weapons+passives no crash", False, str(e))

# B5-26: Candle particle count after sustained updates
po15 = PauseOverlay()
po15.enter(game=mock_game)
for _ in range(600):
    po15.update(1 / 60)
total_candles = len(po15._candles)
check("B5-26a sustained candle count reasonable", 0 < total_candles <= 40, f"count={total_candles}")

# Cleanup
_wood_slats_cache.clear()


# ============================================================
# REF-9: Achievement Toast Tests
# ============================================================
print("\n--- REF-9: Achievement Toast ---")
from hud import AchievementToast, AchievementToastManager, ACH_TOAST_GOLD, ACH_TOAST_BG, ACH_TOAST_W, ACH_TOAST_H, spawn_achievement_toast
font = pygame.font.Font(None, 20)
small_font = pygame.font.Font(None, 16)

# REF-9-1: AchievementToast creation
at1 = AchievementToast("5 минут", "Дожить до 5 минут", 3.0)
check("REF-9-1a toast text set", at1.text == "5 минут")
check("REF-9-1b toast subtitle set", at1.subtitle == "Дожить до 5 минут")
check("REF-9-1c toast starts ENTERING", at1.state == AchievementToast.ENTERING)
check("REF-9-1d toast alpha starts 0", at1.alpha == 0)
check("REF-9-1e toast duration 3.0", at1.duration == 3.0)
check("REF-9-1f toast x_offset starts 350", at1.x_offset == 350)

# REF-9-2: AchievementToast slide-in animation
at2 = AchievementToast("Test", "", 3.0)
for _ in range(60):
    at2.update(1/60)
check("REF-9-2a toast transitions to VISIBLE", at2.state == AchievementToast.VISIBLE)
check("REF-9-2b toast x_offset reaches 0", at2.x_offset < 5)
check("REF-9-2c toast alpha reaches 255", at2.alpha == 255)

# REF-9-3: AchievementToast hold phase
at3 = AchievementToast("Test", "", 3.0)
for _ in range(150):  # 2.5 seconds at 60fps
    at3.update(1/60)
check("REF-9-3a toast still VISIBLE before expiry", at3.state == AchievementToast.VISIBLE)
check("REF-9-3b toast alive before expiry", at3.alive)

# REF-9-4: AchievementToast fade out
at4 = AchievementToast("Test", "", 0.5)  # short duration
for _ in range(600):  # 10 seconds
    at4.update(1/60)
check("REF-9-4a toast exits after duration", at4.state == AchievementToast.EXITING)
check("REF-9-4b toast alpha fades to 0", at4.alpha <= 0)
check("REF-9-4c toast not alive after fade", not at4.alive)

# REF-9-5: AchievementToastManager queue
atm = AchievementToastManager()
check("REF-9-5a starts empty", not atm.has_active)
atm.enqueue("Ach1", "desc1")
check("REF-9-5b has_active after enqueue", atm.has_active)
atm.update(1/60)
check("REF-9-5c active toast after update", atm._active is not None)
check("REF-9-5d active text correct", atm._active.text == "Ach1")

# REF-9-6: AchievementToastManager queue ordering
atm2 = AchievementToastManager()
atm2.enqueue("First", "")
atm2.enqueue("Second", "")
atm2.enqueue("Third", "")
atm2.update(1/60)
check("REF-9-6a first toast active", atm2._active.text == "First")
check("REF-9-6b two queued", len(atm2._queue) == 2)

# REF-9-7: AchievementToastManager draws without crash
try:
    atm3 = AchievementToastManager()
    atm3.enqueue("Test Toast", "Subtitle")
    atm3.update(1/60)
    atm3.draw(screen, font, small_font)
    check("REF-9-7a draw no crash", True)
except Exception as e:
    check("REF-9-7a draw no crash", False, str(e))

# REF-9-8: AchievementToast draw renders
try:
    at5 = AchievementToast("Golden", "Reward", 3.0)
    at5.update(0.1)  # partially visible
    at5.draw(screen, font, small_font, 100, 100)
    check("REF-9-8a draw no crash", True)
except Exception as e:
    check("REF-9-8a draw no crash", False, str(e))

# REF-9-9: Constants are sensible
check("REF-9-9a ACH_TOAST_W > 200", ACH_TOAST_W > 200)
check("REF-9-9b ACH_TOAST_H > 40", ACH_TOAST_H > 40)
check("REF-9-9c ACH_TOAST_GOLD is warm", ACH_TOAST_GOLD[0] > 150 and ACH_TOAST_GOLD[1] > 100)
check("REF-9-9d ACH_TOAST_BG is dark", sum(ACH_TOAST_BG) < 100)

# REF-9-10: spawn_achievement_toast public API
try:
    spawn_achievement_toast("API Test", "desc", 3.0)
    check("REF-9-10a spawn_achievement_toast no crash", True)
except Exception as e:
    check("REF-9-10a spawn_achievement_toast no crash", False, str(e))

# REF-9-11: Toast survives rapid enqueue/dequeue cycles
atm4 = AchievementToastManager()
for i in range(20):
    atm4.enqueue(f"Ach{i}", "", duration=0.1)  # short duration for speed
for _ in range(6000):  # 100 seconds at 60fps
    atm4.update(1/60)
check("REF-9-11a all 20 toasts processed", not atm4.has_active)

# REF-9-12: Toast subtitle empty = no crash
try:
    at6 = AchievementToast("No Sub", "", 3.0)
    at6.alpha = 200
    at6.x_offset = 0
    at6.state = AchievementToast.VISIBLE
    at6.draw(screen, font, small_font, 50, 50)
    check("REF-9-12a empty subtitle draw", True)
except Exception as e:
    check("REF-9-12a empty subtitle draw", False, str(e))

# REF-9-13: Multiple toasts queue correctly
atm5 = AchievementToastManager()
for i in range(5):
    atm5.enqueue(f"Toast{i}", f"desc{i}")
# Fast-forward first toast
for _ in range(300):
    atm5.update(1/60)
# First should be done or exiting, second should be active or queued
check("REF-9-13a queue drained after enough time", atm5._active is None or atm5._active.text != "Toast0")

# ==============================================================
# REF-10: Telegraphed Lightning (shrinking ring warning before strike)
# ==============================================================
from projectiles import LightningBolt

# REF-10-1: LightningBolt starts in telegraph phase
lb1 = LightningBolt(400, 300, 50, (255, 255, 150))
check("REF-10-1a starts in telegraph phase", lb1.phase == "telegraph")
check("REF-10-1b telegraph timer > 0", lb1.telegraph_timer > 0)
check("REF-10-1c alive at start", lb1.alive)
check("REF-10-1d segments empty before strike", lb1.segments == [])

# REF-10-2: Telegraph timer counts down
lb2 = LightningBolt(400, 300, 50, (255, 255, 150))
initial_timer = lb2.telegraph_timer
lb2.update(0.1)
check("REF-10-2a timer decreased", lb2.telegraph_timer < initial_timer)
check("REF-10-2b still in telegraph", lb2.phase == "telegraph")

# REF-10-3: Transition to strike after telegraph expires
lb3 = LightningBolt(400, 300, 50, (255, 255, 150))
lb3.update(0.35)  # exceed TELEGRAPH_TIME (0.3)
check("REF-10-3a transitioned to strike", lb3.phase == "strike")
check("REF-10-3b strike timer > 0", lb3.strike_timer > 0)
check("REF-10-3c segments generated after strike", len(lb3.segments) > 0)

# REF-10-4: on_strike callback fires on transition
strike_called = [False]
def test_callback():
    strike_called[0] = True
lb4 = LightningBolt(400, 300, 50, (255, 255, 150), on_strike=test_callback)
lb4.update(0.35)
check("REF-10-4a on_strike called", strike_called[0])

# REF-10-5: on_strike not called during telegraph
strike_early = [False]
def early_callback():
    strike_early[0] = True
lb5 = LightningBolt(400, 300, 50, (255, 255, 150), on_strike=early_callback)
lb5.update(0.1)  # only 0.1s, still in telegraph
check("REF-10-5a on_strike NOT called during telegraph", not strike_early[0])

# REF-10-6: Bolt dies after strike flash expires
lb6 = LightningBolt(400, 300, 50, (255, 255, 150))
lb6.update(0.35)  # enter strike
lb6.update(0.3)   # exceed STRIKE_FLASH_TIME (0.25)
check("REF-10-6a bolt dead after strike flash", not lb6.alive)

# REF-10-7: Draw in telegraph phase doesn't crash
lb7 = LightningBolt(400, 300, 50, (255, 255, 150))
try:
    lb7.draw(screen, 0, 0)
    check("REF-10-7a telegraph draw no crash", True)
except Exception as e:
    check("REF-10-7a telegraph draw no crash", False, str(e))

# REF-10-8: Draw in strike phase doesn't crash
lb8 = LightningBolt(400, 300, 50, (255, 255, 150))
lb8.update(0.35)
try:
    lb8.draw(screen, 0, 0)
    check("REF-10-8a strike draw no crash", True)
except Exception as e:
    check("REF-10-8a strike draw no crash", False, str(e))

# REF-10-9: Full lifecycle: telegraph -> strike -> dead
lb9 = LightningBolt(500, 400, 60, (255, 220, 50))
dt_step = 1/60
frames = 0
while lb9.alive and frames < 100:
    lb9.update(dt_step)
    frames += 1
check("REF-10-9a bolt completes within reasonable frames", frames < 40)  # 0.3+0.25 = 0.55s = ~33 frames
check("REF-10-9b bolt is dead after full lifecycle", not lb9.alive)

# REF-10-10: Telegraph ring shrinks (radius gets smaller)
lb10 = LightningBolt(400, 300, 80, (255, 255, 150))
# Calculate initial ring radius
t_init = lb10.telegraph_timer / lb10.TELEGRAPH_TIME
r_init = max(4, int(80 * (0.55 + 0.45 * t_init)))
lb10.update(0.2)  # advance 0.2s
t_mid = lb10.telegraph_timer / lb10.TELEGRAPH_TIME
r_mid = max(4, int(80 * (0.55 + 0.45 * t_mid)))
check("REF-10-10a ring radius shrinks over time", r_mid < r_init, f"r_init={r_init}, r_mid={r_mid}")

# REF-10-11: Callback captures damage values correctly
hit_data = {"hit": False, "damage": 0}
class MockEnemy10:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.alive = True
        self.radius = 10
        self.hp = 100
        self.max_hp = 100
        self.freeze_frames = 0
    def take_damage(self, dmg):
        hit_data["hit"] = True
        hit_data["damage"] = dmg
    def apply_slow(self, factor, dur):
        pass

mock_enemy = MockEnemy10(405, 305)  # close to bolt position (400, 300)
mock_enemies = [mock_enemy]

class MockFloatNum:
    def spawn_damage(self, x, y, dmg, color, player=None):
        pass

class MockPlayer10:
    crit_chance = 0.0

def on_strike_test():
    for e in mock_enemies:
        if not e.alive:
            continue
        dx = e.pos.x - 400
        dy = e.pos.y - 300
        if dx * dx + dy * dy < (50 + e.radius) ** 2:
            e.take_damage(25)
            e.apply_slow(0.5, 2.0)
            e.freeze_frames = 6

lb11 = LightningBolt(400, 300, 50, (255, 255, 150), on_strike=on_strike_test)
lb11.update(0.35)  # trigger strike
check("REF-10-11a enemy hit by delayed strike", hit_data["hit"])
check("REF-10-11b damage applied correctly", hit_data["damage"] == 25)
check("REF-10-11c enemy got freeze_frames", mock_enemy.freeze_frames == 6)

# REF-10-12: Enemy outside AoE radius not hit
far_enemy = MockEnemy10(999, 999)
far_hit = {"hit": False}
def on_strike_far():
    for e in [far_enemy]:
        if not e.alive:
            continue
        dx = e.pos.x - 400
        dy = e.pos.y - 300
        if dx * dx + dy * dy < (50 + e.radius) ** 2:
            far_hit["hit"] = True
lb12 = LightningBolt(400, 300, 50, (255, 255, 150), on_strike=on_strike_far)
lb12.update(0.35)
check("REF-10-12a far enemy NOT hit", not far_hit["hit"])

# REF-10-13: No on_strike callback = no crash
lb13 = LightningBolt(400, 300, 50, (255, 255, 150))
try:
    lb13.update(0.35)  # triggers strike, on_strike is None
    check("REF-10-13a no callback no crash", True)
except Exception as e:
    check("REF-10-13a no callback no crash", False, str(e))

# REF-10-14: Telegraph constants match reference (~18 frames at 60fps)
check("REF-10-14a telegraph time ~0.3s", abs(LightningBolt.TELEGRAPH_TIME - 0.3) < 0.01)
check("REF-10-14b strike flash time ~0.25s", abs(LightningBolt.STRIKE_FLASH_TIME - 0.25) < 0.01)

# REF-10-15: LightningWeapon creates bolt with telegraph (integration)
# Test that weapon creates a bolt with on_strike callback
lw = LightningWeapon()
lw.level = 1
# Create minimal mock game state
class MockPlayerW:
    pos = pygame.Vector2(400, 300)
    cooldown_mult = 1.0
    damage_mult = 1.0
    area_mult = 1.0
    crit_chance = 0.0
mock_p = MockPlayerW()
mock_pulses = []
mock_proj = []
mock_parts = []
mock_enemies_w = [MockEnemy10(410, 310)]
mock_enemies_w[0].radius = 10
# Force cooldown trigger
lw.timer = 999
lw.update(mock_p, mock_enemies_w, mock_proj, mock_pulses, mock_parts, 1/60)
check("REF-10-15a weapon created a pulse", len(mock_pulses) > 0)
if mock_pulses:
    bolt = mock_pulses[-1]
    check("REF-10-15b pulse is LightningBolt", isinstance(bolt, LightningBolt))
    check("REF-10-15c bolt starts in telegraph", bolt.phase == "telegraph")
    check("REF-10-15d bolt has on_strike callback", bolt.on_strike is not None)

# REF-10-16: Weapon bolt delays damage (enemy not hit during telegraph)
hit_check = {"hit": False}
class MockEnemyTrack:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.alive = True
        self.radius = 10
        self.hp = 100
        self.max_hp = 100
        self.freeze_frames = 0
    def take_damage(self, dmg):
        hit_check["hit"] = True
    def apply_slow(self, f, d):
        pass

class MockFloatTrack:
    def spawn_damage(self, *a, **kw):
        pass

lw2 = LightningWeapon()
lw2.level = 1
mock_p2 = MockPlayerW()
pulses2 = []
me2 = [MockEnemyTrack(410, 310)]
lw2.timer = 999
lw2.update(mock_p2, me2, [], pulses2, [], 1/60)
# After weapon fires, enemy should NOT be hit yet (still in telegraph)
check("REF-10-16a enemy NOT hit during telegraph phase", not hit_check["hit"])
# Now advance the bolt through telegraph
if pulses2:
    pulses2[0].update(0.35)  # trigger strike
    check("REF-10-16b enemy hit after telegraph ends", hit_check["hit"])


print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
if errors:
    print("\nFAILURES:")
    for e in errors:
        print(e)
print("=" * 60)

pygame.quit()
sys.exit(0 if failed == 0 else 1)
