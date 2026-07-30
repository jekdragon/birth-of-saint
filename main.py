"""
Рождение святого — Main Game Loop
Точка входа. Game loop: input → update → render.
"""
import asyncio
import sys
import pygame
from config import WIDTH, HEIGHT, FPS, TITLE, MAP_WIDTH, MAP_HEIGHT, calc_xp_for_level
from player import Player, CHARACTERS
from camera import Camera
from wave_manager import WaveManager
from xp_system import XPGem, LevelUpScreen
from weapons import create_weapon
from projectiles import DamageNumber, Particle, Pulse
from hud import draw_hud
from effects import ScreenShake, ScreenFlash, draw_grid
from menu import MainMenu
from enemies import ENEMY_TYPES
from obstacles import generate_obstacles
from lobby import MetaProgress, LobbyScreen
from save_system import save_progress, load_progress
from arcana import Arcana
from relics import RelicManager, RELIC_DEFS
from leaderboard import add_score, get_entries

# Глобальные объекты
screen = None
clock = None
font = None
small_font = None
big_font = None
sound_mgr = None
shake = ScreenShake()
flash = ScreenFlash()


def init_pygame():
    global screen, clock, font, small_font, big_font
    pygame.init()
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
        self.damage_numbers = []
        self.particles = []
        self.pulses = []
        self.obstacles = []
        self.elapsed = 0.0
        self._reaper_spawned = False
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
        self.damage_numbers = []
        self.particles = []
        self.pulses = []
        self.elapsed = 0.0
        self._reaper_spawned = False
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
            # Жнец — неубиваемый босс
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
            shake.trigger(15, 0.5)

        # 3. Оружие
        for w in self.player.weapons:
            w.update(self.player, self.enemies, self.projectiles,
                     self.pulses, self.particles, self.damage_numbers, dt)

        # 4. Враги
        enemy_speed_mult = self.arcana_data.get("enemy_speed_mult", 1.0)
        for e in self.enemies:
            if not e.alive:
                continue
            # Аркана: Ярость орды — ускорение врагов
            if enemy_speed_mult != 1.0:
                orig_speed = e.speed
                e.speed *= enemy_speed_mult
                e.update(self.player.pos, dt)
                e.speed = orig_speed
            else:
                e.update(self.player.pos, dt)

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
                    shake.trigger(4, 0.1)

                # Fanatic explode
                if e.explode_radius > 0 and e.explode_damage > 0:
                    self.player.take_damage(e.explode_damage)
                    e.alive = False
                    shake.trigger(8, 0.2)

        # 5. Снаряды
        for p in self.projectiles:
            if not p.alive:
                continue
            p.update(dt)

            # Коллизия снаряд → враг
            for e in self.enemies:
                if not e.alive or id(e) in p.hit_set:
                    continue
                dx = e.pos.x - p.pos.x
                dy = e.pos.y - p.pos.y
                if dx * dx + dy * dy < (p.radius + e.radius) ** 2:
                    killed = e.take_damage(p.damage)
                    p.hit_set.add(id(e))

                    self.damage_numbers.append(
                        DamageNumber(e.pos.x, e.pos.y, p.damage, p.color))
                    for _ in range(3):
                        self.particles.append(Particle(e.pos.x, e.pos.y, p.color))

                    if killed:
                        self.on_enemy_killed(e)

                    if p.pierce <= 0:
                        p.alive = False
                        # Explosive
                        if p.explosive:
                            for e2 in self.enemies:
                                if not e2.alive or e2 is e:
                                    continue
                                dx2 = e2.pos.x - p.pos.x
                                dy2 = e2.pos.y - p.pos.y
                                if dx2 * dx2 + dy2 * dy2 < (p.explode_r + e2.radius) ** 2:
                                    e2.take_damage(p.explode_dmg)
                                    self.damage_numbers.append(
                                        DamageNumber(e2.pos.x, e2.pos.y, p.explode_dmg, p.color))
                        break
                    else:
                        p.pierce -= 1

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

        # 6.5 Реликвии — спавн + обновление + подбор
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

        # 7. Убитые враги → гемы
        dead_enemies = [e for e in self.enemies if not e.alive]
        for e in dead_enemies:
            if not hasattr(e, '_gem_dropped'):
                e._gem_dropped = True
                self.gems.append(XPGem(e.pos.x, e.pos.y, e.xp))
                self.player.kills += 1
                self.player.gold += int(e.score // 10 * self.meta.get_powerup_bonus("greed") * self.player.gold_mult)

        # Очистка + деспавн далёких врагов
        from config import DESPAWN_DISTANCE
        for e in self.enemies:
            if e.alive and not e.is_boss:
                dist = (e.pos - self.player.pos).length()
                if dist > DESPAWN_DISTANCE:
                    e.alive = False
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.gems = [g for g in self.gems if g.alive]
        self.damage_numbers = [d for d in self.damage_numbers if d.alive]
        self.particles = [p for p in self.particles if p.alive]
        self.pulses = [p for p in self.pulses if p.alive]

        # 8. Эффекты
        shake.update(dt)
        flash.update(dt)
        for d in self.damage_numbers:
            d.update(dt)
        for p in self.particles:
            p.update(dt)
        for p in self.pulses:
            p.update(dt)

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

            # Проверить достижения
            boss_killed = any(not e.alive and e.is_boss for e in self.enemies)
            self.meta.check_achievements(
                self.elapsed, self.wave_mgr.wave,
                self.player.kills, self.meta.gold,
                boss_killed=boss_killed
            )

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
        # Проверка эволюции оружия при убийстве босса (сундук)
        if enemy.is_boss:
            for w in self.player.weapons:
                if w.can_evolve(self.player):
                    w.evolve()
                    shake.trigger(10, 0.3)
                    if sound_mgr:
                        sound_mgr.play("levelup")

    def check_levelup(self):
        if self.player.xp >= self.player.xp_to_next:
            self.player.xp -= self.player.xp_to_next
            self.player.level += 1
            self.player.xp_to_next = calc_xp_for_level(self.player.level)

            # Бонусные XP на уровнях 20 и 40
            if self.player.level == 20:
                self.player.xp_to_next += 600
            elif self.player.level == 40:
                self.player.xp_to_next += 2400

            self.levelup_screen.activate(self.player)
            self.state = "levelup"
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

        # Препятствия
        for obs in self.obstacles:
            obs.draw(screen, cam_x, cam_y)

        # XP-гемы
        for g in self.gems:
            g.draw(screen, cam_x, cam_y)

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

        # Частицы
        for p in self.particles:
            p.draw(screen, cam_x, cam_y)

        # Damage numbers
        for d in self.damage_numbers:
            d.draw(screen, cam_x, cam_y, small_font)

        # HUD
        draw_hud(screen, self.player, self.wave_mgr.wave, self.elapsed, font, small_font)

        # LevelUpScreen
        if self.state == "levelup":
            self.levelup_screen.draw(screen, font, small_font)

        # Game Over
        if self.state == "gameover":
            self.menu.draw(screen, font, big_font, small_font)

        # Screen flash
        flash.draw(screen)


async def main():
    """Главная async-функция (для pygbag)."""
    init_pygame()
    init_sounds()

    game = Game()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)  # Ограничение dt

        running = game.handle_events()
        game.update(dt)
        game.render()

        pygame.display.flip()
        await asyncio.sleep(0)  # Для pygbag

    pygame.quit()


if __name__ == "__main__":
    if sys.platform == "emscripten":
        asyncio.run(main())
    else:
        asyncio.run(main())
