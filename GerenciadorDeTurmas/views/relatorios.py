"""
views/relatorios.py - Histórico de relatórios + geração com IA
(Parte 6 e 7 - ainda esqueleto)
"""

import flet as ft


def build_relatorios_view(page: ft.Page) -> ft.Control:
    return ft.Column(
        [
            ft.Text("📄 Relatórios", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Histórico de relatórios de aula e geração de relatório de aluno com IA (Partes 6 e 7).", size=14, color=ft.Colors.GREY_500),
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
