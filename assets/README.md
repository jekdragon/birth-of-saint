# Assets — Рождение святого

## Структура

```
assets/
├── sprites/          # Спрайты (пиксель-арт 16x16 / 32x32)
│   ├── player/       # Персонажи (warrior.png, paladin.png, inquisitor.png)
│   ├── enemies/      # Враги (neophyte.png, acolyte.png, heretic.png, demon.png, fanatic.png, antichrist.png)
│   ├── weapons/      # Визуал оружия (whip.png, fire.png, halo.png, rosary.png, lightning.png, prayer.png)
│   ├── effects/      # Партиклы, glow, удары
│   ├── ui/           # HUD элементы, иконки, карточки
│   └── tiles/        # Тайлы карты (руины, кладбище, лес, пустошь)
└── sounds/           # Звуковые эффекты (MVP: генерируются через synth)
    ├── sfx/          # hit.wav, kill.wav, levelup.wav, boss_spawn.wav
    └── music/        # Фоновая музыка (Phase 3+)
```

## Правила

1. Спрайты: PNG, прозрачный фон, пиксель-арт (nearest neighbor)
2. Размеры: игрок 28x28, враги 24-34, босс 76, гемы 6-10, снаряды 12-14
3. Именование: snake_case (neophyte.png, not Neophyte.png)
4. MVP: кружки вместо спрайтов, без внешних файлов
5. Phase 2+: замена кружков на пиксельные спрайты

## Цветовые палитры (для генерации спрайтов)

| Биом | Фон | Акцент |
|------|-----|--------|
| Руины | #1a1a2e | #6b5b95 |
| Кладбище | #0d0d1a | #2a4a3a |
| Адский лес | #1a0d0d | #ff4444 |
| Пустошь | #0d0d0d | #d4c4a0 |

| Персонаж | Цвет |
|----------|------|
| Воин | #c83c3c |
| Паладин | #3c78d8 |
| Инквизитор | #c8b43c |
| Боссы | #b450dc |
