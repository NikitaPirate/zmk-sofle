# ZMK Keyboard Heatmap System

Система анализа использования клавиш для ZMK клавиатур с генерацией красивых heatmap визуализаций.

![Heatmap Example](data/heatmaps/demo_heatmap.png)

## Возможности

- 📊 **Сбор данных в реальном времени** - используя USB logging ZMK
- 🗺️ **Автоматический парсинг layout** - извлекает информацию из .keymap файлов  
- 🎨 **Красивые визуализации** - генерирует heatmap с подробной статистикой
- 📈 **Детальная аналитика** - количество нажатий, скорость печати, популярные клавиши
- 🚀 **Простота использования** - CLI интерфейс и demo режим

## Быстрый старт

### 1. Установка зависимостей

```bash
cd heatmap
pip install -r requirements.txt
```

### 2. Демо (без реального сбора данных)

```bash
python demo.py
```

Это создаст симулированные данные и покажет как выглядят heatmap'ы.

### 3. Настройка для реального сбора данных

#### Шаг 1: Включить USB Logging

Замените файл `build.yaml` в корне проекта на:

```yaml
---
include:
  - board: eyelash_sofle_left
    shield: nice_view_adapter nice_view_gem
    snippet: zmk-usb-logging
  - board: eyelash_sofle_right
    shield: nice_view_adapter nice_view_gem
```

Или используйте готовый файл:
```bash
cp heatmap/build_heatmap.yaml build.yaml
```

#### Шаг 2: Прошить клавиатуру

Запустите сборку через GitHub Actions или локально:

```bash
# Если сборка локальная
west build -b eyelash_sofle_left -S zmk-usb-logging -- -DSHIELD="nice_view_adapter nice_view_gem"
```

Прошейте левую половину клавиатуры (только она нужна для логирования).

### 4. Сбор данных

#### На Linux/macOS:
```bash
# Найдите ваше устройство
ls /dev/tty* | grep -E "(ACM|usbmodem)"

# Запустите сбор данных (замените device на ваш)
python heatmap_collector.py --device /dev/ttyACM0 --output my_typing_data.json --duration 3600
```

#### На Windows:
```bash
# Проверьте Device Manager для COM порта
python heatmap_collector.py --device COM3 --output my_typing_data.json --duration 3600
```

#### Параметры команды:
- `--device` - путь к серийному устройству  
- `--output` - файл для сохранения данных
- `--duration` - время сбора в секундах (без параметра = бесконечно)
- `--verbose` - подробное логирование

### 5. Генерация heatmap

```bash
# Сгенерировать layout конфигурацию (один раз)
python heatmap_visualizer.py --generate-config --keymap ../config/eyelash_sofle.keymap

# Создать heatmap
python heatmap_visualizer.py --data my_typing_data.json --output beautiful_heatmap.png
```

#### Параметры визуализации:
- `--data` - файл с данными
- `--output` - выходной файл изображения  
- `--colormap` - цветовая схема (YlOrRd, viridis, plasma, magma)
- `--title` - заголовок heatmap
- `--config` - файл конфигурации layout'a

## Структура проекта

```
heatmap/
├── README.md                    # Этот файл
├── requirements.txt             # Python зависимости
├── heatmap_collector.py         # Основной сборщик данных
├── heatmap_visualizer.py        # Генератор heatmap
├── keymap_parser.py            # Парсер .keymap файлов
├── demo.py                     # Демо с фиктивными данными
├── build_heatmap.yaml          # Конфигурация build с USB logging
├── config/
│   └── eyelash_sofle_layout.json # Layout данные
└── data/                       # Директория для данных
    ├── keypress_data.json      # Собранные данные
    └── heatmaps/               # Сгенерированные heatmap'ы
```

## Примеры использования

### Сбор данных на определенное время
```bash
# Собрать данные в течение 1 часа
python heatmap_collector.py --device /dev/ttyACM0 --duration 3600 --output work_session.json
```

