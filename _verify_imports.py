"""Verify all cross-module imports in birth-of-saint project."""
import importlib
import sys

checks = [
    ("bestiary", "config", ["WIDTH", "HEIGHT", "WHITE", "GOLD", "DARK_BG", "RED", "GREEN"]),
    ("bestiary", "enemies", ["ENEMY_TYPES"]),
    ("bestiary", "weapons", ["WEAPON_DEFS", "PASSIVE_DEFS", "EVOLUTIONS"]),
    ("bestiary", "hud", ["generate_parchment", "PARCH_DARK", "PARCH_MID", "PARCH_BASE", "PARCH_LIGHT", "PARCH_INK", "PARCH_INK_DIM"]),
    ("camera", "config", ["WIDTH", "HEIGHT", "MAP_WIDTH", "MAP_HEIGHT"]),
    ("cathedral", "config", ["MAP_WIDTH", "MAP_HEIGHT", "CENTER_X", "CENTER_Y", "TILE_SIZE"]),
    ("char_select", "config", ["WIDTH", "HEIGHT", "WHITE", "GOLD", "DARK_BG", "GREEN"]),
    ("char_select", "player", ["CHARACTERS"]),
    ("confirm_dialog", "config", ["WIDTH", "HEIGHT", "WHITE", "GOLD"]),
    ("effects", "config", ["WIDTH", "HEIGHT", "MAP_WIDTH", "MAP_HEIGHT", "TILE_SIZE", "BIOMES", "CENTER_X", "CENTER_Y"]),
    ("enemies", "config", ["WHITE", "RED", "DARK_RED", "YELLOW", "PURPLE", "ICE_BLUE", "GOLD", "MAP_WIDTH", "MAP_HEIGHT"]),
    ("fade_manager", "config", ["WIDTH", "HEIGHT"]),
    ("game_over_screen", "config", ["WIDTH", "HEIGHT", "WHITE", "GOLD", "RED", "DARK_BG"]),
    ("game_over_screen", "weapons", ["WEAPON_DEFS", "PASSIVE_DEFS"]),
    ("game_over_screen", "hud", ["generate_parchment", "PARCH_INK", "PARCH_INK_DIM", "PARCH_BASE", "PARCH_LIGHT"]),
    ("hud", "weapons", ["WEAPON_DEFS", "PASSIVE_DEFS"]),
    ("lobby", "arcana", ["ARCANA_DEFS"]),
    ("lobby", "player", ["CHARACTERS"]),
    ("lobby", "save_system", ["save_progress"]),
    ("lobby", "weapons", ["WEAPON_DEFS"]),
    ("main", "config", ["WIDTH", "HEIGHT", "FPS", "TITLE", "MAP_WIDTH", "MAP_HEIGHT", "calc_xp_for_level", "RUNE_DEFS", "RUNE_TYPES", "ACHIEVEMENTS"]),
    ("main", "player", ["Player", "CHARACTERS"]),
    ("main", "camera", ["Camera"]),
    ("main", "wave_manager", ["WaveManager"]),
    ("main", "xp_system", ["XPGem", "LevelUpScreen"]),
    ("main", "weapons", ["create_weapon"]),
    ("main", "projectiles", ["DamageNumber", "Particle", "Pulse", "Projectile", "floating_numbers", "EvolutionGlow", "emit_hit_burst", "RingBurst", "GoldCoin"]),
    ("main", "hud", ["draw_hud", "combo_register_kill", "combo_edge_flash", "spawn_achievement_toast"]),
    ("main", "effects", ["ScreenShake", "ScreenFlash", "LowHPVignette", "draw_grid"]),
    ("main", "menu", ["MainMenu"]),
    ("main", "enemies", ["ENEMY_TYPES"]),
    ("main", "obstacles", ["generate_obstacles", "preload_obstacle_sprites"]),
    ("main", "lobby", ["MetaProgress", "LobbyScreen"]),
    ("main", "save_system", ["save_progress", "load_progress"]),
    ("main", "arcana", ["Arcana"]),
    ("main", "relics", ["RelicManager", "RELIC_DEFS"]),
    ("main", "leaderboard", ["add_score", "get_entries"]),
    ("main", "scene_manager", ["SceneManager"]),
    ("main", "scenes", ["SplashScene", "TitleScene", "GameScene", "PauseOverlay", "GameOverScene", "LobbyScene", "SettingsScene", "BestiaryScene", "CodexScene", "RunPrepScene"]),
    ("main", "char_select", ["CharSelectScene"]),
    ("main", "stage_select", ["StageSelectScene"]),
    ("menu", "config", ["WIDTH", "HEIGHT", "WHITE", "GOLD", "DARK_BG", "RED"]),
    ("menu", "player", ["CHARACTERS"]),
    ("menu", "hud", ["generate_parchment", "PARCH_INK", "PARCH_INK_DIM"]),
    ("obstacles", "config", ["MAP_WIDTH", "MAP_HEIGHT", "BIOMES", "CENTER_X", "CENTER_Y", "TILE_SIZE"]),
    ("player", "config", ["WIDTH", "HEIGHT", "WHITE", "GOLD", "DARK_BG", "MAP_WIDTH", "MAP_HEIGHT", "PLAYER_BASE_HP", "PLAYER_BASE_SPEED", "calc_speed_mult", "calc_max_hp", "calc_regen", "calc_pickup_range", "calc_damage_mult", "calc_cooldown_mult"]),
    ("projectiles", "config", ["WHITE"]),
    ("relics", "config", ["MAP_WIDTH", "MAP_HEIGHT", "WHITE", "GOLD", "RED", "BLUE", "GREEN", "PURPLE", "ICE_BLUE", "YELLOW"]),
    ("scenes", "scene_manager", ["Scene", "OverlayScene"]),
    ("scenes", "config", ["WIDTH", "HEIGHT", "WHITE", "GOLD", "DARK_BG", "RED", "GREEN"]),
]

