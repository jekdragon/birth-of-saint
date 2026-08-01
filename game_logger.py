"""
Рождение святого — Game Session Logger
Записывает ошибки, переходы, аномалии и состояние игры в JSONL файл.

Типы записей:
  ERROR        — необработанное исключение
  INPUT        — каждый клик/нажатие + что произошло
  TRANSITION   — переход между сценами + контекст
  LEVELUP      — выбор при левелапе + альтернативы
  PAUSE        — открытие/закрытие паузы
  STATE_SNAP   — снимок состояния (HP, kills, wave, gold)
  FPS_DROP     — FPS ниже порога (< 30)
  ANOMALY      — логическая аномалия (HP<0, leak, impossible state)
  PERF_SAMPLE  — периодический снимок производительности
  ENTITY_LEAK  — утечка объектов (dead враги, протухшие гемы)
"""
from __future__ import annotations
import json
import os
import time
import traceback
import datetime
import threading
from pathlib import Path
from typing import Optional


class LogType:
    ERROR = "ERROR"
    INPUT = "INPUT"
    TRANSITION = "TRANSITION"
    LEVELUP = "LEVELUP"
    PAUSE = "PAUSE"
    STATE_SNAP = "STATE_SNAP"
    FPS_DROP = "FPS_DROP"
    ANOMALY = "ANOMALY"
    PERF_SAMPLE = "PERF_SAMPLE"
    ENTITY_LEAK = "ENTITY_LEAK"
    SESSION_START = "SESSION_START"
    SESSION_END = "SESSION_END"


