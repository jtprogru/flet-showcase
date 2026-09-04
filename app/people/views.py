"""Три представления картотеки: список, таблица и карточки."""

import flet as ft

MUTED = ft.Colors.ON_SURFACE_VARIANT

TABLE_COLUMNS = [
    ("Имя", "name", False),
    ("Роль", "role_title", False),
    ("Группа", "group", False),
    ("Город", "city", False),
    ("Рейтинг", "rating", True),
]


def avatar(person, radius=20):
    return ft.CircleAvatar(
        radius=radius,
        bgcolor=ft.Colors.with_opacity(0.18, person.color),
        content=ft.Text(
            person.initials, color=person.color, weight=ft.FontWeight.BOLD, size=13
        ),
    )


def rating_bar(person, width=90, expand=False):
    color = (
        ft.Colors.GREEN
        if person.rating >= 80
        else ft.Colors.AMBER
        if person.rating >= 60
        else ft.Colors.RED
    )
    return ft.Row(
        tight=not expand,
        spacing=8,
        controls=[
            ft.Text(str(person.rating), size=12, width=26),
            ft.ProgressBar(
                value=person.rating / 100,
                width=None if expand else width,
                expand=expand,
                height=6,
                border_radius=4,
                color=color,
            ),
        ],
    )


def status_dot(person):
    color = ft.Colors.GREEN if person.active else ft.Colors.OUTLINE
    return ft.Container(
        width=8,
        height=8,
        border_radius=4,
        bgcolor=color,
        tooltip="Активен" if person.active else "В архиве",
    )


def empty_state(message, on_reset):
    return ft.Container(
        padding=40,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.PERSON_SEARCH_OUTLINED, size=44, color=MUTED),
                ft.Text(message, size=13, color=MUTED),
                ft.TextButton(
                    content="Сбросить фильтры",
                    icon=ft.Icons.FILTER_ALT_OFF_OUTLINED,
                    on_click=on_reset,
                ),
            ],
        ),
    )


def favorite_button(person, on_toggle):
    return ft.IconButton(
        icon=ft.Icons.STAR if person.favorite else ft.Icons.STAR_BORDER,
        icon_color=ft.Colors.AMBER if person.favorite else MUTED,
        tooltip="Убрать из избранного" if person.favorite else "В избранное",
        data=person.id,
        on_click=on_toggle,
    )


def row_menu(person, on_edit, on_delete):
    return ft.PopupMenuButton(
        icon=ft.Icons.MORE_VERT,
        tooltip="Действия",
        items=[
            ft.PopupMenuItem(
                content="Редактировать",
                icon=ft.Icons.EDIT_OUTLINED,
                data=person.id,
                on_click=on_edit,
            ),
            ft.PopupMenuItem(
                content="Удалить",
                icon=ft.Icons.DELETE_OUTLINE,
                data=person.id,
                on_click=on_delete,
            ),
        ],
    )


def swipe_background(alignment):
    """Подложка, которая проступает под карточкой при свайпе."""
    return ft.Container(
        bgcolor=ft.Colors.with_opacity(0.22, ft.Colors.RED),
        border_radius=12,
        alignment=alignment,
        padding=20,
        content=ft.Icon(ft.Icons.DELETE_SWEEP, color=ft.Colors.RED),
    )


def list_view(people, actions):
    """Список карточек: свайп удаляет, клик открывает подробности."""
    return ft.Column(
        spacing=6,
        controls=[
            ft.Dismissible(
                key=person.id,
                data=person.id,
                dismiss_direction=ft.DismissDirection.HORIZONTAL,
                on_dismiss=actions["on_dismiss"],
                background=swipe_background(ft.Alignment.CENTER_LEFT),
                secondary_background=swipe_background(ft.Alignment.CENTER_RIGHT),
                content=ft.Card(
                    variant=ft.CardVariant.OUTLINED,
                    content=ft.ListTile(
                        leading=avatar(person),
                        title=ft.Row(
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(person.name, weight=ft.FontWeight.W_500),
                                status_dot(person),
                            ],
                        ),
                        subtitle=ft.Text(
                            f"{person.role_title} · {person.group} · {person.email}",
                            size=12,
                            color=MUTED,
                        ),
                        data=person.id,
                        on_click=actions["on_open"],
                        trailing=ft.Row(
                            tight=True,
                            spacing=0,
                            controls=[
                                rating_bar(person, width=70),
                                favorite_button(person, actions["on_toggle_favorite"]),
                                row_menu(
                                    person, actions["on_edit"], actions["on_delete"]
                                ),
                            ],
                        ),
                    ),
                ),
            )
            for person in people
        ],
    )


