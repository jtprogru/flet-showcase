# Витрина компонентов Flet

Интерактивная демонстрация возможностей [Flet](https://flet.dev) на одном приложении: 12 разделов, больше 90 контролов Material и Cupertino, пять типов графиков, рисование на Canvas, анимации и живая смена темы. Запускается нативным окном и собирается в настоящее GUI-приложение.

![Дашборд витрины](docs/screenshots/dashboard.png)

## Быстрый старт

```bash
make install   # зависимости через uv
make run       # нативное окно (GUI)
make run-web   # то же самое в браузере
```

## Что внутри

| Раздел | Что показывает | Ключевые контролы |
|--------|----------------|-------------------|
| Дашборд | метрики, три графика, лента событий, перегенерация данных | `Card`, `ResponsiveRow`, `LineChart`, `BarChart`, `PieChart`, `ListTile` |
| Задачи | классический TodoMVC с приоритетами, фильтрами и прогрессом | `Checkbox`, `TextField`, `TabBar`, `PopupMenuButton`, `ProgressBar` |
| Ввод | текстовые поля, переключатели, ползунки, поиск, выбор даты и файлов | `TextField`, `Dropdown`, `Slider`, `RangeSlider`, `SegmentedButton`, `Chip`, `SearchBar`, `AutoComplete`, `DatePicker`, `TimePicker`, `FilePicker` |
| Данные | таблица с сортировкой и выделением, drag-and-drop, свайпы, сетка | `DataTable`, `ReorderableListView`, `Dismissible`, `GridView`, `ExpansionTile`, `ExpansionPanelList` |
| Действия | все виды кнопок, диалоги, уведомления, меню, подсказки | `FilledButton`, `AlertDialog`, `BottomSheet`, `NavigationDrawer`, `SnackBar`, `Banner`, `MenuBar`, `Tooltip`, `Badge` |
| Графики | пять типов диаграмм с событиями наведения | `LineChart`, `BarChart`, `PieChart`, `ScatterChart`, `RadarChart` |
| Графика | рисование мышью, фигуры, анимации, перетаскивание, слои | `Canvas`, `GestureDetector`, `Draggable`, `DragTarget`, `AnimatedSwitcher`, `Shimmer`, `ShaderMask`, `InteractiveViewer`, `Stack` |
| Галерея | 8825 иконок и 352 цвета с поиском, типографика | `Icons`, `Colors`, `GridView`, `TextSpan`, `SelectionArea` |
| Cupertino | те же сценарии в оформлении iOS | `CupertinoButton`, `CupertinoSwitch`, `CupertinoPicker`, `CupertinoAlertDialog`, `CupertinoActionSheet`, `CupertinoListTile` |
| Оформление | режим темы, seed-цвет, шрифт, палитра ColorScheme, Markdown | `Theme`, `ColorScheme`, `Markdown` |
| Система | буфер обмена, локальное хранилище, окно, скриншот, платформа | `Clipboard`, `SharedPreferences`, `Screenshot`, `Window`, `HapticFeedback` |
| О витрине | что внутри и как запускать | `Markdown`, `Card` |

Тема (светлая/тёмная и seed-цвет) применяется мгновенно ко всем разделам сразу. Горячие клавиши: `Ctrl/Cmd + 1…0` — переход к разделу, `Ctrl/Cmd + D` — переключение темы.

## Как это выглядит

| Графики | Системные возможности |
|---------|----------------------|
| ![Графики](docs/screenshots/charts.png) | ![Система](docs/screenshots/services.png) |

## Структура

```
main.py              точка входа: страница, окно, горячие клавиши
app/shell.py         каркас: NavigationRail, AppBar, переключение разделов
app/theme.py         контроллер темы (режим, seed-цвет, шрифт)
app/ui.py            общие блоки: заголовки страниц, секции, плитки метрик
app/pages/*.py       по одному модулю на раздел
```

Раздел добавляется одной строкой в `SECTIONS` внутри `app/shell.py` — фабрика возвращает любой контрол.

## Сборка GUI

```bash
make build-macos    # .app для macOS
make build-linux    # приложение для Linux
make build-windows  # приложение для Windows
make build-web      # статическая web-версия
make build-matrix   # какие платформы доступны с текущей машины
```

Первая сборка скачивает Flutter SDK в `~/flutter` (около 3.8 ГБ) — это происходит один раз, дальше сборки быстрые.

Обе сборки проверены на macOS 26.6 (Apple Silicon):

- `make build-web` → `build/web`: самодостаточное приложение на Pyodide, работает без Python-сервера (достаточно `python3 -m http.server` из этой папки);
- `make build-macos` → `build/macos/flet-showcase.app`: нативное приложение (~306 МБ), запускается двойным кликом.

Для сборки под macOS нужны полный Xcode (не только Command Line Tools) и CocoaPods:

```bash
# Xcode ставится из App Store, затем
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
brew install cocoapods
```

Без CocoaPods сборка падает с `CocoaPods not installed or not in valid state` — флаг `--swift-package-manager` эту зависимость не снимает, потому что шаблон Flet всё ещё содержит `Podfile`.

## Разработка

```bash
make fmt     # ruff format + автофиксы
make lint    # проверка без изменений
make smoke   # собрать все разделы без запуска GUI
make check   # lint + smoke
```

Зависимости: `flet` и `flet-charts`, dev-группа — `flet-cli`, `flet-desktop`, `flet-web`. Всё ставится через `uv sync --all-groups`.
