"""
views/mes.py - Visao mensal
Parte 4
"""

import flet as ft
from datetime import date, timedelta
from calendar import monthrange

from models import listar_aulas_periodo, listar_eventos
from utils.calendar_helpers import get_mes_calendario


NOMES_MESES = [
    "", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
NOMES_DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]


def build_mes_view(page: ft.Page) -> ft.Control:
    hoje = date.today()
    estado = {"ano": hoje.year, "mes": hoje.month}

    titulo = ft.Text("", size=18, weight=ft.FontWeight.W_600)
    grade = ft.Column(spacing=4, expand=True, scroll=ft.ScrollMode.AUTO)
    painel_dia = ft.Column(
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    mensagem = ft.Text("", size=12, color=ft.Colors.GREY_400)

    def mostrar_msg(texto: str, cor=ft.Colors.GREEN_400):
        mensagem.value = texto
        mensagem.color = cor
        try:
            mensagem.update()
        except Exception:
            pass

    def cor_indicador_aula(aula: dict) -> str:
        d = date.fromisoformat(aula["data"])
        if aula.get("dada"):
            return "#4CAF50"
        if d < hoje:
            return "#78909C"
        # mesma semana civil aproximada: amarelo se for este mes e futuro/hoje
        if d.month == hoje.month and d.year == hoje.year and d >= hoje:
            return "#FFC107"
        return "#B0BEC5"

    def cor_evento(tipo: str) -> str:
        if tipo in ("reposicao", "monitoria"):
            return "#FF9800"
        return "#9C27B0"

    def abrir_dia(dia: date):
        painel_dia.controls.clear()
        painel_dia.controls.append(
            ft.Text(
                f"Dia {dia.strftime('%d/%m/%Y')}",
                size=16,
                weight=ft.FontWeight.W_600,
            )
        )

        inicio = dia.isoformat()
        fim = dia.isoformat()
        aulas = listar_aulas_periodo(inicio, fim)
        eventos = listar_eventos(inicio, fim)

        if not aulas and not eventos:
            painel_dia.controls.append(
                ft.Text("Nada neste dia.", italic=True, color=ft.Colors.GREY_500)
            )
        else:
            for ev in eventos:
                painel_dia.controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"[{ev['tipo']}] {ev['titulo']}",
                            size=12,
                            color=ft.Colors.WHITE,
                        ),
                        bgcolor=cor_evento(ev.get("tipo") or "evento"),
                        padding=8,
                        border_radius=6,
                    )
                )
            for a in aulas:
                status = []
                if a.get("estudada"):
                    status.append("estudada")
                if a.get("dada"):
                    status.append("dada")
                status_txt = ", ".join(status) if status else "planejada"
                painel_dia.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    a.get("turma_nome") or "Turma",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK87,
                                ),
                                ft.Text(
                                    f"{a.get('disciplina') or ''} — {status_txt}",
                                    size=11,
                                    color=ft.Colors.BLACK54,
                                ),
                            ],
                            spacing=2,
                        ),
                        bgcolor=cor_indicador_aula(a),
                        padding=8,
                        border_radius=6,
                    )
                )

        try:
            painel_dia.update()
        except Exception:
            pass
        mostrar_msg(f"Selecionado: {dia.strftime('%d/%m/%Y')}")

    def renderizar():
        ano, mes = estado["ano"], estado["mes"]
        titulo.value = f"{NOMES_MESES[mes]} {ano}"

        # primeiro e ultimo dia do mes
        ultimo = monthrange(ano, mes)[1]
        inicio_mes = date(ano, mes, 1)
        fim_mes = date(ano, mes, ultimo)

        aulas = listar_aulas_periodo(inicio_mes.isoformat(), fim_mes.isoformat())
        eventos = listar_eventos(inicio_mes.isoformat(), fim_mes.isoformat())

        aulas_por_dia = {}
        for a in aulas:
            aulas_por_dia.setdefault(a["data"], []).append(a)

        eventos_por_dia = {}
        for ev in eventos:
            eventos_por_dia.setdefault(ev["data"], []).append(ev)

        matriz = get_mes_calendario(ano, mes)

        grade.controls.clear()

        # cabecalho dos dias
        header = ft.Row(
            [
                ft.Container(
                    content=ft.Text(n, size=11, weight=ft.FontWeight.BOLD),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                )
                for n in NOMES_DIAS
            ],
            spacing=4,
        )
        grade.controls.append(header)

        for semana in matriz:
            linha = []
            for dia in semana:
                if dia is None:
                    linha.append(ft.Container(expand=True, height=72))
                    continue

                iso = dia.isoformat()
                is_hoje = dia == hoje
                n_aulas = len(aulas_por_dia.get(iso, []))
                n_ev = len(eventos_por_dia.get(iso, []))

                # bolinhas (max 4 visiveis)
                bolinhas = []
                for a in aulas_por_dia.get(iso, [])[:3]:
                    bolinhas.append(
                        ft.Container(
                            width=8,
                            height=8,
                            bgcolor=cor_indicador_aula(a),
                            border_radius=4,
                        )
                    )
                for ev in eventos_por_dia.get(iso, [])[:2]:
                    bolinhas.append(
                        ft.Container(
                            width=8,
                            height=8,
                            bgcolor=cor_evento(ev.get("tipo") or "evento"),
                            border_radius=4,
                        )
                    )
                extra = n_aulas + n_ev - len(bolinhas)
                if extra > 0:
                    bolinhas.append(
                        ft.Text(f"+{extra}", size=9, color=ft.Colors.GREY_400)
                    )

                celula = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                str(dia.day),
                                size=12,
                                weight=ft.FontWeight.BOLD if is_hoje else None,
                                color=ft.Colors.BLUE_300 if is_hoje else None,
                            ),
                            ft.Row(bolinhas, spacing=2, wrap=True),
                        ],
                        spacing=4,
                    ),
                    padding=6,
                    expand=True,
                    height=72,
                    border=ft.Border.all(
                        2 if is_hoje else 1,
                        ft.Colors.BLUE_400 if is_hoje else ft.Colors.GREY_800,
                    ),
                    border_radius=8,
                    data=dia,
                    on_click=lambda e, d=dia: abrir_dia(d),
                    ink=True,
                )
                linha.append(celula)

            grade.controls.append(ft.Row(linha, spacing=4, expand=True))

        try:
            titulo.update()
            grade.update()
        except Exception:
            pass

    def mes_anterior(e):
        m = estado["mes"] - 1
        a = estado["ano"]
        if m < 1:
            m = 12
            a -= 1
        estado["mes"], estado["ano"] = m, a
        renderizar()

    def mes_proximo(e):
        m = estado["mes"] + 1
        a = estado["ano"]
        if m > 12:
            m = 1
            a += 1
        estado["mes"], estado["ano"] = m, a
        renderizar()

    def mes_hoje(e):
        estado["ano"] = hoje.year
        estado["mes"] = hoje.month
        renderizar()
        abrir_dia(hoje)

    # carga inicial
    renderizar()
    painel_dia.controls.append(
        ft.Text("Clique num dia para ver o resumo.", italic=True, color=ft.Colors.GREY_500)
    )

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Mes", size=26, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=mes_anterior, tooltip="Mes anterior"),
                    titulo,
                    ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=mes_proximo, tooltip="Proximo mes"),
                    ft.TextButton("Hoje", on_click=mes_hoje),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            mensagem,
            ft.Divider(height=1),
            ft.Row(
                [
                    ft.Container(content=grade, expand=3, padding=4),
                    ft.VerticalDivider(width=1),
                    ft.Container(content=painel_dia, expand=2, padding=8),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=8,
    )