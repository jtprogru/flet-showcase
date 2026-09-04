"""О проекте: что внутри витрины и как её запускать."""

import flet as ft

from app.ui import MUTED, page_header, section

FEATURES = [
    (
        ft.Icons.WIDGETS_OUTLINED,
        "Больше 90 контролов",
        "Material и Cupertino, от кнопок до таблиц и барабанов выбора",
    ),
    (
        ft.Icons.INSIGHTS,
        "Пять типов графиков",
        "Линейный, столбчатый, круговой, точечный и лепестковый из flet-charts",
    ),
    (
        ft.Icons.BRUSH_OUTLINED,
        "Рисование и анимации",
        "Canvas с кистями, анимации свойств, перетаскивание и жесты",
    ),
    (
        ft.Icons.PALETTE_OUTLINED,
        "Живая тема",
        "Seed-цвет и светлый/тёмный режим применяются мгновенно",
    ),
    (
        ft.Icons.DESKTOP_WINDOWS_OUTLINED,
        "Настоящее GUI",
        "Запускается нативным окном и собирается в приложение через flet build",
    ),
    (
        ft.Icons.KEYBOARD_COMMAND_KEY,
        "Горячие клавиши",
        "Ctrl/Cmd+1…0 переключают разделы, Ctrl/Cmd+D меняет тему",
    ),
]

COMMANDS = """
```bash
make install     # поставить зависимости через uv
make run         # запустить как десктопное окно
make run-web     # открыть в браузере
make build-macos # собрать .app для macOS
```
"""


def build():
    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        spacing=16,
        controls=[
            page_header(
                "О витрине",
                "Демонстрация возможностей Flet на одном приложении",
                ft.Icons.INFO_OUTLINE,
            ),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    border_radius=12,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[
                            ft.Colors.PRIMARY_CONTAINER,
                            ft.Colors.TERTIARY_CONTAINER,
                        ],
                    ),
                    content=ft.Column(
                        spacing=8,
                        tight=True,
                        controls=[
                            ft.Text(
                                "Витрина Flet",
                                theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                color=ft.Colors.ON_PRIMARY_CONTAINER,
                            ),
                            ft.Text(
                                "Тринадцать разделов, каждый показывает свою группу "
                                "контролов в работе. Всё интерактивно: меняй значения, "
                                "открывай диалоги, рисуй на холсте и переключай тему.",
                                color=ft.Colors.ON_PRIMARY_CONTAINER,
                            ),
                        ],
                    ),
                )
            ),
            section(
                "Что внутри",
                None,
                [
                    ft.ResponsiveRow(
                        spacing=12,
                        run_spacing=12,
                        controls=[
                            ft.Container(
                                col={"md": 6, "xl": 4},
                                padding=14,
                                border_radius=12,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                                content=ft.Column(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Icon(icon, color=ft.Colors.PRIMARY),
                                        ft.Text(title, weight=ft.FontWeight.BOLD),
                                        ft.Text(text, size=12, color=MUTED),
                                    ],
                                ),
                            )
                            for icon, title, text in FEATURES
                        ],
                    )
                ],
            ),
            section(
                "Как запускать",
                "Зависимости ставятся через uv, запуск и сборка — через make",
                [
                    ft.Markdown(
                        value=COMMANDS,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        code_theme=ft.MarkdownCodeTheme.ATOM_ONE_DARK,
                    ),
                    ft.Row(
                        wrap=True,
                        spacing=8,
                        run_spacing=8,
                        controls=[
                            ft.OutlinedButton(
                                content="flet.dev",
                                icon=ft.Icons.LINK,
                                url="https://flet.dev",
                            ),
                            ft.OutlinedButton(
                                content="Документация контролов",
                                icon=ft.Icons.MENU_BOOK,
                                url="https://flet.dev/docs/controls/",
                            ),
                            ft.OutlinedButton(
                                content="Исходники Flet",
                                icon=ft.Icons.CODE,
                                url="https://github.com/flet-dev/flet",
                            ),
                        ],
                    ),
                ],
                tags=["Markdown", "OutlinedButton", "Url"],
            ),
        ],
    )
