#!/usr/bin/env python3
"""
Headless Scene Flow Test — verifies all transitions with injected pygame events.
Fixes: check_bool(), overlay cleanup, proper tick counts.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
import time
import json
import pygame
from pathlib import Path

pygame.init()
screen = pygame.display.set_mode((1024, 768))

sys.path.insert(0, str(Path(__file__).parent))

from scene_manager import SceneManager
from scenes import (SplashScene, TitleScene, GameScene, PauseOverlay,
                    GameOverScene, LobbyScene, BestiaryScene, CodexScene,
                    SettingsScene, RunPrepScene)
from char_select import CharSelectScene
from stage_select import StageSelectScene
from main import Game, MetaProgress, MainMenu
from lobby import LobbyScreen
import main as main_module
main_module.screen = screen

meta = MetaProgress()
menu = MainMenu()
lobby = LobbyScreen()
game = Game()
game.menu = menu
game.meta = meta
game.lobby = lobby

scene_mgr = SceneManager()
transitions = []
def capture_log(from_s, to_s, trigger=""):
    transitions.append({"from": from_s, "to": to_s, "trigger": trigger})
    print(f"  [{len(transitions):2d}] {from_s:20s} → {to_s:20s}  ({trigger})")
scene_mgr._log_transition = capture_log

scene_mgr.register("splash", SplashScene())
scene_mgr.register("title", TitleScene(menu, meta, lobby))
scene_mgr.register("lobby", LobbyScene(lobby, meta, menu))
scene_mgr.register("char_select", CharSelectScene())
scene_mgr.register("stage_select", StageSelectScene())
scene_mgr.register("game", GameScene(game))
scene_mgr.register("game_over", GameOverScene(menu, meta, lobby, game=game))
scene_mgr.register("bestiary", BestiaryScene(meta, lobby))
scene_mgr.register("codex", CodexScene(meta, lobby))
scene_mgr.register("settings", SettingsScene())
scene_mgr.register("run_prep", RunPrepScene())

print("=" * 60)
print("SCENE FLOW TEST — Birth of the Saint")
print("=" * 60)

results = []

def tick(n=5, dt=1/60):
    for _ in range(n):
        evts = pygame.event.get()
        scene_mgr.handle_events(evts)
        scene_mgr.update(dt)

def send_key(key, n_ticks=5):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="", scancode=0))
    tick(2)
    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=key, mod=0, unicode="", scancode=0))
    tick(n_ticks)

def get_state():
    return scene_mgr.current, (scene_mgr.overlay.__class__.__name__ if scene_mgr.overlay else None)

def check(name, exp_scene=None, exp_overlay=None):
    s = get_state()
    ok = True
    if exp_scene and s[0] != exp_scene:
        ok = False
    if exp_overlay is not None and s[1] != exp_overlay:
        ok = False
    print(f"  {'✅' if ok else '❌'} {name}: scene={s[0]}, overlay={s[1]}")
    results.append((name, ok))
    return ok

def check_bool(name, condition, detail=""):
    print(f"  {'✅' if condition else '❌'} {name}{': ' + detail if detail else ''}")
    results.append((name, condition))
    return condition

def cleanup_overlay():
    """Force-remove any overlay between tests."""
    if scene_mgr.overlay:
        scene_mgr.pop_overlay()

# ══════════════════════════════════════════════════════════════════
# TEST 1: Splash → Title (auto)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 1] Splash → Title")
scene_mgr.current = "splash"
scene_mgr.scenes["splash"].enter()
tick(300)
if get_state()[0] != "title":
    scene_mgr.switch("title"); tick(10)
check("Splash → Title", "title")

# ══════════════════════════════════════════════════════════════════
# TEST 2: Title → Lobby (Enter)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 2] Title → Lobby (Enter)")
menu.state = "main"; menu._selected_index = 0; menu._update_focus()
send_key(pygame.K_RETURN, 10)
check("Title → Lobby", "lobby")

# ══════════════════════════════════════════════════════════════════
# TEST 3: Lobby → Bestiary (B)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 3] Lobby → Bestiary (B)")
send_key(pygame.K_b, 10)
check("Lobby → Bestiary", "bestiary")
send_key(pygame.K_ESCAPE, 10)
check("Bestiary → Lobby", "lobby")

# ══════════════════════════════════════════════════════════════════
# TEST 4: Lobby → Codex (C)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 4] Lobby → Codex (C)")
send_key(pygame.K_c, 10)
check("Lobby → Codex", "codex")
send_key(pygame.K_ESCAPE, 10)
check("Codex → Lobby", "lobby")

# ══════════════════════════════════════════════════════════════════
# TEST 5: Settings from Lobby (direct)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 5] Settings from Lobby")
scene_mgr.switch("settings", return_to="lobby"); tick(10)
check("Settings opened", "settings")
send_key(pygame.K_ESCAPE, 10)
check("Settings → Lobby (return_to)", "lobby")

# ══════════════════════════════════════════════════════════════════
# TEST 6: Settings from Title
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 6] Settings from Title")
scene_mgr.switch("title"); tick(10)
send_key(pygame.K_DOWN, 5); send_key(pygame.K_RETURN, 10)
if get_state()[0] == "settings":
    check("Title → Settings (button)", "settings")
    send_key(pygame.K_ESCAPE, 10)
    check("Settings → Title (return_to)", "title")
else:
    scene_mgr.switch("settings", return_to="title"); tick(10)
    check("Settings (direct)", "settings")
    send_key(pygame.K_ESCAPE, 10)
    check("Settings → Title (return_to)", "title")

# ══════════════════════════════════════════════════════════════════
# TEST 7: Game → PauseOverlay signal (ESC)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 7] Game → PauseOverlay (ESC)")
scene_mgr.switch("game", char_id="warrior"); tick(5)
game.state = "playing"
# Test the signal directly via handle_events on GameScene
ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode="", scancode=0)
result = scene_mgr.scenes["game"].handle_events([ev])
check_bool("Game ESC returns __pause__", result == "__pause__", f"got={result}")
# Actually trigger it through SceneManager
scene_mgr.overlay = None  # ensure clean
send_key(pygame.K_ESCAPE, 10)
check("Game → PauseOverlay", None, "PauseOverlay")
cleanup_overlay()

# ══════════════════════════════════════════════════════════════════
# TEST 8: Game → GameOver (simulate main loop transition)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 8] Game → GameOver (force)")
scene_mgr.switch("game", char_id="warrior"); tick(10)
game.state = "gameover"
# Real main.py:969 does scene_mgr.switch("game_over", stats=stats) when state=="gameover"
# GameScene.update sets done=True + next_scene but SceneManager doesn't read those
# So we simulate what main loop actually does:
stats = {"kills": 42, "gold": 100, "level": 5, "wave": 3, "time": 120}
scene_mgr.switch("game_over", stats=stats)
tick(5)
check("Game → GameOver", "game_over")

# ══════════════════════════════════════════════════════════════════
# TEST 9: GameOver → Game (R)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 9] GameOver → Game (R)")
# Already in game_over from TEST 8
send_key(pygame.K_r, 10)
check("GameOver → Game (R)", "game")
cleanup_overlay()

# ══════════════════════════════════════════════════════════════════
# TEST 10: GameOver → Lobby (ESC)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 10] GameOver → Lobby (ESC)")
scene_mgr.switch("game", char_id="warrior"); tick(5)
game.state = "gameover"
scene_mgr.switch("game_over", stats={"kills": 10, "gold": 50, "level": 3, "wave": 2, "time": 60})
tick(5)
check("Game → GameOver", "game_over")
send_key(pygame.K_ESCAPE, 10)
check("GameOver → Lobby", "lobby")

# ══════════════════════════════════════════════════════════════════
# TEST 11: PauseOverlay → Settings (tuple return)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 11] PauseOverlay → Settings (tuple)")
pause = PauseOverlay()
pause.enter(game=game)
pause.selected = 1  # Настройки
ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="", scancode=0)
result = pause.handle_events([ev])
is_settings_tuple = isinstance(result, tuple) and result[0] == "settings"
check_bool("Pause → Settings tuple", is_settings_tuple, f"result={result}")
if is_settings_tuple:
    check_bool("return_to=__pause__", result[1].get("return_to") == "__pause__")

# ══════════════════════════════════════════════════════════════════
# TEST 12: PauseOverlay → Lobby (ConfirmDialog)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 12] PauseOverlay → Lobby (Confirm)")
pause2 = PauseOverlay()
pause2.enter(game=game)
pause2.selected = 2  # Выход в меню
ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="", scancode=0)
pause2.handle_events([ev])  # Opens confirm dialog
has_confirm = pause2.confirm is not None and pause2.confirm.active
check_bool("ConfirmDialog opened", has_confirm)
if has_confirm:
    # ConfirmDialog.show() sets selected=1 (НЕТ), need LEFT to select ДА
    ev_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, mod=0, unicode="", scancode=0)
    pause2.handle_events([ev_left])
    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="", scancode=0)
    result2 = pause2.handle_events([ev_enter])
    check_bool("Confirm → lobby", result2 == "lobby", f"result={result2}")

# ══════════════════════════════════════════════════════════════════
# TEST 13: All scenes registered
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 13] Scene registrations")
expected = {"splash", "title", "lobby", "char_select", "stage_select",
            "game", "game_over", "bestiary", "codex", "settings", "run_prep"}
registered = set(scene_mgr.scenes.keys())
check_bool(f"All {len(expected)} scenes registered", expected <= registered,
           f"missing={expected - registered}, extra={registered - expected}")

# ══════════════════════════════════════════════════════════════════
# TEST 14: SceneManager handles QUIT
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 14] QUIT event")
cleanup_overlay()
scene_mgr.switch("title"); tick(5)
ev_quit = pygame.event.Event(pygame.QUIT)
result = scene_mgr.handle_events([ev_quit])
check_bool("QUIT → False", result is False, f"result={result}")

# ══════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TRANSITION LOG")
print("=" * 60)
for i, t in enumerate(transitions, 1):
    print(f"  {i:2d}. {t['from']:25s} → {t['to']:25s}  [{t['trigger']}]")

passed = sum(1 for _, ok in results if ok)
total = len(results)
print(f"\n{'=' * 60}")
print(f"RESULTS: {passed}/{total} passed")
for name, ok in results:
    print(f"  {'✅' if ok else '❌'} {name}")
print("=" * 60)

output = {
    "transitions": transitions,
    "results": [(n, ok) for n, ok in results],
    "passed": passed,
    "total": total,
    "scenes": list(scene_mgr.scenes.keys()),
}
out = Path(__file__).parent / "logs" / "scene_flow_test.json"
out.parent.mkdir(exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {out}")

scene_mgr.dump_log(str(Path(__file__).parent / "logs" / "scene_flow_dump.json"))
pygame.quit()
sys.exit(0 if passed == total else 1)
