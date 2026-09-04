"""Представления картотеки и вспомогательные виджеты."""

import flet as ft
import pytest
from conftest import walk

from app.people import views
from app.people.models import Person


@pytest.fixture
def people():
    return [
        Person(id="p001", name="Анна Северова", rating=90, favorite=True),
        Person(id="p002", name="Игорь Балашов", rating=70, active=False),
        Person(id="p003", name="Мария Ковалёва", rating=40),
    ]


@pytest.fixture
def actions():
    calls = {}

    def record(key):
        def handler(e):
            calls.setdefault(key, []).append(getattr(e.control, "data", None))

        return handler

    handlers = {
        name: record(name)
        for name in (
            "on_open",
            "on_edit",
            "on_delete",
            "on_toggle_favorite",
            "on_dismiss",
            "on_sort",
        )
    }
    handlers["calls"] = calls
    return handlers


@pytest.mark.parametrize(
    ("rating", "color"),
    [
        (95, ft.Colors.GREEN),
        (80, ft.Colors.GREEN),
        (70, ft.Colors.AMBER),
        (60, ft.Colors.AMBER),
        (59, ft.Colors.RED),
        (0, ft.Colors.RED),
    ],
)
def test_rating_bar_color_thresholds(rating, color):
    bar = views.rating_bar(Person(id="p1", name="Кто-то", rating=rating))
    assert bar.controls[1].color == color
    assert bar.controls[1].value == pytest.approx(rating / 100)


def test_rating_bar_expands_inside_cards():
    tight = views.rating_bar(Person(id="p1", name="Кто-то"))
    wide = views.rating_bar(Person(id="p1", name="Кто-то"), expand=True)
    assert tight.tight is True and tight.controls[1].width == 90
    assert wide.tight is False and wide.controls[1].expand is True


def test_avatar_shows_initials():
    control = views.avatar(Person(id="p1", name="Анна Северова"))
    assert control.content.value == "АС"


def test_status_dot_marks_archived():
    assert views.status_dot(Person(id="p1", name="A")).bgcolor == ft.Colors.GREEN
    archived = views.status_dot(Person(id="p1", name="A", active=False))
    assert archived.bgcolor == ft.Colors.OUTLINE


def test_favorite_button_reflects_state():
    person = Person(id="p1", name="A", favorite=True)
    button = views.favorite_button(person, lambda e: None)
    assert button.icon == ft.Icons.STAR
    assert button.data == "p1"

    plain = views.favorite_button(Person(id="p2", name="B"), lambda e: None)
    assert plain.icon == ft.Icons.STAR_BORDER


def test_empty_state_calls_reset():
    called = []
    control = views.empty_state("Никого нет", lambda e: called.append(1))
    button = next(c for c in walk(control) if isinstance(c, ft.TextButton))
    button.on_click(None)
    assert called == [1]


def test_list_view_carries_person_id(people, actions):
    view = views.list_view(people, actions)
    assert [c.key for c in view.controls] == ["p001", "p002", "p003"]
    tiles = [c for c in walk(view) if isinstance(c, ft.ListTile)]
    assert [t.data for t in tiles] == ["p001", "p002", "p003"]


def test_list_view_swipe_backgrounds_are_set(people, actions):
    view = views.list_view(people, actions)
    first = view.controls[0]
    assert first.background is not None
    assert first.secondary_background is not None
    assert first.dismiss_direction == ft.DismissDirection.HORIZONTAL


def test_table_view_columns_and_sorting_flags(people, actions):
    table = views.table_view(
        people, actions, sort_index=4, sort_ascending=False
    ).controls[0]
    assert len(table.columns) == len(views.TABLE_COLUMNS) + 1
    assert table.sort_column_index == 4
    assert table.sort_ascending is False
    assert len(table.rows) == 3
    assert table.rows[0].cells[0].data == "p001"


def test_cards_view_builds_card_per_person(people, actions):
    view = views.cards_view(people, actions)
    assert len(view.controls) == 3
    texts = [c.value for c in walk(view) if isinstance(c, ft.Text)]
    assert "Анна Северова" in texts
    assert "активен" in texts and "архив" in texts


def test_view_buttons_report_person_id(people, actions):
    view = views.cards_view(people, actions)
    buttons = [
        c
        for c in walk(view)
        if isinstance(c, ft.IconButton) and c.on_click is actions["on_delete"]
    ]
    buttons[1].on_click(type("E", (), {"control": buttons[1]}))
    assert actions["calls"]["on_delete"] == ["p002"]
