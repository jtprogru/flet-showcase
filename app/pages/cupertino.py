"""Cupertino: набор контролов в стиле iOS."""

import flet as ft

from app.ui import MUTED, page_header, section

FRUITS = ["Яблоко", "Груша", "Слива", "Персик", "Манго"]


class CupertinoPage(ft.Column):
    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True
        self.log = ft.Text("Выбери что-нибудь в iOS-контролах", size=12, color=MUTED)

        self.controls = [
            page_header(
                "Cupertino",
                "Те же сценарии в оформлении iOS: кнопки, переключатели, пикеры",
                ft.Icons.PHONE_IPHONE,
            ),
            ft.Card(
                variant=ft.CardVariant.FILLED,
                content=ft.Container(
                    padding=12,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.PRIMARY),
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
                    self._toggles(),
                    self._segments(),
                    self._pickers(),
                    self._dialogs(),
                    self._lists(),
                ],
            ),
        ]

    def _say(self, message):
        self.log.value = message
        self.log.update()

    def _buttons(self):
        return section(
            "Кнопки",
            "CupertinoButton в трёх вариантах и индикатор активности",
            [
                ft.Row(
                    wrap=True,
                    spacing=10,
                    run_spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.CupertinoButton(
                            content="Обычная",
                            on_click=lambda e: self._say("CupertinoButton"),
                        ),
                        ft.CupertinoFilledButton(
                            content="Залитая",
                            on_click=lambda e: self._say("CupertinoFilledButton"),
                        ),
                        ft.CupertinoTintedButton(
                            content="С подсветкой",
                            on_click=lambda e: self._say("CupertinoTintedButton"),
                        ),
                        ft.CupertinoActivityIndicator(radius=14),
                    ],
                ),
            ],
            tags=[
                "CupertinoButton",
                "CupertinoFilledButton",
                "CupertinoActivityIndicator",
            ],
            col={"md": 6, "xxl": 4},
        )

    def _toggles(self):
        return section(
            "Переключатели",
            "Switch, Checkbox, Radio и Slider в стиле iOS",
            [
                ft.CupertinoSwitch(
                    label="Уведомления",
                    value=True,
                    on_change=lambda e: self._say(
                        f"CupertinoSwitch → {e.control.value}"
                    ),
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.CupertinoCheckbox(
                            label="Согласен",
                            value=True,
                            on_change=lambda e: self._say(
                                f"CupertinoCheckbox → {e.control.value}"
                            ),
                        ),
                    ],
                ),
                ft.RadioGroup(
                    value="a",
                    on_change=lambda e: self._say(
                        f"CupertinoRadio → {e.control.value}"
                    ),
                    content=ft.Row(
                        spacing=16,
                        controls=[
                            ft.CupertinoRadio(value="a", label="Первый"),
                            ft.CupertinoRadio(value="b", label="Второй"),
                        ],
                    ),
                ),
                ft.CupertinoSlider(
                    value=40,
                    min=0,
                    max=100,
                    divisions=10,
                    on_change=lambda e: self._say(
                        f"CupertinoSlider → {e.control.value:.0f}"
                    ),
                ),
            ],
            tags=[
                "CupertinoSwitch",
                "CupertinoCheckbox",
                "CupertinoRadio",
                "CupertinoSlider",
            ],
            col={"md": 6, "xxl": 4},
        )

    def _segments(self):
        return section(
            "Сегментированные переключатели",
            "Классический и скользящий варианты",
            [
                ft.CupertinoSegmentedButton(
                    selected_index=1,
                    selected_color=ft.Colors.PRIMARY,
                    unselected_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    on_change=lambda e: self._say(
                        f"CupertinoSegmentedButton → {e.control.selected_index}"
                    ),
                    controls=[
                        ft.Text("День"),
                        ft.Text("Неделя"),
                        ft.Text("Месяц"),
                    ],
                ),
                ft.CupertinoSlidingSegmentedButton(
                    selected_index=0,
                    thumb_color=ft.Colors.PRIMARY_CONTAINER,
                    on_change=lambda e: self._say(
                        f"CupertinoSlidingSegmentedButton → {e.control.selected_index}"
                    ),
                    controls=[
                        ft.Text("Список"),
                        ft.Text("Сетка"),
                        ft.Text("Карта"),
                    ],
                ),
                ft.CupertinoTextField(
                    placeholder_text="CupertinoTextField",
                    prefix=ft.Icon(ft.Icons.SEARCH, size=18),
                    clear_button_visibility_mode=ft.OverlayVisibilityMode.EDITING,
                    on_change=lambda e: self._say(
                        f"CupertinoTextField → {e.control.value!r}"
                    ),
                ),
            ],
            tags=[
                "CupertinoSegmentedButton",
                "CupertinoSlidingSegmentedButton",
                "CupertinoTextField",
            ],
            col={"md": 6, "xxl": 4},
        )

    def _pickers(self):
        return section(
            "Барабаны выбора",
            "CupertinoPicker и таймер прямо на странице",
            [
                ft.Container(
                    height=150,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    content=ft.CupertinoPicker(
                        item_extent=32,
                        selected_index=1,
                        use_magnifier=True,
                        magnification=1.2,
                        on_change=lambda e: self._say(
                            f"CupertinoPicker → {FRUITS[e.control.selected_index]}"
                        ),
                        controls=[ft.Text(name) for name in FRUITS],
                    ),
                ),
                ft.Container(
                    height=170,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    content=ft.CupertinoTimerPicker(
                        value=600,
                        mode=ft.CupertinoTimerPickerMode.HOUR_MINUTE,
                        on_change=lambda e: self._say(
                            f"CupertinoTimerPicker → {e.control.value} с"
                        ),
                    ),
                ),
            ],
            tags=["CupertinoPicker", "CupertinoTimerPicker"],
            col={"md": 6, "xxl": 4},
        )

    def _dialogs(self):
        return section(
            "Диалоги iOS",
            "CupertinoAlertDialog и нижний ActionSheet",
            [
                ft.Row(
                    wrap=True,
                    spacing=10,
                    run_spacing=10,
                    controls=[
                        ft.CupertinoButton(
                            content="Alert",
                            on_click=self._open_alert,
                        ),
                        ft.CupertinoButton(
                            content="Action sheet",
                            on_click=self._open_sheet,
                        ),
                    ],
                ),
            ],
            tags=[
                "CupertinoAlertDialog",
                "CupertinoActionSheet",
                "CupertinoBottomSheet",
            ],
            col={"md": 6, "xxl": 4},
        )

    def _open_alert(self, e):
        self.page.show_dialog(
            ft.CupertinoAlertDialog(
                title=ft.Text("Удалить фото?"),
                content=ft.Text("Его нельзя будет восстановить."),
                actions=[
                    ft.CupertinoDialogAction(
                        content="Отмена", default=True, on_click=self._close
                    ),
                    ft.CupertinoDialogAction(
                        content="Удалить", destructive=True, on_click=self._close
                    ),
                ],
            )
        )

    def _open_sheet(self, e):
        self.page.show_dialog(
            ft.CupertinoBottomSheet(
                content=ft.CupertinoActionSheet(
                    title=ft.Text("Что сделать с файлом?"),
                    message=ft.Text("Выбери действие"),
                    cancel=ft.CupertinoActionSheetAction(
                        content="Отмена", on_click=self._close
                    ),
                    actions=[
                        ft.CupertinoActionSheetAction(
                            content="Открыть", default=True, on_click=self._close
                        ),
                        ft.CupertinoActionSheetAction(
                            content="Дублировать", on_click=self._close
                        ),
                        ft.CupertinoActionSheetAction(
                            content="Удалить", destructive=True, on_click=self._close
                        ),
                    ],
                )
            )
        )

    def _close(self, e):
        self.page.pop_dialog()
        self._say(f"Выбрано: {e.control.content}")

    def _lists(self):
        return section(
            "Списки",
            "CupertinoListTile с дополнительной информацией и переходом",
            [
                ft.Column(
                    spacing=0,
                    tight=True,
                    controls=[
                        ft.CupertinoListTile(
                            title=ft.Text("Wi-Fi"),
                            additional_info=ft.Text("Home-5G", color=MUTED),
                            leading=ft.Icon(ft.Icons.WIFI),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=MUTED),
                            notched=True,
                            on_click=lambda e: self._say("CupertinoListTile → Wi-Fi"),
                        ),
                        ft.CupertinoListTile(
                            title=ft.Text("Bluetooth"),
                            additional_info=ft.Text("Вкл", color=MUTED),
                            leading=ft.Icon(ft.Icons.BLUETOOTH),
                            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=MUTED),
                            notched=True,
                            on_click=lambda e: self._say(
                                "CupertinoListTile → Bluetooth"
                            ),
                        ),
                        ft.CupertinoListTile(
                            title=ft.Text("Аккумулятор"),
                            subtitle=ft.Text("Экономия энергии выключена"),
                            leading=ft.Icon(ft.Icons.BATTERY_CHARGING_FULL),
                            notched=True,
                            on_click=lambda e: self._say("CupertinoListTile → Батарея"),
                        ),
                    ],
                ),
            ],
            tags=["CupertinoListTile"],
            col={"md": 6, "xxl": 4},
        )


def build():
    return CupertinoPage()
