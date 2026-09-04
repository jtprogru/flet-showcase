"""Раздел «Оформление»: seed-цвета, режим темы и шрифт."""

import flet as ft
import pytest
from conftest import event, mount, walk

from app.pages.theming import ThemingPage
from app.theme import SEED_COLORS, ThemeController


@pytest.fixture
def controller(page):
    control = ThemeController()
    control.attach(page)
    return control


@pytest.fixture
def theming(controller):
    return mount(ThemingPage(controller))


def test_seed_swatches_mark_the_active_color(theming, controller):
    assert len(theming.seed_row.controls) == len(SEED_COLORS)
    active = [c for c in theming.seed_row.controls if c.content is not None]
    assert len(active) == 1
    assert active[0].data == controller.seed


def test_clicking_swatch_changes_theme(theming, controller, page):
    swatch = theming.seed_row.controls[3]
    theming._seed_clicked(event(swatch))
    assert controller.seed == swatch.data
    assert page.theme.color_scheme_seed == swatch.data

    active = [c for c in theming.seed_row.controls if c.content is not None]
    assert active[0].data == swatch.data


def test_mode_switch(theming, controller):
    control = ft.SegmentedButton(selected=[ft.ThemeMode.DARK.value], segments=[])
    theming._mode_changed(event(control, "change"))
    assert controller.mode == ft.ThemeMode.DARK
    assert "Тёмная" in theming.mode_label.value


def test_font_switch(theming, controller, page):
    control = ft.SegmentedButton(selected=["Roboto Mono"], segments=[])
    theming._font_changed(event(control, "change"))
    assert controller.font == "Roboto Mono"
    assert page.theme.font_family == "Roboto Mono"

    control.selected = ["default"]
    theming._font_changed(event(control, "change"))
    assert controller.font is None


def test_page_follows_theme_changes_from_appbar(theming, controller):
    controller.toggle_mode()
    assert theming.mode_button.selected == [controller.mode.value]
    assert theming.mode_label.value.startswith("Текущий режим:")


def test_scheme_preview_is_rendered(theming):
    buttons = [c for c in walk(theming) if isinstance(c, ft.FilledButton)]
    assert buttons
    assert any(isinstance(c, ft.Markdown) for c in walk(theming))
