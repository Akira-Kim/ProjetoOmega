"""
GerenciadorDeTurmas - main.py
Ponto de entrada do aplicativo.
"""

from pathlib import Path

import flet as ft
from database import inicializar_banco
from views.semana import build_semana_view
from views.mes import build_mes_view
from views.turmas import build_turmas_view
from views.gerenciar import build_gerenciar_view
from views.relatorios import build_relatorios_view
from utils.theme import aplicar_tema, COR_PRIMARIA


def main(page: ft.Page):
    # --- Configuracoes da janela ---
    page.title = "Gerenciador de Turmas"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.window.min_width = 900
    page.window.min_height = 600
    page.window.width = 1100
    page.window.height = 700

    # Icone da janela (PNG ou ICO na pasta assets)
    base = Path(__file__).resolve().parent
    for nome in ("icone.png", "icone.ico"):
        caminho = base / "assets" / nome
        if caminho.exists():
            page.window.icon = str(caminho)
            break

        aplicar_tema(page)

    # Inicializa o banco de dados
    inicializar_banco()

    # --- Conteudo de cada aba ---
    content_area = ft.Container(
        content=build_semana_view(page),
        expand=True,
        padding=24,
        bgcolor="#121218",
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
        min_width=88,
        min_extended_width=190,
        group_alignment=-0.9,
        bgcolor="#16161F",
        indicator_color=COR_PRIMARIA,
        selected_label_text_style=ft.TextStyle(color=COR_PRIMARIA, weight=ft.FontWeight.W_600),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_VIEW_WEEK_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_VIEW_WEEK,
                label="Semana",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label="Mes",
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
                label="Relatorios",
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
    ft.run(main)