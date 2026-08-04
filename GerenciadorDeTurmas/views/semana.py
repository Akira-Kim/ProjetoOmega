"""
views/semana.py - Visao semanal das aulas
Parte 3 (completa com detalhe + alunos)
"""

import flet as ft
from datetime import date, timedelta

from models import (
    listar_aulas_periodo,
    listar_eventos,
    obter_aula,
    atualizar_aula,
    listar_alunos_com_registro,
    salvar_registro_aula,
    criar_relatorio_aula,
    listar_relatorios,
)
from utils.calendar_helpers import get_semana_atual


NOMES_DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]


def _cor_aula(aula: dict, semana: list) -> str:
    hoje = date.today()
    data_aula = date.fromisoformat(aula["data"])
    if aula.get("dada"):
        return "#4CAF50"
    if data_aula < hoje:
        return "#78909C"
    if data_aula in semana:
        return "#FFC107"
    return "#ECEFF1"


def _cor_evento(tipo: str) -> str:
    if tipo in ("reposicao", "monitoria"):
        return "#FF9800"
    return "#9C27B0"


def build_semana_view(page: ft.Page) -> ft.Control:
    estado = {"segunda": get_semana_atual()[0]}

    titulo_semana = ft.Text("", size=16, weight=ft.FontWeight.W_600)
    grade = ft.Row(expand=True, spacing=6, vertical_alignment=ft.CrossAxisAlignment.START)
    mensagem = ft.Text("", size=12, color=ft.Colors.GREY_400)

    painel_detalhe = ft.Container(
        content=ft.Text("Clique numa aula para ver detalhes.", italic=True, color=ft.Colors.GREY_500),
        width=340,
        padding=12,
        border=ft.Border.all(1, ft.Colors.GREY_800),
        border_radius=10,
    )

    def mostrar_msg(texto: str, cor=ft.Colors.GREEN_400):
        mensagem.value = texto
        mensagem.color = cor
        try:
            mensagem.update()
        except Exception:
            pass

    def fechar_detalhe(e=None):
        painel_detalhe.content = ft.Text(
            "Clique numa aula para ver detalhes.",
            italic=True,
            color=ft.Colors.GREY_500,
        )
        try:
            painel_detalhe.update()
        except Exception:
            pass

    def abrir_detalhe(aula_id: int):
        aula = obter_aula(aula_id)
        if not aula:
            mostrar_msg("Aula nao encontrada.", ft.Colors.RED_400)
            return

        tf_conteudo = ft.TextField(
            label="Conteudo / o que estudar",
            value=aula.get("conteudo") or "",
            multiline=True,
            min_lines=2,
            max_lines=5,
            text_size=13,
        )
        tf_links = ft.TextField(
            label="Links (separados por ;)",
            value=aula.get("links") or "",
            text_size=13,
        )
        tf_obs = ft.TextField(
            label="Observacao da aula",
            value=aula.get("observacao") or "",
            multiline=True,
            min_lines=1,
            max_lines=3,
            text_size=13,
            
        )
        cb_estudada = ft.Checkbox(label="Ja estudei", value=bool(aula.get("estudada")))
        cb_dada = ft.Checkbox(label="Aula dada", value=bool(aula.get("dada")))

        # ----- alunos -----
        alunos_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
        linhas_alunos = []
        turma_id = aula.get("turma_id")

        try:
            lista = listar_alunos_com_registro(aula_id, turma_id) if turma_id else []
        except Exception:
            lista = []

        if not lista:
            alunos_col.controls.append(
                ft.Text(
                    "Nenhum aluno nesta turma. Cadastre em Turmas.",
                    size=12,
                    italic=True,
                    color=ft.Colors.GREY_500,
                )
            )
        else:
            for item in lista:
                tf_nota = ft.TextField(
                    label="Nota",
                    value="" if item["nota_dia"] is None else str(item["nota_dia"]),
                    width=80,
                    text_size=13,
                )
                tf_coins = ft.TextField(
                    label="Coins",
                    value=str(item.get("coins") if item.get("coins") is not None else 0),
                    width=80,
                    text_size=13,
                )
                tf_analise = ft.TextField(
                    label="Analise / obs. aluno",
                    value=item.get("analise") or "",
                    text_size=13,
                    expand=True,
                    multiline=True,
                    min_lines=1,
                    max_lines=2,
                )
                linhas_alunos.append({
                    "aluno_id": item["aluno_id"],
                    "nota": tf_nota,
                    "coins": tf_coins,
                    "analise": tf_analise,
                })
                alunos_col.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(item["nome"], size=12, weight=ft.FontWeight.W_500),
                                ft.Row([tf_nota, tf_coins], spacing=6),
                                tf_analise,
                            ],
                            spacing=4,
                        ),
                        padding=8,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=6,
                    )
                )        
            tf_relatorio = ft.TextField(
            label="Texto do relatorio (o que rolou na aula)",
            multiline=True,
            min_lines=3,
            max_lines=6,
            text_size=13,
        )
        # se ja existir relatorio desta aula, mostra o ultimo
        try:
            existentes = listar_relatorios(tipo="aula", aula_id=aula_id)
            if existentes:
                tf_relatorio.value = existentes[0].get("conteudo") or ""
        except Exception:
            pass

        def on_salvar_relatorio(e):
            try:
                criar_relatorio_aula(
                    aula_id=aula_id,
                    conteudo=tf_relatorio.value or "",
                    turma_id=aula.get("turma_id"),
                )
                mostrar_msg("Relatorio da aula salvo! Veja na aba Relatorios.")
            except Exception as ex:
                mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)
                
                

        def on_salvar(e):
            estudada = 1 if cb_estudada.value else 0
            dada = 1 if cb_dada.value else 0
            status = "dada" if dada else ("estudada" if estudada else "planejada")
            try:
                atualizar_aula(
                    aula_id,
                    conteudo=tf_conteudo.value or "",
                    links=tf_links.value or "",
                    observacao=tf_obs.value or "",
                    estudada=estudada,
                    dada=dada,
                    status=status,
                )
                for lin in linhas_alunos:
                    nota_raw = (lin["nota"].value or "").strip()
                    coins_raw = (lin["coins"].value or "0").strip()
                    nota = float(nota_raw.replace(",", ".")) if nota_raw else None
                    try:
                        coins = int(float(coins_raw)) if coins_raw else 0
                    except ValueError:
                        coins = 0
                    salvar_registro_aula(
                        aula_id,
                        lin["aluno_id"],
                        nota_dia=nota,
                        coins=coins,
                        analise=lin["analise"].value or "",
                    )
                mostrar_msg("Salvo! Clique de novo na aula para continuar editando.")
                renderizar()
                # nao reabre o painel sozinho (evita trava dos campos)
            except Exception as ex:
                mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

        painel_detalhe.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Detalhe da aula", size=16, weight=ft.FontWeight.W_600, expand=True),
                        ft.IconButton(ft.Icons.CLOSE, icon_size=18, on_click=fechar_detalhe),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text(
                    f"{aula.get('turma_nome') or ''} — {aula.get('disciplina') or ''}",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(f"Data: {aula['data']}", size=12, color=ft.Colors.GREY_400),
                ft.Divider(height=1),
                cb_estudada,
                cb_dada,
                tf_conteudo,
                tf_links,
                tf_obs,
                ft.Divider(height=1),
                ft.Text("Relatorio da aula", size=13, weight=ft.FontWeight.W_600),
                tf_relatorio,
                ft.OutlinedButton(
                    "Salvar relatorio da aula",
                    icon=ft.Icons.DESCRIPTION,
                    on_click=on_salvar_relatorio,
                ),
                ft.Divider(height=1),
                ft.Text("Alunos (nota / coins / analise)", size=13, weight=ft.FontWeight.W_600),
                alunos_col,
                ft.ElevatedButton("Salvar tudo", icon=ft.Icons.SAVE, on_click=on_salvar),
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        try:
            painel_detalhe.update()
        except Exception:
            pass

    def on_click_aula(e):
        aula_id = e.control.data
        if aula_id:
            abrir_detalhe(aula_id)

    def montar_card_aula(aula: dict, semana: list) -> ft.Container:
        cor = _cor_aula(aula, semana)
        tem_conteudo = bool(aula.get("conteudo") or aula.get("links"))
        indicadores = []
        if aula.get("estudada"):
            indicadores.append(ft.Icon(ft.Icons.MENU_BOOK, size=12, color=ft.Colors.BLUE_700))
        if tem_conteudo:
            indicadores.append(ft.Icon(ft.Icons.ATTACHMENT, size=12, color=ft.Colors.GREY_700))
        if aula.get("dada"):
            indicadores.append(ft.Icon(ft.Icons.CHECK_CIRCLE, size=12, color=ft.Colors.GREEN_800))

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        aula.get("turma_nome") or "Turma",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLACK87,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        aula.get("disciplina") or "",
                        size=10,
                        color=ft.Colors.BLACK54,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Row(indicadores, spacing=2) if indicadores else ft.Container(height=12),
                ],
                spacing=2,
            ),
            bgcolor=cor,
            padding=6,
            border_radius=6,
            width=110,
            data=aula["id"],
            on_click=on_click_aula,
            ink=True,
            tooltip=f"{aula.get('turma_nome')} — {aula['data']}",
        )

    def montar_card_evento(ev: dict) -> ft.Container:
        return ft.Container(
            content=ft.Text(
                ev["titulo"],
                size=10,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.WHITE,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            bgcolor=_cor_evento(ev.get("tipo") or "evento"),
            padding=5,
            border_radius=6,
            width=110,
            tooltip=f"{ev['tipo']}: {ev['titulo']}",
        )

    def renderizar():
        segunda = estado["segunda"]
        semana = [segunda + timedelta(days=i) for i in range(7)]
        inicio_s = semana[0].isoformat()
        fim_s = semana[6].isoformat()

        titulo_semana.value = f"{semana[0].strftime('%d/%m')} — {semana[6].strftime('%d/%m/%Y')}"

        aulas = listar_aulas_periodo(inicio_s, fim_s)
        eventos = listar_eventos(inicio_s, fim_s)

        aulas_por_dia = {d.isoformat(): [] for d in semana}
        for a in aulas:
            if a["data"] in aulas_por_dia:
                aulas_por_dia[a["data"]].append(a)

        eventos_por_dia = {d.isoformat(): [] for d in semana}
        for ev in eventos:
            if ev["data"] in eventos_por_dia:
                eventos_por_dia[ev["data"]].append(ev)

        grade.controls.clear()
        hoje = date.today()

        for i, dia in enumerate(semana):
            is_hoje = dia == hoje
            header = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(NOMES_DIAS[i], size=12, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            dia.strftime("%d/%m"),
                            size=11,
                            color=ft.Colors.BLUE_300 if is_hoje else ft.Colors.GREY_400,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                padding=6,
                border_radius=6,
            )

            cards = []
            for ev in eventos_por_dia[dia.isoformat()]:
                cards.append(montar_card_evento(ev))
            for a in aulas_por_dia[dia.isoformat()]:
                cards.append(montar_card_aula(a, semana))

            coluna = ft.Container(
                content=ft.Column(
                    [header] + cards,
                    spacing=4,
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True,
                padding=4,
                border=ft.Border.all(1, ft.Colors.GREY_800),
                border_radius=8,
            )
            grade.controls.append(coluna)

        try:
            titulo_semana.update()
            grade.update()
        except Exception:
            pass

    def semana_anterior(e):
        estado["segunda"] = estado["segunda"] - timedelta(days=7)
        renderizar()

    def semana_proxima(e):
        estado["segunda"] = estado["segunda"] + timedelta(days=7)
        renderizar()

    def semana_hoje(e):
        estado["segunda"] = get_semana_atual()[0]
        renderizar()

    renderizar()

    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Semana", size=26, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=semana_anterior, tooltip="Semana anterior"),
                    titulo_semana,
                    ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=semana_proxima, tooltip="Proxima semana"),
                    ft.TextButton("Hoje", on_click=semana_hoje),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            mensagem,
            ft.Divider(height=1),
            ft.Row(
                [grade, painel_detalhe],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=8,
    )