"""Контроллер темы: режим, seed-цвет, шрифт и подписчики."""

import flet as ft
import pytest

from app.theme import MODE_TITLES, SEED_COLORS, ThemeController


@pytest.fixture
def controller(page):
    control = ThemeController()
    control.attach(page)
    return control


def test_attach_applies_theme_without_page_update(page):
    controller = ThemeController(seed=ft.Colors.TEAL, mode=ft.ThemeMode.DARK)
    controller.attach(page)
    assert page.theme.color_scheme_seed == ft.Colors.TEAL
    assert page.dark_theme.color_scheme_seed == ft.Colors.TEAL
    assert page.theme_mode == ft.ThemeMode.DARK
    assert page.updates == 0


def test_apply_without_page_is_a_noop():
    ThemeController().apply()  # страница ещё не привязана — просто выходим


def test_set_seed_updates_page(controller, page):
    controller.set_seed(ft.Colors.PINK)
    assert page.theme.color_scheme_seed == ft.Colors.PINK
    assert page.updates == 1


def test_set_mode_updates_page(controller, page):
    controller.set_mode(ft.ThemeMode.LIGHT)
    assert page.theme_mode == ft.ThemeMode.LIGHT


def test_set_font_goes_into_both_themes(controller, page):
    controller.set_font("Roboto Mono")
    assert page.theme.font_family == "Roboto Mono"
    assert page.dark_theme.font_family == "Roboto Mono"


@pytest.mark.parametrize(
    ("start", "expected"),
    [
        (ft.ThemeMode.SYSTEM, ft.ThemeMode.DARK),
        (ft.ThemeMode.LIGHT, ft.ThemeMode.DARK),
        (ft.ThemeMode.DARK, ft.ThemeMode.LIGHT),
    ],
)
def test_toggle_mode(page, start, expected):
    controller = ThemeController(mode=start)
    controller.attach(page)
    controller.toggle_mode()
    assert controller.mode == expected


def test_is_dark_follows_system_brightness(controller, page):
    controller.mode = ft.ThemeMode.SYSTEM
    page.platform_brightness = ft.Brightness.DARK
    assert controller.is_dark is True

    page.platform_brightness = ft.Brightness.LIGHT
    assert controller.is_dark is False


def test_is_dark_without_page():
    controller = ThemeController(mode=ft.ThemeMode.SYSTEM)
    assert controller.is_dark is False
    assert ThemeController(mode=ft.ThemeMode.DARK).is_dark is True


def test_subscribers_get_the_controller(controller):
    seen = []
    controller.subscribe(seen.append)
    controller.set_seed(ft.Colors.GREEN)
    controller.toggle_mode()
    assert seen == [controller, controller]


def test_catalogs_are_filled():
    assert len(SEED_COLORS) == 8
    assert set(MODE_TITLES) == {
        ft.ThemeMode.LIGHT,
        ft.ThemeMode.DARK,
        ft.ThemeMode.SYSTEM,
    }
