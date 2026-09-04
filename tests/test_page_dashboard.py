"""Раздел «Дашборд»: метрики, графики и перегенерация данных."""

import random

import flet as ft
import flet_charts as fch
import pytest
from conftest import event, mount, walk

from app.pages import dashboard as dashboard_module
from app.pages.dashboard import EVENTS, WEEK_DAYS, Dashboard


@pytest.fixture
def dashboard(page):
    random.seed(1)
    return mount(Dashboard())


def test_tiles_and_charts_are_filled(dashboard):
    assert len(dashboard.tiles.controls) == 4
    assert len(dashboard.line_chart.data_series) >= 1
    assert len(dashboard.bar_chart.groups) == len(WEEK_DAYS)
    assert len(dashboard.pie_chart.sections) == 4
    assert len(dashboard.pie_legend.controls) == 4


def test_line_chart_follows_series(dashboard):
    points = dashboard.line_chart.data_series[0].points
    assert [p.y for p in points] == dashboard.series


def test_event_feed_lists_every_event(dashboard):
    titles = [c.value for c in walk(dashboard) if isinstance(c, ft.Text)]
    for _, title, _, _ in EVENTS:
        assert title in titles


def test_shuffle_regenerates_data(dashboard):
    before_series = list(dashboard.series)
    before_split = list(dashboard.split)

    dashboard.shuffle()

    assert dashboard.series != before_series
    assert dashboard.split != before_split
    assert sum(dashboard.split) == pytest.approx(100, abs=2)
    assert [p.y for p in dashboard.line_chart.data_series[0].points] == dashboard.series


def test_shuffle_is_wired_to_the_button(page):
    random.seed(3)
    body = mount(dashboard_module.build())
    control = next(c for c in walk(body) if isinstance(c, Dashboard))
    button = next(
        c for c in walk(body) if getattr(c, "content", None) == "Перегенерировать"
    )

    before = list(control.series)
    button.on_click(event(button))
    assert control.series != before


def test_charts_stay_consistent_after_many_shuffles(dashboard):
    for _ in range(10):
        dashboard.shuffle()
        assert len(dashboard.bar_chart.groups) == len(WEEK_DAYS)
        assert all(
            isinstance(section, fch.PieChartSection)
            for section in dashboard.pie_chart.sections
        )
