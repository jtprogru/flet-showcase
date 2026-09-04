"""Оформление: тема, палитра ColorScheme, шрифты и разметка Markdown."""

import flet as ft

from app.theme import MODE_TITLES, SEED_COLORS
from app.ui import MUTED, page_header, section

SCHEME_SLOTS = [
    ("primary", ft.Colors.PRIMARY, ft.Colors.ON_PRIMARY),
    ("primary container", ft.Colors.PRIMARY_CONTAINER, ft.Colors.ON_PRIMARY_CONTAINER),
    ("secondary", ft.Colors.SECONDARY, ft.Colors.ON_SECONDARY),
    (
        "secondary container",
        ft.Colors.SECONDARY_CONTAINER,
        ft.Colors.ON_SECONDARY_CONTAINER,
    ),
    ("tertiary", ft.Colors.TERTIARY, ft.Colors.ON_TERTIARY),
    (
        "tertiary container",
        ft.Colors.TERTIARY_CONTAINER,
        ft.Colors.ON_TERTIARY_CONTAINER,
    ),
    ("error", ft.Colors.ERROR, ft.Colors.ON_ERROR),
    ("error container", ft.Colors.ERROR_CONTAINER, ft.Colors.ON_ERROR_CONTAINER),
    ("surface", ft.Colors.SURFACE, ft.Colors.ON_SURFACE),
    ("surface container", ft.Colors.SURFACE_CONTAINER, ft.Colors.ON_SURFACE),
    ("inverse surface", ft.Colors.INVERSE_SURFACE, ft.Colors.ON_INVERSE_SURFACE),
    ("outline", ft.Colors.OUTLINE, ft.Colors.SURFACE),
]

MARKDOWN_SAMPLE = """
# Markdown внутри приложения

Контрол `Markdown` рендерит **жирный**, *курсив*, `код` и списки:

1. Заголовки и абзацы
2. Таблицы и цитаты
3. Подсветку кода

> Цитата: витрина собрана на Flet и запускается как настоящее GUI-приложение.

```python
import flet as ft

def main(page: ft.Page):
    page.add(ft.Text("Привет"))

ft.run(main)
```

| Контрол | Назначение |
|---------|------------|
| `Markdown` | разметка |
| `Theme` | оформление |
"""


