"""Общие блоки интерфейса."""

import flet as ft
from conftest import walk

from app.ui import control_tag, page_header, scrollable_page, section, stat_tile


def texts(control):
    return [c.value for c in walk(control) if isinstance(c, ft.Text)]


def test_page_header_shows_title_and_subtitle():
    header = page_header("Картотека", "Список людей", ft.Icons.CONTACTS_OUTLINED)
    assert texts(header) == ["Картотека", "Список людей"]
    icons = [c.icon for c in walk(header) if isinstance(c, ft.Icon)]
    assert icons == [ft.Icons.CONTACTS_OUTLINED]


def test_control_tag_lists_every_name():
    tags = control_tag("Text", "Icon", "Card")
    assert texts(tags) == ["Text", "Icon", "Card"]
    assert tags.wrap is True


def test_section_without_extras():
    card = section("Заголовок")
    assert texts(card) == ["Заголовок"]
    assert card.variant == ft.CardVariant.OUTLINED


def test_section_with_description_tags_and_controls():
    card = section(
        "Заголовок",
        "Описание",
        [ft.Text("Содержимое")],
        tags=["Card"],
        col={"md": 12},
    )
    assert texts(card) == ["Заголовок", "Описание", "Card", "Содержимое"]
    assert card.col == {"md": 12}


def test_scrollable_page_collects_controls():
    body = scrollable_page(ft.Text("Раз"), ft.Text("Два"))
    assert body.expand is True
    assert body.scroll == ft.ScrollMode.ADAPTIVE
    assert len(body.controls) == 2


def test_stat_tile_without_delta():
    tile = stat_tile("Всего", "12", ft.Icons.PEOPLE_OUTLINE, ft.Colors.PRIMARY)
    assert texts(tile) == ["Всего", "12"]


def test_stat_tile_shows_growth_and_decline():
    up = stat_tile("Рост", "10", ft.Icons.INSIGHTS, ft.Colors.PRIMARY, delta=4.2)
    assert "+4.2%" in texts(up)
    assert ft.Icons.TRENDING_UP in [c.icon for c in walk(up) if isinstance(c, ft.Icon)]

    down = stat_tile("Спад", "3", ft.Icons.INSIGHTS, ft.Colors.PRIMARY, delta=-1.5)
    assert "-1.5%" in texts(down)
    assert ft.Icons.TRENDING_DOWN in [
        c.icon for c in walk(down) if isinstance(c, ft.Icon)
    ]
