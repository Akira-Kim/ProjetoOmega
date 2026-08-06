"""
utils/theme.py - Cores e estilos compartilhados (v1.1)
"""

import flet as ft


# Paleta principal
COR_PRIMARIA = "#0D7377"       # teal
COR_PRIMARIA_CLARA = "#14919B"
COR_DESTAQUE = "#F4A261"       # amber
COR_FUNDO_CARD = "#1E1E2E"     # card escuro
COR_BORDA = "#2A2A3C"
COR_TEXTO_SUAVE = "#9E9EB5"
COR_SUCESSO = "#4CAF50"
COR_AVISO = "#FFC107"
COR_ERRO = "#EF5350"


def aplicar_tema(page: ft.Page):
    """Aplica tema global na pagina."""
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121218"
    page.padding = 0
    page.theme = ft.Theme(
        color_scheme_seed=COR_PRIMARIA,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def titulo_pagina(texto: str) -> ft.Text:
    return ft.Text(texto, size=26, weight=ft.FontWeight.BOLD)


def subtitulo(texto: str) -> ft.Text:
    return ft.Text(texto, size=13, color=COR_TEXTO_SUAVE)


def card(content, **kwargs) -> ft.Container:
    """Card padrao com borda e cantos arredondados."""
    return ft.Container(
        content=content,
        padding=kwargs.pop("padding", 14),
        bgcolor=kwargs.pop("bgcolor", COR_FUNDO_CARD),
        border=kwargs.pop("border", ft.Border.all(1, COR_BORDA)),
        border_radius=kwargs.pop("border_radius", 12),
        **kwargs,
    )


def botao_primario(texto: str, on_click, icon=None) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        texto,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=COR_PRIMARIA,
            color=ft.Colors.WHITE,
            padding=16,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )