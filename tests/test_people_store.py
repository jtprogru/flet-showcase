"""Хранилище картотеки: выборка, статистика, CRUD и сохранение."""

import asyncio
import json

import pytest

from app.people.models import Person
from app.people.store import STORAGE_KEY, PeopleStore


class FakePrefs:
    """Заглушка SharedPreferences: словарь плюс переключатель отказа."""

    def __init__(self, raw=None, broken=False):
        self.storage = {STORAGE_KEY: raw} if raw is not None else {}
        self.broken = broken

    async def get(self, key):
        if self.broken:
            raise OSError("хранилище недоступно")
        return self.storage.get(key)

    async def set(self, key, value):
        if self.broken:
            raise OSError("хранилище недоступно")
        self.storage[key] = value

    async def clear(self):
        self.storage.clear()


@pytest.fixture
def store():
    return PeopleStore()


def test_starts_with_demo_data(store):
    assert len(store.people) == 12


def test_query_without_filters_sorts_by_name(store):
    names = [p.name for p in store.query()]
    assert names == sorted(names, key=str.lower)


def test_query_filters_by_search(store):
    found = store.query(search="Балашов")
    assert [p.name for p in found] == ["Игорь Балашов"]


def test_query_filters_by_role(store):
    teachers = store.query(role="teacher")
    assert teachers and all(p.role == "teacher" for p in teachers)
    assert len(store.query(role="all")) == 12
    assert len(store.query(role=None)) == 12


def test_query_filters_by_favorites(store):
    favorites = store.query(only_favorites=True)
    assert len(favorites) == 2
    assert all(p.favorite for p in favorites)


@pytest.mark.parametrize("sort", ["name", "rating", "group", "added"])
def test_query_sorts(store, sort):
    people = store.query(sort=sort)
    assert len(people) == 12
    if sort == "rating":
        ratings = [p.rating for p in people]
        assert ratings == sorted(ratings, reverse=True)
    if sort == "added":
        dates = [p.added for p in people]
        assert dates == sorted(dates)


def test_unknown_sort_falls_back_to_name(store):
    assert store.query(sort="звёзды") == store.query(sort="name")


def test_query_combines_filters(store):
    store.people[0] = store.people[0].copy_with(favorite=True, role="student")
    combined = store.query(search="", role="student", only_favorites=True)
    assert all(p.role == "student" and p.favorite for p in combined)


def test_stats(store):
    stats = store.stats()
    assert stats["total"] == 12
    assert stats["active"] == sum(1 for p in store.people if p.active)
    assert stats["favorites"] == 2
    assert 0 < stats["rating"] <= 100


def test_stats_on_empty_store(store):
    store.people = []
    assert store.stats() == {"total": 0, "active": 0, "favorites": 0, "rating": 0}


def test_by_role_and_by_group(store):
    assert sum(store.by_role().values()) == 12
    groups = store.by_group()
    assert sum(groups.values()) == 12
    assert list(groups) == sorted(groups)


def test_next_id_continues_numbering(store):
    assert store.next_id() == "p013"
    store.people = []
    assert store.next_id() == "p001"


def test_next_id_ignores_non_numeric_ids(store):
    store.people = [Person(id="custom", name="Без номера")]
    assert store.next_id() == "p001"


def test_add_and_get(store):
    person = Person(id=store.next_id(), name="Новый Человек")
    store.add(person)
    assert store.get(person.id) is person
    assert store.get("нет такого") is None


def test_update_replaces_record(store):
    person = store.people[0].copy_with(name="Переименована")
    store.update(person)
    assert store.get(person.id).name == "Переименована"
    assert len(store.people) == 12


def test_update_of_missing_person_changes_nothing(store):
    store.update(Person(id="p999", name="Чужой"))
    assert len(store.people) == 12


def test_delete_returns_position_and_restore_puts_it_back(store):
    victim = store.people[3]
    index, removed = store.delete(victim.id)
    assert (index, removed) == (3, victim)
    assert len(store.people) == 11

    store.restore(index, removed)
    assert store.people[3] is victim
    assert len(store.people) == 12


def test_delete_of_missing_person(store):
    assert store.delete("p999") == (None, None)


def test_restore_clamps_index(store):
    person = store.people[0]
    store.people = []
    store.restore(50, person)
    assert store.people == [person]


def test_toggle_favorite(store):
    person = store.people[0]
    store.toggle_favorite(person.id)
    assert store.get(person.id).favorite is not person.favorite

    store.toggle_favorite("p999")  # неизвестный id ничего не ломает
    assert len(store.people) == 12


def test_reset_returns_demo_data(store):
    store.people = []
    store.reset()
    assert len(store.people) == 12


def test_subscribers_are_notified_on_every_change(store):
    calls = []
    store.subscribe(lambda: calls.append(1))

    store.add(Person(id="p100", name="Кто-то"))
    store.update(store.people[0])
    store.delete("p100")
    store.reset()
    assert len(calls) == 4


def test_attach_loads_saved_people(store, page):
    saved = [Person(id="p001", name="Из хранилища").to_dict()]
    store.prefs = FakePrefs(raw=json.dumps(saved))

    asyncio.run(store.attach(page))
    assert [p.name for p in store.people] == ["Из хранилища"]
    assert store.prefs in page.services


def test_attach_twice_registers_service_once(store, page):
    store.prefs = FakePrefs()
    asyncio.run(store.attach(page))
    asyncio.run(store.attach(page))
    assert page.services.count(store.prefs) == 1


def test_attach_survives_broken_json(store, page):
    store.prefs = FakePrefs(raw="{это не json")
    asyncio.run(store.attach(page))
    assert len(store.people) == 12


def test_attach_survives_storage_failure(store, page):
    store.prefs = FakePrefs(broken=True)
    asyncio.run(store.attach(page))
    assert len(store.people) == 12


def test_persist_writes_json_after_attach(store, page):
    prefs = FakePrefs()
    store.prefs = prefs

    asyncio.run(store.persist())
    assert prefs.storage == {}  # до attach ничего не пишем

    asyncio.run(store.attach(page))
    store.add(Person(id="p013", name="Свежий"))
    asyncio.run(store.persist())

    names = [item["name"] for item in json.loads(prefs.storage[STORAGE_KEY])]
    assert "Свежий" in names


def test_persist_swallows_storage_errors(store, page):
    store.prefs = FakePrefs()
    asyncio.run(store.attach(page))
    store.prefs.broken = True
    asyncio.run(store.persist())  # исключение не должно вылететь наружу
