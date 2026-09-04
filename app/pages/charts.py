"""Графики: линии, столбцы, круговая, точечная и лепестковая диаграммы."""

import math
import random

import flet as ft
import flet_charts as fch

from app.ui import MUTED, page_header, section

MONTHS = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг"]


class ChartsPage(ft.Column):
    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True
        self.hint = ft.Text(
            "Наводи курсор на графики — они интерактивные", size=12, color=MUTED
        )

        self.controls = [
            page_header(
                "Графики",
                "Пять типов диаграмм из пакета flet-charts с событиями наведения",
                ft.Icons.INSIGHTS,
            ),
            ft.Card(
                variant=ft.CardVariant.FILLED,
                content=ft.Container(
                    padding=12,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.TOUCH_APP, color=ft.Colors.PRIMARY),
                            self.hint,
                        ],
                    ),
                ),
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    self._line(),
                    self._bar(),
                    self._pie(),
                    self._scatter(),
                    self._radar(),
                ],
            ),
        ]

    def _report(self, text):
        self.hint.value = text
        self.hint.update()

    def _line(self):
        def series(shift, color, curved=True):
            return fch.LineChartData(
                points=[
                    fch.LineChartDataPoint(
                        i, 40 + 30 * math.sin(i / 1.7 + shift) + random.uniform(-4, 4)
                    )
                    for i in range(len(MONTHS))
                ],
                curved=curved,
                color=color,
                stroke_width=3,
                rounded_stroke_cap=True,
                point=fch.ChartCirclePoint(radius=3, color=color),
            )

        chart = fch.LineChart(
            height=280,
            expand=True,
            interactive=True,
            data_series=[
                series(0, ft.Colors.PRIMARY),
                series(1.6, ft.Colors.TERTIARY),
                series(3.2, ft.Colors.ERROR, curved=False),
            ],
            bottom_axis=fch.ChartAxis(
                labels=[
                    fch.ChartAxisLabel(value=i, label=ft.Text(m, size=11, color=MUTED))
                    for i, m in enumerate(MONTHS)
                ],
                label_size=28,
            ),
            left_axis=fch.ChartAxis(label_size=36),
            horizontal_grid_lines=fch.ChartGridLines(
                interval=20,
                color=ft.Colors.OUTLINE_VARIANT,
                width=1,
                dash_pattern=[4, 4],
            ),
            vertical_grid_lines=fch.ChartGridLines(
                interval=1,
                color=ft.Colors.OUTLINE_VARIANT,
                width=1,
                dash_pattern=[4, 4],
            ),
            border=ft.Border.only(
                left=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            ),
            min_y=0,
            max_y=90,
            on_event=lambda e: self._report(
                f"LineChart: серия {e.spots[0].bar_index}, "
                f"точка {e.spots[0].spot_index}"
                if e.spots
                else "LineChart: вне точек"
            ),
        )
        return section(
            "Линейный график",
            "Три серии: сглаженная, пунктирная и ломаная, с сеткой и осями",
            [chart],
            tags=["LineChart", "LineChartData", "ChartCirclePoint"],
            col={"md": 12, "xl": 6},
        )

    def _bar(self):
        values = [random.randint(25, 95) for _ in MONTHS]
        chart = fch.BarChart(
            height=280,
            expand=True,
            interactive=True,
            max_y=100,
            group_spacing=10,
            groups=[
                fch.BarChartGroup(
                    x=i,
                    rods=[
                        fch.BarChartRod(
                            to_y=value,
                            width=14,
                            border_radius=ft.BorderRadius.vertical(top=8),
                            color=ft.Colors.PRIMARY,
                            tooltip=f"{MONTHS[i]}: {value}",
                        ),
                        fch.BarChartRod(
                            to_y=max(10, value - random.randint(10, 30)),
                            width=14,
                            border_radius=ft.BorderRadius.vertical(top=8),
                            color=ft.Colors.TERTIARY,
                            tooltip=f"{MONTHS[i]}: план",
                        ),
                    ],
                )
                for i, value in enumerate(values)
            ],
            bottom_axis=fch.ChartAxis(
                labels=[
                    fch.ChartAxisLabel(value=i, label=ft.Text(m, size=11, color=MUTED))
                    for i, m in enumerate(MONTHS)
                ],
                label_size=28,
            ),
            left_axis=fch.ChartAxis(label_size=36),
            horizontal_grid_lines=fch.ChartGridLines(
                interval=25, color=ft.Colors.OUTLINE_VARIANT, width=1
            ),
            on_event=lambda e: self._report(
                f"BarChart: группа {e.group_index}, столбец {e.rod_index}"
            ),
        )
        return section(
            "Столбчатая диаграмма",
            "Две серии в группе, скруглённые вершины и всплывающие подсказки",
            [chart],
            tags=["BarChart", "BarChartGroup", "BarChartRod"],
            col={"md": 12, "xl": 6},
        )

    def _pie(self):
        self.pie_values = [32, 24, 20, 14, 10]
        self.pie_names = ["Python", "Dart", "SQL", "Bash", "Прочее"]
        self.pie_colors = [
            ft.Colors.BLUE,
            ft.Colors.CYAN,
            ft.Colors.AMBER,
            ft.Colors.GREEN,
            ft.Colors.PURPLE,
        ]
        self.pie = fch.PieChart(
            height=280,
            expand=True,
            sections_space=3,
            center_space_radius=46,
            start_degree_offset=180,
            on_event=self._pie_event,
        )
        self._render_pie(-1)
        return section(
            "Круговая диаграмма",
            "Сектор увеличивается при наведении, в центре — итог",
            [self.pie],
            tags=["PieChart", "PieChartSection"],
            col={"md": 12, "xl": 6},
        )

    def _render_pie(self, active):
        self.pie.sections = [
            fch.PieChartSection(
                value=value,
                title=f"{name}\n{value}%",
                radius=78 if i == active else 66,
                color=color,
                title_style=ft.TextStyle(
                    size=11 if i != active else 13,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
            )
            for i, (name, value, color) in enumerate(
                zip(self.pie_names, self.pie_values, self.pie_colors, strict=True)
            )
        ]

    def _pie_event(self, e):
        self._render_pie(e.section_index)
        self.pie.update()
        if 0 <= e.section_index < len(self.pie_names):
            self._report(
                f"PieChart: {self.pie_names[e.section_index]} — "
                f"{self.pie_values[e.section_index]}%"
            )

    def _scatter(self):
        spots = [
            fch.ScatterChartSpot(
                x=random.uniform(5, 95),
                y=random.uniform(5, 95),
                radius=random.uniform(4, 14),
                color=random.choice(
                    [ft.Colors.PRIMARY, ft.Colors.TERTIARY, ft.Colors.ERROR]
                ),
            )
            for _ in range(28)
        ]
        chart = fch.ScatterChart(
            height=280,
            expand=True,
            spots=spots,
            min_x=0,
            max_x=100,
            min_y=0,
            max_y=100,
            horizontal_grid_lines=fch.ChartGridLines(
                interval=25, color=ft.Colors.OUTLINE_VARIANT, width=1
            ),
            vertical_grid_lines=fch.ChartGridLines(
                interval=25, color=ft.Colors.OUTLINE_VARIANT, width=1
            ),
            left_axis=fch.ChartAxis(label_size=44),
            bottom_axis=fch.ChartAxis(label_size=28),
            on_event=lambda e: self._report(f"ScatterChart: точка {e.spot_index}"),
        )
        return section(
            "Точечная диаграмма",
            "Размер и цвет точки кодируют дополнительные измерения",
            [chart],
            tags=["ScatterChart", "ScatterChartSpot"],
            col={"md": 12, "xl": 6},
        )

    def _radar(self):
        axes = ["Скорость", "Надёжность", "Цена", "Поддержка", "Экосистема", "DX"]
        chart = fch.RadarChart(
            height=300,
            expand=True,
            tick_count=4,
            radar_shape=fch.RadarShape.POLYGON,
            title_text_style=ft.TextStyle(size=11, color=MUTED),
            titles=[fch.RadarChartTitle(text=name, angle=0) for name in axes],
            data_sets=[
                fch.RadarDataSet(
                    fill_color=ft.Colors.with_opacity(0.25, ft.Colors.PRIMARY),
                    border_color=ft.Colors.PRIMARY,
                    entries=[
                        fch.RadarDataSetEntry(value=v) for v in [80, 70, 55, 65, 90, 85]
                    ],
                ),
                fch.RadarDataSet(
                    fill_color=ft.Colors.with_opacity(0.2, ft.Colors.TERTIARY),
                    border_color=ft.Colors.TERTIARY,
                    entries=[
                        fch.RadarDataSetEntry(value=v) for v in [55, 85, 75, 50, 60, 70]
                    ],
                ),
            ],
            on_event=lambda e: self._report("RadarChart: наведение на набор данных"),
        )
        return section(
            "Лепестковая диаграмма",
            "Сравнение двух наборов по шести осям",
            [chart],
            tags=["RadarChart", "RadarDataSet", "RadarChartTitle"],
            col={"md": 12, "xl": 6},
        )


def build():
    return ChartsPage()
