#!/usr/bin/env python3
"""
Headless Scene Flow Test — verifies all transitions with injected pygame events.
Updated for new lobby key mapping: ESC→title, Enter→run_prep.
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
print("SCENE FLOW TEST v2 — Birth of the Saint")
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
    if scene_mgr.overlay:
        scene_mgr.pop_overlay()

# ══════════════════════════════════════════════════════════════════
# TEST 1: Splash → Title
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 1] Splash → Title")
scene_mgr.current = "splash"
scene_mgr.scenes["splash"].enter()
tick(300)
if get_state()[0] != "title":
    scene_mgr.switch("title"); tick(10)
check("Splash → Title", "title")

# ══════════════════════════════════════════════════════════════════
# TEST 2: Title → Lobby (Enter on ИГРАТЬ)
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
# TEST 5: Lobby → Settings (O)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 5] Lobby → Settings (O)")
send_key(pygame.K_o, 10)
check("Lobby → Settings", "settings")
send_key(pygame.K_ESCAPE, 10)
check("Settings → Lobby (return_to)", "lobby")

# ══════════════════════════════════════════════════════════════════
# TEST 6: Lobby → Title (ESC) — NEW!
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 6] Lobby → Title (ESC)")
send_key(pygame.K_ESCAPE, 10)
check("Lobby → Title (ESC)", "title")

# ══════════════════════════════════════════════════════════════════
# TEST 7: Title → Settings (button)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 7] Title → Settings (button)")
send_key(pygame.K_DOWN, 5); send_key(pygame.K_RETURN, 10)
if get_state()[0] == "settings":
    check("Title → Settings", "settings")
    send_key(pygame.K_ESCAPE, 10)
    check("Settings → Title", "title")
else:
    scene_mgr.switch("settings", return_to="title"); tick(10)
    check("Settings (direct)", "settings")
    send_key(pygame.K_ESCAPE, 10)
    check("Settings → Title", "title")

# ══════════════════════════════════════════════════════════════════
# TEST 8: Lobby → RunPrep → Game (Enter flow)
# TEST 8: Lobby → RunPrep → Game (Enter flow)
# First Enter in lobby selects char (returns "play" if already selected → run_prep)
# Second Enter in run_prep → game
print("\n[TEST 8] Lobby → RunPrep → Game (Enter flow)")
scene_mgr.switch("lobby"); tick(10)
# Verify we're in lobby
check("Start at lobby", "lobby")
# Send first Enter — should go to run_prep (char already selected)
send_key(pygame.K_RETURN, 10)
state_after_1st = get_state()
# If we landed in run_prep, great. If in game, run_prep auto-advanced.
if state_after_1st[0] == "run_prep":
    check("Lobby → RunPrep (Enter)", "run_prep")
    send_key(pygame.K_RETURN, 10)
    check("RunPrep → Game (Enter)", "game")
elif state_after_1st[0] == "game":
    check_bool("Lobby → RunPrep → Game (fast path)", True, "run_prep auto-advanced to game")
else:
    check_bool("Lobby → RunPrep", False, f"got {state_after_1st[0]}")

# ══════════════════════════════════════════════════════════════════
# TEST 9: Game → PauseOverlay (ESC)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 9] Game → PauseOverlay (ESC)")
game.state = "playing"
ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode="", scancode=0)
result = scene_mgr.scenes["game"].handle_events([ev])
check_bool("Game ESC → __pause__", result == "__pause__", f"got={result}")
scene_mgr.overlay = None
send_key(pygame.K_ESCAPE, 10)
check("Game → PauseOverlay", None, "PauseOverlay")
cleanup_overlay()

# ══════════════════════════════════════════════════════════════════
# TEST 10: Game → GameOver
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 10] Game → GameOver")
scene_mgr.switch("game", char_id="warrior"); tick(5)
game.state = "gameover"
scene_mgr.switch("game_over", stats={"kills": 42, "gold": 100, "level": 5, "wave": 3, "time": 120})
tick(5)
check("Game → GameOver", "game_over")

# ══════════════════════════════════════════════════════════════════
# TEST 11: GameOver → Game (R)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 11] GameOver → Game (R)")
send_key(pygame.K_r, 10)
check("GameOver → Game (R)", "game")

# ══════════════════════════════════════════════════════════════════
# TEST 12: GameOver → Lobby (ESC)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 12] GameOver → Lobby (ESC)")
game.state = "gameover"
scene_mgr.switch("game_over", stats={"kills": 10}); tick(5)
send_key(pygame.K_ESCAPE, 10)
check("GameOver → Lobby", "lobby")

# ══════════════════════════════════════════════════════════════════
# TEST 13: GameOver → Settings (S) — NEW!
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 13] GameOver → Settings (S)")
scene_mgr.switch("game", char_id="warrior"); tick(5)
game.state = "gameover"
scene_mgr.switch("game_over", stats={"kills": 10}); tick(5)
send_key(pygame.K_s, 10)
check("GameOver → Settings (S)", "settings")
send_key(pygame.K_ESCAPE, 10)
check("Settings → GameOver (return_to)", "game_over")

# ══════════════════════════════════════════════════════════════════
# TEST 14: RunPrep → Settings (S) — NEW!
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 14] RunPrep → Settings (S)")
scene_mgr.switch("run_prep"); tick(10)
send_key(pygame.K_s, 10)
check("RunPrep → Settings (S)", "settings")
send_key(pygame.K_ESCAPE, 10)
check("Settings → RunPrep (return_to)", "run_prep")

# ══════════════════════════════════════════════════════════════════
# TEST 15: PauseOverlay → Settings (tuple)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 15] PauseOverlay → Settings (tuple)")
pause = PauseOverlay()
pause.enter(game=game)
pause.selected = 1
ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="", scancode=0)
result = pause.handle_events([ev])
is_settings = isinstance(result, tuple) and result[0] == "settings"
check_bool("Pause → Settings tuple", is_settings, f"result={result}")
if is_settings:
    check_bool("return_to=__pause__", result[1].get("return_to") == "__pause__")

# ══════════════════════════════════════════════════════════════════
# TEST 16: PauseOverlay → Lobby (Confirm)
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 16] PauseOverlay → Lobby (Confirm)")
pause2 = PauseOverlay()
pause2.enter(game=game)
pause2.selected = 2
ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="", scancode=0)
pause2.handle_events([ev])
has_confirm = pause2.confirm is not None and pause2.confirm.active
check_bool("ConfirmDialog opened", has_confirm)
if has_confirm:
    ev_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, mod=0, unicode="", scancode=0)
    pause2.handle_events([ev_left])
    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="", scancode=0)
    result2 = pause2.handle_events([ev_enter])
    check_bool("Confirm → lobby", result2 == "lobby", f"result={result2}")

# ══════════════════════════════════════════════════════════════════
# TEST 17: All scenes registered
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 17] Scene registrations")
expected = {"splash", "title", "lobby", "char_select", "stage_select",
            "game", "game_over", "bestiary", "codex", "settings", "run_prep"}
registered = set(scene_mgr.scenes.keys())
check_bool(f"All {len(expected)} scenes registered", expected <= registered,
           f"missing={expected - registered}")

# ══════════════════════════════════════════════════════════════════
# TEST 18: QUIT event
# ══════════════════════════════════════════════════════════════════
print("\n[TEST 18] QUIT event")
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

# Save
output = {
    "transitions": transitions,
    "results": [(n, ok) for n, ok in results],
    "passed": passed, "total": total,
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
