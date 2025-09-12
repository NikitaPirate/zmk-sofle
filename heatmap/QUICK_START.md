# 🚀 Быстрый старт ZMK Heatmap

## Демо (без сборки firmware)

```bash
cd heatmap
./install.sh
```

Это установит зависимости и покажет демо heatmap с симулированными данными.

## Реальный сбор данных

### 1. Включить USB Logging

Замените `build.yaml` в корне проекта:

```bash
cp heatmap/build_heatmap.yaml build.yaml
```

### 2. Прошить клавиатуру  

Через GitHub Actions или локально с новым build.yaml

### 3. Собрать данные

```bash
# Linux/macOS
python3 heatmap_collector.py --device /dev/ttyACM0 --duration 3600

# Windows  
python3 heatmap_collector.py --device COM3 --duration 3600
```

### 4. Создать heatmap

```bash
python3 heatmap_visualizer.py --data keypress_data.json --output my_heatmap.png
```

## Результат

Вы получите:
- 📊 Файл с данными о нажатиях клавиш
- 🎨 Красивую heatmap визуализацию  
- 📈 Подробную статистику использования

---

**Подробности в [README.md](README.md)**