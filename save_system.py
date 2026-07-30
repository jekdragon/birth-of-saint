"""
Рождение святого - Save System
Сохранение/загрузка мета-прогресса.
В браузере - localStorage, на десктопе - JSON файл.
"""
import json
import os
import sys

IS_WEB = sys.platform == "emscripten"

SAVE_DIR = os.path.join(os.path.dirname(__file__), "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "progress.json")

_data_cache = {}


def _get_local_storage():
    """Возвращает объект localStorage браузера или None.
    В pygbag/emscripten доступ к localStorage через модуль js (рекомендованный
    pygbag способ); устаревший путь через platform.window оставлен как fallback.
    """
    try:
        from js import localStorage
        return localStorage
    except Exception:
        pass
    try:
        import platform
        return platform.window.localStorage
    except Exception:
        return None


def save_progress(meta) -> bool:
    """Сохраняет MetaProgress."""
    global _data_cache
    data = {
        "gold": meta.gold,
        "total_runs": meta.total_runs,
        "best_wave": meta.best_wave,
        "best_time": meta.best_time,
        "total_kills": meta.total_kills,
        "powerups": meta.powerups,
        "unlocked_chars": list(meta.unlocked_chars),
        "unlocked_weapons": list(meta.unlocked_weapons),
        "achievements_done": list(meta.achievements_done),
        "selected_arcana": meta.selected_arcana,
    }
    _data_cache = data

    if IS_WEB:
        ls = _get_local_storage()
        if ls is None:
            return False
        try:
            ls.setItem("birth_of_saint", json.dumps(data))
            return True
        except Exception:
            return False
    else:
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False


def load_progress(meta) -> bool:
    """Загружает MetaProgress."""
    global _data_cache

    if IS_WEB:
        ls = _get_local_storage()
        raw = None
        if ls is not None:
            try:
                raw = ls.getItem("birth_of_saint")
            except Exception:
                raw = None
        try:
            if raw:
                data = json.loads(raw)
            elif _data_cache:
                data = _data_cache
            else:
                return False
        except Exception:
            return False
    else:
        if not os.path.exists(SAVE_FILE):
            return False
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Load error: {e}")
            return False

    meta.gold = data.get("gold", 0)
    meta.total_runs = data.get("total_runs", 0)
    meta.best_wave = data.get("best_wave", 0)
    meta.best_time = data.get("best_time", 0)
    meta.total_kills = data.get("total_kills", 0)
    meta.powerups = data.get("powerups", meta.powerups)
    meta.unlocked_chars = set(data.get("unlocked_chars", ["warrior", "paladin"]))
    meta.unlocked_weapons = set(data.get("unlocked_weapons", ["whip", "fire", "halo", "rosary"]))
    meta.achievements_done = set(data.get("achievements_done", []))
    meta.selected_arcana = data.get("selected_arcana", None)
    return True
