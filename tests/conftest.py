"""Общая обвязка тестов: подделка страницы и «монтирование» контролов.

Flet разрешает `control.update()` только для контрола, привязанного к Page,
а настоящая Page требует живой сессии с фронтендом. Поэтому в тестах
свойство `page` и метод `update()` подменяются на заглушки — так обработчики
событий выполняются целиком, как в приложении.
"""

import asyncio
import sys
from pathlib import Path

import flet as ft
import pytest
from flet.controls.base_control import BaseControl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class FakeWindow:
    def __init__(self):
        self.width = 1360
        self.height = 900
        self.min_width = 0
        self.min_height = 0
        self.maximized = False
        self.minimized = False
        self.always_on_top = False
        self.centered = False

    async def center(self):
        self.centered = True


class FakeSession:
    """Заглушка сессии: контролы вроде TextField зовут через неё focus()."""

    def __init__(self):
        self.calls = []

    async def invoke_method(
        self, control_id, method_name, arguments=None, timeout=None
    ):
        self.calls.append((control_id, method_name, arguments))
        return None


class FakePage:
    """Минимальная Page: запоминает всё, что приложение с ней делает."""

    def __init__(self):
        self.session = FakeSession()
        self.services = []
        self.overlay = []
        self.dialogs = []
        self.popped = 0
        self.updates = 0
        self.tasks = []
        self._pending = []
        self._draining = False
        self.urls = []
        self.controls = []
        self.registry = {}
        self.window = FakeWindow()
        self.width = 1360
        self.height = 900
        self.web = False
        self.platform = ft.PagePlatform.MACOS
        self.platform_brightness = ft.Brightness.LIGHT
        self.theme = None
        self.dark_theme = None
        self.theme_mode = None
        self.appbar = None
        self.drawer = None
        self.route = "/"
        self.title = ""
        self.padding = None
        self.spacing = None
        self.horizontal_alignment = None
        self.vertical_alignment = None
        self.on_resize = None
        self.on_keyboard_event = None
        self.enable_screenshots = False
        self.drawer_shown = 0

    def update(self, *controls):
        self.updates += 1

    def add(self, *controls):
        """Как настоящая Page: добавленный контрол сразу собирается."""
        for control in controls:
            build_control(control)
        self.controls.extend(controls)
        self.update()

    def register(self, control):
        """Сделать контрол доступным по идентификатору, как это делает Flet."""
        self.registry[control._i] = control
        return control

    def get_control(self, control_id):
        return self.registry.get(control_id)

    def show_dialog(self, dialog):
        self.dialogs.append(dialog)
        return dialog

    def pop_dialog(self):
        self.popped += 1

    async def show_drawer(self, drawer=None):
        self.drawer_shown += 1

    def launch_url(self, url, **kwargs):
        self.urls.append(url)

    def run_task(self, handler, *args):
        """В приложении задача уходит в event loop, в тестах — выполняется сразу.

        Корутины, запущенные изнутри другой корутины, ждут своей очереди:
        вложенный `asyncio.run` внутри работающего цикла невозможен.
        """
        self.tasks.append(handler)
        self._pending.append(handler(*args))
        if self._draining:
            return None
        return self.drain()

    def drain(self):
        """Выполнить накопленные задачи по одной, вне чужого event loop."""
        self._draining = True
        result = None
        try:
            while self._pending:
                result = asyncio.run(self._pending.pop(0))
        finally:
            self._draining = False
        return result

    def close(self):
        """Закрыть корутины, до которых тест не добрался."""
        while self._pending:
            self._pending.pop().close()

    @property
    def last_dialog(self):
        return self.dialogs[-1] if self.dialogs else None


@pytest.fixture
def page(monkeypatch):
    """Подсовывает всем контролам поддельную страницу вместо настоящей."""
    fake = FakePage()
    monkeypatch.setattr(BaseControl, "page", property(lambda self: fake), raising=False)
    monkeypatch.setattr(BaseControl, "update", lambda self: fake.update(self))
    yield fake
    fake.close()


@pytest.fixture
def unmounted(monkeypatch):
    """Контрол вне страницы: `page` и `update()` бросают RuntimeError."""

    def no_page(self):
        raise RuntimeError("Control must be added to the page first")

    monkeypatch.setattr(BaseControl, "page", property(no_page), raising=False)
    return no_page


def event(control, name="click", data=None, **extra):
    """Синтетическое событие Flet для прямого вызова обработчика."""
    return ft.Event(name=name, data=data, control=control, **extra)


def build_control(control):
    """Собрать кастомный контрол так же, как это делает фреймворк."""
    if hasattr(control, "build"):
        control.build()
    return control


CHILD_ATTRS = (
    "controls",
    "content",
    "actions",
    "cancel",
    "items",
    "tabs",
    "leading",
    "trailing",
    "title",
    "subtitle",
    "segments",
    "destinations",
    "cells",
    "rows",
    "columns",
    "label",
)


def children(control):
    """Прямые потомки контрола по всем известным слотам."""
    for attr in CHILD_ATTRS:
        value = getattr(control, attr, None)
        for item in value if isinstance(value, list) else [value]:
            if isinstance(item, BaseControl):
                yield item


def walk(control, seen=None):
    """Обойти дерево контролов вглубь, не зацикливаясь на повторах."""
    seen = set() if seen is None else seen
    if not isinstance(control, BaseControl) or id(control) in seen:
        return
    seen.add(id(control))
    yield control
    for child in children(control):
        yield from walk(child, seen)


def mount(control, seen=None):
    """Собрать контрол и всех потомков — так же поступает фреймворк."""
    seen = set() if seen is None else seen
    if not isinstance(control, BaseControl) or id(control) in seen:
        return control
    seen.add(id(control))
    control.build()
    for child in children(control):
        mount(child, seen)
    return control