# Lazy-loaded (inside functions) — check module can be imported at all
lazy_imports = [
    ("enemies", "sprites", ["SpriteAnimator", "ENEMY_TO_TEMPLATE"]),
    ("player", "sprites", ["SpriteAnimator", "PLAYER_TO_TEMPLATE"]),
    ("hud", "enemies", ["ENEMY_TYPES"]),
    ("hud", "config", ["MAP_WIDTH", "MAP_HEIGHT"]),
    ("lobby", "weapons", ["WEAPON_DEFS", "PASSIVE_DEFS"]),
    ("main", "sounds", ["SoundManager"]),
    ("main", "music", ["MusicManager"]),
    ("main", "cathedral", ["generate_cathedral", "get_cathedral_biome", "CATHEDRAL_COLORS"]),
    ("main", "config", ["SESSION_DURATION", "COIN_MAGNET_RANGE", "COIN_DROP_CHANCE", "COIN_VALUE", "DESPAWN_DISTANCE"]),
    ("main", "hud", ["draw_enemy_indicators", "draw_minimap", "spawn_toast"]),
    ("main", "fade_manager", ["FadeManager"]),
    ("main", "enemies", ["Enemy"]),
    ("menu", "game_over_screen", ["draw_game_over", "GameOverAnimator"]),
    ("menu", "save_system", ["list_profiles", "get_active_profile"]),
    ("scenes", "splash", ["SplashScreen"]),
    ("scenes", "leaderboard", ["get_entries"]),
    ("scenes", "save_system", ["set_active_profile", "load_progress"]),
    ("scenes", "main", []),
    ("scene_manager", "scenes", ["PauseOverlay"]),
    ("lobby", "weapons", ["WEAPON_DEFS", "PASSIVE_DEFS"]),
    ("arcana", "weapons", ["WEAPON_DEFS", "create_weapon"]),
]

errors = []
ok = 0
loaded = {}

def load_mod(name):
    if name not in loaded:
        try:
            loaded[name] = importlib.import_module(name)
        except Exception as e:
            loaded[name] = None
            errors.append(f"MODULE IMPORT FAIL: {name}.py — {e}")
    return loaded.get(name)

# Check top-level imports (these run at import time)
for importer, source, symbols in checks:
    mod = load_mod(source)
    if mod is None:
        continue
    for sym in symbols:
        if not hasattr(mod, sym):
            errors.append(f"{importer} -> {source}.{sym} NOT FOUND")
        else:
            ok += 1

# Check lazy imports (these run inside functions)
for importer, source, symbols in lazy_imports:
    mod = load_mod(source)
    if mod is None:
        continue
    for sym in symbols:
        if sym == "":
            ok += 1
            continue
        if not hasattr(mod, sym):
            errors.append(f"{importer} (lazy) -> {source}.{sym} NOT FOUND")
        else:
            ok += 1

print(f"Total symbols checked: {ok + len(errors)}")
print(f"Passed: {ok}")
print(f"Failed: {len(errors)}")
if errors:
    print("\n=== BROKEN IMPORTS ===")
    for e in sorted(errors):
        print(f"  ❌ {e}")
else:
    print("\n✅ All cross-module imports verified, zero broken symbols.")

# Also check for circular import issues
print("\n=== Circular import test ===")
try:
    import main
    print("✅ main.py imports without circular errors")
except Exception as e:
    print(f"❌ main.py circular import: {e}")
