"""Каждый раздел витрины собирается и содержит осмысленное наполнение."""

import flet as ft
import pytest
from conftest import mount, walk

from app.shell import SECTIONS
from app.theme import ThemeController

SECTION_IDS = [label for _, _, label, _ in SECTIONS]


@pytest.fixture
def controller(page):
    control = ThemeController()
    control.attach(page)
    return control


@pytest.fixture(params=range(len(SECTIONS)), ids=SECTION_IDS)
def built_section(request, controller):
    return mount(SECTIONS[request.param][3](controller))


def test_section_builds_with_controls(built_section):
    controls = list(walk(built_section))
    assert len(controls) > 10


def test_section_has_visible_text(built_section):
    texts = [c.value for c in walk(built_section) if isinstance(c, ft.Text)]
    assert any(isinstance(value, str) and value.strip() for value in texts)


def test_section_handlers_are_callable(built_section):
    handlers = [
        getattr(c, name)
        for c in walk(built_section)
        for name in ("on_click", "on_change", "on_select", "on_submit")
        if getattr(c, name, None) is not None
    ]
    assert all(callable(h) for h in handlers)


def test_every_section_is_unique(controller):
    pages = [mount(factory(controller)) for _, _, _, factory in SECTIONS]
    assert len({id(p) for p in pages}) == len(SECTIONS)
