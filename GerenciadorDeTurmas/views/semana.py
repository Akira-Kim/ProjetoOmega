"""
views/semana.py - Visão semanal das aulas
(Parte 3 - ainda esqueleto)
"""

import flet as ft


def build_semana_view(page: ft.Page) -> ft.Control:
    return ft.Column(
        [
            ft.Text("📅 Semana", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Aqui vai a visão semanal das aulas (Parte 3).", size=14, color=ft.Colors.GREY_500),
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
