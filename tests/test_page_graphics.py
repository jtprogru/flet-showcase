"""Раздел «Графика»: рисование, анимации, drag-and-drop и наведение."""

import flet as ft
import flet.canvas as cv
import pytest
from conftest import event, mount, walk

from app.pages.graphics import GraphicsPage


@pytest.fixture
def graphics(page):
    return mount(GraphicsPage())


def drag_event(control, x, y, name="pan_update"):
    return ft.DragUpdateEvent(
        name=name,
        data=None,
        control=control,
        local_position=ft.Offset(x, y),
        global_position=ft.Offset(x, y),
        local_delta=ft.Offset(0, 0),
        global_delta=ft.Offset(0, 0),
        primary_delta=None,
        timestamp=0,
    )


def test_pan_draws_lines_between_points(graphics):
    graphics._pan_start(drag_event(graphics.canvas, 10, 10, "pan_start"))
    graphics._pan_update(drag_event(graphics.canvas, 20, 30))
    graphics._pan_update(drag_event(graphics.canvas, 40, 35))

    lines = [s for s in graphics.canvas.shapes if isinstance(s, cv.Line)]
    assert len(lines) == 2
    assert (lines[0].x1, lines[0].y1, lines[0].x2, lines[0].y2) == (10, 10, 20, 30)
    assert (lines[1].x1, lines[1].y1) == (20, 30)


def test_pan_without_start_uses_current_point(graphics):
    graphics._pan_update(drag_event(graphics.canvas, 5, 5))
    line = graphics.canvas.shapes[-1]
    assert (line.x1, line.y1, line.x2, line.y2) == (5, 5, 5, 5)


def test_stroke_settings_apply_to_new_lines(graphics):
    graphics._pick_color(event(ft.Container(data=ft.Colors.RED)))
    graphics._set_width(event(ft.Slider(value=12), "change"))
    graphics._pan_update(drag_event(graphics.canvas, 1, 1))

    paint = graphics.canvas.shapes[-1].paint
    assert paint.color == ft.Colors.RED
    assert paint.stroke_width == 12


def test_clear_canvas(graphics):
    graphics._pan_update(drag_event(graphics.canvas, 1, 1))
    graphics._clear_canvas(event(graphics))
    assert graphics.canvas.shapes == []


def test_size_animation_toggles_box(graphics):
    box = graphics.animated_box
    before = (box.width, box.bgcolor, box.border_radius)

    graphics._animate_size(event(graphics))
    assert (box.width, box.bgcolor, box.border_radius) != before

    graphics._animate_size(event(graphics))
    assert (box.width, box.bgcolor, box.border_radius) == before


def test_rotate_scale_offset_and_opacity(graphics):
    angle = graphics.animated_box.rotate.angle
    graphics._animate_rotate(event(graphics))
    assert graphics.animated_box.rotate.angle > angle

    graphics._animate_scale(event(graphics))
    assert graphics.animated_box.scale.scale == 1.4
    graphics._animate_scale(event(graphics))
    assert graphics.animated_box.scale.scale == 1

    graphics._animate_offset(event(graphics))
    assert graphics.animated_box.offset.x == 0.6
    graphics._animate_offset(event(graphics))
    assert graphics.animated_box.offset.x == 0

    graphics._animate_opacity(event(graphics))
    assert graphics.opacity_box.opacity == 0.25
    graphics._animate_opacity(event(graphics))
    assert graphics.opacity_box.opacity == 1.0


def test_switcher_cycles_through_cards(graphics):
    first = graphics.switcher.content.key
    graphics._next_content(event(graphics))
    assert graphics.switcher.content.key != first

    for _ in range(3):
        graphics._next_content(event(graphics))
    assert graphics.switcher.content.key == "4"


def test_switch_transition_changes(graphics):
    control = ft.Dropdown(value=ft.AnimatedSwitcherTransition.ROTATION.value)
    graphics._change_transition(event(control, "select"))
    assert graphics.switcher.transition == ft.AnimatedSwitcherTransition.ROTATION


def test_drag_target_highlights_and_accepts(graphics, page):
    draggable = page.register(
        next(c for c in walk(graphics) if isinstance(c, ft.Draggable))
    )

    will_accept = ft.DragWillAcceptEvent(
        name="will_accept",
        data=None,
        control=graphics.drop_zone,
        src_id=draggable._i,
        accept=True,
    )
    graphics._drag_will_accept(will_accept)
    assert graphics.drop_zone.border.top.color == ft.Colors.GREEN

    will_accept.accept = False
    graphics._drag_will_accept(will_accept)
    assert graphics.drop_zone.border.top.color == ft.Colors.RED

    graphics._drag_leave(event(graphics.drop_zone, "leave"))
    assert graphics.drop_zone.border.top.color == ft.Colors.OUTLINE_VARIANT

    accept = ft.DragTargetEvent(
        name="accept",
        data=None,
        control=graphics.drop_zone,
        src_id=draggable._i,
        local_position=ft.Offset(0, 0),
        global_position=ft.Offset(0, 0),
    )
    graphics._drag_accept(accept)
    assert graphics.drop_zone.content.value == "Принято"
    assert graphics.drop_zone.border.top.color == draggable.data


def test_hover_scales_card(graphics):
    graphics._hover(event(graphics.hover_card, "hover", data="true"))
    assert graphics.hover_card.scale.scale == 1.06
    assert graphics.hover_card.bgcolor == ft.Colors.PRIMARY_CONTAINER

    graphics._hover(event(graphics.hover_card, "hover", data="false"))
    assert graphics.hover_card.scale.scale == 1
    assert graphics.hover_card.bgcolor == ft.Colors.SURFACE_CONTAINER_HIGH


def test_static_shapes_are_drawn(graphics):
    canvases = [c for c in walk(graphics) if isinstance(c, cv.Canvas)]
    assert len(canvases) >= 2
    shapes = [type(s).__name__ for c in canvases for s in c.shapes]
    assert {"Circle", "Path", "Text"} <= set(shapes)
