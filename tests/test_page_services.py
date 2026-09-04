"""Раздел «Система»: буфер обмена, хранилище, окно, скриншот, платформа."""

import asyncio

import pytest
from conftest import event, mount, walk

from app.pages.services import ServicesPage


class FakeClipboard:
    def __init__(self, value=None):
        self.value = value

    async def set(self, value):
        self.value = value

    async def get(self):
        return self.value


class FakePrefs:
    def __init__(self):
        self.storage = {}

    async def set(self, key, value):
        self.storage[key] = value

    async def get(self, key):
        return self.storage.get(key)

    async def clear(self):
        self.storage.clear()


class FakeHaptic:
    def __init__(self):
        self.calls = 0

    async def medium_impact(self):
        self.calls += 1


class FakeScreenshot:
    async def capture(self, **kwargs):
        return "data:image/png;base64,AAAA"


@pytest.fixture
def services(page):
    control = mount(ServicesPage())
    control.clipboard = FakeClipboard()
    control.prefs = FakePrefs()
    control.haptic = FakeHaptic()
    control.shot_target = FakeScreenshot()
    return control


def test_did_mount_registers_services(page):
    control = mount(ServicesPage())
    control.did_mount()
    assert control.clipboard in page.services
    assert control.prefs in page.services
    assert control.haptic in page.services
    assert page.enable_screenshots is True
    assert len(control.platform_info.controls) == 5


def test_did_mount_twice_keeps_one_copy_of_each_service(page):
    control = mount(ServicesPage())
    control.did_mount()
    control.did_mount()
    assert page.services.count(control.clipboard) == 1
    assert len(page.services) == 3


def test_platform_info_reflects_page_state(page):
    page.web = True
    page.route = "/showcase"
    control = mount(ServicesPage())
    control.did_mount()

    values = [row.controls[1].value for row in control.platform_info.controls]
    assert "браузер" in values
    assert "/showcase" in values
    assert "1360 × 900" in values


def test_copy_writes_to_clipboard(services):
    services.clipboard_field.value = "Скопируй меня"
    asyncio.run(services._copy(event(services)))
    assert services.clipboard.value == "Скопируй меня"
    assert services.clipboard_result.value == "Скопировано в системный буфер"


def test_paste_reads_from_clipboard(services):
    services.clipboard.value = "Из буфера"
    asyncio.run(services._paste(event(services)))
    assert services.clipboard_field.value == "Из буфера"
    assert "9 символов" in services.clipboard_result.value


def test_paste_handles_empty_clipboard(services):
    services.clipboard.value = None
    asyncio.run(services._paste(event(services)))
    assert services.clipboard_field.value == ""
    assert "0 символов" in services.clipboard_result.value


def test_prefs_save_load_clear(services):
    services.prefs_field.value = "запомни это"
    asyncio.run(services._prefs_save(event(services)))
    assert services.prefs.storage == {"demo_value": "запомни это"}
    assert services.prefs_result.value == "Сохранено под ключом demo_value"

    asyncio.run(services._prefs_load(event(services)))
    assert services.prefs_result.value == "Прочитано: 'запомни это'"

    asyncio.run(services._prefs_clear(event(services)))
    assert services.prefs.storage == {}
    assert services.prefs_result.value == "Хранилище очищено"

    asyncio.run(services._prefs_load(event(services)))
    assert services.prefs_result.value == "Ключ пока не сохранён"


def test_window_buttons(services, page):
    services._resize_window(event(services))
    assert (page.window.width, page.window.height) == (1280, 860)

    services._maximize(event(services))
    assert page.window.maximized is True
    services._maximize(event(services))
    assert page.window.maximized is False

    services._minimize(event(services))
    assert page.window.minimized is True


def test_always_on_top_toggles_and_explains(services, page):
    services._always_on_top(event(services))
    assert page.window.always_on_top is True
    assert page.last_dialog.content == "Окно закреплено поверх всех"

    services._always_on_top(event(services))
    assert page.window.always_on_top is False
    assert page.last_dialog.content == "Окно ведёт себя обычно"


def test_capture_shows_screenshot(services):
    asyncio.run(services._capture(event(services)))
    assert services.shot_image.src.startswith("data:image/png")
    assert services.shot_image.visible is True


def test_vibrate_calls_haptic(services):
    asyncio.run(services._vibrate(event(services)))
    assert services.haptic.calls == 1


def test_docs_button_opens_site(services, page):
    button = next(
        c for c in walk(services) if getattr(c, "content", None) == "Документация Flet"
    )
    button.on_click(event(button))
    assert page.urls == ["https://flet.dev/docs/"]
