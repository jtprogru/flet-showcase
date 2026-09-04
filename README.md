# Витрина компонентов Flet

Интерактивная демонстрация возможностей [Flet](https://flet.dev) на одном приложении: 13 разделов, больше 90 контролов Material и Cupertino, пять типов графиков, картотека людей с полным CRUD, рисование на Canvas, анимации и живая смена темы. Запускается нативным окном и собирается в настоящее GUI-приложение.

![Дашборд витрины](docs/screenshots/dashboard.png)

## Быстрый старт

```bash
make install   # зависимости через uv
make run       # нативное окно (GUI)
make run-web   # то же самое в браузере
```

## Что нужно установить

Чтобы запустить приложение из исходников, хватает четырёх системных инструментов:

| Инструмент | Версия | Зачем |
|------------|--------|-------|
| Python | 3.10+ (разработка идёт на 3.14, зафиксирован в `.python-version`) | сам код |
| [uv](https://docs.astral.sh/uv/) | 0.12+ | окружение и зависимости, ставит нужный Python сам |
| GNU Make | любая | точки входа проекта (`make run`, `make test`, …) |
| git | любая | получить репозиторий |

Всё остальное — Python-пакеты, они приезжают по `make install` (`uv sync --all-groups`) с точными версиями из `pyproject.toml` и `uv.lock`:

| Группа | Пакеты |
|--------|--------|
| runtime | `flet==0.86.5`, `flet-charts==0.86.5` |
| dev | `flet-cli==0.86.5`, `flet-desktop==0.86.5`, `flet-web==0.86.5` |
| test | `pytest==9.1.1`, `pytest-cov==7.1.0` |
| lint | `ruff==0.16.6`, `mypy==2.3.1` |

`flet-desktop` тянет с собой готовый Flutter-клиент — отдельно ставить Flutter для `make run` не нужно. Он понадобится только для сборки GUI, см. ниже.

## Что внутри

| Раздел | Что показывает | Ключевые контролы |
|--------|----------------|-------------------|
| Дашборд | метрики, три графика, лента событий, перегенерация данных | `Card`, `ResponsiveRow`, `LineChart`, `BarChart`, `PieChart`, `ListTile` |
| Картотека | список студентов и преподавателей: поиск, фильтры, три представления, создание, правка, удаление с отменой, экспорт CSV | `DataTable`, `ListView`, `Dismissible`, `AlertDialog`, `BottomSheet`, `SharedPreferences`, `PieChart` |
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

Картотека — единственный раздел с настоящей моделью данных: одна и та же запись живёт в списке, таблице и карточках, правится через диалог с валидацией, удаляется свайпом или из меню (с кнопкой «Вернуть» в SnackBar) и переживает перезапуск приложения благодаря `SharedPreferences`.

Тема (светлая/тёмная и seed-цвет) применяется мгновенно ко всем разделам сразу. Горячие клавиши: `Ctrl/Cmd + 1…0` — переход к разделу, `Ctrl/Cmd + D` — переключение темы.

## Как это выглядит

| Картотека | Форма записи |
|-----------|--------------|
| ![Картотека](docs/screenshots/people.png) | ![Правка записи](docs/screenshots/people-editor.png) |

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
app/people/          картотека: модель, хранилище, формы и представления
tests/               pytest: логика, обработчики событий и сборка разделов
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

Первая сборка скачивает Flutter SDK в `~/flutter` (около 3.8 ГБ) — это происходит один раз, дальше сборки быстрые. Заложи ещё несколько гигабайт под артефакты в `build/`.

Обе сборки проверены на macOS 26.6 (Apple Silicon):

- `make build-web` → `build/web`: самодостаточное приложение на Pyodide, работает без Python-сервера (достаточно `python3 -m http.server` из этой папки);
- `make build-macos` → `build/macos/flet-showcase.app`: нативное приложение (~306 МБ), запускается двойным кликом.

### Системные зависимости для сборки

Каждая платформа собирается только на себе: `.app` — на macOS, `.exe` — на Windows, бинарник Linux — на Linux. Web собирается везде и ничего дополнительного не требует.

**macOS** (проверено на этой машине):

```bash
sudo softwareupdate --install-rosetta --agree-to-license  # Apple Silicon
# Xcode 15+ ставится из App Store, затем
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
brew install cocoapods                                    # 1.16+
```

Нужен именно полный Xcode, а не Command Line Tools. Без CocoaPods сборка падает с `CocoaPods not installed or not in valid state` — флаг `--swift-package-manager` эту зависимость не снимает, потому что шаблон Flet всё ещё содержит `Podfile`.

**Linux** (Debian/Ubuntu) — GTK, GStreamer и toolchain для компиляции нативных плагинов:

```bash
sudo apt update
sudo apt install -y \
  binutils clang cmake gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 \
  gstreamer1.0-libav gstreamer1.0-plugins-bad gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly \
  gstreamer1.0-pulseaudio gstreamer1.0-qt5 gstreamer1.0-tools \
  gstreamer1.0-x libasound2-dev libgstreamer-plugins-bad1.0-dev \
  libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libgtk-3-dev \
  libmpv-dev libsecret-1-0 libsecret-1-dev libunwind-dev lld llvm mpv \
  ninja-build pkg-config
```

Актуальный список всегда знает сам Flet, так что скрипт установки можно не поддерживать руками:

```bash
sudo apt install -y $(uv run flet --version --json | jq -r '.linux_dependencies | join(" ")')
```

**Windows** — Visual Studio 2022 или 2026 с рабочей нагрузкой «Desktop development with C++». Ещё нужен режим разработчика (`start ms-settings:developers`), иначе сборка с плагинами упадёт на symlink'ах.

## Разработка

```bash
make fmt        # ruff format + автофиксы
make lint       # проверка без изменений
make typecheck  # mypy по main.py, app и tests
make test       # pytest
make test-cov   # pytest с покрытием, порог 80%
make smoke      # собрать все разделы без запуска GUI
make check      # lint + test + smoke
```

Версии всех зависимостей закреплены точно (`==`) в `pyproject.toml`, разрешённое дерево лежит в `uv.lock`, версия интерпретатора — в `.python-version`. Обновление версии делается осознанно: правишь `pyproject.toml`, прогоняешь `make install` и `make check`.

## Тесты

`make test` прогоняет 305 тестов, `make test-cov` считает покрытие (сейчас 100% строк и ветвей при пороге 80%).

Настоящую `Page` создать без работающего фронтенда нельзя, поэтому `tests/conftest.py` подменяет свойство `page` и метод `update()` заглушками. За счёт этого обработчики событий выполняются целиком, как в приложении: тесты кликают по кнопкам, свайпают карточки, сортируют таблицы и открывают диалоги, а `FakePage` запоминает показанные `SnackBar`, `AlertDialog` и `BottomSheet`.

Отдельно проверяются события графиков (`LineChartEvent`, `BarChartEvent`, `PieChartEvent` и остальные создаются настоящими классами `flet-charts`) — именно такие ошибки не ловятся ни линтером, ни сборкой страниц.

## Лицензия

[PolyForm Noncommercial 1.0.0](LICENSE) — тестовое демонстрационное приложение, подготовленное как учебный проект для МТИ. Разрешено любое некоммерческое использование: обучение, исследования, личное изучение, работа образовательных учреждений. Коммерческое использование лицензией не покрывается.
