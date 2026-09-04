"""Каркас приложения: боковая навигация, верхняя панель и переключение страниц."""

import random

import flet as ft

from app.pages import (
    about,
    charts,
    cupertino,
    dashboard,
    data,
    feedback,
    gallery,
    graphics,
    inputs,
    services,
    theming,
    todo,
)
from app.theme import SEED_COLORS
from app.ui import MUTED

# Каждый раздел: иконка, выбранная иконка, название и фабрика содержимого.
SECTIONS = [
    (
        ft.Icons.SPACE_DASHBOARD_OUTLINED,
        ft.Icons.SPACE_DASHBOARD,
        "Дашборд",
        lambda ctx: dashboard.build(),
    ),
    (
        ft.Icons.CHECKLIST_OUTLINED,
        ft.Icons.CHECKLIST,
        "Задачи",
        lambda ctx: todo.build(),
    ),
    (
        ft.Icons.KEYBOARD_ALT_OUTLINED,
        ft.Icons.KEYBOARD_ALT,
        "Ввод",
        lambda ctx: inputs.build(),
    ),
    (
        ft.Icons.TABLE_CHART_OUTLINED,
        ft.Icons.TABLE_CHART,
        "Данные",
        lambda ctx: data.build(),
    ),
    (
        ft.Icons.NOTIFICATIONS_NONE,
        ft.Icons.NOTIFICATIONS,
        "Действия",
        lambda ctx: feedback.build(),
    ),
    (
        ft.Icons.INSIGHTS_OUTLINED,
        ft.Icons.INSIGHTS,
        "Графики",
        lambda ctx: charts.build(),
    ),
    (ft.Icons.BRUSH_OUTLINED, ft.Icons.BRUSH, "Графика", lambda ctx: graphics.build()),
    (
        ft.Icons.PALETTE_OUTLINED,
        ft.Icons.PALETTE,
        "Галерея",
        lambda ctx: gallery.build(),
    ),
    (
        ft.Icons.PHONE_IPHONE,
        ft.Icons.PHONE_IPHONE,
        "Cupertino",
        lambda ctx: cupertino.build(),
    ),
    (
        ft.Icons.COLOR_LENS_OUTLINED,
        ft.Icons.COLOR_LENS,
        "Оформление",
        lambda ctx: theming.build(ctx),
    ),
    (
        ft.Icons.SETTINGS_OUTLINED,
        ft.Icons.SETTINGS,
        "Система",
        lambda ctx: services.build(),
    ),
    (ft.Icons.INFO_OUTLINE, ft.Icons.INFO, "О витрине", lambda ctx: about.build()),
]


class Shell(ft.Row):
    """Двухколоночный каркас: NavigationRail слева, содержимое справа."""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.cache = {}

    def build(self):
        self.expand = True
        self.spacing = 0
        self.vertical_alignment = ft.CrossAxisAlignment.STRETCH

        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.NONE,
            extended=True,
            min_width=64,
            min_extended_width=210,
            group_alignment=-0.9,
            scrollable=True,
            on_change=self._rail_changed,
            leading=ft.Container(
                padding=ft.Padding.only(left=4, top=8, bottom=8),
                content=ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=36,
                            height=36,
                            border_radius=12,
                            alignment=ft.Alignment.CENTER,
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment.TOP_LEFT,
                                end=ft.Alignment.BOTTOM_RIGHT,
                                colors=[ft.Colors.PRIMARY, ft.Colors.TERTIARY],
                            ),
                            content=ft.Icon(
                                ft.Icons.WIDGETS, color=ft.Colors.ON_PRIMARY, size=20
                            ),
                        ),
                        ft.Text("Витрина Flet", weight=ft.FontWeight.BOLD),
                    ],
                ),
            ),
            destinations=[
                ft.NavigationRailDestination(
                    icon=icon, selected_icon=selected_icon, label=label
                )
                for icon, selected_icon, label, _ in SECTIONS
            ],
        )

        self.body = ft.AnimatedSwitcher(
            expand=True,
            duration=250,
            reverse_duration=150,
            transition=ft.AnimatedSwitcherTransition.FADE,
            content=self._page_content(0),
        )

        self.controls = [
            self.rail,
            ft.VerticalDivider(width=1),
            ft.Container(
                expand=True,
                # справа чуть больше отступ — под полосу прокрутки
                padding=ft.Padding.only(left=20, right=28, top=16, bottom=16),
                content=self.body,
            ),
        ]

    # --- навигация -----------------------------------------------------

    def _page_content(self, index):
        if index not in self.cache:
            self.cache[index] = SECTIONS[index][3](self.controller)
        return ft.Container(key=str(index), expand=True, content=self.cache[index])

    def _rail_changed(self, e):
        self.select(e.control.selected_index)

    def select(self, index):
        index = max(0, min(index, len(SECTIONS) - 1))
        self.rail.selected_index = index
        self.body.content = self._page_content(index)
        self.update()

    def adapt(self, width):
        """Компактная навигация на узких экранах."""
        extended = width >= 1100
        if self.rail.extended != extended:
            self.rail.extended = extended
            self.rail.label_type = (
                ft.NavigationRailLabelType.NONE
                if extended
                else ft.NavigationRailLabelType.SELECTED
            )
            self.rail.update()


def build_appbar(controller, shell):
    """Верхняя панель с переключателем темы и случайным seed-цветом."""
    theme_button = ft.IconButton(
        icon=ft.Icons.DARK_MODE_OUTLINED,
        tooltip="Светлая или тёмная тема (Ctrl+D)",
        on_click=lambda e: controller.toggle_mode(),
    )

    def sync(ctrl):
        theme_button.icon = (
            ft.Icons.LIGHT_MODE_OUTLINED
            if ctrl.is_dark
            else ft.Icons.DARK_MODE_OUTLINED
        )

    controller.subscribe(sync)
    sync(controller)

    def random_seed(e):
        controller.set_seed(random.choice(list(SEED_COLORS.values())))

    return ft.AppBar(
        title=ft.Text("Витрина компонентов Flet", size=16, weight=ft.FontWeight.W_600),
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        elevation_on_scroll=2,
        actions=[
            ft.Container(
                padding=ft.Padding.only(right=8),
                content=ft.Row(
                    spacing=4,
                    controls=[
                        ft.Text(
                            f"{len(SECTIONS)} разделов",
                            size=12,
                            color=MUTED,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SHUFFLE,
                            tooltip="Случайный seed-цвет темы",
                            on_click=random_seed,
                        ),
                        theme_button,
                        ft.PopupMenuButton(
                            icon=ft.Icons.HELP_OUTLINE,
                            tooltip="Подсказки",
                            items=[
                                ft.PopupMenuItem(
                                    content="Ctrl/Cmd + 1…0 — разделы",
                                    icon=ft.Icons.KEYBOARD,
                                ),
                                ft.PopupMenuItem(
                                    content="Ctrl/Cmd + D — тема",
                                    icon=ft.Icons.CONTRAST,
                                ),
                                ft.PopupMenuItem(
                                    content="Открыть flet.dev",
                                    icon=ft.Icons.OPEN_IN_NEW,
                                    on_click=lambda e: controller.page.launch_url(
                                        "https://flet.dev"
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            )
        ],
    )
