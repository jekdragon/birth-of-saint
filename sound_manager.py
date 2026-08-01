"""
Рождение святого - Sound Manager (wrapper)
Тонкая обёртка для доступа к SoundManager из UI-кода.
"""
_sound_mgr = None


def init(sound_mgr):
    """Вызвать из main.py после создания SoundManager."""
    global _sound_mgr
    _sound_mgr = sound_mgr


def play(name: str):
    """Воспроизводит звук по имени."""
    if _sound_mgr:
        _sound_mgr.play(name)


def get_volume() -> float:
    if _sound_mgr:
        return getattr(_sound_mgr, 'volume', 0.7)
    return 0.7


def set_volume(vol: float):
    if _sound_mgr:
        _sound_mgr.volume = max(0.0, min(1.0, vol))
