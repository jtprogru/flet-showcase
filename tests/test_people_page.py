"""Страница картотеки: фильтры, представления и действия над записями."""

import flet as ft
import pytest
from conftest import build_control, event, walk

from app.pages.people import PeoplePage
from app.people.models import Person


class FakeFilePicker:
    """Заглушка FilePicker: запоминает содержимое и возвращает заданный путь."""

    def __init__(self, result="/tmp/people.csv"):
        self.result = result
        self.saved = None

    async def save_file(self, **kwargs):
        self.saved = kwargs
        return self.result


@pytest.fixture
def people_page(page):
    control = build_control(PeoplePage())
    control.store._loaded = True  # как после attach, чтобы включилось сохранение
    return control


def visible_ids(control):
    return [c.data for c in walk(control.view_holder) if getattr(c, "data", None)]


def test_initial_render_shows_everyone(people_page):
    assert people_page.counter.value == "Всего записей: 12"
    assert len(people_page.tiles.controls) == 4
    assert people_page.roles_chart.sections
    assert people_page.groups_chart.groups


def test_search_narrows_the_list(people_page):
    people_page.search_field.value = "Балашов"
    people_page._search_changed(event(people_page.search_field, "change"))
    assert people_page.counter.value == "Показано 1 из 12"


def test_search_with_no_matches_shows_empty_state(people_page):
    people_page.search_field.value = "Такого человека нет"
    people_page._search_changed(event(people_page.search_field, "change"))
    texts = [c.value for c in walk(people_page.view_holder) if isinstance(c, ft.Text)]
    assert "Под фильтры никто не подходит" in texts


def test_reset_filters_returns_full_list(people_page):
    people_page.search_field.value = "нет совпадений"
    people_page._search_changed(event(people_page.search_field, "change"))
    people_page._reset_filters(event(people_page))
    assert people_page.search == ""
    assert people_page.role == "all"
    assert people_page.only_favorites is False
    assert people_page.search_field.value == ""
    assert people_page.counter.value == "Всего записей: 12"


def test_role_filter(people_page):
    people_page.role_filter.selected = ["teacher"]
    people_page._role_changed(event(people_page.role_filter, "change"))
    assert people_page.role == "teacher"
    assert people_page.counter.value == "Показано 2 из 12"


def test_favorites_switch(people_page):
    people_page.favorites_switch.value = True
    people_page._favorites_changed(event(people_page.favorites_switch, "change"))
    assert people_page.counter.value == "Показано 2 из 12"


def test_sort_dropdown(people_page):
    people_page.sort_dropdown.value = "rating"
    people_page._sort_changed(event(people_page.sort_dropdown, "select"))
    assert people_page.sort == "rating"

    people_page.sort_dropdown.value = None
    people_page._sort_changed(event(people_page.sort_dropdown, "select"))
    assert people_page.sort == "name"


@pytest.mark.parametrize(
    ("mode", "marker"),
    [("table", ft.DataTable), ("cards", ft.ResponsiveRow), ("list", ft.Dismissible)],
)
def test_view_switch_renders_matching_widget(people_page, mode, marker):
    people_page.view_switch.selected = [mode]
    people_page._view_changed(event(people_page.view_switch, "change"))
    assert people_page.view_mode == mode
    assert any(isinstance(c, marker) for c in walk(people_page.view_holder))


def test_table_sorting_reorders_rows(people_page):
    people_page.view_switch.selected = ["table"]
    people_page._view_changed(event(people_page.view_switch, "change"))

    sort_event = ft.DataColumnSortEvent(
        name="sort",
        data=None,
        control=people_page,
        column_index=4,
        ascending=False,
    )
    people_page._table_sorted(sort_event)
    assert (people_page.table_sort_index, people_page.table_sort_ascending) == (
        4,
        False,
    )

    table = next(
        c for c in walk(people_page.view_holder) if isinstance(c, ft.DataTable)
    )
    ratings = [int(row.cells[4].content.controls[0].value) for row in table.rows]
    assert ratings == sorted(ratings, reverse=True)


def test_table_sorting_clamps_unknown_column(people_page):
    people_page._table_sorted(
        ft.DataColumnSortEvent(
            name="sort", data=None, control=people_page, column_index=99, ascending=True
        )
    )
    assert people_page.table_sort_index == 4


def test_toggle_favorite_through_row_button(people_page):
    person = people_page.store.people[0]
    button = ft.IconButton(data=person.id)
    people_page._toggle_favorite(event(button))
    assert people_page.store.get(person.id).favorite is not person.favorite


def test_open_details_shows_bottom_sheet(people_page, page):
    person = people_page.store.people[0]
    people_page._open_details(event(ft.Container(data=person.id)))
    assert isinstance(page.last_dialog, ft.BottomSheet)


