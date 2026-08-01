import sys, os, traceback, pygame, asyncio

os.chdir("E:/birth-of-saint")
sys.path.insert(0, "E:/birth-of-saint")

pygame.init()
screen = pygame.display.set_mode((1024, 768))
clock = pygame.time.Clock()

from config import WIDTH, HEIGHT, FPS
from scene_manager import SceneManager
from scenes import *
from fade_manager import FadeManager
from menu import MainMenu
from lobby import MetaProgress, LobbyScreen

class MiniGame:
    def __init__(self):
        self.menu = MainMenu()
        self.meta = MetaProgress()
        self.lobby = LobbyScreen()
        self.player = None

game = MiniGame()
scene_mgr = SceneManager()
scene_mgr.fade = FadeManager()

# Register ALL scenes like main.py does
scene_mgr.register("splash", SplashScene())
scene_mgr.register("title", TitleScene(game.menu, game.meta, game.lobby))
scene_mgr.register("lobby", LobbyScene(game.lobby, game.meta, game.menu))
scene_mgr.register("settings", SettingsScene())
scene_mgr.register("bestiary", BestiaryScene(game.meta, game.lobby))
scene_mgr.register("codex", CodexScene(game.meta, game.lobby))
scene_mgr.register("run_prep", RunPrepScene())
scene_mgr.switch("splash")

log = []
log.append("Scene manager created OK")
log.append(f"Registered scenes: {list(scene_mgr.scenes.keys())}")

# Run 120 frames (2 seconds)
for i in range(120):
    dt = clock.tick(FPS) / 1000.0
    dt = min(dt, 0.05)
    try:
        events = pygame.event.get()
        result = scene_mgr.handle_events(events)
        scene_mgr.update(dt)
        scene_mgr.draw(screen)
        pygame.display.flip()
        if i == 60:
            log.append(f"Frame 60: current_scene={scene_mgr.current}")
    except Exception as e:
        log.append(f"CRASH at frame {i}: {e}")
        log.append(traceback.format_exc())
        break

log.append(f"Final: current_scene={scene_mgr.current}")
log.append("120 frames OK")

with open("E:/birth-of-saint/_test_output.txt", "w") as f:
    f.write("\n".join(log))
print("\n".join(log))
