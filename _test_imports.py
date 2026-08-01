import sys, traceback
try:
    from config import WIDTH, HEIGHT, FPS, TITLE, MAP_WIDTH, MAP_HEIGHT, calc_xp_for_level, RUNE_DEFS, RUNE_TYPES, ACHIEVEMENTS
    from player import Player, CHARACTERS
    from camera import Camera
    from wave_manager import WaveManager
    from xp_system import XPGem, LevelUpScreen
    from weapons import create_weapon
    from projectiles import Pulse, Projectile, floating_numbers, EvolutionGlow, emit_hit_burst, RingBurst, GoldCoin
    from hud import draw_hud, combo_register_kill, combo_edge_flash, spawn_achievement_toast
    from effects import ScreenShake, ScreenFlash, LowHPVignette, draw_grid
    from menu import MainMenu
    from enemies import ENEMY_TYPES
    from obstacles import generate_obstacles, preload_obstacle_sprites
    from lobby import MetaProgress, LobbyScreen
    from save_system import save_progress, load_progress
    from arcana import Arcana
    from relics import RelicManager, RELIC_DEFS
    from leaderboard import add_score, get_entries
    from scene_manager import SceneManager
    from scenes import SplashScene, TitleScene, GameScene, GameOverScene, LobbyScene, SettingsScene, BestiaryScene, CodexScene, RunPrepScene
    print("ALL_IMPORTS_OK")
except Exception as e:
    print(f"IMPORT_ERROR: {e}")
    traceback.print_exc()
