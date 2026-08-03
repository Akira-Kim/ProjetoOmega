"""
GerenciadorDeTurmas - main.py
Ponto de entrada do aplicativo.
Parte 1: Fundação (navegação + banco)
"""

import flet as ft
from database import inicializar_banco
from views.semana import build_semana_view
from views.mes import build_mes_view
from views.turmas import build_turmas_view
from views.gerenciar import build_gerenciar_view
from views.relatorios import build_relatorios_view


def main(page: ft.Page):
    # --- Configurações da janela ---
    page.title = "Gerenciador de Turmas"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.window.min_width = 900
    page.window.min_height = 600
    page.window.width = 1100
    page.window.height = 700

    # Inicializa o banco de dados
    inicializar_banco()

    # --- Conteúdo de cada aba ---
    content_area = ft.Container(
        content=build_semana_view(page),
        expand=True,
        padding=20,
    )

    def trocar_aba(e):
        index = e.control.selected_index
        if index == 0:
            content_area.content = build_semana_view(page)
        elif index == 1:
            content_area.content = build_mes_view(page)
        elif index == 2:
            content_area.content = build_turmas_view(page)
        elif index == 3:
            content_area.content = build_gerenciar_view(page)
        elif index == 4:
            content_area.content = build_relatorios_view(page)
        content_area.update()

    # --- NavigationRail (menu lateral) ---
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=180,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_VIEW_WEEK_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_VIEW_WEEK,
                label="Semana",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label="Mês",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.GROUPS_OUTLINED,
                selected_icon=ft.Icons.GROUPS,
                label="Turmas",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Gerenciar",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.DESCRIPTION_OUTLINED,
                selected_icon=ft.Icons.DESCRIPTION,
                label="Relatórios",
            ),
        ],
        on_change=trocar_aba,
    )

    # --- Layout principal ---
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
