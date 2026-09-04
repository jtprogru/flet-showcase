"""Диалог редактирования и карточка подробностей."""

import flet as ft
import pytest
from conftest import event, walk

from app.people.forms import PersonEditor, details_sheet, safe_update
from app.people.models import CITIES, GROUPS, Person


@pytest.fixture
def person():
    return Person(
        id="p001",
        name="Анна Северова",
        email="anna@example.edu",
        phone="+7 900 000-00-00",
        group=GROUPS[1],
        city=CITIES[2],
        rating=64,
    )


@pytest.fixture
def editor(person):
    saved = []
    cancelled = []
    control = PersonEditor(
        person,
        on_save=saved.append,
        on_cancel=lambda: cancelled.append(1),
        title="Правка записи",
    )
    control.saved = saved
    control.cancelled = cancelled
    return control


def test_safe_update_ignores_unmounted_control(unmounted):
    safe_update(ft.Text("вне страницы"))  # RuntimeError не должен вылететь


def test_editor_prefills_fields(editor, person):
    assert editor.name.value == person.name
    assert editor.email.value == person.email
    assert editor.group.value == person.group
    assert editor.city.value == person.city
    assert editor.rating.value == person.rating
    assert editor.role.selected == [person.role]
    assert editor.dialog.title.value == "Правка записи"


def test_dropdown_option_keys_match_values(editor):
    assert [o.key for o in editor.group.options] == GROUPS
    assert editor.group.value in [o.key for o in editor.group.options]
    assert editor.city.value in [o.key for o in editor.city.options]


def test_save_collects_edited_values(editor, page):
    editor.name.value = "  Анна Северова-Иванова  "
    editor.email.value = " anna@mail.ru "
    editor.phone.value = " +7 999 111-11-11 "
    editor.rating.value = 91.6
    editor.active.value = False
    editor.favorite.value = True
    editor.role.selected = ["teacher"]

    editor._save(event(editor.dialog))

    saved = editor.saved[0]
    assert saved.name == "Анна Северова-Иванова"
    assert saved.email == "anna@mail.ru"
    assert saved.phone == "+7 999 111-11-11"
    assert saved.rating == 91
    assert saved.role == "teacher"
    assert (saved.active, saved.favorite) == (False, True)
    assert saved.id == "p001"


def test_save_requires_name(editor, page):
    editor.name.value = "   "
    editor._save(event(editor.dialog))
    assert editor.saved == []
    assert editor.name.error


@pytest.mark.parametrize("email", ["без-собаки", "anna@mail", "anna@"])
def test_save_rejects_broken_email(editor, page, email):
    editor.email.value = email
    editor._save(event(editor.dialog))
    assert editor.saved == []
    assert editor.email.error


def test_empty_email_is_allowed(editor, page):
    editor.email.value = ""
    editor._save(event(editor.dialog))
    assert editor.saved[0].email == ""


def test_typing_clears_previous_error(editor, page):
    editor.name.value = ""
    editor._save(event(editor.dialog))
    assert editor.name.error

    editor.name.value = "Анна"
    editor._clear_error(event(editor.name, "change"))
    assert editor.name.error is None


def test_clear_error_does_nothing_when_field_is_clean(editor, page):
    assert editor.name.error is None
    editor._clear_error(event(editor.name, "change"))
    assert editor.name.error is None


def test_rating_slider_updates_label(editor, page):
    editor.rating.value = 42
    editor._rating_changed(event(editor.rating, "change"))
    assert editor.rating_label.value == "Рейтинг: 42"


def test_cancel_calls_callback(editor):
    editor._cancel(event(editor.dialog))
    assert editor.cancelled == [1]


def test_defaults_when_fields_are_cleared(person, page):
    saved = []
    editor = PersonEditor(person, on_save=saved.append, on_cancel=lambda: None)
    editor.group.value = None
    editor.city.value = None
    editor.role.selected = []
    editor._save(event(editor.dialog))
    assert saved[0].group == GROUPS[0]
    assert saved[0].city == CITIES[0]
    assert saved[0].role == "student"


def test_details_sheet_shows_person_data(person):
    closed, edited, deleted = [], [], []
    sheet = details_sheet(
        person,
        on_edit=lambda e: edited.append(1),
        on_delete=lambda e: deleted.append(1),
        on_close=lambda e: closed.append(1),
    )
    texts = [c.value for c in walk(sheet) if isinstance(c, ft.Text)]
    assert person.name in texts
    assert person.email in texts
    assert "активен" in texts
    assert f"Рейтинг: {person.rating}" in texts

    buttons = [c for c in walk(sheet) if getattr(c, "on_click", None)]
    for button in buttons:
        button.on_click(None)
    assert (closed, deleted, edited) == ([1], [1], [1])


def test_details_sheet_marks_archived(person):
    sheet = details_sheet(
        person.copy_with(active=False, email=""),
        on_edit=lambda e: None,
        on_delete=lambda e: None,
        on_close=lambda e: None,
    )
    texts = [c.value for c in walk(sheet) if isinstance(c, ft.Text)]
    assert "в архиве" in texts
    assert "—" in texts  # пустая почта заменяется прочерком
