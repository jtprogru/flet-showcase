"""Раздел «Действия»: кнопки, диалоги, шторки, уведомления и меню."""

import asyncio
import inspect

import flet as ft
import pytest
from conftest import event, mount, walk

from app.pages.feedback import FeedbackPage


@pytest.fixture
def feedback(page):
    return mount(FeedbackPage())


def buttons_with(control, label):
    return [c for c in walk(control) if getattr(c, "content", None) == label]


def test_every_button_writes_to_the_log(feedback):
    pressed = [
        c
        for c in walk(feedback)
        if isinstance(c, ft.FilledButton | ft.OutlinedButton | ft.TextButton)
        and c.on_click
        and isinstance(c.content, str)
    ]
    assert pressed

    for button in pressed:
        if inspect.iscoroutinefunction(button.on_click):
            continue
        button.on_click(event(button))
    assert feedback.log.value


def test_like_button_toggles(feedback):
    like = ft.IconButton(selected=False)
    feedback._toggle_like(event(like))
    assert like.selected is True
    assert feedback.log.value == "Лайк поставлен"

    feedback._toggle_like(event(like))
    assert like.selected is False
    assert feedback.log.value == "Лайк снят"


def test_alert_dialog_cancel(feedback, page):
    feedback._open_alert(event(feedback))
    dialog = page.last_dialog
    assert isinstance(dialog, ft.AlertDialog)

    cancel = next(c for c in walk(dialog) if isinstance(c, ft.TextButton))
    cancel.on_click(event(cancel))
    assert page.popped == 1
    assert feedback.log.value == "Диалог закрыт без изменений"


def test_alert_dialog_confirm_shows_undoable_snackbar(feedback, page):
    feedback._open_alert(event(feedback))
    dialog = page.last_dialog
    confirm = next(c for c in walk(dialog) if isinstance(c, ft.FilledButton))
    confirm.on_click(event(confirm))

    snack = page.last_dialog
    assert isinstance(snack, ft.SnackBar)
    assert feedback.log.value == "Подтверждено удаление окружения"

    snack.on_action(event(snack, "action"))
    assert feedback.log.value == "Удаление отменено"


def test_bottom_sheet_actions(feedback, page):
    feedback._open_sheet(event(feedback))
    sheet = page.last_dialog
    assert isinstance(sheet, ft.BottomSheet)

    tiles = [c for c in walk(sheet) if isinstance(c, ft.ListTile)]
    assert len(tiles) == 3

    tiles[1].on_click(event(tiles[1]))
    assert page.popped == 1
    assert feedback.log.value == "Из шторки выбрано: Переименовать"


def test_drawer_is_built_and_shown(feedback, page):
    asyncio.run(feedback._open_drawer(event(feedback)))
    assert isinstance(page.drawer, ft.NavigationDrawer)
    assert page.drawer_shown == 1

    page.drawer.selected_index = 2
    page.drawer.on_change(event(page.drawer, "change"))
    assert feedback.log.value == "В боковой панели выбран пункт №3"


def test_snackbar_action(feedback, page):
    feedback._show_snack(event(feedback))
    snack = page.last_dialog
    assert isinstance(snack, ft.SnackBar)
    assert feedback.log.value == "Показан SnackBar"

    snack.on_action(event(snack, "action"))
    assert feedback.log.value == "Из SnackBar нажали «Открыть»"


def test_banner_closes_from_both_buttons(feedback, page):
    feedback._show_banner(event(feedback))
    banner = page.last_dialog
    assert isinstance(banner, ft.Banner)
    assert feedback.log.value == "Показан Banner"

    for action in banner.actions:
        action.on_click(event(action))
    assert page.popped == 2
    assert feedback.log.value == "Banner закрыт"


def test_menu_items_report_choice(feedback):
    items = [
        c for c in walk(feedback) if isinstance(c, ft.PopupMenuItem) and c.on_click
    ]
    assert items

    items[0].on_click(event(items[0]))
    assert feedback.log.value
