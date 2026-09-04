"""Раздел «Данные»: сортировка таблицы, выделение, перестановка и свайпы."""

import flet as ft
import pytest
from conftest import event, mount, walk

from app.pages.data import SERVERS, DataPage


@pytest.fixture
def data_page(page):
    return mount(DataPage())


def sort_event(control, column_index, ascending):
    return ft.DataColumnSortEvent(
        name="sort",
        data=None,
        control=control,
        column_index=column_index,
        ascending=ascending,
    )


def hosts(data_page):
    return [row.cells[0].content.value for row in data_page.table.rows]


def test_table_is_filled_from_source(data_page):
    assert len(data_page.table.rows) == len(SERVERS)
    assert hosts(data_page) == [row[0] for row in SERVERS]


def test_sorting_by_host_and_cpu(data_page):
    data_page._sort(sort_event(data_page.table, 0, False))
    assert hosts(data_page) == sorted([r[0] for r in SERVERS], reverse=True)
    assert data_page.table.sort_column_index == 0
    assert data_page.table.sort_ascending is False

    data_page._sort(sort_event(data_page.table, 3, True))
    cpus = [row[3] for row in data_page.rows_data]
    assert cpus == sorted(cpus)


def test_row_selection_counts_checked_rows(data_page):
    first, second = data_page.table.rows[0], data_page.table.rows[1]
    data_page._row_selected(event(first, "select"))
    assert first.selected is True
    assert data_page.selection_label.value == "Выделено строк: 1"

    data_page._row_selected(event(second, "select"))
    assert data_page.selection_label.value == "Выделено строк: 2"

    data_page._row_selected(event(first, "select"))
    assert first.selected is False
    assert data_page.selection_label.value == "Выделено строк: 1"


def test_reorder_moves_step_and_updates_hint(data_page):
    titles = [c.title.value for c in data_page.reorder_list.controls]
    data_page._reordered(
        ft.OnReorderEvent(
            name="reorder", data=None, control=None, old_index=0, new_index=2
        )
    )
    moved = [c.title.value for c in data_page.reorder_list.controls]
    assert moved[2] == titles[0]
    assert data_page.reorder_hint.value.startswith("Новый порядок: ")
    assert moved[0] in data_page.reorder_hint.value


def test_dismiss_removes_card_and_restore_brings_them_back(data_page):
    assert len(data_page.dismiss_column.controls) == 4
    victim = data_page.dismiss_column.controls[1]

    data_page._dismissed(event(victim, "dismiss"))
    assert victim not in data_page.dismiss_column.controls
    assert len(data_page.dismiss_column.controls) == 3

    data_page._restore_dismissibles(event(data_page))
    assert len(data_page.dismiss_column.controls) == 4


def test_status_chips_cover_every_state(data_page):
    labels = {c.value for c in walk(data_page.table) if isinstance(c, ft.Text)}
    assert {"работает", "деградация", "остановлен"} <= labels


def test_usage_bars_are_normalised(data_page):
    bars = [c for c in walk(data_page.table) if isinstance(c, ft.ProgressBar)]
    assert bars
    assert all(0 <= bar.value <= 1 for bar in bars)


def test_grid_and_expansions_are_present(data_page):
    assert any(isinstance(c, ft.GridView) for c in walk(data_page))
    assert any(isinstance(c, ft.ExpansionTile) for c in walk(data_page))
    assert any(isinstance(c, ft.ExpansionPanelList) for c in walk(data_page))
