"""Витрина компонентов Flet — точка входа приложения."""

import flet as ft

from app.shell import SECTIONS, Shell, build_appbar
from app.theme import ThemeController


async def main(page: ft.Page):
    page.title = "Витрина компонентов Flet"
    page.padding = 0
    page.spacing = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.vertical_alignment = ft.MainAxisAlignment.START

    controller = ThemeController(seed=ft.Colors.INDIGO, mode=ft.ThemeMode.SYSTEM)
    controller.attach(page)

    shell = Shell(controller)
    page.appbar = build_appbar(controller, shell)
    page.add(shell)

    def on_resize(e):
        shell.adapt(page.width or 1360)

    def on_keyboard(e):
        if not (e.ctrl or e.meta):
            return
        if e.key.lower() == "d":
            controller.toggle_mode()
        elif e.key in "1234567890":
            index = int(e.key) - 1 if e.key != "0" else 9
            if index < len(SECTIONS):
                shell.select(index)

    page.on_resize = on_resize
    page.on_keyboard_event = on_keyboard

    if not page.web:
        page.window.min_width = 900
        page.window.min_height = 640
        page.window.width = 1360
        page.window.height = 900
        page.update()
        await page.window.center()

    shell.adapt(page.width or 1360)


if __name__ == "__main__":
    ft.run(main)