class SessionLogger:
    """Записывает события игровой сессии в JSONL файл."""

    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{ts}.jsonl"
        self._lock = threading.Lock()
        self._start_time = time.monotonic()
        self._frame_count = 0
        self._error_count = 0
        self._anomaly_count = 0
        self._active = True
        self._last_scene = "unknown"
        self._scene_enter_time = 0.0
        self._last_perf_sample = 0.0

        # Пороги
        self.fps_threshold = 30
        self.perf_sample_interval = 10.0
        self.entity_warn_enemies = 300
        self.entity_warn_projectiles = 200
        self.entity_warn_particles = 500
        self.entity_warn_total = 1000
        self.gem_max_age = 30.0

        self._write({"type": LogType.SESSION_START,
                      "timestamp": datetime.datetime.now().isoformat(),
                      "log_file": str(self.log_file)})

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self._start_time

    def _write(self, entry: dict):
        if not self._active:
            return
        entry["_t"] = round(self.elapsed, 3)
        entry["_frame"] = self._frame_count
        line = json.dumps(entry, ensure_ascii=False, default=str) + "\n"
        with self._lock:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception:
                pass

    # ----------------------------------------------------------
    # ERROR
    # ----------------------------------------------------------
    def log_error(self, exception: Exception, context: Optional[dict] = None):
        self._error_count += 1
        self._write({
            "type": LogType.ERROR,
            "error_type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "error_count": self._error_count,
        })

    # ----------------------------------------------------------
    # INPUT — каждый клик/нажатие + что произошло
    # ----------------------------------------------------------
    def log_input(self, event_type: str, key_or_button: str,
                  scene: str, pos: Optional[list] = None,
                  element: Optional[str] = None,
                  result: Optional[str] = None,
                  new_scene: Optional[str] = None):
        """
        event_type: "mouse_click" / "key_press" / "mouse_motion"
        key_or_button: "left_click" / "escape" / "return" / "w" / ...
        scene: текущая сцена
        pos: [x, y] для мыши
        element: id элемента под курсором (btn_ИГРАТЬ, tab_Герои, ...)
        result: "scene_change" / "action" / "miss" / "ignored"
        new_scene: если result=scene_change
        """
        time_in_scene = self.elapsed - self._scene_enter_time
        self._write({
            "type": LogType.INPUT,
            "event": event_type,
            "key": key_or_button,
            "scene": scene,
            "pos": pos,
            "element": element,
            "result": result,
            "new_scene": new_scene,
            "time_in_scene": round(time_in_scene, 2),
        })

    # ----------------------------------------------------------
    # TRANSITION — переходы между сценами
    # ----------------------------------------------------------
    def log_transition(self, from_scene: str, to_scene: str,
                       trigger: str, overlay_active: bool = False,
                       fade_type: Optional[str] = None,
                       state_snapshot: Optional[dict] = None):
        """
        trigger: "click_ИГРАТЬ" / "key_enter" / "fade_complete" / "death" / "ESC" / ...
        fade_type: "fade_to_black" / "slide_left" / "instant" / None
        state_snapshot: {selected_char, gold, ...}
        """
        duration = self.elapsed - self._scene_enter_time
        self._scene_enter_time = self.elapsed
        self._last_scene = to_scene
        self._write({
            "type": LogType.TRANSITION,
            "from": from_scene,
            "to": to_scene,
            "trigger": trigger,
            "duration_in_from": round(duration, 2),
            "overlay_active": overlay_active,
            "fade_type": fade_type,
            "state_snapshot": state_snapshot or {},
        })

    # ----------------------------------------------------------
    # LEVELUP — выбор при левелапе
    # ----------------------------------------------------------
    def log_levelup(self, level: int, xp_required: int,
                    choices: list, chosen_index: int,
                    chosen_item: str, rerolls_used: int = 0,
                    time_to_choose: float = 0,
                    player_state: Optional[dict] = None):
        self._write({
            "type": LogType.LEVELUP,
            "level": level,
            "xp_required": xp_required,
            "choices": choices,
            "chosen_index": chosen_index,
            "chosen_item": chosen_item,
            "rerolls_used": rerolls_used,
            "time_to_choose": round(time_to_choose, 2),
            "player_state": player_state or {},
        })

    # ----------------------------------------------------------
    # PAUSE — открытие/закрытие паузы
    # ----------------------------------------------------------
    def log_pause(self, action: str, scene: str = "game",
                  pause_duration: float = 0,
                  game_state: Optional[dict] = None):
        """
        action: "open" / "resume" / "quit_to_lobby" / "settings"
        """
        self._write({
            "type": LogType.PAUSE,
            "action": action,
            "scene": scene,
            "pause_duration": round(pause_duration, 2),
            "game_state": game_state or {},
        })

    # ----------------------------------------------------------
    # STATE_SNAP — снимок состояния
    # ----------------------------------------------------------
    def log_state_snapshot(self, player_hp: float = 0, player_max_hp: float = 0,
                           player_level: int = 0, kills: int = 0,
                           wave: int = 0, elapsed_time: float = 0,
                           gold: int = 0, weapons: Optional[list] = None,
                           enemies_alive: int = 0, **extra):
        self._write({
            "type": LogType.STATE_SNAP,
            "hp": round(player_hp, 1),
            "max_hp": round(player_max_hp, 1),
            "level": player_level,
            "kills": kills,
            "wave": wave,
            "time": round(elapsed_time, 1),
            "gold": gold,
            "weapons": weapons or [],
            "enemies_alive": enemies_alive,
            **extra,
        })

    # ----------------------------------------------------------
    # FPS_DROP
    # ----------------------------------------------------------
    def log_fps_drop(self, fps: float, dt: float, scene: str = ""):
        self._write({
            "type": LogType.FPS_DROP,
            "fps": round(fps, 1),
            "dt": round(dt, 4),
            "scene": scene,
        })

    # ----------------------------------------------------------
    # ANOMALY — логические аномалии
    # ----------------------------------------------------------
    def log_anomaly(self, description: str, details: Optional[dict] = None):
        self._anomaly_count += 1
        self._write({
            "type": LogType.ANOMALY,
            "description": description,
            "details": details or {},
            "anomaly_count": self._anomaly_count,
        })

    # ----------------------------------------------------------
    # ENTITY_LEAK — утечка объектов
    # ----------------------------------------------------------
    def log_entity_leak(self, leak_type: str, count: int, details: Optional[dict] = None):
        """
        leak_type: "dead_enemy" / "stale_gem" / "stale_coin" / "orphan_projectile" / "particle_overflow"
        """
        self._write({
            "type": LogType.ENTITY_LEAK,
            "leak_type": leak_type,
            "count": count,
            "details": details or {},
        })

    # ----------------------------------------------------------
    # PERF_SAMPLE
    # ----------------------------------------------------------
    def maybe_perf_sample(self, fps: float, dt: float, scene: str = "",
                          memory_mb: float = 0, enemy_count: int = 0,
                          projectile_count: int = 0, particle_count: int = 0):
        now = time.monotonic()
        if now - self._last_perf_sample < self.perf_sample_interval:
            return
        self._last_perf_sample = now
        self._write({
            "type": LogType.PERF_SAMPLE,
            "fps": round(fps, 1),
            "dt": round(dt, 4),
            "scene": scene,
            "memory_mb": round(memory_mb, 1),
            "enemies": enemy_count,
            "projectiles": projectile_count,
            "particles": particle_count,
        })

    # ----------------------------------------------------------
    # FRAME TICK — каждый кадр
    # ----------------------------------------------------------
    def tick(self, fps: float, dt: float, scene: str = ""):
        self._frame_count += 1
        if fps < self.fps_threshold:
            self.log_fps_drop(fps, dt, scene)

    # ----------------------------------------------------------
    # CHECK_ANOMALIES — автоматическая проверка состояния игры
    # ----------------------------------------------------------
    def check_anomalies(self, game_state: dict):
        """
        Вызывается каждый кадр (или раз в N кадров).
        game_state = {
            "player_hp", "player_max_hp", "player_level", "player_gold",
            "player_speed_mult", "player_damage_mult",
            "weapons": [{"id", "level"}], "passives": {"id": level},
            "enemies_alive", "enemies_dead_stuck", "projectiles_alive",
            "particles_count", "gems_alive", "coins_alive",
            "wave", "elapsed", "boss_alive_count"
        }
        """
        hp = game_state.get("player_hp", 0)
        max_hp = game_state.get("player_max_hp", 100)
        level = game_state.get("player_level", 1)
        gold = game_state.get("player_gold", 0)
        speed = game_state.get("player_speed_mult", 1.0)
        damage = game_state.get("player_damage_mult", 1.0)
        weapons = game_state.get("weapons", [])
        passives = game_state.get("passives", {})
        enemies = game_state.get("enemies_alive", 0)
        dead_stuck = game_state.get("enemies_dead_stuck", 0)
        projectiles = game_state.get("projectiles_alive", 0)
        particles = game_state.get("particles_count", 0)
        gems = game_state.get("gems_alive", 0)
        coins = game_state.get("coins_alive", 0)
        bosses = game_state.get("boss_alive_count", 0)

        # Player state anomalies
        if hp < 0:
            self.log_anomaly("player_hp_negative", {"hp": hp})
        if hp > max_hp * 1.05:
            self.log_anomaly("player_hp_overflow", {"hp": hp, "max_hp": max_hp})
        if gold < 0:
            self.log_anomaly("player_gold_negative", {"gold": gold})
        if speed <= 0:
            self.log_anomaly("player_speed_zero_or_negative", {"speed": speed})
        if damage < 0:
            self.log_anomaly("player_damage_negative", {"damage": damage})

        # Weapon/passive limits
        if len(weapons) > 6:
            self.log_anomaly("weapon_count_overflow", {"count": len(weapons)})
        for w in weapons:
            if isinstance(w, dict) and w.get("level", 0) > 8:
                self.log_anomaly("weapon_level_overflow", {"weapon": w})
        if len(passives) > 6:
            self.log_anomaly("passive_count_overflow", {"count": len(passives)})
        for pid, lvl in passives.items():
            if lvl > 5:
                self.log_anomaly("passive_level_overflow", {"id": pid, "level": lvl})

        # Boss anomalies
        if bosses > 1:
            self.log_anomaly("multiple_bosses_alive", {"count": bosses})

        # Entity leaks
        if dead_stuck > 5:
            self.log_entity_leak("dead_enemy_stuck", dead_stuck)
        if gems > 100:
            self.log_entity_leak("gem_accumulation", gems)
        if coins > 100:
            self.log_entity_leak("coin_accumulation", coins)

        # Entity count warnings
        total = enemies + projectiles + particles + gems + coins
        if total > self.entity_warn_total:
            self.log_anomaly("entity_total_overflow", {"total": total})
        if enemies > self.entity_warn_enemies:
            self.log_anomaly("enemy_count_high", {"enemies": enemies})
        if projectiles > self.entity_warn_projectiles:
            self.log_anomaly("projectile_count_high", {"projectiles": projectiles})
        if particles > self.entity_warn_particles:
            self.log_anomaly("particle_count_high", {"particles": particles})

    # ----------------------------------------------------------
    # CLOSE
    # ----------------------------------------------------------
    def close(self, reason: str = "normal"):
        self._write({
            "type": LogType.SESSION_END,
            "reason": reason,
            "total_frames": self._frame_count,
            "total_errors": self._error_count,
            "total_anomalies": self._anomaly_count,
            "duration": round(self.elapsed, 1),
        })
        self._active = False

    # ----------------------------------------------------------
    # ANALYZE — чтение и анализ лога
    # ----------------------------------------------------------
    @staticmethod
    def read_log(log_path: str) -> list:
        entries = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return entries

    @staticmethod
    def analyze_log(log_path: str) -> dict:
        entries = SessionLogger.read_log(log_path)
        result = {
            "total_entries": len(entries),
            "errors": [],
            "anomalies": [],
            "entity_leaks": [],
            "inputs": [],
            "transitions": [],
            "levelups": [],
            "pauses": [],
            "fps_drops": [],
            "perf_samples": [],
            "duration": 0,
            "summary": {},
        }

        fps_values = []
        max_enemies = 0

        for e in entries:
            t = e.get("type", "")
            if t == LogType.ERROR:
                result["errors"].append(e)
            elif t == LogType.ANOMALY:
                result["anomalies"].append(e)
            elif t == LogType.ENTITY_LEAK:
                result["entity_leaks"].append(e)
            elif t == LogType.INPUT:
                result["inputs"].append(e)
            elif t == LogType.TRANSITION:
                result["transitions"].append(e)
            elif t == LogType.LEVELUP:
                result["levelups"].append(e)
            elif t == LogType.PAUSE:
                result["pauses"].append(e)
            elif t == LogType.FPS_DROP:
                result["fps_drops"].append(e)
            elif t == LogType.PERF_SAMPLE:
                fps_values.append(e.get("fps", 0))
                max_enemies = max(max_enemies, e.get("enemies", 0))
                result["perf_samples"].append(e)
            elif t == LogType.SESSION_END:
                result["duration"] = e.get("duration", 0)

        result["summary"] = {
            "total_errors": len(result["errors"]),
            "total_anomalies": len(result["anomalies"]),
            "total_entity_leaks": len(result["entity_leaks"]),
            "total_inputs": len(result["inputs"]),
            "total_transitions": len(result["transitions"]),
            "total_levelups": len(result["levelups"]),
            "total_pauses": len(result["pauses"]),
            "total_fps_drops": len(result["fps_drops"]),
            "avg_fps": round(sum(fps_values) / len(fps_values), 1) if fps_values else 0,
            "min_fps": round(min(fps_values), 1) if fps_values else 0,
            "max_enemies": max_enemies,
            "duration_seconds": result["duration"],
        }

        return result


# Глобальный экземпляр
_session_logger: Optional[SessionLogger] = None


def get_logger() -> Optional[SessionLogger]:
    return _session_logger


def init_logger(log_dir: Optional[str] = None) -> SessionLogger:
    global _session_logger
    _session_logger = SessionLogger(log_dir)
    return _session_logger


def close_logger(reason: str = "normal"):
    global _session_logger
    if _session_logger:
        _session_logger.close(reason)
        _session_logger = None
