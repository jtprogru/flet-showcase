"""Графика: рисование на Canvas, анимации, жесты, перетаскивание и слои."""

import math
import random

import flet as ft
import flet.canvas as cv

from app.ui import MUTED, page_header, section

PALETTE = [
    ft.Colors.RED,
    ft.Colors.PINK,
    ft.Colors.PURPLE,
    ft.Colors.INDIGO,
    ft.Colors.BLUE,
    ft.Colors.CYAN,
    ft.Colors.TEAL,
    ft.Colors.GREEN,
    ft.Colors.LIME,
    ft.Colors.AMBER,
    ft.Colors.ORANGE,
    ft.Colors.BROWN,
]


class GraphicsPage(ft.Column):
    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True

        self.controls = [
            page_header(
                "Графика и жесты",
                "Canvas, анимации, перетаскивание, трансформации и наложение слоёв",
                ft.Icons.BRUSH_OUTLINED,
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    self._paint(),
                    self._shapes(),
                    self._animations(),
                    self._switcher(),
                    self._drag_and_drop(),
                    self._stack_and_gradients(),
                    self._interactive_viewer(),
                    self._effects(),
                ],
            ),
        ]

    # --- рисование -----------------------------------------------------

    def _paint(self):
        self.stroke_color = ft.Colors.PRIMARY
        self.stroke_width = 4
        self.canvas = cv.Canvas(
            expand=True,
            shapes=[],
            content=ft.GestureDetector(
                drag_interval=10,
                on_pan_start=self._pan_start,
                on_pan_update=self._pan_update,
                mouse_cursor=ft.MouseCursor.PRECISE,
            ),
        )
        swatches = ft.Row(
            wrap=True,
            spacing=6,
            run_spacing=6,
            controls=[
                ft.Container(
                    width=22,
                    height=22,
                    border_radius=11,
                    bgcolor=color,
                    data=color,
                    ink=True,
                    on_click=self._pick_color,
                    tooltip=str(color).split(".")[-1].lower(),
                )
                for color in PALETTE
            ],
        )
        return section(
            "Рисование мышью",
            "GestureDetector ловит перетаскивание и добавляет линии в Canvas",
            [
                ft.Container(
                    height=260,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=self.canvas,
                ),
                swatches,
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Толщина", size=12, color=MUTED),
                        ft.Slider(
                            value=4,
                            min=1,
                            max=20,
                            divisions=19,
                            expand=True,
                            label="{value}",
                            on_change=self._set_width,
                        ),
                        ft.OutlinedButton(
                            content="Очистить",
                            icon=ft.Icons.CLEAR,
                            on_click=self._clear_canvas,
                        ),
                    ],
                ),
            ],
            tags=["Canvas", "canvas.Path", "GestureDetector", "Paint"],
            col={"md": 12, "xl": 6},
        )

    def _pick_color(self, e):
        self.stroke_color = e.control.data

    def _set_width(self, e):
        self.stroke_width = e.control.value

    def _pan_start(self, e):
        self._last = (e.local_position.x, e.local_position.y)

    def _pan_update(self, e):
        x, y = e.local_position.x, e.local_position.y
        x0, y0 = getattr(self, "_last", (x, y))
        self.canvas.shapes.append(
            cv.Line(
                x0,
                y0,
                x,
                y,
                paint=ft.Paint(
                    color=self.stroke_color,
                    stroke_width=self.stroke_width,
                    stroke_cap=ft.StrokeCap.ROUND,
                ),
            )
        )
        self._last = (x, y)
        self.canvas.update()

    def _clear_canvas(self, e):
        self.canvas.shapes.clear()
        self.canvas.update()

    # --- фигуры --------------------------------------------------------

    def _shapes(self):
        canvas = cv.Canvas(
            expand=True,
            shapes=[
                cv.Circle(
                    70,
                    80,
                    45,
                    paint=ft.Paint(
                        gradient=ft.PaintRadialGradient(
                            (60, 60),
                            60,
                            colors=[ft.Colors.CYAN_200, ft.Colors.BLUE_900],
                        )
                    ),
                ),
                cv.Oval(
                    140,
                    40,
                    110,
                    80,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        stroke_width=4,
                        color=ft.Colors.PINK,
                        stroke_dash_pattern=[10, 6],
                    ),
                ),
                cv.Arc(
                    280,
                    35,
                    90,
                    90,
                    math.pi * 0.8,
                    math.pi * 1.4,
                    use_center=True,
                    paint=ft.Paint(color=ft.Colors.AMBER),
                ),
                cv.Path(
                    elements=[
                        cv.Path.MoveTo(30, 190),
                        cv.Path.QuadraticTo(120, 110, 200, 190),
                        cv.Path.QuadraticTo(280, 265, 370, 175),
                    ],
                    paint=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        stroke_width=5,
                        stroke_cap=ft.StrokeCap.ROUND,
                        gradient=ft.PaintLinearGradient(
                            (30, 0),
                            (370, 0),
                            colors=[ft.Colors.GREEN, ft.Colors.PURPLE],
                        ),
                    ),
                ),
                cv.Points(
                    points=[(30 + i * 22, 235) for i in range(16)],
                    point_mode=cv.PointMode.POINTS,
                    paint=ft.Paint(
                        stroke_width=8,
                        stroke_cap=ft.StrokeCap.ROUND,
                        color=ft.Colors.TERTIARY,
                    ),
                ),
                cv.Text(
                    30,
                    250,
                    "canvas.Text рисует прямо на холсте",
                    ft.TextStyle(size=13, color=MUTED),
                ),
            ],
        )
        return section(
            "Фигуры на холсте",
            "Круги, дуги, кривые Безье, точки и текст с градиентными кистями",
            [
                ft.Container(
                    height=290,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=canvas,
                )
            ],
            tags=["canvas.Circle", "canvas.Arc", "canvas.Path", "PaintLinearGradient"],
            col={"md": 12, "xl": 6},
        )

    # --- анимации ------------------------------------------------------

    def _animations(self):
        self.animated_box = ft.Container(
            width=110,
            height=110,
            border_radius=16,
            bgcolor=ft.Colors.PRIMARY,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.ON_PRIMARY),
            animate=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
            animate_rotation=ft.Animation(500, ft.AnimationCurve.ELASTIC_OUT),
            animate_scale=ft.Animation(400, ft.AnimationCurve.EASE_OUT_BACK),
            animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
            rotate=ft.Rotate(0, ft.Alignment.CENTER),
            scale=ft.Scale(1),
            offset=ft.Offset(0, 0),
        )
        self.opacity_box = ft.Container(
            width=110,
            height=110,
            border_radius=16,
            bgcolor=ft.Colors.TERTIARY,
            opacity=1.0,
            animate_opacity=400,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(ft.Icons.OPACITY, color=ft.Colors.ON_TERTIARY),
        )
        return section(
            "Анимации свойств",
            "Размер, цвет, поворот, масштаб, сдвиг и прозрачность анимируются сами",
            [
                ft.Row(
                    spacing=16,
                    controls=[self.animated_box, self.opacity_box],
                ),
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.OutlinedButton(
                            content="Размер и цвет",
                            icon=ft.Icons.ASPECT_RATIO,
                            on_click=self._animate_size,
                        ),
                        ft.OutlinedButton(
                            content="Поворот",
                            icon=ft.Icons.ROTATE_RIGHT,
                            on_click=self._animate_rotate,
                        ),
                        ft.OutlinedButton(
                            content="Масштаб",
                            icon=ft.Icons.ZOOM_OUT_MAP,
                            on_click=self._animate_scale,
                        ),
                        ft.OutlinedButton(
                            content="Сдвиг",
                            icon=ft.Icons.SWAP_HORIZ,
                            on_click=self._animate_offset,
                        ),
                        ft.OutlinedButton(
                            content="Прозрачность",
                            icon=ft.Icons.OPACITY,
                            on_click=self._animate_opacity,
                        ),
                    ],
                ),
            ],
            tags=["Animation", "Rotate", "Scale", "Offset", "animate_opacity"],
            col={"md": 12, "xl": 6},
        )

    def _animate_size(self, e):
        box = self.animated_box
        box.width = 160 if box.width == 110 else 110
        box.height = 160 if box.height == 110 else 110
        box.bgcolor = (
            ft.Colors.SECONDARY
            if box.bgcolor == ft.Colors.PRIMARY
            else ft.Colors.PRIMARY
        )
        box.border_radius = 60 if box.border_radius == 16 else 16
        box.update()

    def _animate_rotate(self, e):
        self.animated_box.rotate.angle += math.pi / 2
        self.animated_box.update()

    def _animate_scale(self, e):
        current = self.animated_box.scale.scale or 1
        self.animated_box.scale = ft.Scale(1 if current > 1 else 1.4)
        self.animated_box.update()

    def _animate_offset(self, e):
        current = self.animated_box.offset.x
        self.animated_box.offset = ft.Offset(0 if current else 0.6, 0)
        self.animated_box.update()

    def _animate_opacity(self, e):
        self.opacity_box.opacity = 0.25 if self.opacity_box.opacity == 1.0 else 1.0
        self.opacity_box.update()

    # --- переключение содержимого --------------------------------------

    def _switcher(self):
        self._switch_index = 0
        self.switcher = ft.AnimatedSwitcher(
            duration=500,
            reverse_duration=300,
            transition=ft.AnimatedSwitcherTransition.SCALE,
            switch_in_curve=ft.AnimationCurve.EASE_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN,
            content=self._switch_content(0),
        )
        self.transition_dropdown = ft.Dropdown(
            label="Тип перехода",
            value="scale",
            options=[
                ft.DropdownOption(key="scale", text="scale"),
                ft.DropdownOption(key="fade", text="fade"),
                ft.DropdownOption(key="rotation", text="rotation"),
            ],
            on_select=self._change_transition,
        )
        return section(
            "Смена содержимого",
            "AnimatedSwitcher с выбором типа перехода и мерцающий Shimmer",
            [
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.switcher,
                        ft.FilledTonalButton(
                            content="Следующий",
                            icon=ft.Icons.NAVIGATE_NEXT,
                            on_click=self._next_content,
                        ),
                    ],
                ),
                self.transition_dropdown,
                ft.Shimmer(
                    period=1600,
                    base_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    highlight_color=ft.Colors.PRIMARY_CONTAINER,
                    content=ft.Column(
                        spacing=8,
                        tight=True,
                        controls=[
                            ft.Container(
                                height=14,
                                width=220,
                                border_radius=7,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            ),
                            ft.Container(
                                height=14,
                                width=160,
                                border_radius=7,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            ),
                        ],
                    ),
                ),
            ],
            tags=["AnimatedSwitcher", "Shimmer"],
            col={"md": 12, "xl": 6},
        )

    def _switch_content(self, index):
        icons = [
            (ft.Icons.WB_SUNNY, ft.Colors.AMBER, "Солнечно"),
            (ft.Icons.CLOUD, ft.Colors.BLUE_GREY, "Облачно"),
            (ft.Icons.THUNDERSTORM, ft.Colors.INDIGO, "Гроза"),
            (ft.Icons.AC_UNIT, ft.Colors.CYAN, "Снег"),
        ]
        icon, color, label = icons[index % len(icons)]
        return ft.Container(
            key=str(index),
            width=150,
            height=110,
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.16, color),
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=34, color=color),
                    ft.Text(label, size=13),
                ],
            ),
        )

    def _next_content(self, e):
        self._switch_index += 1
        self.switcher.content = self._switch_content(self._switch_index)
        self.switcher.update()

    def _change_transition(self, e):
        self.switcher.transition = ft.AnimatedSwitcherTransition(e.control.value)
        self.switcher.update()

    # --- drag and drop -------------------------------------------------

    def _drag_and_drop(self):
        self.drop_zone = ft.Container(
            width=170,
            height=170,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.Border.all(2, ft.Colors.OUTLINE_VARIANT),
            alignment=ft.Alignment.CENTER,
            content=ft.Text("Перетащи сюда", size=12, color=MUTED),
            animate=250,
        )
        draggables = ft.Row(
            spacing=10,
            controls=[
                ft.Draggable(
                    group="colors",
                    content=self._chip(color),
                    content_feedback=self._chip(color, feedback=True),
                    content_when_dragging=ft.Container(
                        width=54,
                        height=54,
                        border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.2, color),
                    ),
                    data=color,
                )
                for color in [ft.Colors.RED, ft.Colors.GREEN, ft.Colors.BLUE]
            ],
        )
        return section(
            "Перетаскивание",
            "Draggable и DragTarget: перетащи цветной квадрат в приёмник",
            [
                ft.Row(
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        draggables,
                        ft.DragTarget(
                            group="colors",
                            content=self.drop_zone,
                            on_will_accept=self._drag_will_accept,
                            on_accept=self._drag_accept,
                            on_leave=self._drag_leave,
                        ),
                    ],
                ),
            ],
            tags=["Draggable", "DragTarget"],
            col={"md": 12, "xl": 6},
        )

    def _chip(self, color, feedback=False):
        return ft.Container(
            width=54,
            height=54,
            border_radius=12,
            bgcolor=color,
            opacity=0.7 if feedback else 1,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(ft.Icons.DRAG_INDICATOR, color=ft.Colors.WHITE, size=18),
        )

    def _drag_will_accept(self, e):
        self.drop_zone.border = ft.Border.all(
            2, ft.Colors.GREEN if e.accept else ft.Colors.RED
        )
        self.drop_zone.update()

    def _drag_leave(self, e):
        self.drop_zone.border = ft.Border.all(2, ft.Colors.OUTLINE_VARIANT)
        self.drop_zone.update()

    def _drag_accept(self, e):
        self.drop_zone.bgcolor = ft.Colors.with_opacity(0.3, e.src.data)
        self.drop_zone.border = ft.Border.all(2, e.src.data)
        self.drop_zone.content = ft.Text("Принято", size=12)
        self.drop_zone.update()

    # --- слои и градиенты ----------------------------------------------

    def _stack_and_gradients(self):
        stack = ft.Stack(
            width=260,
            height=170,
            controls=[
                ft.Container(
                    width=260,
                    height=170,
                    border_radius=16,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[ft.Colors.INDIGO, ft.Colors.PURPLE, ft.Colors.PINK],
                    ),
                ),
                ft.Container(
                    left=16,
                    top=16,
                    padding=8,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
                    blur=8,
                    content=ft.Text("Стекло и блюр", color=ft.Colors.WHITE, size=12),
                ),
                ft.Container(
                    right=14,
                    bottom=14,
                    content=ft.CircleAvatar(
                        radius=22,
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Icon(ft.Icons.LAYERS, color=ft.Colors.INDIGO),
                    ),
                ),
            ],
        )
        gradients = ft.Row(
            spacing=10,
            controls=[
                ft.Container(
                    width=76,
                    height=76,
                    border_radius=14,
                    gradient=ft.RadialGradient(
                        center=ft.Alignment.CENTER,
                        radius=0.8,
                        colors=[ft.Colors.AMBER, ft.Colors.DEEP_ORANGE],
                    ),
                ),
                ft.Container(
                    width=76,
                    height=76,
                    border_radius=14,
                    gradient=ft.SweepGradient(
                        center=ft.Alignment.CENTER,
                        colors=[
                            ft.Colors.CYAN,
                            ft.Colors.BLUE,
                            ft.Colors.PURPLE,
                            ft.Colors.CYAN,
                        ],
                    ),
                ),
                ft.Container(
                    width=76,
                    height=76,
                    border_radius=14,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=18,
                            spread_radius=1,
                            color=ft.Colors.with_opacity(0.4, ft.Colors.PRIMARY),
                            offset=ft.Offset(0, 8),
                        )
                    ],
                    content=ft.Icon(ft.Icons.LIGHT_MODE, color=ft.Colors.PRIMARY),
                    alignment=ft.Alignment.CENTER,
                ),
            ],
        )
        return section(
            "Слои, градиенты и тени",
            "Stack с абсолютным позиционированием, три вида градиентов и BoxShadow",
            [stack, gradients],
            tags=[
                "Stack",
                "LinearGradient",
                "RadialGradient",
                "SweepGradient",
                "BoxShadow",
            ],
            col={"md": 12, "xl": 6},
        )

    # --- прочее --------------------------------------------------------

    def _interactive_viewer(self):
        grid = ft.Column(
            spacing=4,
            controls=[
                ft.Row(
                    spacing=4,
                    controls=[
                        ft.Container(
                            width=44,
                            height=44,
                            border_radius=8,
                            bgcolor=random.choice(PALETTE),
                            opacity=0.85,
                        )
                        for _ in range(8)
                    ],
                )
                for _ in range(5)
            ],
        )
        return section(
            "Масштабирование и панорама",
            "InteractiveViewer: колесо мыши приближает, перетаскивание двигает",
            [
                ft.Container(
                    height=240,
                    border_radius=12,
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.InteractiveViewer(
                        min_scale=0.5,
                        max_scale=5,
                        boundary_margin=ft.Margin.all(60),
                        content=ft.Container(
                            padding=20, alignment=ft.Alignment.CENTER, content=grid
                        ),
                    ),
                )
            ],
            tags=["InteractiveViewer"],
            col={"md": 12, "xl": 6},
        )

    def _effects(self):
        self.hover_card = ft.Container(
            width=190,
            height=110,
            border_radius=14,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            alignment=ft.Alignment.CENTER,
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            scale=ft.Scale(1),
            content=ft.Text("Наведи курсор", size=12),
            on_hover=self._hover,
        )
        return section(
            "Эффекты и реакция на курсор",
            "ShaderMask с градиентом, RotatedBox и увеличение карточки при наведении",
            [
                ft.Row(
                    spacing=16,
                    wrap=True,
                    run_spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.ShaderMask(
                            border_radius=12,
                            blend_mode=ft.BlendMode.MODULATE,
                            shader=ft.LinearGradient(
                                begin=ft.Alignment.TOP_CENTER,
                                end=ft.Alignment.BOTTOM_CENTER,
                                colors=[ft.Colors.WHITE, ft.Colors.TRANSPARENT],
                            ),
                            content=ft.Container(
                                width=150,
                                height=110,
                                bgcolor=ft.Colors.PRIMARY,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    "ShaderMask",
                                    color=ft.Colors.ON_PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                        ),
                        ft.Container(
                            width=110,
                            height=110,
                            border_radius=12,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                            alignment=ft.Alignment.CENTER,
                            content=ft.RotatedBox(
                                quarter_turns=3,
                                content=ft.Text("RotatedBox", size=13),
                            ),
                        ),
                        self.hover_card,
                    ],
                ),
            ],
            tags=["ShaderMask", "RotatedBox", "on_hover"],
            col={"md": 12, "xl": 6},
        )

    def _hover(self, e):
        entered = e.data == "true" if isinstance(e.data, str) else bool(e.data)
        self.hover_card.scale = ft.Scale(1.06 if entered else 1)
        self.hover_card.bgcolor = (
            ft.Colors.PRIMARY_CONTAINER if entered else ft.Colors.SURFACE_CONTAINER_HIGH
        )
        self.hover_card.update()


def build():
    return GraphicsPage()
