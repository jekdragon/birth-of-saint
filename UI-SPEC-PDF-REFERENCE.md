# Концепция спецификации пользовательского интерфейса (UI)
> Источник: Google Gemini, 01.08.2026
> Жанр: Pixel Art Game | Стек: Python (Pygame) | Статус: Draft v1.0

---

## 1. Обзор и принципы дизайна (Design Principles)

### 1.1. Визуальный стиль
- **Эстетика:** Классический пиксель-арт (16-bit / 32-bit)
- **Пиксельная точность:** Все элементы UI строго привязаны к пиксельной сетке. Отсутствует сглаживание (anti-aliasing) для шрифтов и спрайтов
- **Цветовая палитра:** Ограниченная палитра (16, 32 или 64 цвета из палитр NES/SNES или Lospec, таких как PICO-8 или JUGGLER 64), обеспечивающая высокий контраст элементов интерфейса над игровым миром
- **Типографика:** Моноширинные пиксельные шрифты (Press Start 2P, Silkscreen, ThaleahFat)

### 1.2. Технические ограничения и разрешение
- **Базовое внутреннее разрешение:** 320x180 или 480x270 (соотношение 16:9)
- **Масштабирование:** Целочисленное (Integer Scaling: 2x, 3x, 4x) для сохранения чёткости пикселей
- **Управление:** Полная поддержка клавиатуры, мыши и геймпада (переключение фокуса по элементам через D-Pad / Стрелки)

---

## 2. Архитектура UI-системы

### 2.1. Иерархия классов
```
UIManager
├── ScreenManager
│   ├── MainMenuScreen
│   ├── GameplayHUD
│   ├── InventoryScreen
│   └── PauseMenuScreen
└── UIComponents
    ├── UIElement (Base)
    │   ├── UIButton
    │   ├── UILabel
    │   ├── UIProgressBar (Health/Mana)
    │   ├── UIGridSlot (Inventory)
    │   └── UITextBox (Dialogues)
    └── TooltipManager
```

### 2.2. Состояния интерфейса (UI States)
1. **Main Menu State** — Главное меню игры
2. **HUD State** — Минималистичный оверлей во время геймплея
3. **Modal Window State** — Пауза, инвентарь, диалог (игра полностью или частично приостанавливается)
4. **Game Over / Victory State** — Экраны окончания игры

---

## 3. Детализация компонентов UI

### 3.1. Игровой оверлей (HUD)
- **Индикатор здоровья/ресурсов:** Иконка сердца/драгоценного камня, полоса прогресса с дискретным заполнением по пикселям или счётчик "сердечек"
- **Быстрые слоты (Hotbar):** 4-8 квадратных слотов внизу экрана, нумерация (1-8), подсветка активного, отображение stack count
- **Всплывающий текст (Floating Combat Text):** Урон/лечение над сущностями, плавно поднимающийся вверх и исчезающий за dt=0.8 сек

### 3.2. Система диалогов (Dialogue Box)
- **Размещение:** Нижняя треть экрана
- **Стилизация:** Тёмное пиксельное окно с светлой 2px-рамкой
- **Компоненты:**
  - Портрет персонажа (анимированный пиксельный спрайт 32x32 или 64x64)
  - Имя говорящего
  - Эффект "печатной машинки" (Typewriter) — появление символов по одному с задержкой ~0.03 сек
  - Иконка прокрутки (мигающая стрелка) при завершении реплики

### 3.3. Экран инвентаря (Inventory Window)
- **Сетка:** N x M слотов (например, 5x4)
- **Интерактивность:**
  - Выделение слота при наведении мыши или выборе с геймпада
  - Перетаскивание предметов (Drag-and-Drop) или перемещение через Click-to-select -> Click-to-move
- **Окно информации (Tooltip):** Появляется при задержке курсора. Отображает: Название (цветом редкости), тип, характеристики, описание

### 3.4. Главное меню и настройки
- **Элементы:** "Новая игра", "Продолжить", "Настройки", "Выход"
- **Состояния кнопок:**
  1. **Normal** — Стандартный вид
  2. **Hover/Focused** — Смещение текста/спрайта на 1-2 пикселя вправо/вверх, появление пиксельного указателя (курсор-меч/стрелка)
  3. **Pressed** — Смещение кнопки вниз на 1 пиксель, затемнение палитры

---

## 4. Соочные эффекты (UI Juice & Polish)

1. **Пиксельный Shake:** При критическом уроне полоска HP слегка встряхивается по оси X/Y на +/-1-2 px
2. **Переходы между экранами:**
   - Pixelate Fade — пикселизация с уменьшением разрешения до полного затемнения
   - Wipe Transition — закрытие экрана пиксельной "шторой"
3. **Звуковой фидбек (UI SFX):**
   - Hover: короткий 8-битный клик/блик (`expand`)
   - Click: чёткий 8-битный звук нажатия (`tune`)
   - Open/Close Menu: шелест/кликер (`chat_spark`)

---

## 5. Прототип структуры кода (Pygame)

```python
import pygame

class UIElement:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface):
        pass


class UIButton(UIElement):
    def __init__(self, x, y, width, height, text, font, callback):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.callback()

    def draw(self, surface):
        color = (200, 200, 200) if not self.is_hovered else (255, 255, 255)
        offset_y = 1 if self.is_hovered else 0
        pygame.draw.rect(surface, (40, 40, 50), self.rect)
        pygame.draw.rect(surface, color, self.rect, width=1)  # Пиксельный контур
        text_surf = self.font.render(self.text, False, color)  # antialias = False
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery + offset_y))
        surface.blit(text_surf, text_rect)
```

---

## 6. Чек-лист разработки UI

- [ ] Настроить рендеринг на виртуальный Canvas малого разрешения с последующим Integer Scaling
- [ ] Подключить пиксельный .ttf/.otf шрифт со сбросом антиалиасинга
- [ ] Реализовать базовый класс UIManager и менеджер сцен/экранов
- [ ] Разработать спрайтшиты для рамок, кнопок и слотов инвентаря (9-slice scaling)
- [ ] Настроить навигацию с клавиатуры/геймпада (Focus Management)
- [ ] Интегрировать 8-битные звуковые эффекты для всех взаимодействий с UI
