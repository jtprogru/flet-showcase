"""Модель человека: производные поля, поиск и сериализация."""

import pytest

from app.people.models import (
    AVATAR_COLORS,
    GROUPS,
    ROLES,
    Person,
    demo_people,
)


def make(**changes):
    base = dict(
        id="p001",
        name="Анна Северова",
        role="student",
        group=GROUPS[0],
        email="anna@example.edu",
        phone="+7 900 000-00-00",
        city="Казань",
        rating=88,
    )
    base.update(changes)
    return Person(**base)


@pytest.mark.parametrize(
    ("name", "initials"),
    [
        ("Анна Северова", "АС"),
        ("Анна", "АН"),
        ("  ", "?"),
        ("", "?"),
        ("Мария Ковалёва Петровна", "МК"),
    ],
)
def test_initials(name, initials):
    assert make(name=name).initials == initials


def test_role_title_falls_back_to_code():
    assert make(role="teacher").role_title == ROLES["teacher"]
    assert make(role="alien").role_title == "alien"


def test_color_depends_only_on_id():
    person = make()
    assert person.color in AVATAR_COLORS
    assert make(name="Другое имя", rating=1).color == person.color
    palette = {make(id=f"p{i:03d}").color for i in range(len(AVATAR_COLORS))}
    assert len(palette) > 1


@pytest.mark.parametrize(
    "query",
    ["", "  ", "анна", "АННА", "example.edu", GROUPS[0], "Казань", "Студент"],
)
def test_matches_finds_person(query):
    assert make().matches(query) is True


@pytest.mark.parametrize("query", ["Пётр", "unknown@mail", "Томск", "Преподаватель"])
def test_matches_rejects_others(query):
    assert make().matches(query) is False


def test_to_dict_from_dict_roundtrip():
    person = make(favorite=True, active=False)
    restored = Person.from_dict(person.to_dict())
    assert restored == person


def test_from_dict_ignores_unknown_keys():
    data = make().to_dict()
    data["unexpected"] = "мусор из старой версии"
    assert Person.from_dict(data).name == "Анна Северова"


def test_copy_with_does_not_touch_original():
    person = make()
    changed = person.copy_with(rating=10, favorite=True)
    assert (changed.rating, changed.favorite) == (10, True)
    assert (person.rating, person.favorite) == (88, False)


def test_defaults_are_sane():
    person = Person(id="p999", name="Без полей")
    assert person.role == "student"
    assert person.rating == 70
    assert person.active is True
    assert person.favorite is False
    assert len(person.added) == 10


def test_demo_people_is_deterministic():
    first, second = demo_people(), demo_people()
    assert len(first) == 12
    assert [p.to_dict() for p in first] == [p.to_dict() for p in second]
    assert len({p.id for p in first}) == 12
    assert {p.role for p in first} <= set(ROLES)
    assert sum(1 for p in first if p.favorite) == 2
