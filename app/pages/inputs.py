"""Контролы ввода: текст, переключатели, ползунки, выбор даты и файлов."""

import flet as ft

from app.ui import MUTED, page_header, section

CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Самара",
    "Омск",
    "Уфа",
]


class InputsPage(ft.Column):
    """Все основные поля ввода с живым отображением значений."""

    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True

        self.state = ft.Text(
            "Изменяй контролы — значения появятся здесь",
            size=12,
            color=MUTED,
            selectable=True,
        )

        self.controls = [
            page_header(
                "Ввод",
                "Текстовые поля, переключатели, ползунки, выбор даты, времени и файлов",
                ft.Icons.KEYBOARD_ALT_OUTLINED,
            ),
            ft.Card(
                variant=ft.CardVariant.FILLED,
                content=ft.Container(
                    padding=12,
                    content=ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.SENSORS, color=ft.Colors.PRIMARY),
                            self.state,
                        ],
                    ),
                ),
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    self._text_fields(),
                    self._toggles(),
                    self._sliders(),
                    self._selection(),
                    self._search(),
                    self._pickers(),
                ],
            ),
        ]

    def _report(self, name):
        def handler(e):
            value = getattr(e.control, "value", None)
            self.state.value = f"{name} → {value!r}"
            self.state.update()

        return handler

    def _text_fields(self):
        return section(
            "Текстовые поля",
            "Варианты TextField: обычный, пароль, многострочный, с фильтром ввода",
            [
                ft.TextField(
                    label="Имя",
                    hint_text="Как к тебе обращаться",
                    prefix_icon=ft.Icons.PERSON_OUTLINE,
                    helper="Обычное поле с подсказкой",
                    on_change=self._report("TextField «Имя»"),
                ),
                ft.TextField(
                    label="Пароль",
                    password=True,
                    can_reveal_password=True,
                    prefix_icon=ft.Icons.LOCK_OUTLINE,
                    on_change=self._report("TextField «Пароль»"),
                ),
                ft.TextField(
                    label="Только цифры",
                    input_filter=ft.NumbersOnlyInputFilter(),
                    prefix_icon=ft.Icons.PIN_OUTLINED,
                    suffix="₽",
                    on_change=self._report("TextField «Цифры»"),
                ),
                ft.TextField(
                    label="Комментарий",
                    multiline=True,
                    min_lines=2,
                    max_lines=4,
                    max_length=140,
                    filled=True,
                    on_change=self._report("TextField «Комментарий»"),
                ),
            ],
            tags=["TextField", "InputFilter"],
            col={"md": 6, "xxl": 4},
        )

    def _toggles(self):
        return section(
            "Переключатели",
            "Checkbox с тремя состояниями, Switch и группа Radio",
            [
                ft.Checkbox(
                    label="Обычный чекбокс",
                    value=True,
                    on_change=self._report("Checkbox"),
                ),
                ft.Checkbox(
                    label="Трёхпозиционный (tristate)",
                    tristate=True,
                    value=None,
                    on_change=self._report("Checkbox tristate"),
                ),
                ft.Switch(
                    label="Уведомления",
                    value=True,
                    on_change=self._report("Switch"),
                ),
                ft.Switch(
                    label="Слева от подписи",
                    label_position=ft.LabelPosition.LEFT,
                    active_color=ft.Colors.TERTIARY,
                    on_change=self._report("Switch (label слева)"),
                ),
                ft.RadioGroup(
                    value="mid",
                    on_change=self._report("RadioGroup"),
                    content=ft.Column(
                        tight=True,
                        spacing=0,
                        controls=[
                            ft.Radio(value="low", label="Низкий приоритет"),
                            ft.Radio(value="mid", label="Средний приоритет"),
                            ft.Radio(value="high", label="Высокий приоритет"),
                        ],
                    ),
                ),
            ],
            tags=["Checkbox", "Switch", "Radio", "RadioGroup"],
            col={"md": 6, "xxl": 4},
        )

    def _sliders(self):
        self.slider_value = ft.Text("60", size=12, color=MUTED)
        return section(
            "Ползунки",
            "Slider с делениями, RangeSlider и индикаторы прогресса",
            [
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.VOLUME_DOWN, size=18),
                        ft.Slider(
                            value=60,
                            min=0,
                            max=100,
                            divisions=20,
                            label="{value}%",
                            expand=True,
                            on_change=self._slider_changed,
                        ),
                        self.slider_value,
                    ],
                ),
                ft.RangeSlider(
                    start_value=20,
                    end_value=80,
                    min=0,
                    max=100,
                    divisions=10,
                    round=0,
                    label="{value}",
                    on_change=self._range_changed,
                ),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.ProgressRing(width=22, height=22, stroke_width=3),
                        ft.ProgressBar(expand=True, border_radius=6),
                        ft.ProgressRing(
                            value=0.65, width=22, height=22, stroke_width=3
                        ),
                    ],
                ),
            ],
            tags=["Slider", "RangeSlider", "ProgressBar", "ProgressRing"],
            col={"md": 6, "xxl": 4},
        )

    def _slider_changed(self, e):
        self.slider_value.value = f"{e.control.value:.0f}"
        self.slider_value.update()
        self.state.value = f"Slider → {e.control.value:.0f}"
        self.state.update()

    def _range_changed(self, e):
        self.state.value = (
            f"RangeSlider → {e.control.start_value:.0f}…{e.control.end_value:.0f}"
        )
        self.state.update()

    def _selection(self):
        self.chips = ft.Row(wrap=True, spacing=8, run_spacing=8)
        self.chips.controls = [
            ft.Chip(
                label=name,
                leading=ft.Icon(ft.Icons.TAG),
                selected=name == "flet",
                show_checkmark=True,
                on_select=self._chip_selected,
                on_delete=self._chip_deleted,
                delete_icon_tooltip="Убрать",
            )
            for name in ["python", "flet", "gui", "demo"]
        ]
        return section(
            "Выбор из набора",
            "Dropdown с поиском, SegmentedButton и удаляемые Chip",
            [
                ft.Dropdown(
                    label="Город",
                    enable_filter=True,
                    editable=True,
                    leading_icon=ft.Icons.LOCATION_CITY,
                    options=[ft.DropdownOption(key=city, text=city) for city in CITIES],
                    on_select=self._report("Dropdown"),
                ),
                ft.SegmentedButton(
                    selected=["day"],
                    allow_multiple_selection=False,
                    on_change=self._segment_changed,
                    segments=[
                        ft.Segment(value="day", label="День", icon=ft.Icons.LIGHT_MODE),
                        ft.Segment(
                            value="week", label="Неделя", icon=ft.Icons.DATE_RANGE
                        ),
                        ft.Segment(
                            value="month", label="Месяц", icon=ft.Icons.CALENDAR_MONTH
                        ),
                    ],
                ),
                self.chips,
            ],
            tags=["Dropdown", "SegmentedButton", "Chip"],
            col={"md": 6, "xxl": 4},
        )

    def _segment_changed(self, e):
        self.state.value = f"SegmentedButton → {sorted(e.control.selected)}"
        self.state.update()

    def _chip_selected(self, e):
        self.state.value = f"Chip «{e.control.label}» → {e.control.selected}"
        self.state.update()

    def _chip_deleted(self, e):
        self.chips.controls.remove(e.control)
        self.chips.update()
        self.state.value = f"Chip «{e.control.label}» удалён"
        self.state.update()

    def _search(self):
        self.search_bar = ft.SearchBar(
            bar_hint_text="Поиск по городам",
            view_hint_text="Начни вводить название",
            bar_leading=ft.Icon(ft.Icons.SEARCH),
            on_change=self._search_changed,
            on_tap=self._search_open,
            controls=[
                ft.ListTile(title=ft.Text(city), on_click=self._search_pick, data=city)
                for city in CITIES
            ],
        )
        return section(
            "Поиск и подсказки",
            "SearchBar с выпадающим списком и AutoComplete по мере ввода",
            [
                self.search_bar,
                ft.AutoComplete(
                    suggestions=[
                        ft.AutoCompleteSuggestion(key=city.lower(), value=city)
                        for city in CITIES
                    ],
                    on_select=self._autocomplete_selected,
                ),
            ],
            tags=["SearchBar", "AutoComplete"],
            col={"md": 6, "xxl": 4},
        )

    def _search_changed(self, e):
        query = (e.control.value or "").lower()
        for tile in self.search_bar.controls:
            tile.visible = query in tile.data.lower()
        self.search_bar.update()

    async def _search_open(self, e):
        await self.search_bar.open_view()

    async def _search_pick(self, e):
        self.search_bar.value = e.control.data
        await self.search_bar.close_view(e.control.data)
        self.state.value = f"SearchBar → {e.control.data}"
        self.state.update()

    def _autocomplete_selected(self, e):
        self.state.value = f"AutoComplete → {e.selection.value}"
        self.state.update()

    def _pickers(self):
        self.picker_result = ft.Text("Ничего не выбрано", size=12, color=MUTED)
        self.file_picker = ft.FilePicker()
        return section(
            "Дата, время и файлы",
            "DatePicker, TimePicker и системный выбор файлов",
            [
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.FilledTonalButton(
                            content="Выбрать дату",
                            icon=ft.Icons.CALENDAR_MONTH,
                            on_click=self._pick_date,
                        ),
                        ft.FilledTonalButton(
                            content="Выбрать время",
                            icon=ft.Icons.SCHEDULE,
                            on_click=self._pick_time,
                        ),
                        ft.FilledTonalButton(
                            content="Выбрать файл",
                            icon=ft.Icons.ATTACH_FILE,
                            on_click=self._pick_file,
                        ),
                    ],
                ),
                self.picker_result,
            ],
            tags=["DatePicker", "TimePicker", "FilePicker"],
            col={"md": 6, "xxl": 4},
        )

    def _pick_date(self, e):
        import datetime

        self.page.show_dialog(
            ft.DatePicker(
                first_date=datetime.datetime(2020, 1, 1),
                last_date=datetime.datetime(2030, 12, 31),
                help_text="Выбери дату",
                cancel_text="Отмена",
                confirm_text="Готово",
                on_change=self._date_selected,
            )
        )

    def _date_selected(self, e):
        self.picker_result.value = f"Дата: {e.control.value:%d.%m.%Y}"
        self.picker_result.update()

    def _pick_time(self, e):
        self.page.show_dialog(
            ft.TimePicker(
                help_text="Выбери время",
                cancel_text="Отмена",
                confirm_text="Готово",
                on_change=self._time_selected,
            )
        )

    def _time_selected(self, e):
        self.picker_result.value = f"Время: {e.control.value:%H:%M}"
        self.picker_result.update()

    async def _pick_file(self, e):
        if self.file_picker not in self.page.services:
            self.page.services.append(self.file_picker)
        files = await self.file_picker.pick_files(dialog_title="Выбери любой файл")
        if files:
            names = ", ".join(f.name for f in files)
            self.picker_result.value = f"Файл: {names}"
        else:
            self.picker_result.value = "Выбор файла отменён"
        self.picker_result.update()


def build():
    return InputsPage()
