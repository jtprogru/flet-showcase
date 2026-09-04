"""Точка входа: сборка страницы, горячие клавиши и настройки окна."""

import asyncio

import flet as ft

import main as entry


def run_main(page):
    asyncio.run(entry.main(page))
    return page.controls[0]


def test_main_builds_page(page):
    shell = run_main(page)
    assert page.title == "Витрина компонентов Flet"
    assert page.appbar is not None
    assert page.theme is not None
    assert isinstance(shell, ft.Row)
    assert page.on_resize and page.on_keyboard_event


def test_desktop_window_is_sized_and_centered(page):
    run_main(page)
    assert (page.window.width, page.window.height) == (1360, 900)
    assert page.window.min_width == 900
    assert page.window.centered is True


def test_web_run_skips_window_setup(page):
    page.web = True
    run_main(page)
    assert page.window.width == 1360  # значение по умолчанию, окно не трогали
    assert page.window.centered is False


def key_event(key, ctrl=False, meta=False):
    return ft.KeyboardEvent(
        name="keyboard",
        data=None,
        control=None,
        key=key,
        shift=False,
        ctrl=ctrl,
        alt=False,
        meta=meta,
    )


def test_hotkey_toggles_theme(page):
    run_main(page)
    page.on_keyboard_event(key_event("D", ctrl=True))
    assert page.theme_mode == ft.ThemeMode.DARK

    page.on_keyboard_event(key_event("d", meta=True))
    assert page.theme_mode == ft.ThemeMode.LIGHT


def test_hotkeys_switch_sections(page):
    shell = run_main(page)
    page.on_keyboard_event(key_event("3", ctrl=True))
    assert shell.rail.selected_index == 2

    page.on_keyboard_event(key_event("0", ctrl=True))
    assert shell.rail.selected_index == 9


def test_keys_without_modifier_are_ignored(page):
    shell = run_main(page)
    page.on_keyboard_event(key_event("5"))
    assert shell.rail.selected_index == 0


def test_unknown_hotkeys_change_nothing(page):
    shell = run_main(page)
    mode = page.theme_mode
    page.on_keyboard_event(key_event("q", ctrl=True))
    page.on_keyboard_event(key_event("F5", meta=True))
    assert shell.rail.selected_index == 0
    assert page.theme_mode == mode


def test_digit_beyond_section_count_is_ignored(page, monkeypatch):
    shell = run_main(page)
    monkeypatch.setattr(entry, "SECTIONS", entry.SECTIONS[:2])
    page.on_keyboard_event(key_event("9", ctrl=True))
    assert shell.rail.selected_index == 0


def test_resize_switches_rail_mode(page):
    shell = run_main(page)
    page.width = 800
    page.on_resize(None)
    assert shell.rail.extended is False

    page.width = 1200
    page.on_resize(None)
    assert shell.rail.extended is True
