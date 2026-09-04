"""Модель человека и демонстрационный набор данных."""

import random
from dataclasses import asdict, dataclass, field, replace
from datetime import date, timedelta

import flet as ft

ROLES = {
    "student": "Студент",
    "senior": "Староста",
    "teacher": "Преподаватель",
}

GROUPS = ["ИУ7-31Б", "ИУ7-32Б", "ИУ5-41Б", "РК6-11М", "Кафедра"]

CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Казань",
    "Новосибирск",
    "Екатеринбург",
    "Томск",
]

AVATAR_COLORS = [
    ft.Colors.BLUE,
    ft.Colors.TEAL,
    ft.Colors.PURPLE,
    ft.Colors.ORANGE,
    ft.Colors.PINK,
    ft.Colors.GREEN,
    ft.Colors.INDIGO,
    ft.Colors.BROWN,
]


@dataclass
class Person:
    """Запись картотеки. Хранится и редактируется как единое целое."""

    id: str
    name: str
    role: str = "student"
    group: str = GROUPS[0]
    email: str = ""
    phone: str = ""
    city: str = CITIES[0]
    rating: int = 70
    active: bool = True
    favorite: bool = False
    added: str = field(default_factory=lambda: date.today().isoformat())

    @property
    def initials(self):
        parts = [part for part in self.name.split() if part]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[1][0]).upper()

    @property
    def role_title(self):
        return ROLES.get(self.role, self.role)

    @property
    def color(self):
        """Цвет аватара стабилен для конкретной записи."""
        return AVATAR_COLORS[sum(map(ord, self.id)) % len(AVATAR_COLORS)]

    def matches(self, query):
        """Поиск по имени, почте, группе и городу."""
        if not query:
            return True
        query = query.strip().lower()
        haystack = " ".join(
            [self.name, self.email, self.group, self.city, self.role_title]
        ).lower()
        return query in haystack

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        known = {f: data[f] for f in cls.__dataclass_fields__ if f in data}
        return cls(**known)

    def copy_with(self, **changes):
        return replace(self, **changes)


DEMO_NAMES = [
    ("Анна Северова", "student", 0),
    ("Игорь Балашов", "senior", 0),
    ("Мария Ковалёва", "student", 0),
    ("Пётр Дорохов", "student", 1),
    ("Ольга Тимофеева", "senior", 1),
    ("Даниил Рыжов", "student", 1),
    ("Елена Гаврилова", "teacher", 4),
    ("Сергей Панин", "teacher", 4),
    ("Артём Лапшин", "student", 2),
    ("Вера Никитина", "student", 2),
    ("Кирилл Ершов", "student", 3),
    ("Наталья Зуева", "senior", 3),
]


def demo_people():
    """Стартовый набор: двенадцать человек с правдоподобными данными."""
    rng = random.Random(7)
    people = []
    for index, (name, role, group_index) in enumerate(DEMO_NAMES):
        translit = f"user{index + 1:02d}"
        people.append(
            Person(
                id=f"p{index + 1:03d}",
                name=name,
                role=role,
                group=GROUPS[group_index],
                email=f"{translit}@example.edu",
                phone=f"+7 9{rng.randint(10, 99)} {rng.randint(100, 999)}-"
                f"{rng.randint(10, 99)}-{rng.randint(10, 99)}",
                city=rng.choice(CITIES),
                rating=rng.randint(45, 98),
                active=rng.random() > 0.15,
                favorite=index in (1, 6),
                added=(date.today() - timedelta(days=rng.randint(5, 400))).isoformat(),
            )
        )
    return people
