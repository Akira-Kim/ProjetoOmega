"""
views/mes.py - Visão mensal
(Parte 4 - ainda esqueleto)
"""

import flet as ft


def build_mes_view(page: ft.Page) -> ft.Control:
    return ft.Column(
        [
            ft.Text("🗓️ Mês", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Aqui vai o calendário mensal (Parte 4).", size=14, color=ft.Colors.GREY_500),
            ft.Divider(),
            ft.Container(
                content=ft.Text("Em construção...", italic=True),
                padding=20,
                alignment=ft.Alignment(0, 0),
                expand=True,
            ),
        ],
        expand=True,
        spacing=10,
    )
