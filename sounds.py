"""
Рождение святого - Sound System
Генерация звуков через synth (без внешних файлов).
"""
import math
import random
import struct
import pygame
from config import SAMPLE_RATE, SOUND_VOLUME


class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
        except Exception:
            try:
                pygame.mixer.init()
            except Exception:
                pass
        self.sounds = {}
        self._generate_sounds()

    def _synth(self, freq: float, duration: float, vol: float = 0.3,
               wave: str = 'sine', sweep: float = 0) -> pygame.mixer.Sound:
        """Генерирует звук."""
        n_samples = int(SAMPLE_RATE * duration)
        buf = bytearray(n_samples * 2)

        for i in range(n_samples):
            t = i / SAMPLE_RATE
            f = freq + sweep * t

            if wave == 'sine':
                v = math.sin(2 * math.pi * f * t)
            elif wave == 'square':
                v = 1 if math.sin(2 * math.pi * f * t) > 0 else -1
            elif wave == 'tri':
                v = 4 * abs((f * t) % 1.0 - 0.5) - 1
            elif wave == 'noise':
                v = random.uniform(-1, 1)
            else:
                v = math.sin(2 * math.pi * f * t)

            # Fade out
            fade = 1 - (t / duration)
            sample = int(v * vol * fade * 32767)
            sample = max(-32767, min(32767, sample))
            struct.pack_into('<h', buf, i * 2, sample)

        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(SOUND_VOLUME)
        return sound

    def _generate_sounds(self):
        self.sounds["hit"] = self._synth(400, 0.08, 0.2, 'square')
        self.sounds["kill"] = self._synth(600, 0.12, 0.25, 'sine', sweep=-200)
        self.sounds["levelup"] = self._synth(800, 0.3, 0.3, 'sine', sweep=200)
        self.sounds["player_hit"] = self._synth(200, 0.15, 0.3, 'square')
        self.sounds["boss_spawn"] = self._synth(100, 0.5, 0.4, 'tri', sweep=-50)
        self.sounds["gem_pickup"] = self._synth(1000, 0.05, 0.15, 'sine')
        self.sounds["game_over"] = self._synth(300, 0.8, 0.3, 'sine', sweep=-100)
        self.sounds["whip"] = self._synth(500, 0.1, 0.2, 'noise')
        self.sounds["fire"] = self._synth(300, 0.1, 0.15, 'square', sweep=100)
        self.sounds["aura"] = self._synth(700, 0.08, 0.15, 'sine')
        # UI sounds
        self.sounds["ui_hover"] = self._synth(800, 0.04, 0.15, 'sine')
        self.sounds["ui_select"] = self._synth(600, 0.1, 0.25, 'sine')
        self.sounds["ui_back"] = self._synth(400, 0.06, 0.15, 'sine', sweep=-100)
        self.sounds["ui_confirm"] = self._synth(500, 0.15, 0.2, 'sine', sweep=200)

    def play(self, name: str):
        sound = self.sounds.get(name)
        if sound:
            sound.play()
