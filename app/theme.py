"""Управление темой приложения: режим, seed-цвет и шрифт."""

import flet as ft

SEED_COLORS = {
    "Индиго": ft.Colors.INDIGO,
    "Бирюза": ft.Colors.TEAL,
    "Пурпур": ft.Colors.PURPLE,
    "Янтарь": ft.Colors.AMBER,
    "Малина": ft.Colors.PINK,
    "Океан": ft.Colors.BLUE,
    "Лес": ft.Colors.GREEN,
    "Закат": ft.Colors.DEEP_ORANGE,
}

MODE_TITLES = {
    ft.ThemeMode.LIGHT: "Светлая",
    ft.ThemeMode.DARK: "Тёмная",
    ft.ThemeMode.SYSTEM: "Как в системе",
}


class ThemeController:
    """Единая точка изменения темы: страницы и панель сверху смотрят сюда."""

    def __init__(self, seed=ft.Colors.INDIGO, mode=ft.ThemeMode.SYSTEM):
        self.page = None
        self.seed = seed
        self.mode = mode
        self.font = None
        self._listeners = []

    def attach(self, page):
        self.page = page
        self.apply(update=False)

    def subscribe(self, callback):
        self._listeners.append(callback)

    def apply(self, update=True):
        if self.page is None:
            return
        self.page.theme = ft.Theme(color_scheme_seed=self.seed, font_family=self.font)
        self.page.dark_theme = ft.Theme(
            color_scheme_seed=self.seed, font_family=self.font
        )
        self.page.theme_mode = self.mode
        for callback in self._listeners:
            callback(self)
        if update:
            self.page.update()

    def set_mode(self, mode):
        self.mode = mode
        self.apply()

    def set_seed(self, seed):
        self.seed = seed
        self.apply()

    def set_font(self, font):
        self.font = font
        self.apply()

    def toggle_mode(self):
        """Переключение светлая ↔ тёмная одной кнопкой."""
        self.mode = (
            ft.ThemeMode.DARK
            if self.mode in (ft.ThemeMode.LIGHT, ft.ThemeMode.SYSTEM)
            else ft.ThemeMode.LIGHT
        )
        self.apply()

    @property
    def is_dark(self):
        if self.mode == ft.ThemeMode.SYSTEM and self.page is not None:
            return self.page.platform_brightness == ft.Brightness.DARK
        return self.mode == ft.ThemeMode.DARK
