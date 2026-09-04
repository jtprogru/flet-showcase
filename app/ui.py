"""Общие строительные блоки интерфейса: заголовки страниц, секции, подписи."""

import flet as ft

MUTED = ft.Colors.ON_SURFACE_VARIANT


def page_header(title, subtitle, icon):
    """Крупный заголовок страницы с иконкой и подзаголовком."""
    return ft.Container(
        padding=ft.Padding.only(bottom=8),
        content=ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=52,
                    height=52,
                    border_radius=16,
                    alignment=ft.Alignment.CENTER,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[ft.Colors.PRIMARY, ft.Colors.TERTIARY],
                    ),
                    content=ft.Icon(icon, color=ft.Colors.ON_PRIMARY, size=26),
                ),
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(title, theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                        ft.Text(subtitle, size=12, color=MUTED),
                    ],
                ),
            ],
        ),
    )


def control_tag(*names):
    """Подпись с именами контролов Flet, которые показаны в секции."""
    return ft.Row(
        wrap=True,
        spacing=6,
        run_spacing=6,
        controls=[
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=6,
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                content=ft.Text(
                    name,
                    size=11,
                    font_family="monospace",
                    color=ft.Colors.ON_SECONDARY_CONTAINER,
                ),
            )
            for name in names
        ],
    )


def section(title, description=None, controls=(), tags=(), col=None):
    """Карточка-секция: заголовок, описание, теги контролов и содержимое."""
    body = [ft.Text(title, weight=ft.FontWeight.BOLD, size=15)]
    if description:
        body.append(ft.Text(description, size=12, color=MUTED))
    if tags:
        body.append(control_tag(*tags))
    body.append(ft.Divider(height=9, thickness=1))
    body.extend(controls)
    card = ft.Card(
        variant=ft.CardVariant.OUTLINED,
        content=ft.Container(
            padding=16,
            content=ft.Column(controls=body, spacing=10, tight=True),
        ),
    )
    if col is not None:
        card.col = col
    return card


def scrollable_page(*controls):
    """Вертикально прокручиваемое тело страницы с внутренними отступами."""
    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        spacing=16,
        controls=list(controls),
    )


def stat_tile(label, value, icon, color, delta=None):
    """Плитка с метрикой для дашборда."""
    trend = []
    if delta is not None:
        up = delta >= 0
        trend = [
            ft.Row(
                spacing=2,
                controls=[
                    ft.Icon(
                        ft.Icons.TRENDING_UP if up else ft.Icons.TRENDING_DOWN,
                        size=14,
                        color=ft.Colors.GREEN if up else ft.Colors.RED,
                    ),
                    ft.Text(
                        f"{delta:+.1f}%",
                        size=11,
                        color=ft.Colors.GREEN if up else ft.Colors.RED,
                    ),
                ],
            )
        ]
    return ft.Card(
        content=ft.Container(
            padding=16,
            content=ft.Column(
                spacing=6,
                tight=True,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(label, size=12, color=MUTED),
                            ft.Icon(icon, size=18, color=color),
                        ],
                    ),
                    ft.Text(value, theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                    *trend,
                ],
            ),
        ),
    )
