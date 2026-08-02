"""
Рождение святого - Main Game Loop
Точка входа. Game loop: input → update → render.
"""
import asyncio
import sys
import traceback
import pygame
from config import WIDTH, HEIGHT, FPS, TITLE, MAP_WIDTH, MAP_HEIGHT, calc_xp_for_level, RUNE_DEFS, RUNE_TYPES, ACHIEVEMENTS
from game_logger import init_logger, get_logger, close_logger
from player import Player, CHARACTERS
from camera import Camera
from wave_manager import WaveManager
from xp_system import XPGem, LevelUpScreen
from weapons import create_weapon
from projectiles import Pulse, Projectile, floating_numbers, EvolutionGlow, emit_hit_burst, RingBurst, GoldCoin
from hud import draw_hud, combo_register_kill, combo_edge_flash, spawn_achievement_toast
from effects import ScreenShake, ScreenFlash, LowHPVignette, draw_grid


def _hit_direction(from_pos, to_pos):
    """Compute normalized direction vector from from_pos to to_pos.
    Returns pygame.Vector2 or None if positions overlap."""
    d = to_pos - from_pos
    if d.length_squared() > 0:
        return d.normalize()
    return None
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
from char_select import CharSelectScene
from stage_select import StageSelectScene

# Глобальные объекты
screen = None
clock = None
font = None
small_font = None
big_font = None
sound_mgr = None
shake = ScreenShake()
flash = ScreenFlash()
vignette = LowHPVignette()


