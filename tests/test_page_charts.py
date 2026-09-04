"""Раздел «Графики»: подписи событий у всех типов диаграмм.

Обработчики читают поля событий, которых в других типах графиков нет,
поэтому проверяются настоящими объектами событий flet-charts.
"""

import flet_charts as fch
import pytest
from conftest import mount, walk

from app.pages.charts import ChartsPage

TAP = fch.ChartEventType.TAP_UP


@pytest.fixture
def charts(page):
    return mount(ChartsPage())


def test_all_charts_are_built(charts):
    kinds = {type(c).__name__ for c in walk(charts)}
    assert {
        "LineChart",
        "BarChart",
        "PieChart",
        "ScatterChart",
        "RadarChart",
    } <= kinds


def test_line_chart_reports_series_and_point(charts):
    handler = next(c.on_event for c in walk(charts) if isinstance(c, fch.LineChart))
    handler(
        fch.LineChartEvent(
            name="event",
            data=None,
            control=None,
            type=TAP,
            spots=[fch.LineChartEventSpot(bar_index=1, spot_index=4)],
        )
    )
    assert charts.hint.value == "LineChart: серия 1, точка 4"


def test_line_chart_outside_points(charts):
    handler = next(c.on_event for c in walk(charts) if isinstance(c, fch.LineChart))
    handler(
        fch.LineChartEvent(name="event", data=None, control=None, type=TAP, spots=[])
    )
    assert charts.hint.value == "LineChart: вне точек"


def test_bar_chart_reports_group_and_rod(charts):
    handler = next(c.on_event for c in walk(charts) if isinstance(c, fch.BarChart))
    handler(
        fch.BarChartEvent(
            name="event",
            data=None,
            control=None,
            type=TAP,
            group_index=2,
            rod_index=1,
            stack_item_index=-1,
        )
    )
    assert charts.hint.value == "BarChart: группа 2, столбец 1"


def test_pie_chart_highlights_section(charts):
    charts._pie_event(
        fch.PieChartEvent(
            name="event",
            data=None,
            control=None,
            type=TAP,
            section_index=1,
            local_x=0.0,
            local_y=0.0,
        )
    )
    assert charts.hint.value.startswith("PieChart: Dart — ")
    radii = [s.radius for s in charts.pie.sections]
    assert radii[1] == max(radii)


def test_pie_chart_ignores_pointer_outside(charts):
    before = charts.hint.value
    charts._pie_event(
        fch.PieChartEvent(
            name="event",
            data=None,
            control=None,
            type=TAP,
            section_index=-1,
            local_x=0.0,
            local_y=0.0,
        )
    )
    assert charts.hint.value == before
    assert all(section.radius == 66 for section in charts.pie.sections)


def test_scatter_chart_reports_spot(charts):
    handler = next(c.on_event for c in walk(charts) if isinstance(c, fch.ScatterChart))
    handler(
        fch.ScatterChartEvent(
            name="event", data=None, control=None, type=TAP, spot_index=7
        )
    )
    assert charts.hint.value == "ScatterChart: точка 7"


def test_radar_chart_reports_hover(charts):
    handler = next(c.on_event for c in walk(charts) if isinstance(c, fch.RadarChart))
    handler(
        fch.RadarChartEvent(
            name="event",
            data=None,
            control=None,
            type=TAP,
            data_set_index=0,
            entry_index=1,
            entry_value=42.0,
        )
    )
    assert charts.hint.value == "RadarChart: наведение на набор данных"
