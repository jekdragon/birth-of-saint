"""
Рождение святого - Procedural Music
Амбиентная музыка через pygame.mixer.music с procedural генерацией WAV.
"""
import sys
import struct
import math
import random
import os
import pygame

SAMPLE_RATE = 22050


def generate_ambient_wav(filepath: str, duration: float = 30.0, bpm: int = 60):
    """Генерирует амбиентный WAV файл."""
    n_samples = int(SAMPLE_RATE * duration)
    
    # Ноты (частоты в Hz) - минорные, тёмные
    notes = [110, 130.81, 146.83, 164.81, 196, 220, 261.63]
    bass_notes = [55, 65.41, 73.42, 82.41]
    
    # Beat timing
    beat_samples = int(60.0 / bpm * SAMPLE_RATE)
    
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        
        # Bass drone (subtle)
        bass_freq = bass_notes[int(t / 4) % len(bass_notes)]
        bass = 0.15 * math.sin(2 * math.pi * bass_freq * t)
        
        # Pad (low-pass filtered noise)
        pad_freq = notes[int(t / 2) % len(notes)]
        pad = 0.08 * math.sin(2 * math.pi * pad_freq * t)
        pad += 0.04 * math.sin(2 * math.pi * pad_freq * 1.5 * t)
        
        # Rhythm (subtle pulse)
        beat_pos = i % beat_samples
        rhythm = 0.0
        if beat_pos < SAMPLE_RATE * 0.05:  # 50ms pulse
            rhythm = 0.1 * math.sin(2 * math.pi * 80 * (beat_pos / SAMPLE_RATE))
        
        # Dark ambience (low noise)
        dark = 0.02 * math.sin(2 * math.pi * 40 * t + math.sin(t * 0.5) * 2)
        
        # Mix
        sample = bass + pad + rhythm + dark
        
        # Envelope (fade in/out at edges)
        if t < 2.0:
            sample *= t / 2.0
        elif t > duration - 2.0:
            sample *= (duration - t) / 2.0
        
        # Clamp
        sample = max(-1.0, min(1.0, sample))
        samples.append(sample)
    
    # Write WAV
    with open(filepath, 'wb') as f:
        # WAV header
        data_size = n_samples * 2  # 16-bit mono
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<IHHIIHH', 16, 1, 1, SAMPLE_RATE, SAMPLE_RATE * 2, 2, 16))
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        
        # Samples
        for s in samples:
            val = int(s * 32767)
            f.write(struct.pack('<h', val))


class MusicManager:
    """Управление музыкой."""
    def __init__(self):
        self.music_path = None
        self.playing = False
    
    def init(self):
        """Генерирует и запускает музыку."""
        # В браузере (pygbag) WAV не поддерживается - пропускаем
        if sys.platform == "emscripten":
            return
        
        self.music_path = os.path.join(os.path.dirname(__file__), "assets", "sounds", "ambient.wav")
        if not os.path.exists(self.music_path):
            os.makedirs(os.path.dirname(self.music_path), exist_ok=True)
            generate_ambient_wav(self.music_path, duration=60.0, bpm=50)
        
        try:
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)  # loop forever
            self.playing = True
        except Exception as e:
            print(f"Music init error: {e}")
    
    def stop(self):
        if self.playing:
            pygame.mixer.music.stop()
            self.playing = False
