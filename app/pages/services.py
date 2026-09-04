"""Системные возможности: буфер обмена, хранилище, окно, скриншот, платформа."""

import flet as ft

from app.ui import MUTED, page_header, section


class ServicesPage(ft.Column):
    def build(self):
        self.spacing = 16
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.expand = True

        self.clipboard = ft.Clipboard()
        self.prefs = ft.SharedPreferences()
        self.haptic = ft.HapticFeedback()

        self.clipboard_field = ft.TextField(
            label="Текст для буфера",
            value="Витрина Flet",
            dense=True,
            expand=True,
        )
        self.clipboard_result = ft.Text(size=12, color=MUTED)
        self.prefs_field = ft.TextField(
            label="Значение для сохранения",
            value="демо",
            dense=True,
            expand=True,
        )
        self.prefs_result = ft.Text(size=12, color=MUTED)
        self.shot_image = ft.Image(
            src="", width=260, border_radius=10, visible=False, fit=ft.BoxFit.CONTAIN
        )
        self.shot_target = ft.Screenshot(
            content=ft.Container(
                width=260,
                height=120,
                border_radius=12,
                alignment=ft.Alignment.CENTER,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT,
                    colors=[ft.Colors.PRIMARY, ft.Colors.TERTIARY],
                ),
                content=ft.Text(
                    "Снимок этой области",
                    color=ft.Colors.ON_PRIMARY,
                    weight=ft.FontWeight.BOLD,
                ),
            )
        )
        self.platform_info = ft.Column(spacing=4, tight=True)

        self.controls = [
            page_header(
                "Система",
                "Буфер обмена, локальное хранилище, окно, скриншот "
                "и данные о платформе",
                ft.Icons.SETTINGS_APPLICATIONS_OUTLINED,
            ),
            ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                controls=[
                    section(
                        "Буфер обмена",
                        "Сервис Clipboard читает и пишет системный буфер",
                        [
                            ft.Row(
                                spacing=8,
                                controls=[
                                    self.clipboard_field,
                                    ft.IconButton(
                                        icon=ft.Icons.CONTENT_COPY,
                                        tooltip="Скопировать",
                                        on_click=self._copy,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CONTENT_PASTE,
                                        tooltip="Вставить",
                                        on_click=self._paste,
                                    ),
                                ],
                            ),
                            self.clipboard_result,
                        ],
                        tags=["Clipboard"],
                        col={"md": 6, "xxl": 4},
                    ),
                    section(
                        "Локальное хранилище",
                        "SharedPreferences переживает перезапуск приложения",
                        [
                            ft.Row(
                                spacing=8,
                                controls=[
                                    self.prefs_field,
                                    ft.IconButton(
                                        icon=ft.Icons.SAVE_OUTLINED,
                                        tooltip="Сохранить",
                                        on_click=self._prefs_save,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DOWNLOAD_OUTLINED,
                                        tooltip="Прочитать",
                                        on_click=self._prefs_load,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        tooltip="Удалить",
                                        on_click=self._prefs_clear,
                                    ),
                                ],
                            ),
                            self.prefs_result,
                        ],
                        tags=["SharedPreferences"],
                        col={"md": 6, "xxl": 4},
                    ),
                    section(
                        "Окно приложения",
                        "Управление настоящим окном: размер, центр, полный экран",
                        [
                            ft.Row(
                                wrap=True,
                                spacing=8,
                                run_spacing=8,
                                controls=[
                                    ft.OutlinedButton(
                                        content="1280×860",
                                        icon=ft.Icons.CROP_LANDSCAPE,
                                        on_click=self._resize_window,
                                    ),
                                    ft.OutlinedButton(
                                        content="Развернуть",
                                        icon=ft.Icons.FULLSCREEN,
                                        on_click=self._maximize,
                                    ),
                                    ft.OutlinedButton(
                                        content="Свернуть",
                                        icon=ft.Icons.MINIMIZE,
                                        on_click=self._minimize,
                                    ),
                                    ft.OutlinedButton(
                                        content="Поверх всех",
                                        icon=ft.Icons.PUSH_PIN_OUTLINED,
                                        on_click=self._always_on_top,
                                    ),
                                ],
                            ),
                            ft.Text(
                                "В браузере часть операций с окном недоступна",
                                size=11,
                                color=MUTED,
                            ),
                        ],
                        tags=["Window"],
                        col={"md": 6, "xxl": 4},
                    ),
                    section(
                        "Скриншот",
                        "Screenshot снимает область интерфейса в PNG "
                        "и показывает результат",
                        [
                            self.shot_target,
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.FilledTonalButton(
                                        content="Снять",
                                        icon=ft.Icons.PHOTO_CAMERA_OUTLINED,
                                        on_click=self._capture,
                                    ),
                                ],
                            ),
                            self.shot_image,
                        ],
                        tags=["Screenshot", "Image"],
                        col={"md": 6, "xxl": 4},
                    ),
                    section(
                        "Ссылки и отклик",
                        "Открытие внешних ссылок и тактильный отклик на мобильных",
                        [
                            ft.Row(
                                wrap=True,
                                spacing=8,
                                run_spacing=8,
                                controls=[
                                    ft.FilledTonalButton(
                                        content="Документация Flet",
                                        icon=ft.Icons.OPEN_IN_NEW,
                                        on_click=lambda e: self.page.launch_url(
                                            "https://flet.dev/docs/"
                                        ),
                                    ),
                                    ft.FilledTonalButton(
                                        content="Вибрация",
                                        icon=ft.Icons.VIBRATION,
                                        on_click=self._vibrate,
                                    ),
                                ],
                            ),
                        ],
                        tags=["Page.launch_url", "HapticFeedback"],
                        col={"md": 6, "xxl": 4},
                    ),
                    section(
                        "Платформа",
                        "Что приложение знает о среде, в которой запущено",
                        [self.platform_info],
                        tags=["Page.platform", "PageMediaData"],
                        col={"md": 6, "xxl": 4},
                    ),
                ],
            ),
        ]

    def did_mount(self):
        for service in (self.clipboard, self.prefs, self.haptic):
            if service not in self.page.services:
                self.page.services.append(service)
        self.page.enable_screenshots = True
        self._render_platform()
        self.update()

    # --- буфер обмена ---------------------------------------------------

    async def _copy(self, e):
        await self.clipboard.set(self.clipboard_field.value or "")
        self.clipboard_result.value = "Скопировано в системный буфер"
        self.clipboard_result.update()

    async def _paste(self, e):
        value = await self.clipboard.get()
        self.clipboard_field.value = value or ""
        self.clipboard_result.value = f"Из буфера получено {len(value or '')} символов"
        self.clipboard_field.update()
        self.clipboard_result.update()

    # --- хранилище ------------------------------------------------------

    async def _prefs_save(self, e):
        await self.prefs.set("demo_value", self.prefs_field.value or "")
        self.prefs_result.value = "Сохранено под ключом demo_value"
        self.prefs_result.update()

    async def _prefs_load(self, e):
        value = await self.prefs.get("demo_value")
        self.prefs_result.value = (
            f"Прочитано: {value!r}" if value is not None else "Ключ пока не сохранён"
        )
        self.prefs_result.update()

    async def _prefs_clear(self, e):
        await self.prefs.clear()
        self.prefs_result.value = "Хранилище очищено"
        self.prefs_result.update()

    # --- окно -----------------------------------------------------------

    def _resize_window(self, e):
        self.page.window.width = 1280
        self.page.window.height = 860
        self.page.update()

    def _maximize(self, e):
        self.page.window.maximized = not self.page.window.maximized
        self.page.update()

    def _minimize(self, e):
        self.page.window.minimized = True
        self.page.update()

    def _always_on_top(self, e):
        self.page.window.always_on_top = not self.page.window.always_on_top
        self.page.show_dialog(
            ft.SnackBar(
                content=(
                    "Окно закреплено поверх всех"
                    if self.page.window.always_on_top
                    else "Окно ведёт себя обычно"
                ),
                behavior=ft.SnackBarBehavior.FLOATING,
                width=340,
            )
        )
        self.page.update()

    # --- скриншот и прочее ----------------------------------------------

    async def _capture(self, e):
        data = await self.shot_target.capture()
        self.shot_image.src = data
        self.shot_image.visible = True
        self.shot_image.update()

    async def _vibrate(self, e):
        await self.haptic.medium_impact()

    def _render_platform(self):
        page = self.page
        rows = [
            ("Платформа", str(page.platform).split(".")[-1].lower()),
            ("Режим", "браузер" if page.web else "нативное окно"),
            ("Тема ОС", str(page.platform_brightness).split(".")[-1].lower()),
            ("Размер окна", f"{page.width:.0f} × {page.height:.0f}"),
            ("Маршрут", page.route),
        ]
        self.platform_info.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(name, size=12, color=MUTED),
                    ft.Text(str(value), size=12, font_family="monospace"),
                ],
            )
            for name, value in rows
        ]


def build():
    return ServicesPage()
