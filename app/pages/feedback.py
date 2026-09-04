"""Обратная связь: кнопки, диалоги, уведомления, меню и подсказки."""

import flet as ft

from app.ui import MUTED, page_header, section


class FeedbackPage(ft.Column):
    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True
        self.log = ft.Text("Здесь появится последнее действие", size=12, color=MUTED)

        self.controls = [
            page_header(
                "Действия и уведомления",
                "Все виды кнопок, диалоги, снекбары, баннеры и меню",
                ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED,
            ),
            ft.Card(
                variant=ft.CardVariant.FILLED,
                content=ft.Container(
                    padding=12,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.HISTORY, color=ft.Colors.PRIMARY),
                            self.log,
                        ],
                    ),
                ),
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    self._buttons(),
                    self._icon_buttons(),
                    self._dialogs(),
                    self._notifications(),
                    self._menus(),
                    self._hints(),
                ],
            ),
        ]

    def _say(self, message):
        self.log.value = message
        self.log.update()

    # --- кнопки --------------------------------------------------------

    def _buttons(self):
        def click(name):
            return lambda e: self._say(f"Нажата кнопка «{name}»")

        return section(
            "Кнопки",
            "Material-кнопки всех вариантов, включая состояние disabled",
            [
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.ElevatedButton(
                            content="Elevated",
                            icon=ft.Icons.ARROW_UPWARD,
                            on_click=click("ElevatedButton"),
                        ),
                        ft.FilledButton(
                            content="Filled",
                            icon=ft.Icons.CHECK,
                            on_click=click("FilledButton"),
                        ),
                        ft.FilledTonalButton(
                            content="Filled tonal",
                            icon=ft.Icons.TONALITY,
                            on_click=click("FilledTonalButton"),
                        ),
                        ft.OutlinedButton(
                            content="Outlined",
                            icon=ft.Icons.CROP_SQUARE,
                            on_click=click("OutlinedButton"),
                        ),
                        ft.TextButton(
                            content="Text",
                            icon=ft.Icons.TEXT_FIELDS,
                            on_click=click("TextButton"),
                        ),
                        ft.FilledButton(content="Выключена", disabled=True),
                    ],
                ),
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.FloatingActionButton(
                            icon=ft.Icons.ADD,
                            mini=True,
                            tooltip="FloatingActionButton mini",
                            on_click=click("FAB mini"),
                        ),
                        ft.FloatingActionButton(
                            content="Действие",
                            icon=ft.Icons.BOLT,
                            on_click=click("FAB расширенный"),
                        ),
                    ],
                ),
            ],
            tags=[
                "ElevatedButton",
                "FilledButton",
                "OutlinedButton",
                "TextButton",
                "FloatingActionButton",
            ],
            col={"md": 6, "xxl": 4},
        )

    def _icon_buttons(self):
        def click(name):
            return lambda e: self._say(f"Нажата иконка «{name}»")

        self.like_button = ft.IconButton(
            icon=ft.Icons.FAVORITE_BORDER,
            selected_icon=ft.Icons.FAVORITE,
            selected=False,
            icon_color=ft.Colors.RED,
            selected_icon_color=ft.Colors.RED,
            tooltip="Переключаемая иконка",
            on_click=self._toggle_like,
        )
        return section(
            "Иконки-кнопки",
            "Обычные, заполненные, с обводкой и переключаемые",
            [
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            tooltip="IconButton",
                            on_click=click("IconButton"),
                        ),
                        ft.FilledIconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            tooltip="FilledIconButton",
                            on_click=click("FilledIconButton"),
                        ),
                        ft.FilledTonalIconButton(
                            icon=ft.Icons.PAUSE,
                            tooltip="FilledTonalIconButton",
                            on_click=click("FilledTonalIconButton"),
                        ),
                        ft.OutlinedIconButton(
                            icon=ft.Icons.STOP,
                            tooltip="OutlinedIconButton",
                            on_click=click("OutlinedIconButton"),
                        ),
                        self.like_button,
                        ft.IconButton(
                            icon=ft.Icons.SHOPPING_CART_OUTLINED,
                            badge=ft.Badge(label="7", small_size=14),
                            tooltip="Иконка с Badge",
                            on_click=click("IconButton с Badge"),
                        ),
                    ],
                ),
            ],
            tags=["IconButton", "FilledIconButton", "OutlinedIconButton", "Badge"],
            col={"md": 6, "xxl": 4},
        )

    def _toggle_like(self, e):
        e.control.selected = not e.control.selected
        e.control.update()
        self._say("Лайк поставлен" if e.control.selected else "Лайк снят")

    # --- диалоги -------------------------------------------------------

    def _dialogs(self):
        return section(
            "Диалоги",
            "Модальное окно, нижняя шторка и полноэкранный лист",
            [
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.FilledTonalButton(
                            content="AlertDialog",
                            icon=ft.Icons.WARNING_AMBER,
                            on_click=self._open_alert,
                        ),
                        ft.FilledTonalButton(
                            content="BottomSheet",
                            icon=ft.Icons.VERTICAL_ALIGN_BOTTOM,
                            on_click=self._open_sheet,
                        ),
                        ft.FilledTonalButton(
                            content="Боковая панель",
                            icon=ft.Icons.MENU_OPEN,
                            on_click=self._open_drawer,
                        ),
                    ],
                ),
            ],
            tags=["AlertDialog", "BottomSheet", "NavigationDrawer"],
            col={"md": 6, "xxl": 4},
        )

    def _open_alert(self, e):
        dialog = ft.AlertDialog(
            modal=True,
            icon=ft.Icon(ft.Icons.DELETE_FOREVER, color=ft.Colors.ERROR),
            title=ft.Text("Удалить окружение?"),
            content=ft.Text(
                "Действие необратимо: под удаление попадут все поды и тома.",
            ),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton(content="Отмена", on_click=self._close_dialog),
                ft.FilledButton(
                    content="Удалить",
                    icon=ft.Icons.DELETE,
                    on_click=self._confirm_delete,
                ),
            ],
        )
        self.page.show_dialog(dialog)

    def _close_dialog(self, e):
        self.page.pop_dialog()
        self._say("Диалог закрыт без изменений")

    def _confirm_delete(self, e):
        self.page.pop_dialog()
        self.page.show_dialog(
            ft.SnackBar(
                content="Окружение удалено",
                bgcolor=ft.Colors.ERROR_CONTAINER,
                action=ft.SnackBarAction(label="Отменить"),
                on_action=lambda e: self._say("Удаление отменено"),
            )
        )
        self._say("Подтверждено удаление окружения")

    def _open_sheet(self, e):
        sheet = ft.BottomSheet(
            show_drag_handle=True,
            content=ft.Container(
                padding=24,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Text("Быстрые действия", size=18, weight=ft.FontWeight.BOLD),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.SHARE),
                            title=ft.Text("Поделиться"),
                            on_click=lambda e: self._close_sheet("Поделиться"),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.EDIT),
                            title=ft.Text("Переименовать"),
                            on_click=lambda e: self._close_sheet("Переименовать"),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.ARCHIVE),
                            title=ft.Text("В архив"),
                            on_click=lambda e: self._close_sheet("В архив"),
                        ),
                    ],
                ),
            ),
        )
        self.page.show_dialog(sheet)

    def _close_sheet(self, action):
        self.page.pop_dialog()
        self._say(f"Из шторки выбрано: {action}")

    async def _open_drawer(self, e):
        self.page.drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(
                    padding=ft.Padding.only(left=16, top=24, bottom=8),
                    content=ft.Text("Разделы", size=16, weight=ft.FontWeight.BOLD),
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED, label="Дашборд"
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED, label="Настройки"
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.HELP_OUTLINE, label="Помощь"
                ),
            ],
            on_change=lambda e: self._say(
                f"В боковой панели выбран пункт №{e.control.selected_index + 1}"
            ),
        )
        await self.page.show_drawer()

    # --- уведомления ---------------------------------------------------

    def _notifications(self):
        return section(
            "Уведомления",
            "SnackBar с действием и Banner в верхней части экрана",
            [
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.FilledTonalButton(
                            content="SnackBar",
                            icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
                            on_click=self._show_snack,
                        ),
                        ft.FilledTonalButton(
                            content="Banner",
                            icon=ft.Icons.CAMPAIGN_OUTLINED,
                            on_click=self._show_banner,
                        ),
                    ],
                ),
            ],
            tags=["SnackBar", "SnackBarAction", "Banner"],
            col={"md": 6, "xxl": 4},
        )

    def _show_snack(self, e):
        self.page.show_dialog(
            ft.SnackBar(
                content="Изменения сохранены",
                show_close_icon=True,
                behavior=ft.SnackBarBehavior.FLOATING,
                width=340,
                action=ft.SnackBarAction(label="Открыть"),
                on_action=lambda e: self._say("Из SnackBar нажали «Открыть»"),
            )
        )
        self._say("Показан SnackBar")

    def _show_banner(self, e):
        banner = ft.Banner(
            bgcolor=ft.Colors.TERTIARY_CONTAINER,
            leading=ft.Icon(
                ft.Icons.INFO_OUTLINE, color=ft.Colors.ON_TERTIARY_CONTAINER
            ),
            content=ft.Text(
                "Доступна новая версия витрины. Обновить сейчас?",
                color=ft.Colors.ON_TERTIARY_CONTAINER,
            ),
            actions=[
                ft.TextButton(content="Позже", on_click=self._close_banner),
                ft.FilledButton(content="Обновить", on_click=self._close_banner),
            ],
        )
        self.page.show_dialog(banner)
        self._say("Показан Banner")

    def _close_banner(self, e):
        self.page.pop_dialog()
        self._say("Banner закрыт")

    # --- меню ----------------------------------------------------------

    def _menus(self):
        def pick(name):
            return lambda e: self._say(f"Пункт меню: {name}")

        return section(
            "Меню",
            "Строка меню с подменю и всплывающее контекстное меню",
            [
                ft.MenuBar(
                    expand=True,
                    controls=[
                        ft.SubmenuButton(
                            content="Файл",
                            leading=ft.Icon(ft.Icons.FOLDER_OPEN),
                            controls=[
                                ft.MenuItemButton(
                                    content="Создать",
                                    leading=ft.Icon(ft.Icons.ADD),
                                    on_click=pick("Создать"),
                                ),
                                ft.MenuItemButton(
                                    content="Открыть",
                                    leading=ft.Icon(ft.Icons.FILE_OPEN),
                                    on_click=pick("Открыть"),
                                ),
                                ft.SubmenuButton(
                                    content="Экспорт",
                                    controls=[
                                        ft.MenuItemButton(
                                            content="в PNG",
                                            on_click=pick("Экспорт PNG"),
                                        ),
                                        ft.MenuItemButton(
                                            content="в PDF",
                                            on_click=pick("Экспорт PDF"),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.SubmenuButton(
                            content="Правка",
                            leading=ft.Icon(ft.Icons.EDIT_NOTE),
                            controls=[
                                ft.MenuItemButton(
                                    content="Отменить",
                                    leading=ft.Icon(ft.Icons.UNDO),
                                    on_click=pick("Отменить"),
                                ),
                                ft.MenuItemButton(
                                    content="Повторить",
                                    leading=ft.Icon(ft.Icons.REDO),
                                    on_click=pick("Повторить"),
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Контекстное меню:", size=12, color=MUTED),
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            tooltip="Открыть меню",
                            items=[
                                ft.PopupMenuItem(
                                    content="Обновить",
                                    icon=ft.Icons.REFRESH,
                                    on_click=pick("Обновить"),
                                ),
                                ft.PopupMenuItem(
                                    content="Показывать сетку",
                                    checked=True,
                                    on_click=pick("Показывать сетку"),
                                ),
                                ft.PopupMenuItem(),
                                ft.PopupMenuItem(
                                    content="Удалить",
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    on_click=pick("Удалить"),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            tags=["MenuBar", "SubmenuButton", "MenuItemButton", "PopupMenuButton"],
            col={"md": 6, "xxl": 4},
        )

    def _hints(self):
        return section(
            "Подсказки и метки",
            "Tooltip с богатым содержимым и Badge поверх контрола",
            [
                ft.Row(
                    wrap=True,
                    spacing=16,
                    run_spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=12,
                            border_radius=10,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                            content=ft.Text("Наведи курсор", size=12),
                            tooltip=ft.Tooltip(
                                message="Tooltip умеет показывать длинный текст "
                                "и настраиваемый фон",
                                bgcolor=ft.Colors.INVERSE_SURFACE,
                                text_style=ft.TextStyle(
                                    color=ft.Colors.ON_INVERSE_SURFACE, size=12
                                ),
                                padding=10,
                                wait_duration=200,
                            ),
                        ),
                        ft.Icon(
                            ft.Icons.MAIL_OUTLINE,
                            size=30,
                            badge=ft.Badge(label="12", small_size=16),
                        ),
                        ft.Icon(
                            ft.Icons.NOTIFICATIONS_NONE,
                            size=30,
                            badge=ft.Badge(bgcolor=ft.Colors.RED, small_size=10),
                        ),
                        ft.ProgressRing(width=20, height=20, stroke_width=2),
                        ft.Text("Индикатор загрузки", size=12, color=MUTED),
                    ],
                ),
            ],
            tags=["Tooltip", "Badge", "ProgressRing"],
            col={"md": 6, "xxl": 4},
        )


def build():
    return FeedbackPage()
