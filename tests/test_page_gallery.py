"""Раздел «Галерея»: поиск по иконкам и цветам, копирование имени."""

import asyncio

import flet as ft
import pytest
from conftest import event, mount

from app.pages.gallery import COLOR_NAMES, ICON_NAMES, MAX_SHOWN, GalleryPage


@pytest.fixture
def gallery(page):
    return mount(GalleryPage())


def test_initial_grids_are_capped(gallery):
    assert len(gallery.icon_grid.controls) == MAX_SHOWN
    assert len(gallery.color_grid.controls) == MAX_SHOWN
    assert gallery.icon_counter.value == (
        f"Найдено {len(ICON_NAMES)}, показаны первые {MAX_SHOWN}"
    )


def test_icon_search_narrows_results(gallery):
    gallery._icon_search(event(ft.TextField(value="rocket"), "change"))
    names = [c.data for c in gallery.icon_grid.controls]
    assert names and all("ROCKET" in name for name in names)
    assert gallery.icon_counter.value == f"Найдено {len(names)}"


def test_icon_search_can_find_nothing(gallery):
    gallery._icon_search(event(ft.TextField(value="такой-иконки-нет"), "change"))
    assert gallery.icon_grid.controls == []
    assert gallery.icon_counter.value == "Найдено 0"


def test_empty_query_restores_full_list(gallery):
    gallery._icon_search(event(ft.TextField(value=None), "change"))
    assert len(gallery.icon_grid.controls) == MAX_SHOWN


def test_color_search(gallery):
    gallery._color_search(event(ft.TextField(value="indigo"), "change"))
    names = [c.data for c in gallery.color_grid.controls]
    assert names and all("INDIGO" in name for name in names)
    assert set(names) <= set(COLOR_NAMES)


@pytest.fixture
def clipboard_writes(monkeypatch):
    """Настоящий ft.Clipboard, но без похода в систему."""
    written = []

    async def fake_set(self, value):
        written.append(value)

    monkeypatch.setattr(ft.Clipboard, "set", fake_set)
    return written


def test_copy_name_uses_clipboard_and_reports(gallery, page, clipboard_writes):
    tile = gallery.icon_grid.controls[0]
    asyncio.run(gallery._copy_name(event(tile)))

    assert clipboard_writes == [tile.data]
    assert page.last_dialog.content == f"Скопировано: {tile.data}"
    assert len(page.services) == 1


def test_clipboard_service_is_registered_once(gallery, page, clipboard_writes):
    for tile in gallery.color_grid.controls[:3]:
        asyncio.run(gallery._copy_name(event(tile)))
    assert len(clipboard_writes) == 3
    assert len(page.services) == 1