class ThemingPage(ft.Column):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True

        self.mode_button = ft.SegmentedButton(
            selected=[self.controller.mode.value],
            allow_multiple_selection=False,
            on_change=self._mode_changed,
            segments=[
                ft.Segment(
                    value=ft.ThemeMode.LIGHT.value,
                    label="Светлая",
                    icon=ft.Icons.LIGHT_MODE,
                ),
                ft.Segment(
                    value=ft.ThemeMode.DARK.value,
                    label="Тёмная",
                    icon=ft.Icons.DARK_MODE,
                ),
                ft.Segment(
                    value=ft.ThemeMode.SYSTEM.value,
                    label="Системная",
                    icon=ft.Icons.BRIGHTNESS_AUTO,
                ),
            ],
        )
        self.seed_row = ft.Row(wrap=True, spacing=10, run_spacing=10)
        self._render_seeds()
        self.mode_label = ft.Text(size=12, color=MUTED)
        self._render_mode_label()
        self.controller.subscribe(self._on_theme_changed)

        self.controls = [
            page_header(
                "Оформление",
                "Тема, палитра Material 3, шрифты и рендер Markdown",
                ft.Icons.COLOR_LENS_OUTLINED,
            ),
            section(
                "Тема приложения",
                "Режим и seed-цвет применяются мгновенно ко всем страницам",
                [
                    self.mode_button,
                    self.mode_label,
                    ft.Divider(height=8),
                    ft.Text("Seed-цвет", size=12, color=MUTED),
                    self.seed_row,
                    ft.Divider(height=8),
                    ft.Text("Шрифт интерфейса", size=12, color=MUTED),
                    ft.SegmentedButton(
                        selected=["default"],
                        allow_multiple_selection=False,
                        on_change=self._font_changed,
                        segments=[
                            ft.Segment(value="default", label="Системный"),
                            ft.Segment(value="monospace", label="Моноширинный"),
                            ft.Segment(value="serif", label="С засечками"),
                        ],
                    ),
                ],
                tags=["Theme", "ThemeMode", "SegmentedButton"],
            ),
            section(
                "Палитра текущей темы",
                "Роли ColorScheme: смени seed-цвет и посмотри, что изменится",
                [self._scheme_grid()],
                tags=["ColorScheme", "Colors"],
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    section(
                        "Как выглядят контролы",
                        "Один и тот же набор в выбранной теме",
                        [self._preview()],
                        tags=["Card", "Chip", "Switch", "Slider"],
                        col={"md": 12, "xl": 5},
                    ),
                    section(
                        "Markdown",
                        "Полноценный рендер разметки с таблицами и подсветкой кода",
                        [
                            ft.Container(
                                padding=12,
                                border_radius=12,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                content=ft.Markdown(
                                    value=MARKDOWN_SAMPLE,
                                    selectable=True,
                                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                    code_theme=ft.MarkdownCodeTheme.ATOM_ONE_DARK,
                                    auto_follow_links=True,
                                ),
                            )
                        ],
                        tags=["Markdown", "MarkdownExtensionSet"],
                        col={"md": 12, "xl": 7},
                    ),
                ],
            ),
        ]

    # --- тема ----------------------------------------------------------

    def _render_seeds(self):
        self.seed_row.controls = [
            ft.Container(
                width=46,
                height=46,
                border_radius=23,
                bgcolor=color,
                data=color,
                ink=True,
                tooltip=name,
                on_click=self._seed_clicked,
                alignment=ft.Alignment.CENTER,
                border=(
                    ft.Border.all(3, ft.Colors.ON_SURFACE)
                    if color == self.controller.seed
                    else None
                ),
                content=(
                    ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=20)
                    if color == self.controller.seed
                    else None
                ),
            )
            for name, color in SEED_COLORS.items()
        ]

    def _render_mode_label(self):
        self.mode_label.value = (
            f"Текущий режим: {MODE_TITLES[self.controller.mode]} "
            f"({'тёмный' if self.controller.is_dark else 'светлый'} на экране)"
        )

    def _seed_clicked(self, e):
        self.controller.set_seed(e.control.data)

    def _mode_changed(self, e):
        value = next(iter(e.control.selected))
        self.controller.set_mode(ft.ThemeMode(value))

    def _font_changed(self, e):
        value = next(iter(e.control.selected))
        self.controller.set_font(None if value == "default" else value)

    def _on_theme_changed(self, controller):
        """Синхронизация с изменениями темы из панели сверху."""
        self.mode_button.selected = [controller.mode.value]
        self._render_mode_label()
        self._render_seeds()

    # --- превью --------------------------------------------------------

    def _scheme_grid(self):
        return ft.ResponsiveRow(
            spacing=8,
            run_spacing=8,
            controls=[
                ft.Container(
                    col={"xs": 6, "sm": 4, "md": 3, "xl": 2},
                    height=64,
                    padding=10,
                    border_radius=10,
                    bgcolor=bg,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    content=ft.Text(name, size=11, color=fg),
                )
                for name, bg, fg in SCHEME_SLOTS
            ],
        )

    def _preview(self):
        return ft.Column(
            spacing=12,
            tight=True,
            controls=[
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.FilledButton(content="Основная"),
                        ft.FilledTonalButton(content="Вторичная"),
                        ft.OutlinedButton(content="Контурная"),
                        ft.TextButton(content="Текстовая"),
                    ],
                ),
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.Chip(label="Тег", leading=ft.Icon(ft.Icons.TAG)),
                        ft.Chip(label="Выбран", selected=True),
                        ft.Switch(value=True),
                        ft.Checkbox(value=True, label="Опция"),
                    ],
                ),
                ft.Slider(value=0.6, label="{value}"),
                ft.ProgressBar(value=0.45, border_radius=6),
                ft.TextField(label="Поле ввода", hint_text="Введи текст", dense=True),
                ft.Card(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.INFO_OUTLINE),
                        title=ft.Text("Карточка в теме"),
                        subtitle=ft.Text("Цвета берутся из ColorScheme", size=12),
                    )
                ),
            ],
        )


def build(controller):
    return ThemingPage(controller)
