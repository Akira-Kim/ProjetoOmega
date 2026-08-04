"""
views/relatorios.py - Historico de relatorios de aula
Parte 6
"""

import flet as ft

from models import (
    listar_relatorios,
    obter_relatorio,
    atualizar_relatorio,
    excluir_relatorio,
    listar_turmas,
    obter_aula,
)


def build_relatorios_view(page: ft.Page) -> ft.Control:
    lista_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    painel = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    mensagem = ft.Text("", size=12)

    dd_turma = ft.Dropdown(
        label="Filtrar por turma",
        width=220,
        options=[ft.dropdown.Option("", "Todas")],
    )

    def mostrar_msg(texto: str, cor=ft.Colors.GREEN_400):
        mensagem.value = texto
        mensagem.color = cor
        try:
            mensagem.update()
        except Exception:
            pass

    def carregar_filtro_turmas():
        opts = [ft.dropdown.Option(key="", text="Todas")]
        for t in listar_turmas():
            opts.append(ft.dropdown.Option(key=str(t["id"]), text=t["nome"]))
        dd_turma.options = opts

    def atualizar_lista(e=None):
        lista_col.controls.clear()

        valor = dd_turma.value
        turma_id = None
        if valor not in (None, ""):
            try:
                turma_id = int(valor)
            except (TypeError, ValueError):
                turma_id = None

        rels = listar_relatorios(tipo="aula", turma_id=turma_id)

        if not rels:
            lista_col.controls.append(
                ft.Text("Nenhum relatorio com este filtro.", italic=True, color=ft.Colors.GREY_500)
            )
        else:
            for r in rels:
                lista_col.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(r.get("titulo") or "Sem titulo", weight=ft.FontWeight.BOLD, size=13),
                                ft.Text(
                                    f"{r.get('data_geracao') or ''}  |  id={r['id']}",
                                    size=11,
                                    color=ft.Colors.GREY_500,
                                ),
                            ],
                            spacing=2,
                        ),
                        padding=10,
                        border=ft.Border.all(1, ft.Colors.GREY_800),
                        border_radius=8,
                        data=r["id"],
                        on_click=on_abrir,
                        ink=True,
                    )
                )
        try:
            lista_col.update()
        except Exception:
            pass

        painel.controls.clear()
        painel.controls.append(
            ft.Text("Selecione um relatorio a esquerda.", italic=True, color=ft.Colors.GREY_500)
        )
        try:
            painel.update()
        except Exception:
            pass

    # Dropdown com key/text explicitos
    dd_turma = ft.Dropdown(
        label="Filtrar por turma",
        width=220,
        options=[ft.dropdown.Option(key="", text="Todas")],
        value="",
        on_change=atualizar_lista,
    )
    def on_abrir(e):
        rid = e.control.data
        r = obter_relatorio(rid)
        if not r:
            mostrar_msg("Relatorio nao encontrado.", ft.Colors.RED_400)
            return

        tf_titulo = ft.TextField(label="Titulo", value=r.get("titulo") or "", text_size=13)
        tf_conteudo = ft.TextField(
            label="Conteudo",
            value=r.get("conteudo") or "",
            multiline=True,
            min_lines=8,
            max_lines=20,
            text_size=13,
            expand=True,
        )

        info_aula = ""
        if r.get("aula_id"):
            aula = obter_aula(r["aula_id"])
            if aula:
                info_aula = f"Aula: {aula.get('turma_nome')} — {aula.get('data')}"

        def on_salvar(ev):
            try:
                atualizar_relatorio(rid, titulo=tf_titulo.value or "", conteudo=tf_conteudo.value or "")
                mostrar_msg("Relatorio atualizado.")
                atualizar_lista()
            except Exception as ex:
                mostrar_msg(f"Erro: {ex}", ft.Colors.RED_400)

        def on_excluir(ev):
            excluir_relatorio(rid)
            mostrar_msg("Relatorio excluido.", ft.Colors.ORANGE_400)
            atualizar_lista()

        painel.controls.clear()
        painel.controls.extend(
            [
                ft.Text("Editar relatorio", size=16, weight=ft.FontWeight.W_600),
                ft.Text(info_aula, size=12, color=ft.Colors.GREY_400) if info_aula else ft.Container(),
                tf_titulo,
                tf_conteudo,
                ft.Row(
                    [
                        ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, on_click=on_salvar),
                        ft.OutlinedButton(
                            "Excluir",
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=on_excluir,
                        ),
                    ],
                    spacing=10,
                ),
            ]
        )
        try:
            painel.update()
        except Exception:
            pass

    # carga inicial
    carregar_filtro_turmas()
    rels = listar_relatorios(tipo="aula")
    if not rels:
        lista_col.controls.append(
            ft.Text("Nenhum relatorio ainda.", italic=True, color=ft.Colors.GREY_500)
        )
    else:
        for r in rels:
            lista_col.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(r.get("titulo") or "Sem titulo", weight=ft.FontWeight.BOLD, size=13),
                            ft.Text(
                                f"{r.get('data_geracao') or ''}  |  id={r['id']}",
                                size=11,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        spacing=2,
                    ),
                    padding=10,
                    border=ft.Border.all(1, ft.Colors.GREY_800),
                    border_radius=8,
                    data=r["id"],
                    on_click=on_abrir,
                    ink=True,
                )
            )
    painel.controls.append(
        ft.Text("Selecione um relatorio a esquerda.", italic=True, color=ft.Colors.GREY_500)
    )

    dd_turma.on_change = atualizar_lista

    return ft.Column(
        [
            ft.Text("Relatorios", size=26, weight=ft.FontWeight.BOLD),
            ft.Text("Historico de relatorios de aula.", size=13, color=ft.Colors.GREY_500),
            mensagem,
            ft.Row([dd_turma, ft.TextButton("Atualizar", on_click=atualizar_lista)]),
            ft.Divider(height=1),
            ft.Row(
                [
                    ft.Column([lista_col], width=300),
                    ft.VerticalDivider(width=1),
                    painel,
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=8,
    )