class RunePickup:
    """Руна на земле — подбирается игроком, вставляется в оружие."""
    def __init__(self, x: float, y: float, rune_type: str):
        self.pos = pygame.Vector2(x, y)
        self.rune_type = rune_type
        self.alive = True
        self.attracting = False
        self.timer = 0.0  # for pulsing animation
        rdef = RUNE_DEFS[rune_type]
        self.color = rdef["color"]
        self.name = rdef["name"]
        self.radius = 8

    def update(self, player_pos: pygame.Vector2, pickup_range: float, dt: float):
        self.timer += dt
        dist = (self.pos - player_pos).length()
        if dist < pickup_range * 1.5:  # runes have 1.5x pickup range
            self.attracting = True
        if self.attracting:
            d = player_pos - self.pos
            if d.length() > 0:
                self.pos += d.normalize() * 10 * 60 * dt  # faster attraction
            if dist < 15:
                self.alive = False
                return self.rune_type
        return None

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float):
        sx = int(self.pos.x - cam_x)
        sy = int(self.pos.y - cam_y)
        if sx < -20 or sx > 1044 or sy < -20 or sy > 788:
            return
        import math
        # Pulsing glow
        pulse = 0.6 + 0.4 * math.sin(self.timer * 4.0)
        r, g, b = self.color
        alpha = int(80 * pulse)
        glow = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(glow, (r, g, b, alpha), (16, 16), 16)
        surface.blit(glow, (sx - 16, sy - 16))
        # Diamond shape
        size = int(self.radius * (0.9 + 0.1 * pulse))
        pygame.draw.polygon(surface, self.color, [
            (sx, sy - size), (sx + size, sy),
            (sx, sy + size), (sx - size, sy)
        ])
        pygame.draw.polygon(surface, (255, 255, 255), [
            (sx, sy - size // 2), (sx + size // 2, sy),
            (sx, sy + size // 2), (sx - size // 2, sy)
        ])


def init_pygame():
    global screen, clock, font, small_font, big_font
    pygame.init()
    # На emscripten (pygbag WASM) canvas уже создан шаблоном фиксированного
    # размера (1280x720). pygame.SCALED позволяет SDL2 смасштабировать наш
    # виртуальный framebuffer (WIDTH x HEIGHT) под реальный canvas - без этого
    # флага на WASM часто получается пустой/серый экран.
    if sys.platform == "emscripten":
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=0)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Шрифты (pygame default)
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    big_font = pygame.font.Font(None, 56)


def init_sounds():
    global sound_mgr
    try:
        from sounds import SoundManager
        sound_mgr = SoundManager()
        import sound_manager
        sound_manager.init(sound_mgr)
    except Exception:
        sound_mgr = None
    
    # Инициализация музыки
    try:
        from music import MusicManager
        music_mgr = MusicManager()
        music_mgr.init()
    except Exception:
        pass


class Game:
    """Основной игровой объект. Управляет игровым процессом."""
    def __init__(self):
        self.state = "menu"  # "menu", "playing", "levelup", "gameover", "lobby"
        self.menu = MainMenu()
        self.meta = MetaProgress()
        load_progress(self.meta)  # загрузить сохранённый прогресс
        self.lobby = LobbyScreen()
        self.player = None
        self.camera = Camera()
        self.wave_mgr = WaveManager()
        self.levelup_screen = LevelUpScreen()
        self.enemies = []
        self.projectiles = []
        self.gems = []
        self.particles = []
        self.pulses = []
        self.evolution_glows = []
        self.ring_bursts = []
        self.obstacles = []
        self.rune_pickups = []  # C3: Rune pickups from bosses
        self.gold_coins = []  # REF-8: Gold coin pickups
        self.elapsed = 0.0
        self._reaper_spawned = False
        self._slowmo_frames = 0
        self._ach_check_timer = 0.0  # REF-9: periodic achievement check
        self.relic_mgr = RelicManager()
        self.relics = []
        self.arcana_data = {}

    def start_game(self, char_id: str):
        """Начинает новую игру."""
        self.state = "playing"
        self.player = Player(char_id, MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.camera = Camera()
        self.wave_mgr = WaveManager()
        self.levelup_screen = LevelUpScreen()
        self.enemies = []
        self.projectiles = []
        self.gems = []
        self.particles = []
        self.pulses = []
        self.evolution_glows = []
        self.ring_bursts = []
        self.rune_pickups = []  # C3: Rune pickups
        self.gold_coins = []  # REF-8: Gold coin pickups
        self.elapsed = 0.0
        self._reaper_spawned = False
        self._slowmo_frames = 0
        self._ach_check_timer = 0.0  # REF-9: periodic achievement check
        self.relic_mgr.reset()
        self.relics = []
        # Стартовое оружие
        start_weapon_id = CHARACTERS[char_id]["start_weapon"]
        self.player.weapons.append(create_weapon(start_weapon_id))

        # Применить бонусы мета-прогресса
        self.player.base_speed *= self.meta.get_powerup_bonus("swiftness")
        self.player.speed = self.player.base_speed
        self.player.max_hp = int(self.player.max_hp * self.meta.get_powerup_bonus("sturdiness"))
        self.player.hp = self.player.max_hp

        # Применить аркану (если выбрана)
        self.arcana_data = {}
        if self.meta.selected_arcana:
            arcana = Arcana.create(self.meta.selected_arcana)
            if arcana:
                arcana.apply(self, self.meta)

        # Препятствия (карта)
        self.current_map = self.menu.selected_map
        if self.current_map == "cathedral":
            from cathedral import generate_cathedral
            self.obstacles = generate_cathedral()
        else:
            self.obstacles = generate_obstacles(25)
        preload_obstacle_sprites()
        self._reaper_spawned = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == "menu":
                result = self.menu.handle_event(event)
                if result == "start":
                    self.start_game(self.menu.selected_char)
                elif result == "restart":
                    self.start_game(self.menu.selected_char)
                elif result == "menu":
                    self.state = "menu"

            elif self.state == "levelup":
                done = self.levelup_screen.handle_event(event, self.player)
                if done:
                    self.state = "playing"

            elif self.state == "gameover":
                result = self.menu.handle_event(event)
                if result == "restart":
                    self.start_game(self.menu.selected_char)
                elif result == "menu":
                    # Переход в лобби вместо меню
                    self.lobby.activate(self.meta)
                    self.state = "lobby"

            elif self.state == "lobby":
                result = self.lobby.handle_event(event)
                if result == "play":
                    self.start_game(self.menu.selected_char)

        return True

    def update(self, dt: float):
        self._last_dt = dt
        if self.state == "lobby":
            self.lobby.update(dt)
            return
        if self.state != "playing":
            return

        self.elapsed += dt

        # A4: Slowmo from combo — 25% speed for N frames
        if self._slowmo_frames > 0:
            dt *= 0.25
            self._slowmo_frames -= 1

        # 1. Игрок
        self.player.handle_input(dt)

        # 1.5 Коллизия игрока с препятствиями
        for obs in self.obstacles:
            if obs.collides_with(self.player.pos, self.player.radius):
                # Выталкиваем игрока
                d = self.player.pos - obs.pos
                if d.length() > 0:
                    d = d.normalize()
                    self.player.pos = obs.pos + d * (obs.radius + self.player.radius + 1)

        self.camera.update(self.player.pos.x, self.player.pos.y)

        # 2. Волны
        new_enemies = self.wave_mgr.update(
            dt, len(self.enemies),
            self.camera.cam_x, self.camera.cam_y,
            self.player.pos
        )
        self.enemies.extend(new_enemies)

        # Обновить boss_alive
        boss_alive = any(e.is_boss and e.alive for e in self.enemies)
        self.wave_mgr.boss_alive = boss_alive

        # 2.5 Жнец на 15 минуте
        from config import SESSION_DURATION
        if self.elapsed >= SESSION_DURATION and not self._reaper_spawned:
            self._reaper_spawned = True
            # Жнец - неубиваемый босс
            from enemies import Enemy
            reaper = Enemy("antichrist", self.player.pos.x, self.player.pos.y - 500, 99)
            reaper.hp = 999999
            reaper.max_hp = 999999
            reaper.damage = 9999
            reaper.speed = 2.0
            reaper.radius = 50
            reaper.color = (50, 50, 50)
            reaper.blood_color = (100, 100, 100)
            self.enemies.append(reaper)
            shake.trigger(0.5, _hit_direction(self.player.pos, reaper.pos))

        # 3. Оружие
        pulses_before = len(self.pulses)
        for w in self.player.weapons:
            w.update(self.player, self.enemies, self.projectiles,
                     self.pulses, self.particles, dt)

        # Screen shake + attack animation при атаках оружия
        if len(self.pulses) > pulses_before:
            # Attack animation на игроке
            self.player.animator.start_attack()

            last_pulse = self.pulses[-1]
            pulse_type = type(last_pulse).__name__
            if pulse_type == "WhipSweep":
                shake.trigger(0.05)
            elif pulse_type == "LightningBolt":
                shake.trigger(0.12)
            elif pulse_type == "RingWave":
                shake.trigger(0.1)

        # 4. Враги
        enemy_speed_mult = self.arcana_data.get("enemy_speed_mult", 1.0)
        for e in self.enemies:
            if not e.alive:
                continue
            # Аркана: Ярость орды - ускорение врагов
            shot = None
            if enemy_speed_mult != 1.0:
                orig_speed = e.speed
                e.speed *= enemy_speed_mult
                shot = e.update(self.player.pos, dt)
                e.speed = orig_speed
            else:
                shot = e.update(self.player.pos, dt)

            # Demon/Cultist ranged attack → Projectile
            if shot:
                self.projectiles.append(Projectile(
                    shot["x"], shot["y"], shot["vx"], shot["vy"],
                    damage=shot["damage"], radius=6, lifetime=2.0,
                    pierce=0, color=shot["color"], from_enemy=True,
                ))

            # Коллизия враг → игрок
            dx = e.pos.x - self.player.pos.x
            dy = e.pos.y - self.player.pos.y
            dist_sq = dx * dx + dy * dy
            min_dist = e.radius + self.player.radius
            if dist_sq < min_dist * min_dist:
                if e.damage > 0:
                    self.player.take_damage(e.damage)
                    if sound_mgr:
                        sound_mgr.play("player_hit")
                    flash.trigger()
                    shake.trigger(0.08, _hit_direction(self.player.pos, e.pos))

                # Fanatic explode
                if e.explode_radius > 0 and e.explode_damage > 0:
                    self.player.take_damage(e.explode_damage)
                    e.alive = False
                    shake.trigger(0.25, _hit_direction(self.player.pos, e.pos))

        # 5. Снаряды
        for p in self.projectiles:
            if not p.alive:
                continue
            p.update(dt)

            # Коллизия снаряд → враг (только снаряды игрока)
            if not p.from_enemy:
                for e in self.enemies:
                    if not e.alive or id(e) in p.hit_set:
                        continue
                    dx = e.pos.x - p.pos.x
                    dy = e.pos.y - p.pos.y
                    if dx * dx + dy * dy < (p.radius + e.radius) ** 2:
                        killed = e.take_damage(p.damage)
                        p.hit_set.add(id(e))

                        floating_numbers.spawn_damage(
                            e.pos.x, e.pos.y, p.damage, p.color)
                        # A3: Tiered hit particles
                        hit_tier = "heavy" if e.is_boss else "medium" if e.radius >= 22 else "light"
                        emit_hit_burst(self.particles, e.pos.x, e.pos.y,
                                       hit_tier, p.color,
                                       hit_dir=_hit_direction(p.pos, e.pos))

                        # Hitstop on projectile hit (light: 3 frames)
                        e.freeze_frames = 3

                        if killed:
                            e._on_killed_called = True
                            # A3: Kill = crit burst + ring
                            emit_hit_burst(self.particles, e.pos.x, e.pos.y,
                                           "crit", (255, 220, 100))
                            self.ring_bursts.append(
                                RingBurst(e.pos.x, e.pos.y,
                                          radius=45, color=e.blood_color))
                            self.on_enemy_killed(e)

                        if p.pierce <= 0:
                            p.alive = False
                            # Explosive
                            if p.explosive:
                                # Визуал взрыва
                                self.pulses.append(Pulse(p.pos.x, p.pos.y, p.explode_r, p.color, duration=0.3))
                                # A3: Explosive = medium burst
                                emit_hit_burst(self.particles, p.pos.x, p.pos.y,
                                               "medium", p.color)
                                for e2 in self.enemies:
                                    if not e2.alive or e2 is e:
                                        continue
                                    dx2 = e2.pos.x - p.pos.x
                                    dy2 = e2.pos.y - p.pos.y
                                    if dx2 * dx2 + dy2 * dy2 < (p.explode_r + e2.radius) ** 2:
                                        e2.take_damage(p.explode_dmg)
                                        floating_numbers.spawn_damage(
                                            e2.pos.x, e2.pos.y, p.explode_dmg, p.color)
                                        e2.freeze_frames = 3  # hitstop on explosion
                            break
                        else:
                            p.pierce -= 1

            # Коллизия вражеский снаряд → игрок
            if p.from_enemy and p.alive:
                dx = self.player.pos.x - p.pos.x
                dy = self.player.pos.y - p.pos.y
                if dx * dx + dy * dy < (p.radius + self.player.radius) ** 2:
                    self.player.take_damage(p.damage)
                    p.alive = False
                    if sound_mgr:
                        sound_mgr.play("player_hit")
                    flash.trigger()
                    shake.trigger(0.08, _hit_direction(self.player.pos, p.pos))
                    floating_numbers.spawn_damage(
                        self.player.pos.x, self.player.pos.y, p.damage, p.color)

        # 6. XP-гемы
        for gem in self.gems:
            if not gem.alive:
                continue
            xp = gem.update(self.player.pos, self.player.pickup_range, dt)
            if xp > 0:
                # Бонус Пилигрима: +30% XP
                if self.player.char_bonus == "xp_bonus":
                    xp = int(xp * 1.3)
                # Аркана: Двойная угроза +50% XP
                xp_mult = self.arcana_data.get("xp_mult", 1.0)
                if xp_mult != 1.0:
                    xp = int(xp * xp_mult)
                self.player.add_xp(xp)
                if sound_mgr:
                    sound_mgr.play("gem_pickup")
                self.check_levelup()

        # 6.5 Реликвии - спавн + обновление + подбор
        new_relic = self.relic_mgr.update(dt, len([r for r in self.relics if r.alive]), self.player.pos)
        if new_relic:
            self.relics.append(new_relic)
        for relic in self.relics:
            if not relic.alive:
                continue
            relic.update(self.player.pos, dt)
            if relic.collected:
                relic_id = relic.relic_id
                bonuses = RELIC_DEFS[relic_id]["bonuses"]
                self.player.apply_relic(relic_id, bonuses)
                if sound_mgr:
                    sound_mgr.play("gem_pickup")
        self.relics = [r for r in self.relics if r.alive]

        # 6.6 C3: Rune pickups — подбор + вставка в оружие
        for rp in self.rune_pickups:
            if not rp.alive:
                continue
            rune_type = rp.update(self.player.pos, self.player.pickup_range, dt)
            if rune_type:
                # Auto-socket into first weapon with empty slot
                socketed = False
                for w in self.player.weapons:
                    if w.socket_rune(rune_type):
                        socketed = True
                        from hud import spawn_toast
                        spawn_toast(f"{RUNE_DEFS[rune_type]['name']} -> {w.name}", RUNE_DEFS[rune_type]["color"])
                        if sound_mgr:
                            sound_mgr.play("gem_pickup")
                        break
                if not socketed:
                    from hud import spawn_toast
                    spawn_toast("Все слоты рун заполнены!", (150, 150, 150))
                    if sound_mgr:
                        sound_mgr.play("ui_back")
        self.rune_pickups = [rp for rp in self.rune_pickups if rp.alive]

        # 6.7 REF-8: Gold coin pickups
        from config import COIN_MAGNET_RANGE
        for coin in self.gold_coins:
            if not coin.alive:
                continue
            collected = coin.update(self.player.pos, COIN_MAGNET_RANGE, dt)
            if collected > 0:
                gold_gain = int(collected * self.player.gold_mult)
                self.player.gold += gold_gain
                floating_numbers.spawn_xp(coin.pos.x, coin.pos.y, gold_gain)
                if sound_mgr:
                    sound_mgr.play("gem_pickup")
        self.gold_coins = [c for c in self.gold_coins if c.alive]

        # 7. Убитые враги → гемы
        dead_enemies = [e for e in self.enemies if not e.alive]
        for e in dead_enemies:
            # Melee kills: on_enemy_killed для эволюции боссов
            if not getattr(e, '_on_killed_called', False):
                self.on_enemy_killed(e)
            if not hasattr(e, '_gem_dropped'):
                e._gem_dropped = True
                self.gems.append(XPGem(e.pos.x, e.pos.y, e.xp))
                self.player.kills += 1
                # REF-8: Replace auto-gold with physical coin drops
                import random as _r
                from config import COIN_DROP_CHANCE, COIN_VALUE
                drop_chance = COIN_DROP_CHANCE * self.meta.get_powerup_bonus("greed")
                if e.is_boss:
                    # Boss = coin rain (5-10 coins)
                    for _ in range(_r.randint(5, 10)):
                        ox = _r.uniform(-40, 40)
                        oy = _r.uniform(-40, 40)
                        self.gold_coins.append(
                            GoldCoin(e.pos.x + ox, e.pos.y + oy, value=COIN_VALUE * _r.randint(3, 8)))
                elif _r.random() < drop_chance:
                    self.gold_coins.append(
                        GoldCoin(e.pos.x, e.pos.y, value=COIN_VALUE))

                # C2: Per-type kill tracking for codex
                etype = getattr(e, 'type_id', None)
                if etype:
                    self.meta.enemy_kills[etype] = self.meta.enemy_kills.get(etype, 0) + 1

                # A4: Combo counter — register kill, apply juice
                juice = combo_register_kill()
                if juice["slowmo"] > 0:
                    self._slowmo_frames = juice["slowmo"]
                if juice.get("label") == "MASSACRE":
                    flash.trigger(color=(255, 255, 255), duration=0.3)

                # A3: Death particles — melee kills only
                blood_color = getattr(e, 'blood_color', (200, 50, 50))
                if not getattr(e, '_on_killed_called', False):
                    emit_hit_burst(self.particles, e.pos.x, e.pos.y,
                                   "crit", (255, 220, 100))
                    self.ring_bursts.append(
                        RingBurst(e.pos.x, e.pos.y,
                                  radius=45, color=blood_color))

        # Очистка + деспавн далёких врагов
        from config import DESPAWN_DISTANCE
        for e in self.enemies:
            if e.alive and not e.is_boss:
                dist = (e.pos - self.player.pos).length()
                if dist > DESPAWN_DISTANCE:
                    e.alive = False

        # Death fade: умершие враги сначала затухают, потом удаляются
        for e in self.enemies:
            if not e.alive and e.death_fade <= 0:
                e.death_fade = 0.4  # 0.4 секунды fade
            if e.death_fade > 0:
                e.death_fade -= dt

        # Удаляем полностью затухших + далеко деспавненных
        self.enemies = [e for e in self.enemies if e.alive or e.death_fade > 0]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.gems = [g for g in self.gems if g.alive]
        floating_numbers.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        self.pulses = [p for p in self.pulses if p.alive]
        self.evolution_glows = [g for g in self.evolution_glows if g.alive]
        self.ring_bursts = [r for r in self.ring_bursts if r.alive]

        # 8. Эффекты
        shake.update(dt)
        flash.update(dt)
        vignette.update(self.player.hp / max(1, self.player.max_hp), dt)
        for p in self.particles:
            p.update(dt)
        for p in self.pulses:
            p.update(dt)
        for g in self.evolution_glows:
            g.update(dt, self.player.pos)
        for r in self.ring_bursts:
            r.update(dt)

        # 8.5 REF-9: Periodic achievement check during gameplay
        self._ach_check_timer += dt
        if self._ach_check_timer >= 2.0:
            self._ach_check_timer = 0.0
            boss_killed = any(not e.alive and e.is_boss for e in self.enemies)
            new_unlocks = self.meta.check_achievements(
                self.elapsed, self.wave_mgr.wave,
                self.player.kills, self.meta.gold,
                boss_killed=boss_killed
            )
            for aid, reward in new_unlocks:
                adef = ACHIEVEMENTS.get(aid, {})
                ach_name = adef.get("name", aid)
                ach_desc = adef.get("desc", "")
                spawn_achievement_toast(ach_name, ach_desc, duration=3.0)

        # 9. Смерть игрока
        if not self.player.alive:
            self.state = "gameover"
            self.menu.state = "game_over"
            self.menu.final_stats = {
                "wave": self.wave_mgr.wave,
                "time": int(self.elapsed),
                "kills": self.player.kills,
                "level": self.player.level,
                "gold": self.player.gold,
            }

            # Обновить мета-прогресс
            self.meta.gold += self.player.gold
            self.meta.total_runs += 1
            self.meta.total_kills += self.player.kills
            if self.wave_mgr.wave > self.meta.best_wave:
                self.meta.best_wave = self.wave_mgr.wave
            if int(self.elapsed) > self.meta.best_time:
                self.meta.best_time = int(self.elapsed)

            # Проверить достижения (финальный шанс на разблокировку)
            boss_killed = any(not e.alive and e.is_boss for e in self.enemies)
            final_unlocks = self.meta.check_achievements(
                self.elapsed, self.wave_mgr.wave,
                self.player.kills, self.meta.gold,
                boss_killed=boss_killed
            )
            for aid, reward in final_unlocks:
                adef = ACHIEVEMENTS.get(aid, {})
                spawn_achievement_toast(adef.get("name", aid), adef.get("desc", ""), 3.0)

            # Сохранить прогресс
            save_progress(self.meta)

            # Лидерборд
            map_name = getattr(self, 'current_map', 'arena')
            char_name = CHARACTERS.get(self.player.char_id, {}).get('name', self.player.char_id)
            self.leaderboard_rank = add_score(
                char_name, self.wave_mgr.wave,
                self.player.kills, self.player.gold,
                self.elapsed, map_name
            )
            self.leaderboard_entries = get_entries()
            self.menu.leaderboard_rank = self.leaderboard_rank
            self.menu.leaderboard_entries = self.leaderboard_entries

            if sound_mgr:
                sound_mgr.play("game_over")

    def on_enemy_killed(self, enemy):
        if sound_mgr:
            sound_mgr.play("kill")
        # C3: Boss drops rune on death
        if enemy.is_boss and not getattr(enemy, '_rune_dropped', False):
            enemy._rune_dropped = True
            import random
            rune_type = random.choice(RUNE_TYPES)
            self.rune_pickups.append(RunePickup(enemy.pos.x, enemy.pos.y, rune_type))
        # Проверка эволюции оружия при убийстве босса (сундук)
        if enemy.is_boss:
            for w in self.player.weapons:
                if w.can_evolve(self.player):
                    w.evolve()
                    shake.trigger(0.4)
                    # Evolution glow - пульсирующая аура
                    self.evolution_glows.append(
                        EvolutionGlow(self.player.pos.x, self.player.pos.y)
                    )
                    if sound_mgr:
                        sound_mgr.play("levelup")

    def check_levelup(self):
        while self.player.xp >= self.player.xp_to_next:
            self.player.xp -= self.player.xp_to_next
            self.player.level += 1
            self.player.xp_to_next = calc_xp_for_level(self.player.level)

            # Бонусные XP на уровнях 20 и 40
            if self.player.level == 20:
                self.player.xp_to_next += 600
            elif self.player.level == 40:
                self.player.xp_to_next += 2400

            self.levelup_screen.activate(self.player, self.meta.banned_items)
            self.state = "levelup"

            # Level up burst — кольцо частиц (A3: crit tier)
            emit_hit_burst(self.particles, self.player.pos.x, self.player.pos.y,
                           "crit", (255, 220, 100))
            self.ring_bursts.append(
                RingBurst(self.player.pos.x, self.player.pos.y,
                          radius=80, color=(255, 220, 100), duration=0.4))
            self.pulses.append(Pulse(self.player.pos.x, self.player.pos.y,
                                     80, (255, 220, 100), duration=0.4))
            if sound_mgr:
                sound_mgr.play("levelup")

    def render(self):
        if self.state == "menu":
            self.menu.draw(screen, font, big_font, small_font)
            return

        if self.state == "lobby":
            self.lobby.draw(screen, font, big_font, small_font)
            return

        cam_x = self.camera.cam_x + shake.offset_x
        cam_y = self.camera.cam_y + shake.offset_y

        # Фон (сетка)
        if hasattr(self, 'current_map') and self.current_map == "cathedral":
            from cathedral import get_cathedral_biome, CATHEDRAL_COLORS
            biome = get_cathedral_biome(self.player.pos.x, self.player.pos.y)
            screen.fill(biome["bg"])
            # Рисуем сетку собора
            cam_x2 = cam_x
            cam_y2 = cam_y
            start_col = int(cam_x2 // 64)
            start_row = int(cam_y2 // 64)
            for col in range(start_col, start_col + 17):
                x = int(col * 64 - cam_x2)
                pygame.draw.line(screen, biome["grid"], (x, 0), (x, HEIGHT))
            for row in range(start_row, start_row + 13):
                y = int(row * 64 - cam_y2)
                pygame.draw.line(screen, biome["grid"], (0, y), (WIDTH, y))
        else:
            draw_grid(screen, cam_x, cam_y, self.player.pos.x, self.player.pos.y)

        # Пульсы (AoE)
        for p in self.pulses:
            p.draw(screen, cam_x, cam_y)

        # Evolution glow (поверх пульсов, под препятствиями)
        for g in self.evolution_glows:
            g.draw(screen, cam_x, cam_y)

        # Препятствия
        for obs in self.obstacles:
            obs.draw(screen, cam_x, cam_y)

        # XP-гемы
        for g in self.gems:
            g.draw(screen, cam_x, cam_y)

        # REF-8: Gold coins
        for c in self.gold_coins:
            c.draw(screen, cam_x, cam_y)

        # Реликвии
        for r in self.relics:
            r.draw(screen, cam_x, cam_y)

        # Враги
        for e in self.enemies:
            e.draw(screen, cam_x, cam_y, font)

        # Снаряды
        for p in self.projectiles:
            p.draw(screen, cam_x, cam_y)

        # Игрок
        self.player.draw(screen, cam_x, cam_y)

        # Оружие (Halo, Rosary, Incense — орбитальное/бумеранги)
        for w in self.player.weapons:
            if hasattr(w, 'draw'):
                w.draw(screen, cam_x, cam_y, self.player)

        # Частицы
        for p in self.particles:
            p.draw(screen, cam_x, cam_y)

        # A3: Ring bursts (on top of particles)
        for r in self.ring_bursts:
            r.draw(screen, cam_x, cam_y)

        # Damage numbers (floating manager)
        floating_numbers.draw(screen, cam_x, cam_y, small_font)

        # HUD
        draw_hud(screen, self.player, self.wave_mgr.wave, self.elapsed, font, small_font, self.enemies)

        # Enemy direction indicators
        from hud import draw_enemy_indicators, draw_minimap
        draw_enemy_indicators(screen, self.player, self.enemies, cam_x, cam_y)

        # Minimap
        draw_minimap(screen, self.player, self.enemies, cam_x, cam_y)

        # LevelUpScreen
        if self.state == "levelup":
            self.levelup_screen.draw(screen, font, small_font)

        # Game Over
        if self.state == "gameover":
            self.menu.draw(screen, font, big_font, small_font)

        # Screen flash
        flash.draw(screen)

        # Low HP vignette
        vignette.draw(screen)

        # A4: Combo edge flash overlay
        combo_edge_flash(screen)


def _render_error_screen(err_text: str):
    """Рисует traceback прямо на canvas (диагностика WASM без консоли браузера)."""
    global screen
    if screen is None:
        return
    import traceback as _tb
    screen.fill((20, 0, 0))
    lines = ("FATAL ERROR\n\n" + err_text).splitlines()
    err_font = pygame.font.Font(None, 20)
    y = 20
    for line in lines:
        for chunk in (line[i:i + 90] for i in range(0, len(line), 90)):
            try:
                surf = err_font.render(chunk, True, (255, 80, 80))
            except Exception:
                surf = err_font.render(repr(chunk), True, (255, 80, 80))
            screen.blit(surf, (20, y))
            y += 22
            if y > HEIGHT - 30:
                return
        y += 2


async def main():
    """Главная async-функция (для pygbag)."""
    global screen

    # Инициализируем логгер сессии
    logger = init_logger()

    try:
        init_pygame()
        init_sounds()
    except Exception as e:
        if logger:
            logger.log_error(e, {"stage": "init"})
        # На WASM выводим ошибку в консоль pygbag
        print(f"INIT ERROR: {e}")
        traceback.print_exc()
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        _render_error_screen(f"INIT ERROR:\n{traceback.format_exc()}")
        pygame.display.flip()
        while True:
            pygame.event.pump()
            await asyncio.sleep(0.1)
        return

    try:
        game = Game()
        # Создаём SceneManager и регистрируем сцены
        scene_mgr = SceneManager()
        # Fade transitions
        from fade_manager import FadeManager
        scene_mgr.fade = FadeManager()
        scene_mgr.register("splash", SplashScene())
        scene_mgr.register("title", TitleScene(game.menu, game.meta, game.lobby))
        scene_mgr.register("game", GameScene(game))
        scene_mgr.register("game_over", GameOverScene(game.menu, game.meta, game.lobby, game=game))
        scene_mgr.register("lobby", LobbyScene(game.lobby, game.meta, game.menu))
        scene_mgr.register("settings", SettingsScene())
        scene_mgr.register("bestiary", BestiaryScene(game.meta, game.lobby))
        scene_mgr.register("codex", CodexScene(game.meta, game.lobby))
        scene_mgr.register("run_prep", RunPrepScene())
        scene_mgr.register("char_select", CharSelectScene())
        scene_mgr.register("stage_select", StageSelectScene())
        scene_mgr.switch("splash")
    except Exception:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        _render_error_screen(tb)
        pygame.display.flip()
        try:
            while True:
                pygame.event.pump()
                await asyncio.sleep(0.1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        return

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)
        current_fps = 1.0 / max(dt, 0.001)

        # Логгер: FPS tick
        if logger:
            scene_name = getattr(scene_mgr, 'current', None) or 'unknown'
            logger.tick(current_fps, dt, scene_name)

        try:
            events = pygame.event.get()
            scene_before = getattr(scene_mgr, 'current', 'unknown')

            # Логгер: записываем каждый клик/нажатие
            if logger:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        logger.log_input(
                            "mouse_click", str(event.button),
                            scene_before, pos=list(event.pos))
                    elif event.type == pygame.KEYDOWN:
                        logger.log_input(
                            "key_press", pygame.key.name(event.key),
                            scene_before)

            result = scene_mgr.handle_events(events)
            running = result  # scene_mgr returns False to quit

            # Логгер: что произошло после обработки событий
            scene_after = getattr(scene_mgr, 'current', 'unknown')
            if logger and scene_before != scene_after:
                logger.log_transition(scene_before, scene_after, "event_handler")
            
            # Обработка специальных переходов из GameScene
            game_scene = scene_mgr.scenes.get("game")
            if game_scene and game_scene.done:
                stats = {
                    "wave": game.wave_mgr.wave,
                    "time": int(game.elapsed),
                    "kills": game.player.kills if game.player else 0,
                    "level": game.player.level if game.player else 1,
                    "gold": game.player.gold if game.player else 0,
                }
                # Логгер: снимок состояния при смерти
                if logger:
                    logger.log_transition("game", "game_over", "death")
                    logger.log_state_snapshot(
                        player_hp=0,
                        player_max_hp=game.player.max_hp if game.player else 0,
                        player_level=stats["level"],
                        kills=stats["kills"],
                        wave=stats["wave"],
                        elapsed_time=stats["time"],
                        gold=stats["gold"],
                    )
                scene_mgr.switch("game_over", stats=stats)
                game_scene.done = False
            
            # Обработка перехода из SplashScene
            splash_scene = scene_mgr.scenes.get("splash")
            if splash_scene and splash_scene.done:
                if logger:
                    logger.log_transition("splash", "title", "fade_complete")
                scene_mgr.switch("title")
                splash_scene.done = False
            
            scene_mgr.update(dt)
            if screen:
                scene_mgr.draw(screen)
        except Exception as e:
            # Логгер: записываем ошибку с контекстом
            if logger:
                logger.log_error(e, {
                    "scene": scene_mgr.current if hasattr(scene_mgr, 'current') else 'unknown',
                    "dt": dt,
                    "fps": current_fps,
                })
            tb = traceback.format_exc()
            print(tb, file=sys.stderr)
            _render_error_screen(tb)
            pygame.display.flip()
            try:
                while True:
                    pygame.event.pump()
                    await asyncio.sleep(0.1)
            except (KeyboardInterrupt, asyncio.CancelledError):
                pass
            return

        pygame.display.flip()
        await asyncio.sleep(0)

    # Логгер: нормальное завершение
    if logger:
        close_logger("normal")
    scene_mgr.dump_log("logs/scene_flow.json")
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
