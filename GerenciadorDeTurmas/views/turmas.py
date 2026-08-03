"""
views/turmas.py - Lista de turmas + alunos + notas/coins
(Parte 5 - ainda esqueleto)
"""

import flet as ft


def build_turmas_view(page: ft.Page) -> ft.Control:
    return ft.Column(
        [
            ft.Text("👥 Turmas", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Gerenciamento de turmas, alunos, notas e coins (Parte 5).", size=14, color=ft.Colors.GREY_500),
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
