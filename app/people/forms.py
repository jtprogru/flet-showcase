"""Диалог редактирования человека и карточка с подробностями."""

import contextlib

import flet as ft

from app.people.models import CITIES, GROUPS, ROLES, Person

MUTED = ft.Colors.ON_SURFACE_VARIANT


def safe_update(control):
    """Обновить контрол, если он уже показан на странице."""
    with contextlib.suppress(RuntimeError):
        control.update()


class PersonEditor:
    """Модальная форма создания и правки записи с проверкой полей."""

    def __init__(self, person, on_save, on_cancel, title=None):
        self.person = person
        self.on_save = on_save
        self.on_cancel = on_cancel

        self.name = ft.TextField(
            label="Имя и фамилия",
            value=person.name,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            autofocus=True,
            on_change=self._clear_error,
        )
        self.email = ft.TextField(
            label="Почта",
            value=person.email,
            prefix_icon=ft.Icons.ALTERNATE_EMAIL,
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=self._clear_error,
        )
        self.phone = ft.TextField(
            label="Телефон",
            value=person.phone,
            prefix_icon=ft.Icons.PHONE_OUTLINED,
            keyboard_type=ft.KeyboardType.PHONE,
        )
        self.group = ft.Dropdown(
            label="Группа",
            value=person.group,
            leading_icon=ft.Icons.GROUPS_OUTLINED,
            options=[ft.DropdownOption(key=name, text=name) for name in GROUPS],
        )
        self.city = ft.Dropdown(
            label="Город",
            value=person.city,
            leading_icon=ft.Icons.LOCATION_CITY,
            enable_filter=True,
            editable=True,
            options=[ft.DropdownOption(key=name, text=name) for name in CITIES],
        )
        self.role = ft.SegmentedButton(
            selected=[person.role],
            allow_multiple_selection=False,
            segments=[
                ft.Segment(value=code, label=title) for code, title in ROLES.items()
            ],
        )
        self.rating_label = ft.Text(f"Рейтинг: {person.rating}", size=12, color=MUTED)
        self.rating = ft.Slider(
            value=person.rating,
            min=0,
            max=100,
            divisions=20,
            label="{value}",
            on_change=self._rating_changed,
        )
        self.active = ft.Switch(label="Активен", value=person.active)
        self.favorite = ft.Switch(label="В избранном", value=person.favorite)

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title or "Новая запись"),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    controls=[
                        self.name,
                        self.email,
                        self.phone,
                        self.group,
                        self.city,
                        ft.Text("Роль", size=12, color=MUTED),
                        self.role,
                        self.rating_label,
                        self.rating,
                        ft.Row(controls=[self.active, self.favorite]),
                    ],
                ),
            ),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton(content="Отмена", on_click=self._cancel),
                ft.FilledButton(
                    content="Сохранить",
                    icon=ft.Icons.CHECK,
                    on_click=self._save,
                ),
            ],
        )

    def _rating_changed(self, e):
        self.rating_label.value = f"Рейтинг: {e.control.value:.0f}"
        safe_update(self.rating_label)

    def _clear_error(self, e):
        if e.control.error:
            e.control.error = None
            safe_update(e.control)

    def _validate(self):
        ok = True
        if not (self.name.value or "").strip():
            self.name.error = "Без имени запись не сохранить"
            safe_update(self.name)
            ok = False
        email = (self.email.value or "").strip()
        if email and ("@" not in email or "." not in email.split("@")[-1]):
            self.email.error = "Похоже, адрес неполный"
            safe_update(self.email)
            ok = False
        return ok

    def _collect(self):
        return self.person.copy_with(
            name=self.name.value.strip(),
            email=(self.email.value or "").strip(),
            phone=(self.phone.value or "").strip(),
            group=self.group.value or GROUPS[0],
            city=self.city.value or CITIES[0],
            role=next(iter(self.role.selected), "student"),
            rating=int(self.rating.value),
            active=self.active.value,
            favorite=self.favorite.value,
        )

    def _save(self, e):
        if self._validate():
            self.on_save(self._collect())

    def _cancel(self, e):
        self.on_cancel()


def details_sheet(person: Person, on_edit, on_delete, on_close):
    """Нижняя шторка с полной карточкой человека."""

    def row(icon, label, value):
        return ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon, size=18, color=MUTED),
                ft.Text(label, size=12, color=MUTED, width=90),
                ft.Text(value or "—", size=13, selectable=True, expand=True),
            ],
        )

    return ft.BottomSheet(
        show_drag_handle=True,
        content=ft.Container(
            padding=ft.Padding.only(left=24, right=24, top=8, bottom=24),
            content=ft.Column(
                tight=True,
                spacing=14,
                controls=[
                    ft.Row(
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.CircleAvatar(
                                radius=28,
                                bgcolor=ft.Colors.with_opacity(0.18, person.color),
                                content=ft.Text(
                                    person.initials,
                                    color=person.color,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                            ft.Column(
                                spacing=2,
                                tight=True,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        person.name,
                                        theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
                                    ),
                                    ft.Text(
                                        f"{person.role_title} · {person.group}",
                                        size=12,
                                        color=MUTED,
                                    ),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                border_radius=20,
                                bgcolor=ft.Colors.with_opacity(
                                    0.16,
                                    ft.Colors.GREEN
                                    if person.active
                                    else ft.Colors.GREY,
                                ),
                                content=ft.Text(
                                    "активен" if person.active else "в архиве",
                                    size=11,
                                    color=(
                                        ft.Colors.GREEN
                                        if person.active
                                        else ft.Colors.GREY
                                    ),
                                ),
                            ),
                        ],
                    ),
                    ft.Divider(height=4),
                    row(ft.Icons.ALTERNATE_EMAIL, "Почта", person.email),
                    row(ft.Icons.PHONE_OUTLINED, "Телефон", person.phone),
                    row(ft.Icons.LOCATION_CITY, "Город", person.city),
                    row(ft.Icons.EVENT_OUTLINED, "В картотеке с", person.added),
                    ft.Column(
                        spacing=4,
                        tight=True,
                        controls=[
                            ft.Text(f"Рейтинг: {person.rating}", size=12, color=MUTED),
                            ft.ProgressBar(
                                value=person.rating / 100, height=8, border_radius=6
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        spacing=8,
                        controls=[
                            ft.TextButton(content="Закрыть", on_click=on_close),
                            ft.OutlinedButton(
                                content="Удалить",
                                icon=ft.Icons.DELETE_OUTLINE,
                                on_click=on_delete,
                            ),
                            ft.FilledButton(
                                content="Редактировать",
                                icon=ft.Icons.EDIT_OUTLINED,
                                on_click=on_edit,
                            ),
                        ],
                    ),
                ],
            ),
        ),
    )
