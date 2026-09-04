"""Отображение данных: таблица с сортировкой, списки, сетка, drag-and-drop."""

import flet as ft

from app.ui import MUTED, page_header, section

SERVERS = [
    ("web-01", "Frankfurt", "running", 34, 61),
    ("web-02", "Frankfurt", "running", 51, 72),
    ("db-master", "Amsterdam", "running", 78, 84),
    ("db-replica", "Amsterdam", "degraded", 92, 88),
    ("cache-01", "Warsaw", "running", 12, 40),
    ("worker-01", "Warsaw", "stopped", 0, 5),
    ("worker-02", "Helsinki", "running", 44, 55),
    ("gateway", "Helsinki", "running", 23, 38),
]

STATUS_STYLE = {
    "running": ("работает", ft.Colors.GREEN),
    "degraded": ("деградация", ft.Colors.ORANGE),
    "stopped": ("остановлен", ft.Colors.RED),
}


class DataPage(ft.Column):
    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True
        self.rows_data = list(SERVERS)
        self.sort_index = 0
        self.sort_asc = True

        self.table = ft.DataTable(
            show_checkbox_column=True,
            sort_column_index=0,
            sort_ascending=True,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=12,
            horizontal_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            column_spacing=24,
            columns=[
                ft.DataColumn(label=ft.Text("Хост"), on_sort=self._sort),
                ft.DataColumn(label=ft.Text("Регион"), on_sort=self._sort),
                ft.DataColumn(label=ft.Text("Статус"), on_sort=self._sort),
                ft.DataColumn(label=ft.Text("CPU %"), numeric=True, on_sort=self._sort),
                ft.DataColumn(label=ft.Text("RAM %"), numeric=True, on_sort=self._sort),
            ],
        )
        self.selection_label = ft.Text("Выделено строк: 0", size=12, color=MUTED)
        self._fill_table()

        self.reorder_list = ft.ReorderableListView(
            expand=False,
            height=230,
            spacing=4,
            on_reorder=self._reordered,
            controls=[
                ft.ListTile(
                    leading=ft.Icon(icon),
                    title=ft.Text(title),
                    subtitle=ft.Text(subtitle, size=12, color=MUTED),
                    dense=True,
                )
                for icon, title, subtitle in [
                    (ft.Icons.LOOKS_ONE, "Собрать образ", "docker build"),
                    (ft.Icons.LOOKS_TWO, "Прогнать тесты", "pytest -q"),
                    (ft.Icons.LOOKS_3, "Выкатить на stage", "helm upgrade"),
                    (ft.Icons.LOOKS_4, "Прогнать smoke", "curl /healthz"),
                    (ft.Icons.LOOKS_5, "Выкатить в прод", "helm upgrade --prod"),
                ]
            ],
        )
        self.reorder_hint = ft.Text(
            "Перетащи строку за ручку справа", size=12, color=MUTED
        )

        self.dismiss_column = ft.Column(spacing=6, tight=True)
        self._fill_dismissibles()

        self.controls = [
            page_header(
                "Данные",
                "Таблица с сортировкой и выбором, списки, сетка и перетаскивание",
                ft.Icons.TABLE_CHART_OUTLINED,
            ),
            section(
                "Таблица серверов",
                "Клик по заголовку сортирует, чекбоксы выделяют строки",
                [
                    ft.Row(
                        scroll=ft.ScrollMode.ADAPTIVE,
                        controls=[self.table],
                    ),
                    self.selection_label,
                ],
                tags=["DataTable", "DataColumn", "DataRow", "DataCell"],
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    section(
                        "Перетаскивание элементов",
                        "ReorderableListView меняет порядок шагов пайплайна",
                        [self.reorder_list, self.reorder_hint],
                        tags=["ReorderableListView", "ListTile"],
                        col={"md": 12, "xl": 6},
                    ),
                    section(
                        "Свайп для удаления",
                        "Dismissible убирает карточку жестом влево или вправо",
                        [
                            self.dismiss_column,
                            ft.TextButton(
                                content="Вернуть все",
                                icon=ft.Icons.RESTORE,
                                on_click=self._restore_dismissibles,
                            ),
                        ],
                        tags=["Dismissible", "Card"],
                        col={"md": 12, "xl": 6},
                    ),
                    section(
                        "Сетка",
                        "GridView с адаптивным числом колонок",
                        [self._grid()],
                        tags=["GridView", "Container"],
                        col={"md": 12, "xl": 6},
                    ),
                    section(
                        "Раскрывающиеся блоки",
                        "ExpansionTile и ExpansionPanelList для длинного контента",
                        [self._expansions()],
                        tags=["ExpansionTile", "ExpansionPanelList", "ExpansionPanel"],
                        col={"md": 12, "xl": 6},
                    ),
                ],
            ),
        ]

    # --- таблица -------------------------------------------------------

    def _status_chip(self, status):
        title, color = STATUS_STYLE[status]
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=10, vertical=3),
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.16, color),
            content=ft.Row(
                tight=True,
                spacing=6,
                controls=[
                    ft.Container(width=8, height=8, border_radius=4, bgcolor=color),
                    ft.Text(title, size=12, color=color),
                ],
            ),
        )

    def _usage_bar(self, value):
        color = (
            ft.Colors.RED
            if value >= 85
            else ft.Colors.ORANGE
            if value >= 60
            else ft.Colors.GREEN
        )
        return ft.Row(
            tight=True,
            spacing=8,
            controls=[
                ft.Text(f"{value}", size=12),
                ft.ProgressBar(
                    value=value / 100, width=70, height=6, border_radius=4, color=color
                ),
            ],
        )

    def _fill_table(self):
        self.table.rows = [
            ft.DataRow(
                on_select_change=self._row_selected,
                cells=[
                    ft.DataCell(ft.Text(host, weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(region)),
                    ft.DataCell(self._status_chip(status)),
                    ft.DataCell(self._usage_bar(cpu)),
                    ft.DataCell(self._usage_bar(ram)),
                ],
            )
            for host, region, status, cpu, ram in self.rows_data
        ]

    def _sort(self, e):
        self.sort_index = e.column_index
        self.sort_asc = e.ascending
        self.rows_data.sort(key=lambda r: r[self.sort_index], reverse=not e.ascending)
        self.table.sort_column_index = e.column_index
        self.table.sort_ascending = e.ascending
        self._fill_table()
        self.table.update()

    def _row_selected(self, e):
        e.control.selected = not e.control.selected
        selected = sum(1 for row in self.table.rows if row.selected)
        self.selection_label.value = f"Выделено строк: {selected}"
        self.table.update()
        self.selection_label.update()

    # --- прочие блоки --------------------------------------------------

    def _reordered(self, e):
        control = self.reorder_list.controls.pop(e.old_index)
        self.reorder_list.controls.insert(e.new_index, control)
        order = ", ".join(c.title.value for c in self.reorder_list.controls)
        self.reorder_hint.value = f"Новый порядок: {order}"
        self.reorder_list.update()
        self.reorder_hint.update()

    def _fill_dismissibles(self):
        palette = [ft.Colors.BLUE, ft.Colors.PURPLE, ft.Colors.TEAL, ft.Colors.ORANGE]
        self.dismiss_column.controls = [
            ft.Dismissible(
                on_dismiss=self._dismissed,
                background=ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.RED),
                    border_radius=12,
                    alignment=ft.Alignment.CENTER_LEFT,
                    padding=16,
                    content=ft.Icon(ft.Icons.DELETE_SWEEP, color=ft.Colors.RED),
                ),
                content=ft.Card(
                    variant=ft.CardVariant.FILLED,
                    content=ft.ListTile(
                        leading=ft.CircleAvatar(
                            bgcolor=ft.Colors.with_opacity(0.18, color),
                            content=ft.Icon(
                                ft.Icons.MAIL_OUTLINE, color=color, size=18
                            ),
                        ),
                        title=ft.Text(f"Уведомление №{i + 1}"),
                        subtitle=ft.Text("Свайпни, чтобы убрать", size=12, color=MUTED),
                        dense=True,
                    ),
                ),
            )
            for i, color in enumerate(palette)
        ]

    def _dismissed(self, e):
        self.dismiss_column.controls.remove(e.control)
        self.dismiss_column.update()

    def _restore_dismissibles(self, e):
        self._fill_dismissibles()
        self.dismiss_column.update()

    def _grid(self):
        icons = [
            ft.Icons.CLOUD,
            ft.Icons.DNS,
            ft.Icons.MEMORY,
            ft.Icons.ROUTER,
            ft.Icons.STORAGE,
            ft.Icons.LAN,
            ft.Icons.SECURITY,
            ft.Icons.SPEED,
            ft.Icons.BACKUP,
            ft.Icons.MONITOR_HEART,
            ft.Icons.HUB,
            ft.Icons.TERMINAL,
        ]
        return ft.GridView(
            height=240,
            runs_count=4,
            max_extent=110,
            spacing=8,
            run_spacing=8,
            child_aspect_ratio=1.0,
            controls=[
                ft.Container(
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                    alignment=ft.Alignment.CENTER,
                    ink=True,
                    tooltip=str(icon).split(".")[-1].lower(),
                    on_click=lambda e: None,
                    content=ft.Column(
                        tight=True,
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(icon, size=26, color=ft.Colors.PRIMARY),
                            ft.Text(f"node-{i + 1:02d}", size=11, color=MUTED),
                        ],
                    ),
                )
                for i, icon in enumerate(icons)
            ],
        )

    def _expansions(self):
        return ft.Column(
            spacing=8,
            tight=True,
            controls=[
                ft.ExpansionTile(
                    title=ft.Text("Что внутри витрины"),
                    subtitle=ft.Text("ExpansionTile с иконкой", size=12, color=MUTED),
                    leading=ft.Icon(ft.Icons.WIDGETS_OUTLINED),
                    affinity=ft.TileAffinity.LEADING,
                    controls=[
                        ft.ListTile(title=ft.Text("Больше 90 контролов Flet")),
                        ft.ListTile(title=ft.Text("Пять типов графиков")),
                        ft.ListTile(title=ft.Text("Рисование на Canvas")),
                    ],
                ),
                ft.ExpansionPanelList(
                    expand_icon_color=ft.Colors.PRIMARY,
                    elevation=1,
                    controls=[
                        ft.ExpansionPanel(
                            header=ft.ListTile(title=ft.Text(f"Панель {i}")),
                            content=ft.Container(
                                padding=16,
                                content=ft.Text(
                                    "Содержимое панели раскрывается по клику "
                                    "на заголовок или стрелку справа.",
                                    size=12,
                                ),
                            ),
                        )
                        for i in (1, 2)
                    ],
                ),
            ],
        )


def build():
    return DataPage()
