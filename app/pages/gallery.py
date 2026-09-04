"""Галерея: поиск по иконкам Material, палитра цветов и типографика."""

import flet as ft

from app.ui import MUTED, page_header, section

ICON_NAMES = sorted(n for n in dir(ft.Icons) if n.isupper())
COLOR_NAMES = sorted(n for n in dir(ft.Colors) if n.isupper())
MAX_SHOWN = 180

TEXT_STYLES = [
    ("DISPLAY_SMALL", ft.TextThemeStyle.DISPLAY_SMALL),
    ("HEADLINE_MEDIUM", ft.TextThemeStyle.HEADLINE_MEDIUM),
    ("TITLE_LARGE", ft.TextThemeStyle.TITLE_LARGE),
    ("BODY_LARGE", ft.TextThemeStyle.BODY_LARGE),
    ("BODY_MEDIUM", ft.TextThemeStyle.BODY_MEDIUM),
    ("LABEL_SMALL", ft.TextThemeStyle.LABEL_SMALL),
]


class GalleryPage(ft.Column):
    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True

        self.icon_grid = ft.GridView(
            height=420,
            max_extent=110,
            spacing=8,
            run_spacing=8,
            child_aspect_ratio=0.95,
            build_controls_on_demand=True,
        )
        self.icon_counter = ft.Text(size=12, color=MUTED)
        self.color_grid = ft.GridView(
            height=380,
            max_extent=140,
            spacing=8,
            run_spacing=8,
            child_aspect_ratio=1.6,
            build_controls_on_demand=True,
        )
        self.color_counter = ft.Text(size=12, color=MUTED)
        self._render_icons("")
        self._render_colors("")

        self.controls = [
            page_header(
                "Галерея",
                f"{len(ICON_NAMES)} иконок и {len(COLOR_NAMES)} цветов Material "
                "с поиском",
                ft.Icons.PALETTE_OUTLINED,
            ),
            section(
                "Иконки",
                "Введи часть названия, чтобы отфильтровать. Клик копирует имя иконки",
                [
                    ft.TextField(
                        hint_text="Например: cloud, rocket, arrow",
                        prefix_icon=ft.Icons.SEARCH,
                        dense=True,
                        border_radius=12,
                        on_change=self._icon_search,
                    ),
                    self.icon_counter,
                    self.icon_grid,
                ],
                tags=["Icons", "GridView", "TextField"],
            ),
            section(
                "Цвета",
                "Именованные цвета Material. Клик копирует имя цвета",
                [
                    ft.TextField(
                        hint_text="Например: blue, deep, 300",
                        prefix_icon=ft.Icons.SEARCH,
                        dense=True,
                        border_radius=12,
                        on_change=self._color_search,
                    ),
                    self.color_counter,
                    self.color_grid,
                ],
                tags=["Colors", "Container", "GridView"],
            ),
            section(
                "Типографика",
                "Стили текста из темы Material 3 и оформление через TextSpan",
                [
                    *[
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=170,
                                    content=ft.Text(
                                        name,
                                        size=11,
                                        font_family="monospace",
                                        color=MUTED,
                                    ),
                                ),
                                ft.Text("Витрина Flet", theme_style=style),
                            ],
                        )
                        for name, style in TEXT_STYLES
                    ],
                    ft.Divider(),
                    ft.Text(
                        spans=[
                            ft.TextSpan("Один Text — "),
                            ft.TextSpan(
                                "жирный",
                                ft.TextStyle(weight=ft.FontWeight.BOLD),
                            ),
                            ft.TextSpan(", "),
                            ft.TextSpan(
                                "курсив",
                                ft.TextStyle(italic=True, color=ft.Colors.TERTIARY),
                            ),
                            ft.TextSpan(", "),
                            ft.TextSpan(
                                "подчёркнутый",
                                ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                            ),
                            ft.TextSpan(", "),
                            ft.TextSpan(
                                "зачёркнутый",
                                ft.TextStyle(
                                    decoration=ft.TextDecoration.LINE_THROUGH,
                                    color=ft.Colors.ERROR,
                                ),
                            ),
                            ft.TextSpan(" и "),
                            ft.TextSpan(
                                "моноширинный",
                                ft.TextStyle(
                                    font_family="monospace",
                                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                ),
                            ),
                        ]
                    ),
                    ft.SelectionArea(
                        content=ft.Text(
                            "Этот абзац завёрнут в SelectionArea — текст выделяется "
                            "мышью и копируется как в браузере.",
                            size=13,
                        )
                    ),
                ],
                tags=["TextThemeStyle", "TextSpan", "SelectionArea"],
            ),
        ]

    # --- иконки --------------------------------------------------------

    def _render_icons(self, query):
        query = query.strip().upper()
        matched = [n for n in ICON_NAMES if query in n] if query else ICON_NAMES
        shown = matched[:MAX_SHOWN]
        self.icon_counter.value = (
            f"Найдено {len(matched)}, показаны первые {len(shown)}"
            if len(matched) > len(shown)
            else f"Найдено {len(matched)}"
        )
        self.icon_grid.controls = [
            ft.Container(
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                padding=6,
                ink=True,
                data=name,
                on_click=self._copy_name,
                tooltip=name,
                content=ft.Column(
                    spacing=4,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(getattr(ft.Icons, name), size=24),
                        ft.Text(
                            name.lower(),
                            size=9,
                            color=MUTED,
                            max_lines=2,
                            text_align=ft.TextAlign.CENTER,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
            )
            for name in shown
        ]

    def _icon_search(self, e):
        self._render_icons(e.control.value or "")
        self.icon_grid.update()
        self.icon_counter.update()

    # --- цвета ---------------------------------------------------------

    def _render_colors(self, query):
        query = query.strip().upper()
        matched = [n for n in COLOR_NAMES if query in n] if query else COLOR_NAMES
        shown = matched[:MAX_SHOWN]
        self.color_counter.value = (
            f"Найдено {len(matched)}, показаны первые {len(shown)}"
            if len(matched) > len(shown)
            else f"Найдено {len(matched)}"
        )
        self.color_grid.controls = [
            ft.Container(
                border_radius=10,
                bgcolor=getattr(ft.Colors, name),
                padding=8,
                ink=True,
                data=name,
                on_click=self._copy_name,
                tooltip=name,
                alignment=ft.Alignment.BOTTOM_LEFT,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                content=ft.Container(
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                    border_radius=6,
                    bgcolor=ft.Colors.with_opacity(0.75, ft.Colors.SURFACE),
                    content=ft.Text(name.lower(), size=9, max_lines=1),
                ),
            )
            for name in shown
        ]

    def _color_search(self, e):
        self._render_colors(e.control.value or "")
        self.color_grid.update()
        self.color_counter.update()

    async def _copy_name(self, e):
        name = e.control.data
        clipboard = ft.Clipboard()
        if clipboard not in self.page.services:
            self.page.services.append(clipboard)
        await clipboard.set(name)
        self.page.show_dialog(
            ft.SnackBar(
                content=f"Скопировано: {name}",
                behavior=ft.SnackBarBehavior.FLOATING,
                width=320,
                duration=1500,
            )
        )


def build():
    return GalleryPage()