def test_open_details_ignores_unknown_id(people_page, page):
    people_page._open_details(event(ft.Container(data="p999")))
    assert page.dialogs == []


def test_edit_from_sheet_opens_editor(people_page, page):
    person = people_page.store.people[0]
    people_page._edit_from_sheet(person.id)
    assert page.popped == 1
    assert isinstance(page.last_dialog, ft.AlertDialog)


def test_delete_from_sheet_removes_person(people_page, page):
    person = people_page.store.people[0]
    people_page._delete_from_sheet(person.id)
    assert people_page.store.get(person.id) is None
    assert isinstance(page.last_dialog, ft.SnackBar)


def test_create_saves_new_person(people_page, page):
    people_page._create(event(people_page))
    dialog = page.last_dialog
    assert isinstance(dialog, ft.AlertDialog)

    name_field = next(c for c in walk(dialog) if isinstance(c, ft.TextField))
    name_field.value = "Новый Студент"
    save_button = next(
        c for c in walk(dialog) if isinstance(c, ft.FilledButton) and c.on_click
    )
    save_button.on_click(event(save_button))

    assert people_page.store.get("p013").name == "Новый Студент"
    assert len(people_page.store.people) == 13
    assert isinstance(page.last_dialog, ft.SnackBar)


def test_edit_updates_existing_person(people_page, page):
    person = people_page.store.people[0]
    people_page._edit(event(ft.IconButton(data=person.id)))
    dialog = page.last_dialog

    name_field = next(c for c in walk(dialog) if isinstance(c, ft.TextField))
    name_field.value = "Переименована"
    save_button = next(
        c for c in walk(dialog) if isinstance(c, ft.FilledButton) and c.on_click
    )
    save_button.on_click(event(save_button))

    assert people_page.store.get(person.id).name == "Переименована"
    assert len(people_page.store.people) == 12


def test_edit_of_unknown_person_does_nothing(people_page, page):
    people_page._edit(event(ft.IconButton(data="p999")))
    assert page.dialogs == []


def test_editor_cancel_closes_dialog(people_page, page):
    people_page._create(event(people_page))
    dialog = page.last_dialog
    cancel = next(c for c in walk(dialog) if isinstance(c, ft.TextButton))
    cancel.on_click(event(cancel))
    assert page.popped == 1
    assert len(people_page.store.people) == 12


def test_delete_offers_undo_and_restores_position(people_page, page):
    person = people_page.store.people[2]
    people_page._confirm_delete(event(ft.IconButton(data=person.id)))

    snack = page.last_dialog
    assert isinstance(snack, ft.SnackBar)
    assert snack.action.label == "Вернуть"
    assert people_page.store.get(person.id) is None

    snack.on_action(event(snack, "action"))
    assert people_page.store.people[2] is person
    assert len(people_page.store.people) == 12


def test_delete_of_missing_person_is_silent(people_page, page):
    people_page._delete("p999")
    assert page.dialogs == []


def test_swipe_dismiss_deletes_person(people_page, page):
    person = people_page.store.people[0]
    people_page._dismissed(event(ft.Dismissible(data=person.id, content=ft.Text("x"))))
    assert people_page.store.get(person.id) is None


def test_reset_restores_demo_data(people_page, page):
    people_page.store.people = [Person(id="p001", name="Один")]
    people_page._reset(event(people_page))
    assert len(people_page.store.people) == 12
    assert isinstance(page.last_dialog, ft.SnackBar)


def test_export_csv_writes_current_selection(people_page, page):
    import asyncio

    picker = FakeFilePicker()
    people_page.file_picker = picker
    people_page.role = "teacher"

    asyncio.run(people_page._export_csv(event(people_page)))

    payload = picker.saved["src_bytes"].decode("utf-8").splitlines()
    assert payload[0].startswith("name;role;group")
    assert len(payload) == 3  # заголовок и два преподавателя
    assert picker.saved["file_name"] == "people.csv"
    assert page.last_dialog.content == "Сохранено в /tmp/people.csv"


def test_export_csv_reports_cancelled_dialog(people_page, page):
    import asyncio

    people_page.file_picker = FakeFilePicker(result=None)
    asyncio.run(people_page._export_csv(event(people_page)))
    assert page.last_dialog.content == "Экспорт отменён"


def test_did_mount_registers_picker_and_loads_store(people_page, page):
    people_page.did_mount()
    assert people_page.file_picker in page.services
    assert people_page.store._loaded is True


def test_did_mount_twice_keeps_one_picker(people_page, page):
    people_page.did_mount()
    people_page.did_mount()
    assert page.services.count(people_page.file_picker) == 1


def test_refresh_skips_update_before_mount(unmounted):
    control = build_control(PeoplePage())
    control.store.notify()  # подписка сработала, пока страница не на экране
    assert control._mounted() is False
