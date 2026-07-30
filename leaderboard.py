"""
Рождение святого — Leaderboard
Локальная таблица рекордов (localStorage в браузере, JSON на десктопе).
"""
import json
import os
import time

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "saves", "leaderboard.json")
MAX_ENTRIES = 20


def _load_entries() -> list:
    """Загрузить записи."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_entries(entries: list):
    """Сохранить записи."""
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
    # Сортировка: больше волн → больше убийств → дольше выжил
    entries.sort(key=lambda e: (e["wave"], e["kills"], e["survived"]), reverse=True)
    entries = entries[:MAX_ENTRIES]
    _save_entries(entries)
    return entries.index(entry) + 1  # позиция в таблице


def get_entries() -> list:
    """Получить все записи."""
    return _load_entries()


def get_best() -> dict:
    """Получить лучший результат."""
    entries = _load_entries()
    return entries[0] if entries else None


def clear():
    """Очистить таблицу."""
    _save_entries([])