def table_view(people, actions, sort_index=0, sort_ascending=True):
    """Таблица с сортировкой по колонкам."""
    return ft.Row(
        scroll=ft.ScrollMode.ADAPTIVE,
        controls=[
            ft.DataTable(
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                horizontal_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                column_spacing=22,
                sort_column_index=sort_index,
                sort_ascending=sort_ascending,
                columns=[
                    ft.DataColumn(
                        label=ft.Text(title),
                        numeric=numeric,
                        on_sort=actions["on_sort"],
                    )
                    for title, _, numeric in TABLE_COLUMNS
                ]
                + [ft.DataColumn(label=ft.Text(""))],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Row(
                                    tight=True,
                                    spacing=10,
                                    controls=[
                                        avatar(person, radius=14),
                                        ft.Text(person.name),
                                        status_dot(person),
                                    ],
                                ),
                                data=person.id,
                                on_tap=actions["on_open"],
                            ),
                            ft.DataCell(ft.Text(person.role_title)),
                            ft.DataCell(ft.Text(person.group)),
                            ft.DataCell(ft.Text(person.city)),
                            ft.DataCell(rating_bar(person, width=80)),
                            ft.DataCell(
                                ft.Row(
                                    tight=True,
                                    spacing=0,
                                    controls=[
                                        favorite_button(
                                            person, actions["on_toggle_favorite"]
                                        ),
                                        row_menu(
                                            person,
                                            actions["on_edit"],
                                            actions["on_delete"],
                                        ),
                                    ],
                                )
                            ),
                        ]
                    )
                    for person in people
                ],
            )
        ],
    )


def cards_view(people, actions):
    """Плитка карточек — удобно, когда людей немного."""
    return ft.ResponsiveRow(
        spacing=12,
        run_spacing=12,
        controls=[
            ft.Card(
                col={"sm": 6, "lg": 4, "xxl": 3},
                variant=ft.CardVariant.OUTLINED,
                content=ft.Container(
                    padding=16,
                    border_radius=12,
                    ink=True,
                    data=person.id,
                    on_click=actions["on_open"],
                    content=ft.Column(
                        spacing=10,
                        tight=True,
                        controls=[
                            ft.Row(
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    avatar(person, radius=22),
                                    ft.Column(
                                        spacing=2,
                                        tight=True,
                                        expand=True,
                                        controls=[
                                            ft.Text(
                                                person.name,
                                                weight=ft.FontWeight.W_600,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                            ft.Text(
                                                person.role_title,
                                                size=12,
                                                color=MUTED,
                                            ),
                                        ],
                                    ),
                                    favorite_button(
                                        person, actions["on_toggle_favorite"]
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.GROUPS_OUTLINED, size=14, color=MUTED
                                    ),
                                    ft.Text(person.group, size=12, color=MUTED),
                                    ft.Icon(
                                        ft.Icons.LOCATION_ON_OUTLINED,
                                        size=14,
                                        color=MUTED,
                                    ),
                                    ft.Text(person.city, size=12, color=MUTED),
                                ],
                            ),
                            ft.Text(
                                person.email,
                                size=12,
                                color=MUTED,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            rating_bar(person, expand=True),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(
                                        tight=True,
                                        spacing=6,
                                        controls=[
                                            status_dot(person),
                                            ft.Text(
                                                "активен" if person.active else "архив",
                                                size=11,
                                                color=MUTED,
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        tight=True,
                                        spacing=0,
                                        controls=[
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_OUTLINED,
                                                icon_size=18,
                                                tooltip="Редактировать",
                                                data=person.id,
                                                on_click=actions["on_edit"],
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                icon_size=18,
                                                tooltip="Удалить",
                                                data=person.id,
                                                on_click=actions["on_delete"],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            )
            for person in people
        ],
    )
