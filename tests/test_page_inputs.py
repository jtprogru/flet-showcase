"""Раздел «Ввод»: поля, ползунки, чипы, поиск и системные диалоги."""

import asyncio
import datetime

import flet as ft
import pytest
from conftest import event, mount, walk

from app.pages.inputs import CITIES, InputsPage


@pytest.fixture
def inputs(page):
    return mount(InputsPage())


def test_state_line_starts_with_a_hint(inputs):
    assert "Изменяй контролы" in inputs.state.value


def test_report_shows_control_value(inputs):
    field = ft.TextField(value="Привет")
    inputs._report("TextField")(event(field, "change"))
    assert inputs.state.value == "TextField → 'Привет'"


def test_slider_updates_label_and_state(inputs):
    inputs._slider_changed(event(ft.Slider(value=42.4), "change"))
    assert inputs.slider_value.value == "42"
    assert inputs.state.value == "Slider → 42"


def test_range_slider_reports_both_ends(inputs):
    control = ft.RangeSlider(start_value=20.2, end_value=75.9, min=0, max=100)
    inputs._range_changed(event(control, "change"))
    assert inputs.state.value == "RangeSlider → 20…76"


def test_segmented_button_reports_selection(inputs):
    control = ft.SegmentedButton(selected=["week", "day"], segments=[])
    inputs._segment_changed(event(control, "change"))
    assert inputs.state.value == "SegmentedButton → ['day', 'week']"


def test_chip_selection_and_deletion(inputs):
    chip = inputs.chips.controls[0]
    chip.selected = True
    inputs._chip_selected(event(chip, "select"))
    assert inputs.state.value == "Chip «python» → True"

    inputs._chip_deleted(event(chip, "delete"))
    assert chip not in inputs.chips.controls
    assert inputs.state.value == "Chip «python» удалён"


def test_search_filters_suggestions(inputs):
    inputs.search_bar.value = "каз"
    inputs._search_changed(event(inputs.search_bar, "change"))
    visible = [t.data for t in inputs.search_bar.controls if t.visible]
    assert visible == ["Казань"]

    inputs.search_bar.value = ""
    inputs._search_changed(event(inputs.search_bar, "change"))
    assert len([t for t in inputs.search_bar.controls if t.visible]) == len(CITIES)


def test_search_pick_closes_view_and_writes_state(inputs, page):
    tile = inputs.search_bar.controls[0]
    asyncio.run(inputs._search_pick(event(tile)))

    assert inputs.search_bar.value == tile.data
    assert inputs.state.value == f"SearchBar → {tile.data}"
    assert ("close_view", {"text": tile.data}) in [
        (name, args) for _, name, args in page.session.calls
    ]


def test_tap_opens_suggestion_view(inputs, page):
    asyncio.run(inputs._search_open(event(inputs.search_bar, "tap")))
    assert "open_view" in [name for _, name, _ in page.session.calls]


def test_autocomplete_selection(inputs):
    selection = ft.AutoCompleteSuggestion(key="kazan", value="Казань")
    inputs._autocomplete_selected(
        ft.AutoCompleteSelectEvent(
            name="select", data=None, control=None, selection=selection, index=0
        )
    )
    assert inputs.state.value == "AutoComplete → Казань"


def test_date_picker_dialog_and_result(inputs, page):
    inputs._pick_date(event(inputs))
    picker = page.last_dialog
    assert isinstance(picker, ft.DatePicker)

    picker.value = datetime.datetime(2026, 9, 4)
    inputs._date_selected(event(picker, "change"))
    assert inputs.picker_result.value == "Дата: 04.09.2026"


def test_time_picker_dialog_and_result(inputs, page):
    inputs._pick_time(event(inputs))
    picker = page.last_dialog
    assert isinstance(picker, ft.TimePicker)

    picker.value = datetime.time(14, 30)
    inputs._time_selected(event(picker, "change"))
    assert inputs.picker_result.value == "Время: 14:30"


class FakeFilePicker:
    def __init__(self, files=()):
        self.files = list(files)

    async def pick_files(self, **kwargs):
        return self.files


def test_pick_file_reports_chosen_names(inputs, page):
    picked = [type("F", (), {"name": "report.pdf"})()]
    inputs.file_picker = FakeFilePicker(picked)

    asyncio.run(inputs._pick_file(event(inputs)))
    assert inputs.picker_result.value == "Файл: report.pdf"
    assert inputs.file_picker in page.services


def test_pick_file_registers_service_once(inputs, page):
    inputs.file_picker = FakeFilePicker()
    asyncio.run(inputs._pick_file(event(inputs)))
    asyncio.run(inputs._pick_file(event(inputs)))
    assert page.services.count(inputs.file_picker) == 1


def test_pick_file_reports_cancel(inputs, page):
    inputs.file_picker = FakeFilePicker()
    asyncio.run(inputs._pick_file(event(inputs)))
    assert inputs.picker_result.value == "Выбор файла отменён"


def test_dropdown_options_have_keys(inputs):
    dropdowns = [c for c in walk(inputs) if isinstance(c, ft.Dropdown)]
    assert dropdowns
    for dropdown in dropdowns:
        assert all(option.key for option in dropdown.options)
