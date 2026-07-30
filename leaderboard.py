"""
Рождение святого - Leaderboard
Локальная таблица рекордов (localStorage в браузере, JSON на десктопе).
"""
import json
import os
import sys
import time

IS_WEB = sys.platform == "emscripten"
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "saves", "leaderboard.json")
MAX_ENTRIES = 20

_entries_cache = []


def _load_entries() -> list:
    """Загрузить записи."""
    global _entries_cache

    if IS_WEB:
        try:
            import platform
            raw = platform.window.localStorage.getItem("birth_of_saint_lb")
            if raw:
                _entries_cache = json.loads(raw)
        except Exception:
            pass
        return list(_entries_cache)

    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_entries(entries: list):
    """Сохранить записи."""
    global _entries_cache
    _entries_cache = entries

    if IS_WEB:
        try:
            import platform
            platform.window.localStorage.setItem("birth_of_saint_lb", json.dumps(entries))
        except Exception:
            pass
        return

    os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def add_score(character: str, wave: int, kills: int, gold: int, survived: float, map_name: str = "arena"):
    """Добавить результат в таблицу."""
    entries = _load_entries()
    entry = {
        "character": character,
        "wave": wave,
        "kills": kills,
        "gold": gold,
        "survived": round(survived, 1),
        "map": map_name,
        "timestamp": int(time.time()),
    }
    entries.append(entry)
    entries.sort(key=lambda e: (e["wave"], e["kills"], e["survived"]), reverse=True)
    rank = entries.index(entry) + 1
    entries = entries[:MAX_ENTRIES]
    _save_entries(entries)
    return rank if rank <= MAX_ENTRIES else -1


def get_entries() -> list:
    return _load_entries()


def get_best() -> dict:
    entries = _load_entries()
    return entries[0] if entries else None


def clear():
    _save_entries([])
