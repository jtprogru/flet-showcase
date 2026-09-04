"""Классическая тудушка: чекбоксы, инлайн-редактирование, фильтры, прогресс."""

import flet as ft

from app.ui import MUTED, page_header, scrollable_page, section

FILTER_ALL = 0
FILTER_ACTIVE = 1
FILTER_COMPLETED = 2

PRIORITIES = {
    "low": ("Низкий", ft.Colors.BLUE, ft.Icons.KEYBOARD_ARROW_DOWN),
    "normal": ("Обычный", ft.Colors.AMBER, ft.Icons.DRAG_HANDLE),
    "high": ("Высокий", ft.Colors.RED, ft.Icons.KEYBOARD_ARROW_UP),
}


def pluralize_tasks(count):
    """Правильная форма слова «задача» для числа."""
    if 11 <= count % 100 <= 14:
        return "задач"
    last_digit = count % 10
    if last_digit == 1:
        return "задача"
    if 2 <= last_digit <= 4:
        return "задачи"
    return "задач"


class Task(ft.Column):
    def __init__(self, task_name, task_delete, task_changed, priority="normal"):
        super().__init__()
        self.completed = False
        self.priority = priority
        self.task_name = task_name
        self.task_delete = task_delete
        self.task_changed = task_changed
        self.spacing = 0

    def build(self):
        self.display_task = ft.Checkbox(
            value=False, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = ft.TextField(
            expand=1, dense=True, on_submit=self.save_clicked, autofocus=True
        )
        self.priority_badge = ft.Container(
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            border_radius=20,
            content=ft.Text(size=11),
        )
        self._render_priority()

        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.priority_badge,
                        ft.PopupMenuButton(
                            icon=ft.Icons.FLAG_OUTLINED,
                            tooltip="Приоритет",
                            items=[
                                ft.PopupMenuItem(
                                    content=title,
                                    icon=icon,
                                    on_click=self._priority_setter(code),
                                )
                                for code, (title, _, icon) in PRIORITIES.items()
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CREATE_OUTLINED,
                            tooltip="Изменить задачу",
                            on_click=self.edit_clicked,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip="Удалить задачу",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                ft.IconButton(
                    icon=ft.Icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Сохранить задачу",
                    on_click=self.save_clicked,
                ),
            ],
        )
        self.controls = [self.display_view, self.edit_view]

    def _render_priority(self):
        title, color, _ = PRIORITIES[self.priority]
        self.priority_badge.bgcolor = ft.Colors.with_opacity(0.16, color)
        self.priority_badge.content.value = title
        self.priority_badge.content.color = color

    def _priority_setter(self, code):
        def handler(e):
            self.priority = code
            self._render_priority()
            self.update()

        return handler

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_changed()

    def delete_clicked(self, e):
        self.task_delete(self)


class TodoBoard(ft.Column):
    """Ядро тудушки: ввод, фильтры, список задач, статистика."""

    def build(self):
        self.new_task = ft.TextField(
            key="new_task",
            hint_text="Что нужно сделать?",
            on_submit=self.add_clicked,
            expand=True,
            border_radius=12,
            prefix_icon=ft.Icons.EDIT_NOTE,
        )
        self.tasks = ft.Column(spacing=0)

        self.filter = ft.TabBar(
            scrollable=False,
            tabs=[
                ft.Tab(label="Все", icon=ft.Icons.LIST_ALT),
                ft.Tab(label="Активные", icon=ft.Icons.RADIO_BUTTON_UNCHECKED),
                ft.Tab(label="Выполненные", icon=ft.Icons.TASK_ALT),
            ],
        )
        self.filter_tabs = ft.Tabs(
            length=3,
            selected_index=FILTER_ALL,
            on_change=lambda e: self.update(),
            content=self.filter,
        )

        self.items_left = ft.Text(f"Осталось 0 {pluralize_tasks(0)}", size=12)
        self.progress = ft.ProgressBar(value=0, border_radius=8, height=8)
        self.progress_label = ft.Text("Прогресс 0%", size=12, color=MUTED)

        self.spacing = 14
        self.controls = [
            ft.Row(
                spacing=10,
                controls=[
                    self.new_task,
                    ft.FloatingActionButton(
                        key="add_task",
                        icon=ft.Icons.ADD,
                        tooltip="Добавить задачу",
                        on_click=self.add_clicked,
                    ),
                ],
            ),
            self.filter_tabs,
            self.tasks,
            ft.Column(
                spacing=4,
                controls=[self.progress, self.progress_label],
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.items_left,
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.OutlinedButton(
                                content="Демо-задачи",
                                icon=ft.Icons.AUTO_AWESOME,
                                on_click=self.seed_clicked,
                            ),
                            ft.OutlinedButton(
                                content="Очистить выполненные",
                                icon=ft.Icons.CLEANING_SERVICES_OUTLINED,
                                on_click=self.clear_clicked,
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def _add(self, name, priority="normal"):
        self.tasks.controls.append(
            Task(name, self.task_delete, self.task_changed, priority)
        )

    async def add_clicked(self, e):
        if self.new_task.value:
            self._add(self.new_task.value)
            self.new_task.value = ""
            self.update()
            await self.new_task.focus()

    def seed_clicked(self, e):
        for name, priority in [
            ("Прочитать документацию Flet", "high"),
            ("Собрать приложение через flet build", "normal"),
            ("Показать витрину коллегам", "low"),
        ]:
            self._add(name, priority)
        self.update()

    def task_changed(self):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.tasks.controls.remove(task)
        self.update()

    def before_update(self):
        selected = self.filter_tabs.selected_index
        active = 0
        total = len(self.tasks.controls)
        for task in self.tasks.controls:
            task.visible = (
                selected == FILTER_ALL
                or (selected == FILTER_ACTIVE and not task.completed)
                or (selected == FILTER_COMPLETED and task.completed)
            )
            if not task.completed:
                active += 1
        done = total - active
        self.items_left.value = f"Осталось {active} {pluralize_tasks(active)}"
        ratio = (done / total) if total else 0
        self.progress.value = ratio
        self.progress_label.value = (
            f"Прогресс {ratio * 100:.0f}% — выполнено {done} из {total}"
        )


def build():
    return scrollable_page(
        page_header(
            "Задачи",
            "Классический TodoMVC: состояние в кастомных контролах, фильтры и прогресс",
            ft.Icons.CHECKLIST_ROUNDED,
        ),
        section(
            "Список дел",
            "Инлайн-редактирование, приоритеты через PopupMenuButton "
            "и фильтрация вкладками",
            [TodoBoard()],
            tags=["Checkbox", "TextField", "TabBar", "PopupMenuButton", "ProgressBar"],
        ),
    )
