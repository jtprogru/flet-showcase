"""Раздел Cupertino: iOS-контролы, диалоги и листы действий."""

import flet as ft
import pytest
from conftest import event, mount, walk

from app.pages.cupertino import CupertinoPage


@pytest.fixture
def cupertino(page):
    return mount(CupertinoPage())


def test_ios_controls_are_present(cupertino):
    kinds = {type(c).__name__ for c in walk(cupertino)}
    assert {
        "CupertinoButton",
        "CupertinoSwitch",
        "CupertinoSlider",
        "CupertinoSegmentedButton",
        "CupertinoListTile",
    } <= kinds


def test_alert_dialog_actions_report_choice(cupertino, page):
    cupertino._open_alert(event(cupertino))
    dialog = page.last_dialog
    assert isinstance(dialog, ft.CupertinoAlertDialog)

    delete = dialog.actions[1]
    delete.on_click(event(delete))
    assert page.popped == 1
    assert cupertino.log.value == "Выбрано: Удалить"


def test_action_sheet_actions_report_choice(cupertino, page):
    cupertino._open_sheet(event(cupertino))
    sheet = page.last_dialog
    assert isinstance(sheet, ft.CupertinoBottomSheet)

    actions = [c for c in walk(sheet) if isinstance(c, ft.CupertinoActionSheetAction)]
    labels = [a.content for a in actions]
    assert labels == ["Открыть", "Дублировать", "Удалить", "Отмена"]

    for action in actions:
        action.on_click(event(action))
    assert cupertino.log.value == "Выбрано: Отмена"
    assert page.popped == len(actions)


def test_buttons_and_toggles_write_to_log(cupertino):
    handlers = [
        (c, name)
        for c in walk(cupertino)
        for name in ("on_click", "on_change")
        if getattr(c, name, None) is not None
        and not isinstance(c, ft.CupertinoDialogAction)
    ]
    assert handlers

    for control, name in handlers:
        getattr(control, name)(event(control, name.removeprefix("on_")))
    assert cupertino.log.value
