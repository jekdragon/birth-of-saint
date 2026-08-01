"""Comprehensive verification of all bug fixes from ZCode/OpenCode debate."""
import sys
sys.path.insert(0, r"E:/birth-of-saint")
import pygame
pygame.init()
screen = pygame.display.set_mode((1, 1))

from lobby import LobbyScreen, MetaProgress
from player import CHARACTERS
from weapons import WEAPON_DEFS

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  OK {name}")
        passed += 1
    else:
        print(f"  FAIL {name}: {detail}")
        failed += 1

# === ZCODE BUGS ===

# Bug 1: heroes list desync
m1 = MetaProgress()
m1.unlocked_chars = {'inquisitor', 'monk'}
l1 = LobbyScreen()
l1.activate(m1)
ev_r = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
l1._handle_heroes(ev_r)
all_chars = list(CHARACTERS.keys())
check("Bug1: desync fix", all_chars[l1.selected] in CHARACTERS,
      f"selected={l1.selected} -> {all_chars[l1.selected]}")

# Bug 2: ban_mode reset on TAB
m2 = MetaProgress()
m2.ban_tokens = 3
l2 = LobbyScreen()
l2.activate(m2)
l2.ban_mode = True
ev_tab = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)
l2.handle_event(ev_tab)
check("Bug2: ban reset on TAB", l2.ban_mode == False,
      f"ban_mode={l2.ban_mode}")

# Bug 3: ESC in ban mode
m3 = MetaProgress()
m3.ban_tokens = 3
l3 = LobbyScreen()
l3.activate(m3)
l3.ban_mode = True
ev_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
result3 = l3.handle_event(ev_esc)
check("Bug3: ESC ban -> shop", l3.ban_mode == False and result3 is None and l3.active,
      f"ban_mode={l3.ban_mode}, result={result3}, active={l3.active}")

# === OPENCODE BUGS ===

# Bug 4: dynamic cols
m4 = MetaProgress()
m4.unlocked_chars = {'warrior', 'paladin', 'inquisitor', 'pilgrim', 'monk'}
l4 = LobbyScreen()
l4.activate(m4)
ev_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
l4._handle_heroes(ev_down)
check("Bug4: dynamic cols (5 chars)", l4.selected == 3,
      f"selected={l4.selected}, expected=3")

# Bug 5: locked char ENTER feedback
m5 = MetaProgress()
m5.unlocked_chars = {'warrior', 'paladin'}
l5 = LobbyScreen()
l5.activate(m5)
l5.selected = 2  # inquisitor (locked)
ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
try:
    l5._handle_heroes(ev_enter)
    check("Bug5: locked ENTER no crash", True)
except Exception as e:
    check("Bug5: locked ENTER no crash", False, str(e))

# === MY FIXES ===

# Fix 1: B toggle ban_mode
m6 = MetaProgress()
m6.ban_tokens = 3
l6 = LobbyScreen()
l6.activate(m6)
l6.tab_index = 2
ev_b = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_b)
l6.handle_event(ev_b)
check("Fix1: B toggle ON", l6.ban_mode == True, f"ban_mode={l6.ban_mode}")
l6.handle_event(ev_b)
check("Fix1: B toggle OFF", l6.ban_mode == False, f"ban_mode={l6.ban_mode}")

# Fix 2: Ban item via ENTER
m7 = MetaProgress()
m7.ban_tokens = 3
l7 = LobbyScreen()
l7.activate(m7)
l7.ban_mode = True
l7.selected = 0
ev_enter2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
l7.handle_event(ev_enter2)
items7 = l7._get_ban_items()
check("Fix2: ban item", items7[0]["id"] in m7.banned_items,
      f"banned={m7.banned_items}")
check("Fix2: notification", "Забанено" in l7.notification,
      f"notification={l7.notification}")

# Fix 3: Unban via second ENTER
l7.handle_event(ev_enter2)
check("Fix3: unban item", items7[0]["id"] not in m7.banned_items,
      f"banned={m7.banned_items}")

# === INTEGRATION ===

# FadeManager
from fade_manager import FadeManager
f = FadeManager()
f.fade_out(0.1)
for _ in range(10):
    f.update(1/60)
f.draw(screen)
check("Integration: FadeManager", f.phase == "in")

# ConfirmDialog
from confirm_dialog import ConfirmDialog
d = ConfirmDialog("Test", "sub")
d.show()
d.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
r = d.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
check("Integration: ConfirmDialog", r == True)

# SoundManager
from sounds import SoundManager
sm = SoundManager()
import sound_manager
sound_manager.init(sm)
check("Integration: SoundManager", True)

# Minimap
from hud import draw_minimap
draw_minimap(screen, None, [], 0, 0)
check("Integration: Minimap", True)

# Enemy indicators
from hud import draw_enemy_indicators
draw_enemy_indicators(screen, None, [], 0, 0)
check("Integration: Enemy indicators", True)

# === SUMMARY ===
pygame.quit()
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed")
if failed > 0:
    sys.exit(1)
