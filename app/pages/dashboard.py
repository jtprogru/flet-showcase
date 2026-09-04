"""Дашборд: метрики, графики и лента событий с живым обновлением данных."""

import random
from datetime import datetime, timedelta

import flet as ft
import flet_charts as fch

from app.ui import MUTED, page_header, scrollable_page, section, stat_tile

WEEK_DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

EVENTS = [
    (
        ft.Icons.ROCKET_LAUNCH,
        "Деплой v1.4.2",
        "CI прошёл за 3 мин 12 с",
        ft.Colors.GREEN,
    ),
    (
        ft.Icons.BUG_REPORT,
        "Баг #418 закрыт",
        "Гонка при обновлении списка",
        ft.Colors.ORANGE,
    ),
    (
        ft.Icons.PERSON_ADD,
        "Новый участник",
        "К проекту подключился ревьюер",
        ft.Colors.BLUE,
    ),
    (ft.Icons.STORAGE, "Миграция БД", "12 таблиц, простой 0 с", ft.Colors.PURPLE),
    (ft.Icons.SECURITY, "Аудит зависимостей", "Уязвимостей не найдено", ft.Colors.TEAL),
]


class Dashboard(ft.Column):
    """Сводка с перегенерируемыми данными."""

    def build(self):
        self.spacing = 16
        self.series = [random.randint(20, 90) for _ in WEEK_DAYS]
        self.split = [38, 27, 21, 14]

        self.tiles = ft.ResponsiveRow(spacing=12, run_spacing=12)
        self.line_chart = fch.LineChart(expand=True, height=260, interactive=True)
        self.bar_chart = fch.BarChart(expand=True, height=260, interactive=True)
        self.pie_chart = fch.PieChart(expand=True, height=240, sections_space=2)
        self.pie_legend = ft.Column(spacing=6, tight=True)

        self.controls = [
            self.tiles,
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    section(
                        "Активность за неделю",
                        "LineChart с сеткой, подписями осей и заливкой под кривой",
                        [self.line_chart],
                        tags=["LineChart", "ChartAxis", "ChartGridLines"],
                        col={"md": 12, "xl": 8},
                    ),
                    section(
                        "Источники трафика",
                        "PieChart с центральным отверстием и легендой",
                        [self.pie_chart, self.pie_legend],
                        tags=["PieChart", "PieChartSection"],
                        col={"md": 12, "xl": 4},
                    ),
                ],
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    section(
                        "Задачи по дням",
                        "BarChart со скруглёнными столбцами и фоновой подложкой",
                        [self.bar_chart],
                        tags=["BarChart", "BarChartGroup", "BarChartRod"],
                        col={"md": 12, "xl": 7},
                    ),
                    section(
                        "Лента событий",
                        "ListTile с иконками, CircleAvatar и относительным временем",
                        [self._events()],
                        tags=["ListTile", "CircleAvatar", "Badge"],
                        col={"md": 12, "xl": 5},
                    ),
                ],
            ),
        ]
        self._refresh_data()

    def _events(self):
        now = datetime.now()
        return ft.Column(
            spacing=0,
            tight=True,
            controls=[
                ft.ListTile(
                    leading=ft.CircleAvatar(
                        bgcolor=ft.Colors.with_opacity(0.18, color),
                        content=ft.Icon(icon, color=color, size=18),
                    ),
                    title=ft.Text(title, size=14),
                    subtitle=ft.Text(subtitle, size=12, color=MUTED),
                    trailing=ft.Text(
                        (now - timedelta(minutes=7 * (i + 1) ** 2)).strftime("%H:%M"),
                        size=12,
                        color=MUTED,
                    ),
                    dense=True,
                )
                for i, (icon, title, subtitle, color) in enumerate(EVENTS)
            ],
        )

    def _refresh_data(self):
        total = sum(self.series)
        done = int(total * random.uniform(0.55, 0.85))
        self.tiles.controls = [
            ft.Container(
                col={"sm": 6, "xl": 3},
                content=stat_tile(
                    "Задач за неделю",
                    str(total),
                    ft.Icons.TASK_ALT,
                    ft.Colors.PRIMARY,
                    delta=random.uniform(-8, 22),
                ),
            ),
            ft.Container(
                col={"sm": 6, "xl": 3},
                content=stat_tile(
                    "Выполнено",
                    str(done),
                    ft.Icons.CHECK_CIRCLE,
                    ft.Colors.GREEN,
                    delta=random.uniform(-4, 18),
                ),
            ),
            ft.Container(
                col={"sm": 6, "xl": 3},
                content=stat_tile(
                    "Среднее время",
                    f"{random.uniform(1.2, 4.8):.1f} ч",
                    ft.Icons.TIMER_OUTLINED,
                    ft.Colors.ORANGE,
                    delta=random.uniform(-12, 6),
                ),
            ),
            ft.Container(
                col={"sm": 6, "xl": 3},
                content=stat_tile(
                    "Активных участников",
                    str(random.randint(4, 12)),
                    ft.Icons.GROUPS_OUTLINED,
                    ft.Colors.TERTIARY,
                    delta=random.uniform(-2, 9),
                ),
            ),
        ]
        self._build_line()
        self._build_bar()
        self._build_pie()

    def _build_line(self):
        self.line_chart.data_series = [
            fch.LineChartData(
                points=[
                    fch.LineChartDataPoint(x, y) for x, y in enumerate(self.series)
                ],
                curved=True,
                stroke_width=3,
                color=ft.Colors.PRIMARY,
                below_line_gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_CENTER,
                    end=ft.Alignment.BOTTOM_CENTER,
                    colors=[
                        ft.Colors.with_opacity(0.35, ft.Colors.PRIMARY),
                        ft.Colors.with_opacity(0.0, ft.Colors.PRIMARY),
                    ],
                ),
                point=fch.ChartCirclePoint(radius=4, color=ft.Colors.PRIMARY),
            ),
            fch.LineChartData(
                points=[
                    fch.LineChartDataPoint(x, max(5, y - random.randint(5, 30)))
                    for x, y in enumerate(self.series)
                ],
                curved=True,
                stroke_width=2,
                dash_pattern=[6, 4],
                color=ft.Colors.TERTIARY,
            ),
        ]
        self.line_chart.bottom_axis = fch.ChartAxis(
            labels=[
                fch.ChartAxisLabel(value=i, label=ft.Text(day, size=11, color=MUTED))
                for i, day in enumerate(WEEK_DAYS)
            ],
            label_size=28,
        )
        self.line_chart.left_axis = fch.ChartAxis(label_size=36, label_spacing=25)
        self.line_chart.horizontal_grid_lines = fch.ChartGridLines(
            interval=25, color=ft.Colors.OUTLINE_VARIANT, width=1, dash_pattern=[3, 4]
        )
        self.line_chart.min_y = 0
        self.line_chart.max_y = 100

    def _build_bar(self):
        self.bar_chart.groups = [
            fch.BarChartGroup(
                x=i,
                rods=[
                    fch.BarChartRod(
                        to_y=value,
                        width=18,
                        border_radius=6,
                        bg_to_y=100,
                        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.ON_SURFACE),
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment.BOTTOM_CENTER,
                            end=ft.Alignment.TOP_CENTER,
                            colors=[ft.Colors.PRIMARY, ft.Colors.TERTIARY],
                        ),
                        tooltip=f"{WEEK_DAYS[i]}: {value}",
                    )
                ],
            )
            for i, value in enumerate(self.series)
        ]
        self.bar_chart.bottom_axis = fch.ChartAxis(
            labels=[
                fch.ChartAxisLabel(value=i, label=ft.Text(day, size=11, color=MUTED))
                for i, day in enumerate(WEEK_DAYS)
            ],
            label_size=28,
        )
        self.bar_chart.max_y = 100
        self.bar_chart.horizontal_grid_lines = fch.ChartGridLines(
            interval=25, color=ft.Colors.OUTLINE_VARIANT, width=1
        )

    def _build_pie(self):
        names = ["Прямые заходы", "Поиск", "Соцсети", "Реферальные"]
        colors = [
            ft.Colors.PRIMARY,
            ft.Colors.TERTIARY,
            ft.Colors.SECONDARY,
            ft.Colors.ERROR,
        ]
        self.pie_chart.sections = [
            fch.PieChartSection(
                value=value,
                title=f"{value}%",
                radius=58,
                color=color,
                title_style=ft.TextStyle(
                    size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
                ),
            )
            for value, color in zip(self.split, colors, strict=True)
        ]
        self.pie_chart.center_space_radius = 42
        self.pie_legend.controls = [
            ft.Row(
                spacing=8,
                controls=[
                    ft.Container(width=10, height=10, border_radius=3, bgcolor=color),
                    ft.Text(name, size=12, expand=True),
                    ft.Text(f"{value}%", size=12, color=MUTED),
                ],
            )
            for name, value, color in zip(names, self.split, colors, strict=True)
        ]

    def shuffle(self, e=None):
        """Перегенерировать все показатели."""
        self.series = [random.randint(20, 95) for _ in WEEK_DAYS]
        raw = [random.randint(10, 45) for _ in range(4)]
        total = sum(raw)
        self.split = [round(v * 100 / total) for v in raw]
        self._refresh_data()
        self.update()


def build():
    dashboard = Dashboard()
    return scrollable_page(
        ft.Row(
            wrap=True,
            spacing=12,
            run_spacing=8,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                page_header(
                    "Дашборд",
                    "Метрики, графики и лента событий на живых данных",
                    ft.Icons.SPACE_DASHBOARD_ROUNDED,
                ),
                ft.FilledButton(
                    content="Перегенерировать",
                    icon=ft.Icons.CASINO_OUTLINED,
                    on_click=dashboard.shuffle,
                ),
            ],
        ),
        dashboard,
    )
