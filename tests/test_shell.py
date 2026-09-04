"""Каркас приложения: навигация, кэш страниц и верхняя панель."""

import flet as ft
import pytest
from conftest import build_control, event, walk

from app.shell import SECTIONS, Shell, build_appbar
from app.theme import ThemeController


@pytest.fixture
def controller(page):
    control = ThemeController()
    control.attach(page)
    return control


@pytest.fixture
def shell(controller):
    return build_control(Shell(controller))


def test_sections_catalog():
    assert len(SECTIONS) == 13
    labels = [label for _, _, label, _ in SECTIONS]
    assert labels[:3] == ["Дашборд", "Картотека", "Задачи"]
    assert len(set(labels)) == len(labels)


def test_rail_has_destination_per_section(shell):
    assert len(shell.rail.destinations) == len(SECTIONS)
    assert shell.rail.selected_index == 0
    assert shell.body.content is not None


def test_pages_are_built_once_and_cached(shell):
    first = shell.body.content.content
    shell.select(2)
    assert shell.rail.selected_index == 2

    shell.select(0)
    assert shell.body.content.content is first
    assert len(shell.cache) == 2


def test_select_clamps_index(shell):
    shell.select(-5)
    assert shell.rail.selected_index == 0

    shell.select(999)
    assert shell.rail.selected_index == len(SECTIONS) - 1


def test_rail_change_switches_page(shell):
    shell.rail.selected_index = 4
    shell._rail_changed(event(shell.rail, "change"))
    assert shell.body.content.key == "4"


def test_adapt_collapses_rail_on_narrow_window(shell):
    shell.adapt(900)
    assert shell.rail.extended is False
    assert shell.rail.label_type == ft.NavigationRailLabelType.SELECTED

    shell.adapt(1400)
    assert shell.rail.extended is True
    assert shell.rail.label_type == ft.NavigationRailLabelType.NONE


def test_adapt_does_nothing_when_width_class_is_unchanged(shell, page):
    shell.adapt(1400)
    before = page.updates
    shell.adapt(1300)
    assert page.updates == before


def test_appbar_theme_button_follows_controller(controller, shell, page):
    appbar = build_appbar(controller, shell)
    button = next(
        c
        for c in walk(appbar)
        if isinstance(c, ft.IconButton) and c.icon == ft.Icons.DARK_MODE_OUTLINED
    )

    button.on_click(event(button))
    assert controller.mode == ft.ThemeMode.DARK
    assert button.icon == ft.Icons.LIGHT_MODE_OUTLINED

    button.on_click(event(button))
    assert controller.mode == ft.ThemeMode.LIGHT
    assert button.icon == ft.Icons.DARK_MODE_OUTLINED


def test_appbar_shuffle_changes_seed(controller, shell, page):
    appbar = build_appbar(controller, shell)
    shuffle = next(
        c
        for c in walk(appbar)
        if isinstance(c, ft.IconButton) and c.icon == ft.Icons.SHUFFLE
    )
    seeds = set()
    for _ in range(20):
        shuffle.on_click(event(shuffle))
        seeds.add(controller.seed)
    assert len(seeds) > 1
    assert page.theme.color_scheme_seed == controller.seed


def test_appbar_help_menu_opens_site(controller, shell, page):
    appbar = build_appbar(controller, shell)
    items = [c for c in walk(appbar) if isinstance(c, ft.PopupMenuItem)]
    assert len(items) == 3

    items[-1].on_click(event(items[-1]))
    assert page.urls == ["https://flet.dev"]


def test_appbar_shows_section_count(controller, shell):
    appbar = build_appbar(controller, shell)
    values = [c.value for c in walk(appbar) if isinstance(c, ft.Text)]
    assert f"{len(SECTIONS)} разделов" in values
