"""
Рождение святого - Save System (C5: Multi-Profile)
Сохранение/загрузка мета-прогресса с поддержкой 3 слотов профилей.
В браузере - localStorage, на десктопе - JSON файлы.
"""
import json
import os
import sys

IS_WEB = sys.platform == "emscripten"

SAVE_DIR = os.path.join(os.path.dirname(__file__), "saves")
# Совместимость: старые тесты используют SAVE_FILE
SAVE_FILE = os.path.join(SAVE_DIR, "progress.json")

# Активный профиль (1-3)
_active_profile = 1

_data_cache = {}  # {profile_id: data_dict}


def _get_local_storage():
    """Возвращает объект localStorage браузера или None."""
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


def _profile_key(profile_id: int) -> str:
    """Ключ localStorage для профиля."""
    return f"birth_of_saint_{profile_id}"


def _profile_file(profile_id: int) -> str:
    """Путь к JSON-файлу профиля."""
    return os.path.join(SAVE_DIR, f"save_profile_{profile_id}.json")


def set_active_profile(profile_id: int):
    """Установить активный профиль (1-3)."""
    global _active_profile
    _active_profile = max(1, min(3, profile_id))


def get_active_profile() -> int:
    """Получить номер активного профиля."""
    return _active_profile


def save_progress(meta, profile_id=None) -> bool:
    """Сохраняет MetaProgress в указанный профиль."""
    global _data_cache
    pid = profile_id if profile_id is not None else _active_profile
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
        "banned_items": list(meta.banned_items),
        "ban_tokens": meta.ban_tokens,
        "enemy_kills": meta.enemy_kills,
        "altar_level": meta.altar_level,
        "weapon_archive": list(meta.weapon_archive),
        "faction_rep": meta.faction_rep,
        "obelisks": list(meta.obelisks),
    }
    _data_cache[pid] = data

    if IS_WEB:
        ls = _get_local_storage()
        if ls is None:
            return False
        try:
            ls.setItem(_profile_key(pid), json.dumps(data))
            return True
        except Exception:
            return False
    else:
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            with open(_profile_file(pid), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False


def load_progress(meta, profile_id=None) -> bool:
    """Загружает MetaProgress из указанного профиля."""
    global _data_cache
    pid = profile_id if profile_id is not None else _active_profile
    data = None

    if IS_WEB:
        ls = _get_local_storage()
        raw = None
        if ls is not None:
            try:
                raw = ls.getItem(_profile_key(pid))
            except Exception:
                raw = None
        try:
            if raw:
                data = json.loads(raw)
            elif pid in _data_cache:
                data = _data_cache[pid]
            else:
                return False
        except Exception:
            return False
    else:
        save_file = _profile_file(pid)
        # Совместимость: если файла профиля нет, проверяем старый progress.json
        if not os.path.exists(save_file):
            old_file = os.path.join(SAVE_DIR, "progress.json")
            if pid == 1 and os.path.exists(old_file):
                save_file = old_file
            else:
                return False
        try:
            with open(save_file, "r", encoding="utf-8") as f:
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
    meta.banned_items = set(data.get("banned_items", []))
    meta.ban_tokens = data.get("ban_tokens", 0)
    meta.enemy_kills = data.get("enemy_kills", {})
    meta.altar_level = data.get("altar_level", {"might_altar": 0, "regen_altar": 0, "magnet_altar": 0, "luck_altar": 0})
    meta.weapon_archive = set(data.get("weapon_archive", []))
    meta.faction_rep = data.get("faction_rep", {"angels": 0, "demons": 0, "humans": 0})
    meta.obelisks = set(data.get("obelisks", []))
    return True


def get_profile_summary(profile_id: int) -> dict | None:
    """Возвращает краткую сводку по профилю (без загрузки в MetaProgress).
    Возвращает None если профиль пуст."""
    data = None

    if IS_WEB:
        ls = _get_local_storage()
        if ls is not None:
            try:
                raw = ls.getItem(_profile_key(profile_id))
                if raw:
                    data = json.loads(raw)
            except Exception:
                pass
    else:
        save_file = _profile_file(profile_id)
        # Совместимость с progress.json для профиля 1
        if not os.path.exists(save_file):
            old_file = os.path.join(SAVE_DIR, "progress.json")
            if profile_id == 1 and os.path.exists(old_file):
                save_file = old_file
            else:
                return None
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return None

    if data is None:
        return None

    return {
        "gold": data.get("gold", 0),
        "total_runs": data.get("total_runs", 0),
        "best_wave": data.get("best_wave", 0),
        "best_time": data.get("best_time", 0),
        "total_kills": data.get("total_kills", 0),
        "unlocked_chars_count": len(data.get("unlocked_chars", ["warrior", "paladin"])),
        "achievements_count": len(data.get("achievements_done", [])),
    }


def list_profiles() -> list:
    """Возвращает список из 3 профилей: [{id, summary|None}, ...]"""
    profiles = []
    for pid in range(1, 4):
        summary = get_profile_summary(pid)
        profiles.append({"id": pid, "summary": summary})
    return profiles
