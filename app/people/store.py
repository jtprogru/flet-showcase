"""Хранилище картотеки: CRUD, фильтрация и сохранение между запусками."""

import contextlib
import json

import flet as ft

from app.people.models import Person, demo_people

STORAGE_KEY = "showcase.people"

SORTS = {
    "name": ("По имени", lambda p: p.name.lower()),
    "rating": ("По рейтингу", lambda p: -p.rating),
    "group": ("По группе", lambda p: (p.group, p.name.lower())),
    "added": ("По дате добавления", lambda p: p.added),
}


class PeopleStore:
    """Список людей плюс подписки на изменения.

    Данные лежат в памяти, а после каждой правки уезжают в SharedPreferences,
    поэтому картотека переживает перезапуск приложения.
    """

    def __init__(self):
        self.people = demo_people()
        self.prefs = ft.SharedPreferences()
        self._listeners = []
        self._page = None
        self._loaded = False

    # --- подписки ------------------------------------------------------

    def subscribe(self, callback):
        self._listeners.append(callback)

    def notify(self):
        for callback in self._listeners:
            callback()

    # --- сохранение ----------------------------------------------------

    async def attach(self, page):
        """Подключить сервис хранилища и подтянуть сохранённые данные."""
        self._page = page
        if self.prefs not in page.services:
            page.services.append(self.prefs)
        try:
            raw = await self.prefs.get(STORAGE_KEY)
        except Exception:
            raw = None
        if raw:
            with contextlib.suppress(ValueError, TypeError):
                self.people = [Person.from_dict(item) for item in json.loads(raw)]
        self._loaded = True
        self.notify()

    async def persist(self):
        """Сохранить текущее состояние. Ошибки хранилища не ломают работу."""
        if not self._loaded:
            return
        with contextlib.suppress(Exception):
            await self.prefs.set(
                STORAGE_KEY, json.dumps([p.to_dict() for p in self.people])
            )

    # --- CRUD ----------------------------------------------------------

    def next_id(self):
        numbers = [int(p.id[1:]) for p in self.people if p.id[1:].isdigit()]
        return f"p{(max(numbers) + 1) if numbers else 1:03d}"

    def get(self, person_id):
        return next((p for p in self.people if p.id == person_id), None)

    def add(self, person):
        self.people.append(person)
        self.notify()

    def update(self, person):
        for index, existing in enumerate(self.people):
            if existing.id == person.id:
                self.people[index] = person
                break
        self.notify()

    def delete(self, person_id):
        """Удалить запись и вернуть её вместе с позицией — для отмены."""
        for index, existing in enumerate(self.people):
            if existing.id == person_id:
                self.people.pop(index)
                self.notify()
                return index, existing
        return None, None

    def restore(self, index, person):
        self.people.insert(min(index, len(self.people)), person)
        self.notify()

    def toggle_favorite(self, person_id):
        person = self.get(person_id)
        if person is not None:
            self.update(person.copy_with(favorite=not person.favorite))

    def reset(self):
        self.people = demo_people()
        self.notify()

    # --- выборка -------------------------------------------------------

    def query(self, search="", role=None, only_favorites=False, sort="name"):
        """Отфильтрованный и отсортированный срез картотеки."""
        result = [
            person
            for person in self.people
            if person.matches(search)
            and (role in (None, "all") or person.role == role)
            and (not only_favorites or person.favorite)
        ]
        key = SORTS.get(sort, SORTS["name"])[1]
        return sorted(result, key=key)

    # --- статистика ----------------------------------------------------

    def stats(self):
        total = len(self.people)
        active = sum(1 for p in self.people if p.active)
        favorites = sum(1 for p in self.people if p.favorite)
        rating = round(sum(p.rating for p in self.people) / total) if total else 0
        return {
            "total": total,
            "active": active,
            "favorites": favorites,
            "rating": rating,
        }

    def by_role(self):
        counts = {}
        for person in self.people:
            counts[person.role] = counts.get(person.role, 0) + 1
        return counts

    def by_group(self):
        counts = {}
        for person in self.people:
            counts[person.group] = counts.get(person.group, 0) + 1
        return dict(sorted(counts.items()))
