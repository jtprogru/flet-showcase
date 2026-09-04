"""Картотека людей: поиск, фильтры, три представления и полный CRUD."""

import flet as ft
import flet_charts as fch

from app.people.forms import PersonEditor, details_sheet
from app.people.models import ROLES, Person
from app.people.store import SORTS, PeopleStore
from app.people.views import cards_view, empty_state, list_view, table_view
from app.ui import MUTED, page_header, section, stat_tile

VIEWS = {
    "list": ("Список", ft.Icons.VIEW_LIST_OUTLINED),
    "table": ("Таблица", ft.Icons.TABLE_ROWS_OUTLINED),
    "cards": ("Карточки", ft.Icons.GRID_VIEW_OUTLINED),
}

TABLE_SORT_KEYS = ["name", "role_title", "group", "city", "rating"]

ROLE_COLORS = {
    "student": ft.Colors.PRIMARY,
    "senior": ft.Colors.TERTIARY,
    "teacher": ft.Colors.SECONDARY,
}


class PeoplePage(ft.Column):
    """Одна сущность — четыре способа с ней работать."""

    def __init__(self):
        super().__init__()
        self.store = PeopleStore()
        self.search = ""
        self.role = "all"
        self.only_favorites = False
        self.sort = "name"
        self.view_mode = "list"
        self.table_sort_index = 0
        self.table_sort_ascending = True
        self.file_picker = ft.FilePicker()

    # --- разметка ------------------------------------------------------

    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True

        self.search_field = ft.TextField(
            hint_text="Поиск по имени, почте, группе или городу",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            border_radius=12,
            expand=True,
            on_change=self._search_changed,
        )
        self.role_filter = ft.SegmentedButton(
            selected=["all"],
            allow_multiple_selection=False,
            on_change=self._role_changed,
            segments=[
                ft.Segment(value="all", label="Все", icon=ft.Icons.GROUPS_OUTLINED),
                *[ft.Segment(value=code, label=title) for code, title in ROLES.items()],
            ],
        )
        self.favorites_switch = ft.Switch(
            label="Только избранные",
            value=False,
            on_change=self._favorites_changed,
        )
        self.sort_dropdown = ft.Dropdown(
            label="Сортировка",
            value="name",
            width=210,
            leading_icon=ft.Icons.SORT,
            options=[
                ft.DropdownOption(key=code, text=title)
                for code, (title, _) in SORTS.items()
            ],
            on_select=self._sort_changed,
        )
        self.view_switch = ft.SegmentedButton(
            selected=["list"],
            allow_multiple_selection=False,
            on_change=self._view_changed,
            segments=[
                ft.Segment(value=code, label=title, icon=icon)
                for code, (title, icon) in VIEWS.items()
            ],
        )

        self.tiles = ft.ResponsiveRow(spacing=12, run_spacing=12)
        self.roles_chart = fch.PieChart(
            height=180, sections_space=2, center_space_radius=34
        )
        self.roles_legend = ft.Column(spacing=6, tight=True)
        self.groups_chart = fch.BarChart(height=180, max_y=10, interactive=True)
        self.view_holder = ft.Container()
        self.counter = ft.Text(size=12, color=MUTED)

        self.controls = [
            ft.Row(
                wrap=True,
                spacing=12,
                run_spacing=8,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    page_header(
                        "Картотека",
                        "Список студентов и преподавателей: поиск, правка, удаление",
                        ft.Icons.CONTACTS_OUTLINED,
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.OutlinedButton(
                                content="Экспорт CSV",
                                icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
                                on_click=self._export_csv,
                            ),
                            ft.OutlinedButton(
                                content="Демо-данные",
                                icon=ft.Icons.RESTART_ALT,
                                on_click=self._reset,
                            ),
                            ft.FilledButton(
                                content="Добавить",
                                icon=ft.Icons.PERSON_ADD_ALT,
                                on_click=self._create,
                            ),
                        ],
                    ),
                ],
            ),
            self.tiles,
            section(
                "Список людей",
                "Поиск, фильтры и три представления одних и тех же записей",
                [
                    # без wrap: внутри строки лежит поле с expand,
                    # а Wrap во Flutter не умеет растягивать детей
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[self.search_field, self.sort_dropdown],
                    ),
                    ft.Row(
                        wrap=True,
                        spacing=12,
                        run_spacing=8,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                wrap=True,
                                spacing=12,
                                run_spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[self.role_filter, self.favorites_switch],
                            ),
                            self.view_switch,
                        ],
                    ),
                    self.counter,
                    self.view_holder,
                ],
                tags=[
                    "DataTable",
                    "ListView",
                    "Dismissible",
                    "AlertDialog",
                    "BottomSheet",
                    "SharedPreferences",
                ],
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    section(
                        "Кто в картотеке",
                        "Доли ролей пересчитываются при каждой правке",
                        [self.roles_chart, self.roles_legend],
                        tags=["PieChart"],
                        col={"md": 12, "xl": 5},
                    ),
                    section(
                        "Люди по группам",
                        "BarChart строится прямо из данных картотеки",
                        [self.groups_chart],
                        tags=["BarChart"],
                        col={"md": 12, "xl": 7},
                    ),
                ],
            ),
        ]

        self.store.subscribe(self.refresh)
        self.refresh(update=False)

    def did_mount(self):
        """Подтянуть сохранённую картотеку и подключить выбор файлов."""
        if self.file_picker not in self.page.services:
            self.page.services.append(self.file_picker)
        self.page.run_task(self._load)

    async def _load(self):
        await self.store.attach(self.page)

    # --- перерисовка ---------------------------------------------------

    def refresh(self, update=True):
        people = self.store.query(
            search=self.search,
            role=self.role,
            only_favorites=self.only_favorites,
            sort=self.sort,
        )
        self._render_stats()
        self._render_view(people)
        total = len(self.store.people)
        self.counter.value = (
            f"Показано {len(people)} из {total}"
            if len(people) != total
            else f"Всего записей: {total}"
        )
        if update and self._mounted():
            self.update()
            self.page.run_task(self.store.persist)

    def _mounted(self):
        """Страница может получить уведомление раньше, чем попадёт на экран."""
        try:
            return self.page is not None
        except RuntimeError:
            return False

    def _render_stats(self):
        stats = self.store.stats()
        self.tiles.controls = [
            ft.Container(
                col={"sm": 6, "xl": 3},
                content=stat_tile(
                    "Всего людей",
                    str(stats["total"]),
                    ft.Icons.PEOPLE_OUTLINE,
                    ft.Colors.PRIMARY,
                ),
            ),
            ft.Container(
                col={"sm": 6, "xl": 3},
                content=stat_tile(
                    "Активных",
                    str(stats["active"]),
                    ft.Icons.HOW_TO_REG_OUTLINED,
                    ft.Colors.GREEN,
                ),
            ),
            ft.Container(
                col={"sm": 6, "xl": 3},
                content=stat_tile(
                    "В избранном",
                    str(stats["favorites"]),
                    ft.Icons.STAR_OUTLINE,
                    ft.Colors.AMBER,
                ),
            ),
            ft.Container(
                col={"sm": 6, "xl": 3},
                content=stat_tile(
                    "Средний рейтинг",
                    str(stats["rating"]),
                    ft.Icons.INSIGHTS,
                    ft.Colors.TERTIARY,
                ),
            ),
        ]

        by_role = self.store.by_role()
        total = sum(by_role.values()) or 1
        self.roles_chart.sections = [
            fch.PieChartSection(
                value=count,
                title=f"{round(count * 100 / total)}%",
                radius=52,
                color=ROLE_COLORS.get(code, ft.Colors.PRIMARY),
                title_style=ft.TextStyle(
                    size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
                ),
            )
            for code, count in by_role.items()
        ]
        self.roles_legend.controls = [
            ft.Row(
                spacing=8,
                controls=[
                    ft.Container(
                        width=10,
                        height=10,
                        border_radius=3,
                        bgcolor=ROLE_COLORS.get(code, ft.Colors.PRIMARY),
                    ),
                    ft.Text(ROLES.get(code, code), size=12, expand=True),
                    ft.Text(str(count), size=12, color=MUTED),
                ],
            )
            for code, count in by_role.items()
        ]

        by_group = self.store.by_group()
        names = list(by_group)
        self.groups_chart.groups = [
            fch.BarChartGroup(
                x=index,
                rods=[
                    fch.BarChartRod(
                        to_y=count,
                        width=20,
                        border_radius=ft.BorderRadius.vertical(top=6),
                        color=ft.Colors.PRIMARY,
                        tooltip=f"{name}: {count}",
                    )
                ],
            )
            for index, (name, count) in enumerate(by_group.items())
        ]
        self.groups_chart.bottom_axis = fch.ChartAxis(
            labels=[
                fch.ChartAxisLabel(
                    value=index, label=ft.Text(name, size=10, color=MUTED)
                )
                for index, name in enumerate(names)
            ],
            label_size=26,
        )
        self.groups_chart.left_axis = fch.ChartAxis(label_size=28)
        self.groups_chart.max_y = max(by_group.values(), default=1) + 1

    def _render_view(self, people):
        actions = {
            "on_open": self._open_details,
            "on_edit": self._edit,
            "on_delete": self._confirm_delete,
            "on_toggle_favorite": self._toggle_favorite,
            "on_dismiss": self._dismissed,
            "on_sort": self._table_sorted,
        }
        if not people:
            self.view_holder.content = empty_state(
                "Под фильтры никто не подходит", self._reset_filters
            )
            return
        if self.view_mode == "table":
            people = sorted(
                people,
                key=lambda p: getattr(p, TABLE_SORT_KEYS[self.table_sort_index]),
                reverse=not self.table_sort_ascending,
            )
            self.view_holder.content = table_view(
                people, actions, self.table_sort_index, self.table_sort_ascending
            )
        elif self.view_mode == "cards":
            self.view_holder.content = cards_view(people, actions)
        else:
            self.view_holder.content = list_view(people, actions)

    # --- фильтры -------------------------------------------------------

    def _search_changed(self, e):
        self.search = e.control.value or ""
        self.refresh()

    def _role_changed(self, e):
        self.role = next(iter(e.control.selected), "all")
        self.refresh()

    def _favorites_changed(self, e):
        self.only_favorites = e.control.value
        self.refresh()

    def _sort_changed(self, e):
        self.sort = e.control.value or "name"
        self.refresh()

    def _view_changed(self, e):
        self.view_mode = next(iter(e.control.selected), "list")
        self.refresh()

    def _table_sorted(self, e):
        self.table_sort_index = min(e.column_index, len(TABLE_SORT_KEYS) - 1)
        self.table_sort_ascending = e.ascending
        self.refresh()

    def _reset_filters(self, e):
        self.search = ""
        self.role = "all"
        self.only_favorites = False
        self.search_field.value = ""
        self.role_filter.selected = ["all"]
        self.favorites_switch.value = False
        self.refresh()

    # --- действия ------------------------------------------------------

    def _toggle_favorite(self, e):
        self.store.toggle_favorite(e.control.data)

    def _open_details(self, e):
        person = self.store.get(e.control.data)
        if person is None:
            return
        sheet = details_sheet(
            person,
            on_edit=lambda _: self._edit_from_sheet(person.id),
            on_delete=lambda _: self._delete_from_sheet(person.id),
            on_close=lambda _: self.page.pop_dialog(),
        )
        self.page.show_dialog(sheet)

    def _edit_from_sheet(self, person_id):
        self.page.pop_dialog()
        self._open_editor(self.store.get(person_id), "Правка записи")

    def _delete_from_sheet(self, person_id):
        self.page.pop_dialog()
        self._delete(person_id)

    def _create(self, e):
        person = Person(id=self.store.next_id(), name="")
        self._open_editor(person, "Новая запись", is_new=True)

    def _edit(self, e):
        person = self.store.get(e.control.data)
        if person is not None:
            self._open_editor(person, "Правка записи")

    def _open_editor(self, person, title, is_new=False):
        editor = PersonEditor(
            person,
            on_save=lambda updated: self._save(updated, is_new),
            on_cancel=self.page.pop_dialog,
            title=title,
        )
        self.page.show_dialog(editor.dialog)

    def _save(self, person, is_new):
        self.page.pop_dialog()
        if is_new:
            self.store.add(person)
            self._toast(f"Добавлен: {person.name}")
        else:
            self.store.update(person)
            self._toast(f"Сохранено: {person.name}")

    def _confirm_delete(self, e):
        self._delete(e.control.data)

    def _dismissed(self, e):
        """Свайп по карточке удаляет запись сразу, но с возможностью отмены."""
        self._delete(e.control.data, already_removed_from_view=True)

    def _delete(self, person_id, already_removed_from_view=False):
        index, person = self.store.delete(person_id)
        if person is None:
            return
        self.page.show_dialog(
            ft.SnackBar(
                content=f"Удалён: {person.name}",
                behavior=ft.SnackBarBehavior.FLOATING,
                width=380,
                duration=4000,
                action=ft.SnackBarAction(label="Вернуть"),
                on_action=lambda e: self._restore(index, person),
            )
        )

    def _restore(self, index, person):
        self.store.restore(index, person)
        self._toast(f"Запись возвращена: {person.name}")

    def _reset(self, e):
        self.store.reset()
        self._toast("Картотека заполнена демо-данными")

    async def _export_csv(self, e):
        """Сохранить текущую выборку в CSV через системный диалог."""
        people = self.store.query(
            search=self.search,
            role=self.role,
            only_favorites=self.only_favorites,
            sort=self.sort,
        )
        header = "name;role;group;email;phone;city;rating;active;favorite;added"
        rows = [
            ";".join(
                [
                    p.name,
                    p.role_title,
                    p.group,
                    p.email,
                    p.phone,
                    p.city,
                    str(p.rating),
                    "да" if p.active else "нет",
                    "да" if p.favorite else "нет",
                    p.added,
                ]
            )
            for p in people
        ]
        payload = "\n".join([header, *rows]).encode("utf-8")
        path = await self.file_picker.save_file(
            dialog_title="Куда сохранить картотеку",
            file_name="people.csv",
            allowed_extensions=["csv"],
            src_bytes=payload,
        )
        self._toast(
            f"Сохранено в {path}" if path else "Экспорт отменён",
        )

    def _toast(self, message):
        self.page.show_dialog(
            ft.SnackBar(
                content=message,
                behavior=ft.SnackBarBehavior.FLOATING,
                width=380,
                duration=2500,
            )
        )


def build():
    return PeoplePage()