### Создание heatmap с кастомным стилем
```bash
# Heatmap с темной темой
python heatmap_visualizer.py --data work_session.json --colormap viridis --title "Work Session Heatmap"
```

### Мониторинг в реальном времени
```bash
# Сбор данных (в одном терминале)
python heatmap_collector.py --device /dev/ttyACM0 --output live_data.json

# Обновление heatmap каждые 5 минут (в другом терминале)
while true; do
    python heatmap_visualizer.py --data live_data.json --output live_heatmap.png
    sleep 300
done
```

## Интерпретация результатов

### Цветовая схема
- **Синий/Холодный** - редко используемые клавиши
- **Зеленый/Желтый** - умеренно используемые  
- **Красный/Горячий** - часто используемые клавиши

### Статистика
- **Total Keypresses** - общее количество нажатий
- **Unique Keys Used** - количество различных клавиш
- **Average Rate** - скорость печати (клавиш/минуту)
- **Most Used Key** - самая активная клавиша

### Анализ паттернов
- Проверьте нагрузку на мизинцы (крайние колонки)
- Оцените использование домашнего ряда
- Найдите недоиспользуемые клавиши для переназначения

## Устранение проблем

### Устройство не найдено
```bash
# Linux: проверьте права доступа
sudo chmod 666 /dev/ttyACM0

# Или добавьте себя в группу dialout
sudo usermod -a -G dialout $USER
```

### Нет данных в логах
1. Убедитесь что USB logging включен в firmware
2. Проверьте что прошивка собрана с правильным snippet
3. Попробуйте переподключить клавиатуру

### Ошибки Python
```bash
# Переустановите зависимости
pip install --upgrade -r requirements.txt
```

## Расширенные возможности

### Кастомизация layout'a
Отредактируйте `config/eyelash_sofle_layout.json` для изменения физического расположения клавиш в визуализации.

### Различные цветовые схемы
Доступные colormap'ы:
- `YlOrRd` (желтый-оранжевый-красный, по умолчанию)
- `viridis` (фиолетовый-синий-зеленый-желтый)  
- `plasma` (фиолетовый-розовый-желтый)
- `magma` (черный-фиолетовый-розовый-желтый)
- `Blues`, `Reds`, `Greens` (монохромные)

### Экспорт данных
Данные сохраняются в JSON формате и могут быть легко импортированы в другие инструменты:

```python
import json
with open('my_typing_data.json', 'r') as f:
    data = json.load(f)
    
# Данные содержат:
# data['total_keypresses'] - общее количество
# data['keypress_data'] - детали по каждой клавише
# data['session_duration_minutes'] - длительность сессии
```

## Безопасность

⚠️ **Важно**: USB logging записывает только события матрицы клавиатуры (row/col/position), НЕ содержимое того что вы печатаете. Ваши пароли и текст в безопасности.

## Вклад в проект

Идеи для развития:
- [ ] Поддержка других layouts клавиатур
- [ ] Анализ по слоям (layer-specific heatmaps)
- [ ] Веб-интерфейс для просмотра
- [ ] Интеграция с QMK
- [ ] Анализ временных паттернов

---

## FAQ

**Q: Влияет ли USB logging на батарею?**  
A: Да, увеличивает потребление. Используйте только для сбора данных, потом прошейте обычную версию.

**Q: Можно ли использовать с другими клавиатурами?**  
A: Да, но нужно создать layout конфигурацию для вашей клавиатуры.

**Q: Сколько данных нужно для репрезентативной статистики?**  
A: Минимум несколько тысяч нажатий. Для полной картины лучше собирать 1-2 недели.

**Q: Можно ли анализировать исторические данные?**  
A: В текущей версии нет, но данные сохраняются с timestamp'ами для будущих улучшений.

---

*Система разработана для анализа эффективности использования клавиатуры и оптимизации layout'ов. Используйте ответственно и наслаждайтесь данными о вашей печати!* 🚀

Created with ❤️ for ZMK community