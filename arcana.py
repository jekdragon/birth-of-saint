"""
Рождение святого — Arcana System
Модификаторы, меняющие правила рана. Игрок выбирает 1 аркану перед стартом.
"""
import random
import pygame

# === ОПРЕДЕЛЕНИЯ АРКАН ===
ARCANA_DEFS = {
    "double_threat": {
        "name": "Двойная угроза",
        "desc": "Врагов вдвое больше, но XP с них +50%",
        "color": (255, 80, 80),
        "unlock_condition": None,
    },
    "vow_of_silence": {
        "name": "Обет молчания",
        "desc": "Нет регенерации и лечения, но урон +100%",
        "color": (180, 140, 220),
        "unlock_condition": None,
    },
    "gift_of_providence": {
        "name": "Дар провидения",
        "desc": "Начать с дополнительным случайным оружием",
        "color": (100, 220, 255),
        "unlock_condition": None,
    },
    "horde_fury": {
        "name": "Ярость орды",
        "desc": "Враги на 40% быстрее, но золота с них вдвое больше",
        "color": (255, 180, 60),
        "unlock_condition": None,
    },
    "swift_judgment": {
        "name": "Скорый суд",
        "desc": "Босс приходит каждые 2 волны вместо 3",
        "color": (220, 200, 100),
        "unlock_condition": None,
    },
}


class Arcana:
    """Базовый класс арканы."""

    def __init__(self, arcana_id: str):
        self.arcana_id = arcana_id
        d = ARCANA_DEFS[arcana_id]
        self.name = d["name"]
        self.description = d["desc"]
        self.color = d["color"]

    def apply(self, game, meta):
        """Применяет эффекты арканы к game.
        Вызывается в start_game() после настройки игрока/волн.
        """
        pass

    @staticmethod
    def create(arcana_id):
        """Фабрика: возвращает экземпляр арканы по ID."""
        cls = ARCANA_CLASSES.get(arcana_id)
        if cls:
            return cls()
        return None


# ─── Конкретные арканы ───────────────────────────────────────────


class DoubleThreatArcana(Arcana):
    """Врагов вдвое больше, но XP с них +50%."""

    def __init__(self):
        super().__init__("double_threat")

    def apply(self, game, meta):
        # Увеличиваем мин. врагов за волну
        game.wave_mgr.min_enemies_per_wave *= 2
        # Ускоряем спавн
        game.wave_mgr.spawn_interval *= 0.5
        game.wave_mgr.spawn_interval = max(game.wave_mgr.spawn_interval, 0.15)
        # Флаг для XP бонуса — проверяется в on_enemy_killed / update
        game.arcana_data["xp_mult"] = 1.5


class VowOfSilenceArcana(Arcana):
    """Нет регенерации и лечения, но урон +100%."""

    def __init__(self):
        super().__init__("vow_of_silence")

    def apply(self, game, meta):
        # Отключаем регенерацию и лечение у игрока
        game.player.arcana_no_heal = True
        # Удваиваем урон игрока (используется в Player.damage_mult)
        game.player.arcana_damage_bonus = 2.0


class GiftOfProvidenceArcana(Arcana):
    """Начать с дополнительным случайным оружием."""

    def __init__(self):
        super().__init__("gift_of_providence")

    def apply(self, game, meta):
        # Выбираем случайное оружие из доступных игроку
        from weapons import WEAPON_DEFS, create_weapon

        owned_ids = [w.weapon_id for w in game.player.weapons]
        available = [
            wid for wid in WEAPON_DEFS
            if wid not in owned_ids and wid in meta.unlocked_weapons
        ]
        if not available:
            available = [wid for wid in WEAPON_DEFS if wid not in owned_ids]
        if available:
            pick = random.choice(available)
            game.player.weapons.append(create_weapon(pick))
            game.arcana_data["bonus_weapon"] = pick


class HordeFuryArcana(Arcana):
    """Враги на 40% быстрее, но золота с них вдвое больше."""

    def __init__(self):
        super().__init__("horde_fury")

    def apply(self, game, meta):
        game.arcana_data["enemy_speed_mult"] = 1.4
        game.player.arcana_gold_mult = 2.0


class SwiftJudgmentArcana(Arcana):
    """Босс приходит каждые 2 волны вместо 3."""

    def __init__(self):
        super().__init__("swift_judgment")

    def apply(self, game, meta):
        game.wave_mgr.next_boss_wave = 2
        game.wave_mgr.boss_every_n_waves = 2


# ─── Реестр ──────────────────────────────────────────────────────

ARCANA_CLASSES = {
    "double_threat": DoubleThreatArcana,
    "vow_of_silence": VowOfSilenceArcana,
    "gift_of_providence": GiftOfProvidenceArcana,
    "horde_fury": HordeFuryArcana,
    "swift_judgment": SwiftJudgmentArcana,
}